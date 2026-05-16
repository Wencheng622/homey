from __future__ import annotations

from django.db import IntegrityError
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema

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


class RegisterView(APIView):
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
    
class LoginView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    @extend_schema(
        request=LoginSerializer,
        responses={200: LoginResponseSerializer},
        summary="login",
        description="Log in with email and password to retrieve user information."
    )

    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        
        out = LoginResponseSerializer(user)
        return Response(out.data, status=status.HTTP_200_OK)


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
