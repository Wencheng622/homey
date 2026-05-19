from __future__ import annotations

from django.contrib.auth import login, logout
from django.db import IntegrityError
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.authentication import SessionAuthentication
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from users.exceptions import AdminInvitationUserExistsError
from users.permissions import IsAdminRole
from users.serializers import (
    AdminInvitationCreateSerializer,
    AdminInvitationResponseSerializer,
    RegisterSerializer,
    UserRegistrationResponseSerializer,
    LoginSerializer,
    LoginResponseSerializer,
    GoogleRegisterSerializer,
    GoogleRegisterResponseSerializer,
    GoogleLoginSerializer,
)
from users.services import (
    create_admin_invitation,
    register_email_password_user,
    verify_google_id_token,
    register_google_user,
    login_google_user,
    GoogleTokenVerificationError,
    GoogleRegistrationConflictError,
    GoogleLoginNotFoundError,
    GoogleLoginConflictError,
    GoogleLoginSuspendedError,
)


@method_decorator(csrf_exempt, name="dispatch")
class RegisterView(APIView):
    """
    CSRF exempt: JSON API signup without browser CSRF token round-trip.
    Rate-limit in production if exposed publicly.
    """
    permission_classes = [AllowAny]
    authentication_classes = []

    @extend_schema(
        request=RegisterSerializer,
        responses={201: UserRegistrationResponseSerializer},
        summary="register",
        description="Register a new account using an email and password. Only the roles of tenant or landlord can be registered."
    )

    def post(self, request, *args, **kwargs):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        try:
            user = register_email_password_user(
                email=data["email"],
                password=data["password"],
                role=data["role"],
                name=data["name"],
            )
        except IntegrityError:
            raise ValidationError(
                {"email": ["A user with this email already exists."]},
            ) from None
        out = UserRegistrationResponseSerializer(user)
        return Response(out.data, status=status.HTTP_201_CREATED)


@method_decorator(csrf_exempt, name="dispatch")
class LoginView(APIView):
    """
    CSRF exempt: JSON API login without CSRF cookie/header (consistent with RegisterView).
    Establishes a Django session (sessionid cookie, HttpOnly, Secure per settings).
    """
    permission_classes = [AllowAny]
    authentication_classes = []

    @extend_schema(
        request=LoginSerializer,
        responses={200: LoginResponseSerializer},
        summary="login",
        description=(
            "Log in with email and password. Returns user JSON and sets an HttpOnly "
            "session cookie (24-hour expiry per SESSION_COOKIE_AGE)."
        ),
    )
    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]

        login(request, user)

        out = LoginResponseSerializer(user)
        return Response(out.data, status=status.HTTP_200_OK)


@method_decorator(csrf_exempt, name="dispatch")
class LogoutView(APIView):
    """
    CSRF exempt: session-authenticated JSON logout without CSRF header on POST.
    """
    permission_classes = [IsAuthenticated]
    authentication_classes = [SessionAuthentication]

    @extend_schema(
        request=None,
        responses={204: None},
        summary="logout",
        description="End the current session and clear the session cookie.",
    )
    def post(self, request, *args, **kwargs):
        logout(request)
        return Response(status=status.HTTP_204_NO_CONTENT)


class GoogleRegisterView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    @extend_schema(
        request=GoogleRegisterSerializer,
        responses={201: GoogleRegisterResponseSerializer},
        summary="google register",
        description=(
            "Register or link an account using a Google ID token. "
            "Does not log the user in or issue tokens."
        ),
    )
    def post(self, request, *args, **kwargs):
        serializer = GoogleRegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        try:
            claims = verify_google_id_token(data["id_token"])
        except GoogleTokenVerificationError:
            raise ValidationError(
                {"id_token": ["Invalid or expired Google ID token."]},
            ) from None

        try:
            user = register_google_user(
                google_id=claims["google_id"],
                email=claims["email"],
                name=claims["name"],
                picture=claims["picture"],
                email_verified=claims["email_verified"],
                role=data["role"],
            )
        except GoogleRegistrationConflictError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_409_CONFLICT)
        except IntegrityError:
            raise ValidationError(
                {"email": ["A user with this email already exists."]},
            ) from None

        out = GoogleRegisterResponseSerializer(user)
        return Response(out.data, status=status.HTTP_201_CREATED)


@method_decorator(csrf_exempt, name="dispatch")
class GoogleLoginView(APIView):
    """
    CSRF exempt: JSON API Google login (consistent with LoginView).
    Establishes a Django session; does not create new users.
    """
    permission_classes = [AllowAny]
    authentication_classes = []

    @extend_schema(
        request=GoogleLoginSerializer,
        responses={200: LoginResponseSerializer},
        summary="google login",
        description=(
            "Log in with a Google ID token. Returns user JSON and sets an HttpOnly "
            "session cookie (24-hour expiry per SESSION_COOKIE_AGE). "
            "Account must already exist (use google register first)."
        ),
    )
    def post(self, request, *args, **kwargs):
        serializer = GoogleLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            claims = verify_google_id_token(serializer.validated_data["id_token"])
        except GoogleTokenVerificationError:
            raise ValidationError(
                {"id_token": ["Invalid or expired Google ID token."]},
            ) from None

        try:
            user = login_google_user(
                google_id=claims["google_id"],
                email=claims["email"],
                name=claims["name"],
                picture=claims["picture"],
                email_verified=claims["email_verified"],
            )
        except GoogleLoginNotFoundError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_401_UNAUTHORIZED)
        except GoogleLoginConflictError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_409_CONFLICT)
        except GoogleLoginSuspendedError as exc:
            raise PermissionDenied(detail=str(exc))

        login(request, user)

        out = LoginResponseSerializer(user)
        return Response(out.data, status=status.HTTP_200_OK)


class AdminInvitationCreateView(APIView):
    """
    Session-authenticated admin endpoint. CSRF required (not csrf_exempt).
    """

    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated, IsAdminRole]

    @extend_schema(
        request=AdminInvitationCreateSerializer,
        responses={201: AdminInvitationResponseSerializer},
        summary="send admin invitation",
        description=(
            "Invite a new admin by email. Revokes prior pending invitations for "
            "the same email and sends an invitation link by email."
        ),
    )
    def post(self, request, *args, **kwargs):
        serializer = AdminInvitationCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            invitation = create_admin_invitation(
                email=serializer.validated_data["email"],
                created_by=request.user,
            )
        except AdminInvitationUserExistsError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_409_CONFLICT)
        except IntegrityError:
            return Response(
                {"detail": "Could not create invitation due to a conflict. Please retry."},
                status=status.HTTP_409_CONFLICT,
            )

        out = AdminInvitationResponseSerializer(invitation)
        return Response(out.data, status=status.HTTP_201_CREATED)
