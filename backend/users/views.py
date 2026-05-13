from __future__ import annotations

from django.db import IntegrityError
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from users.serializers import RegisterSerializer, UserRegistrationResponseSerializer
from users.services import register_email_password_user


class RegisterView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

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
