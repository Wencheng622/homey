"""
Public auth registration and Google account linking.

Token verification against Google is out of scope here; callers must verify
the ID token server-side before invoking `google_login_or_link`.
"""
from __future__ import annotations

from django.db import transaction

from users.models import Profile, User, UserRole, UserStatus


class PublicRegistrationError(ValueError):
    """Raised when public signup rules are violated."""


def normalize_email(email: str) -> str:
    return email.strip().lower()


def validate_public_registration_role(role: str) -> None:
    """Only tenant and landlord may self-register; admin is internal-only."""
    if role not in (UserRole.TENANT, UserRole.LANDLORD):
        raise PublicRegistrationError(
            "Only tenant or landlord may register through public signup."
        )


@transaction.atomic
def register_email_password_user(
    *,
    email: str,
    password: str,
    role: str,
    name: str,
) -> User:
    """
    Create User + Profile in one transaction. Name is stored on Profile.display_name only.
    """
    validate_public_registration_role(role)
    email_norm = normalize_email(email)
    user = User.objects.create_user(
        email=email_norm,
        password=password,
        role=role,
        status=UserStatus.EMAIL_UNVERIFIED,
        is_email_verified=False,
    )
    Profile.objects.update_or_create(
        user=user,
        defaults={"display_name": name.strip()},
    )
    return User.objects.select_related("profile").get(pk=user.pk)





@transaction.atomic
def google_login_or_link(
    *,
    google_id: str,
    email: str,
    email_verified_by_provider: bool,
    role: str = UserRole.TENANT,
) -> User:
    """
    Google OAuth success path: create user or link to existing email.

    - If a user exists with the same normalized email (non-deleted), reuse that row
      and set google_id when empty.
    - If google_id is already set to a different value, raise (possible takeover).
    - If no user exists, create one (password unusable until set locally).
    """
    if not google_id:
        raise ValueError("google_id is required")
    email_norm = normalize_email(email)

    existing = User.objects.filter(email_normalized=email_norm).first()
    if existing:
        if existing.google_id and existing.google_id != google_id:
            raise PublicRegistrationError(
                "This email is already linked to a different Google account."
            )
        existing.google_id = google_id
        if email_verified_by_provider:
            existing.is_email_verified = True
            if existing.status == UserStatus.EMAIL_UNVERIFIED:
                existing.status = UserStatus.ACTIVE
        existing.save()
        return existing

    validate_public_registration_role(role)
    user = User.objects.create_user(
        email=email_norm,
        password=None,
        google_id=google_id,
        role=role,
        status=UserStatus.ACTIVE if email_verified_by_provider else UserStatus.EMAIL_UNVERIFIED,
        is_email_verified=email_verified_by_provider,
    )
    return user
