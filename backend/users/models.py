from __future__ import annotations

import secrets
import uuid
from datetime import datetime, timedelta

from django.conf import settings
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.db.models import Q
from django.utils import timezone

from users.exceptions import InvalidInvitationTransition


class UserRole(models.TextChoices):
    TENANT = "tenant", "Tenant"
    LANDLORD = "landlord", "Landlord"
    ADMIN = "admin", "Admin"


class UserStatus(models.TextChoices):
    EMAIL_UNVERIFIED = "email_unverified", "Email unverified"
    ACTIVE = "active", "Active"
    SUSPENDED = "suspended", "Suspended"
    DELETED = "deleted", "Deleted"


class AdminInvitationStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    ACCEPTED = "accepted", "Accepted"
    REJECTED = "rejected", "Rejected"
    EXPIRED = "expired", "Expired"
    REVOKED = "revoked", "Revoked"


def generate_invitation_token() -> str:
    return secrets.token_urlsafe(32)


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


class AdminInvitation(models.Model):
    """
    Admin invite lifecycle. Does not create a User until acceptance.

    Creation (service layer): normalize email, reject if User exists, revoke pending
    rows for the email, then insert with expires_at from settings.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(max_length=254)
    email_normalized = models.CharField(max_length=254, editable=False, db_index=True)
    token = models.CharField(
        max_length=64,
        unique=True,
        editable=False,
        default=generate_invitation_token,
    )
    status = models.CharField(
        max_length=16,
        choices=AdminInvitationStatus.choices,
        default=AdminInvitationStatus.PENDING,
        db_index=True,
    )
    created_by = models.ForeignKey(
        "users.User",
        on_delete=models.PROTECT,
        related_name="admin_invitations_created",
    )
    accepted_user = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="admin_invitations_accepted",
    )
    expires_at = models.DateTimeField()
    accepted_at = models.DateTimeField(null=True, blank=True)
    rejected_at = models.DateTimeField(null=True, blank=True)
    revoked_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "admin_invitations"
        verbose_name = "admin invitation"
        verbose_name_plural = "admin invitations"
        constraints = [
            models.CheckConstraint(
                condition=models.Q(status__in=[c.value for c in AdminInvitationStatus]),
                name="users_admininvitation_status_valid",
            ),
            models.UniqueConstraint(
                fields=["email_normalized"],
                condition=Q(status=AdminInvitationStatus.PENDING),
                name="users_admininvitation_one_pending_per_email",
            ),
        ]
        indexes = [
            models.Index(fields=["email"]),
            models.Index(fields=["email_normalized"]),
            models.Index(fields=["token"]),
            models.Index(fields=["status"]),
            models.Index(fields=["created_by"]),
            models.Index(fields=["accepted_user"]),
            models.Index(fields=["email_normalized", "status"]),
        ]

    def __str__(self) -> str:
        return f"AdminInvitation({self.email}, {self.status})"

    @classmethod
    def default_expires_at(cls) -> datetime:
        return timezone.now() + timedelta(seconds=settings.ADMIN_INVITATION_EXPIRY_SECONDS)

    def _sync_normalized_email(self) -> None:
        from users.services import normalize_email

        if self.email:
            self.email_normalized = normalize_email(self.email)
            self.email = self.email_normalized
        else:
            self.email_normalized = ""

    def clean(self) -> None:
        super().clean()
        self._sync_normalized_email()

    def save(self, *args, **kwargs) -> None:
        self._sync_normalized_email()
        super().save(*args, **kwargs)

    def is_expired(self) -> bool:
        return timezone.now() >= self.expires_at

    def is_valid(self) -> bool:
        return self.status == AdminInvitationStatus.PENDING and not self.is_expired()

    def _require_pending_transition(self) -> None:
        if self.status != AdminInvitationStatus.PENDING:
            raise InvalidInvitationTransition(
                f"Cannot transition invitation from status '{self.status}'."
            )
        if self.is_expired():
            raise InvalidInvitationTransition("Invitation has expired.")

    def mark_accepted(self, user: User) -> None:
        self._require_pending_transition()
        now = timezone.now()
        self.status = AdminInvitationStatus.ACCEPTED
        self.accepted_user = user
        self.accepted_at = now
        self.save(
            update_fields=["status", "accepted_user", "accepted_at", "updated_at"],
        )

    def mark_rejected(self) -> None:
        self._require_pending_transition()
        now = timezone.now()
        self.status = AdminInvitationStatus.REJECTED
        self.rejected_at = now
        self.save(update_fields=["status", "rejected_at", "updated_at"])

    def mark_revoked(self) -> None:
        self._require_pending_transition()
        now = timezone.now()
        self.status = AdminInvitationStatus.REVOKED
        self.revoked_at = now
        self.save(update_fields=["status", "revoked_at", "updated_at"])

    def mark_expired(self) -> None:
        if self.status != AdminInvitationStatus.PENDING:
            raise InvalidInvitationTransition(
                f"Cannot expire invitation from status '{self.status}'."
            )
        now = timezone.now()
        self.status = AdminInvitationStatus.EXPIRED
        self.save(update_fields=["status", "updated_at"])
