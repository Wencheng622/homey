from __future__ import annotations

from django.contrib.auth import login, logout
from django.db import IntegrityError
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.authentication import SessionAuthentication
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from users.serializers import (
    RegisterSerializer,
    UserRegistrationResponseSerializer,
    LoginSerializer,
    LoginResponseSerializer,
    GoogleRegisterSerializer,
    GoogleRegisterResponseSerializer,
)
from users.services import (
    register_email_password_user,
    verify_google_id_token,
    register_google_user,
    GoogleTokenVerificationError,
    GoogleRegistrationConflictError,
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
