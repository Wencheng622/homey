from __future__ import annotations

from django.contrib.auth import password_validation
from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied
from django.contrib.auth import authenticate

from users.models import User, UserRole, UserStatus
from users.services import normalize_email


class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=254)
    password = serializers.CharField(write_only=True, style={"input_type": "password"})
    role = serializers.CharField(max_length=32)
    name = serializers.CharField(max_length=120, min_length=1, trim_whitespace=True)

    def validate_email(self, value: str) -> str:
        normalized = normalize_email(value)
        if User.objects.filter(email_normalized=normalized).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return normalized

    def validate_password(self, value: str) -> str:
        try:
            password_validation.validate_password(value, user=None)
        except password_validation.ValidationError as exc:
            raise serializers.ValidationError(list(exc.messages))
        return value

    def validate_role(self, value: str) -> str:
        role = value.strip()
        if role == UserRole.ADMIN:
            raise PermissionDenied(detail="Admin accounts cannot be self-registered.")
        if role not in (UserRole.TENANT, UserRole.LANDLORD):
            raise serializers.ValidationError("Role must be tenant or landlord.")
        return role


class UserRegistrationResponseSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source="profile.display_name", read_only=True)

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "role",
            "status",
            "is_email_verified",
            "name",
            "created_at",
        )
        read_only_fields = fields

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=254)
    password = serializers.CharField(write_only=True, style={"input_type": "password"})

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")
        
        normalized_email = normalize_email(email)
        
        try:
            user = User.objects.get(email_normalized=normalized_email)
        except User.DoesNotExist:
            raise serializers.ValidationError(
                {"detail": "Invalid email or password."}
            )
        
        if user.status == UserStatus.SUSPENDED:
            raise serializers.ValidationError(
                {"detail": "This account has been suspended."}
            )
        
        user = authenticate(email=user.email, password=password)
        if not user:
            raise serializers.ValidationError(
                {"detail": "Invalid email or password."}
            )
        
        attrs["user"] = user
        return attrs


class LoginResponseSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source="profile.display_name", read_only=True)

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "role",
            "status",
            "is_email_verified",
            "name",
        )
        read_only_fields = fields


class GoogleLoginSerializer(serializers.Serializer):
    id_token = serializers.CharField()


class GoogleRegisterSerializer(serializers.Serializer):
    id_token = serializers.CharField()
    role = serializers.CharField(max_length=32)

    def validate_role(self, value: str) -> str:
        role = value.strip()
        if role == UserRole.ADMIN:
            raise PermissionDenied(detail="Admin accounts cannot be self-registered.")
        if role not in (UserRole.TENANT, UserRole.LANDLORD):
            raise serializers.ValidationError("Role must be tenant or landlord.")
        return role


class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=254)
    password = serializers.CharField(write_only=True, style={"input_type": "password"})
    password_confirm = serializers.CharField(write_only=True, style={"input_type": "password"})

    def validate_email(self, value: str) -> str:
        normalized = normalize_email(value)
        if not User.objects.filter(email_normalized=normalized).exists():
            raise serializers.ValidationError("No account found with this email address.")
        return normalized

    def validate_password(self, value: str) -> str:
        try:
            password_validation.validate_password(value, user=None)
        except password_validation.ValidationError as exc:
            raise serializers.ValidationError(list(exc.messages))
        return value

    def validate(self, attrs):
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError(
                {"password_confirm": ["Passwords do not match."]}
            )
        return attrs


class PasswordResetResponseSerializer(serializers.Serializer):
    detail = serializers.CharField()
    email = serializers.EmailField()


class GoogleRegisterResponseSerializer(UserRegistrationResponseSerializer):
    message = serializers.SerializerMethodField()

    class Meta(UserRegistrationResponseSerializer.Meta):
        fields = UserRegistrationResponseSerializer.Meta.fields + ("message",)
        read_only_fields = fields

    def get_message(self, obj: User) -> str:
        return "Registration successful. Please log in."
