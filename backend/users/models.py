from __future__ import annotations

import uuid

from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.db.models import Q
from django.utils import timezone


class UserRole(models.TextChoices):
    TENANT = "tenant", "Tenant"
    LANDLORD = "landlord", "Landlord"
    ADMIN = "admin", "Admin"


class UserStatus(models.TextChoices):
    EMAIL_UNVERIFIED = "email_unverified", "Email unverified"
    ACTIVE = "active", "Active"
    SUSPENDED = "suspended", "Suspended"
    DELETED = "deleted", "Deleted"


class UserQuerySet(models.QuerySet):
    """QuerySet for non-soft-deleted users."""

    def active_accounts(self) -> UserQuerySet:
        return self.filter(deleted_at__isnull=True)


class AllUserQuerySet(models.QuerySet):
    """Includes soft-deleted rows (for admin / audit)."""


class AllUsersManager(BaseUserManager):
    """Manager that does not hide soft-deleted users."""

    def get_queryset(self) -> AllUserQuerySet:
        return AllUserQuerySet(self.model, using=self._db)


class UserManager(BaseUserManager):
    """Default manager: excludes soft-deleted users."""

    def get_queryset(self) -> UserQuerySet:
        return UserQuerySet(self.model, using=self._db).filter(deleted_at__isnull=True)

    def create_user(
        self,
        email: str,
        password: str | None = None,
        **extra_fields,
    ):
        if not email:
            raise ValueError("The email address must be set")
        user = self.model(email=email, **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.full_clean(exclude=["password"])
        user.save(using=self._db)
        return user

    def create_superuser(self, email: str, password: str | None = None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("role", UserRole.ADMIN)
        extra_fields.setdefault("status", UserStatus.ACTIVE)
        extra_fields.setdefault("is_email_verified", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(max_length=254, verbose_name="email address", unique=True)
    email_normalized = models.CharField(max_length=254, editable=False, db_index=True)
    google_id = models.CharField(max_length=255, null=True, blank=True)

    role = models.CharField(
        max_length=32,
        choices=UserRole.choices,
        default=UserRole.TENANT,
    )
    status = models.CharField(
        max_length=32,
        choices=UserStatus.choices,
        default=UserStatus.EMAIL_UNVERIFIED,
    )
    is_email_verified = models.BooleanField(default=False)

    is_active = models.BooleanField(
        default=True,
        help_text="Designates whether this user can authenticate (Django auth flag).",
    )
    is_staff = models.BooleanField(
        default=False,
        help_text="Designates whether the user can log into the admin site.",
    )

    date_joined = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    objects = UserManager()
    all_objects = AllUsersManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS: list[str] = []

    class Meta:
        verbose_name = "user"
        verbose_name_plural = "users"
        constraints = [
            models.CheckConstraint(
                condition=models.Q(role__in=[c.value for c in UserRole]),
                name="users_user_role_valid",
            ),
            models.CheckConstraint(
                condition=models.Q(status__in=[c.value for c in UserStatus]),
                name="users_user_status_valid",
            ),
            models.CheckConstraint(
                condition=~models.Q(
                    is_email_verified=True,
                    status=UserStatus.EMAIL_UNVERIFIED,
                ),
                name="users_user_email_verified_status_consistency",
            ),
            models.UniqueConstraint(
                fields=["email_normalized"],
                condition=Q(deleted_at__isnull=True),
                name="users_user_email_normalized_active_uniq",
            ),
            models.UniqueConstraint(
                fields=["google_id"],
                condition=Q(deleted_at__isnull=True, google_id__isnull=False),
                name="users_user_google_id_active_uniq",
            ),
        ]
        indexes = [
            models.Index(fields=["role", "status", "created_at"]),
            models.Index(fields=["deleted_at", "is_active"]),
            models.Index(fields=["is_email_verified", "created_at"]),
        ]

    def __str__(self) -> str:
        return self.email

    def _sync_email_verified_with_status(self) -> None:
        if self.status == UserStatus.ACTIVE:
            self.is_email_verified = True
        elif self.status == UserStatus.EMAIL_UNVERIFIED:
            self.is_email_verified = False

    def clean(self) -> None:
        super().clean()
        if self.email:
            self.email_normalized = self.email.strip().lower()
        else:
            self.email_normalized = ""
        if self.google_id == "":
            self.google_id = None
        self._sync_email_verified_with_status()

    def save(self, *args, **kwargs) -> None:
        # Keep normalized email in sync for constraints and lookups
        if self.email:
            self.email_normalized = self.email.strip().lower()
        else:
            self.email_normalized = ""
        if self.google_id == "":
            self.google_id = None
        self._sync_email_verified_with_status()
        super().save(*args, **kwargs)

    def soft_delete(self) -> None:
        self.deleted_at = timezone.now()
        self.status = UserStatus.DELETED
        self.is_active = False
        self.save(update_fields=["deleted_at", "status", "is_active", "updated_at"])


class Profile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        "users.User",
        on_delete=models.CASCADE,
        related_name="profile",
    )
    display_name = models.CharField(max_length=120, blank=True, default="")
    avatar_url = models.URLField(max_length=500, blank=True, default="")
    phone_number = models.CharField(max_length=32, blank=True, default="")
    locale = models.CharField(max_length=16, default="en")
    timezone = models.CharField(max_length=64, default="UTC")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "profile"
        verbose_name_plural = "profiles"

    def __str__(self) -> str:
        return f"Profile({self.user_id})"
