"""
Public auth registration and Google account linking.
"""
from __future__ import annotations

from typing import Any, TypedDict

from django.conf import settings
from django.db import transaction
from django.utils import timezone
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token

from users.emails import send_admin_invitation_email
from users.exceptions import AdminInvitationUserExistsError
from users.models import (
    AdminInvitation,
    AdminInvitationStatus,
    Profile,
    User,
    UserRole,
    UserStatus,
)


class PublicRegistrationError(ValueError):
    """Raised when public signup rules are violated."""


class GoogleTokenVerificationError(ValueError):
    """Raised when Google ID token verification fails."""


class GoogleRegistrationConflictError(ValueError):
    """Raised when email is already linked to a Google account."""


class GoogleLoginNotFoundError(ValueError):
    """Raised when no user exists for this Google identity (register first)."""


class GoogleLoginConflictError(ValueError):
    """Raised when email is linked to a different Google account."""


class GoogleLoginSuspendedError(ValueError):
    """Raised when the matched account is suspended."""


class GoogleTokenClaims(TypedDict):
    google_id: str
    email: str
    name: str
    picture: str
    email_verified: bool


def normalize_email(email: str) -> str:
    return email.strip().lower()


def validate_public_registration_role(role: str) -> None:
    """Only tenant and landlord may self-register; admin is internal-only."""
    if role not in (UserRole.TENANT, UserRole.LANDLORD):
        raise PublicRegistrationError(
            "Only tenant or landlord may register through public signup."
        )


def verify_google_id_token(id_token_str: str) -> GoogleTokenClaims:
    """Verify Google ID token and return normalized identity claims."""
    try:
        idinfo: dict[str, Any] = id_token.verify_oauth2_token(
            id_token_str,
            google_requests.Request(),
            settings.GOOGLE_CLIENT_ID,
        )
    except (ValueError, Exception) as exc:
        raise GoogleTokenVerificationError("Invalid or expired Google ID token.") from exc

    google_sub = idinfo.get("sub")
    email = idinfo.get("email")
    if not google_sub or not email:
        raise GoogleTokenVerificationError("Invalid or expired Google ID token.")

    return GoogleTokenClaims(
        google_id=str(google_sub),
        email=str(email),
        name=str(idinfo.get("name") or ""),
        picture=str(idinfo.get("picture") or ""),
        email_verified=bool(idinfo.get("email_verified", False)),
    )


def _update_profile_from_google(
    user: User,
    *,
    name: str,
    picture: str,
) -> None:
    Profile.objects.update_or_create(
        user=user,
        defaults={
            "display_name": name.strip(),
            "avatar_url": picture,
        },
    )


def _apply_email_verified_from_google(user: User, *, email_verified: bool) -> None:
    if email_verified:
        user.is_email_verified = True
        if user.status == UserStatus.EMAIL_UNVERIFIED:
            user.status = UserStatus.ACTIVE


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
def register_google_user(
    *,
    google_id: str,
    email: str,
    name: str,
    picture: str,
    email_verified: bool,
    role: str,
) -> User:
    """
    Register or link a user via Google ID token claims (token must be verified first).

    - New email: create user with role from request, unusable password, google_id set.
    - Existing email without google_id: link google_id; do not change role.
    - Existing email with google_id: raise GoogleRegistrationConflictError.
    """
    if not google_id:
        raise ValueError("google_id is required")

    email_norm = normalize_email(email)
    existing = User.objects.filter(email_normalized=email_norm).first()

    if existing:
        if existing.google_id:
            raise GoogleRegistrationConflictError(
                "This email is already registered with Google."
            )
        existing.google_id = google_id
        _apply_email_verified_from_google(existing, email_verified=email_verified)
        existing.save()
        user = existing
    else:
        validate_public_registration_role(role)
        user = User.objects.create_user(
            email=email_norm,
            password=None,
            google_id=google_id,
            role=role,
            status=UserStatus.ACTIVE if email_verified else UserStatus.EMAIL_UNVERIFIED,
            is_email_verified=email_verified,
        )

    _update_profile_from_google(user, name=name, picture=picture)
    return User.objects.select_related("profile").get(pk=user.pk)


@transaction.atomic
def login_google_user(
    *,
    google_id: str,
    email: str,
    name: str,
    picture: str,
    email_verified: bool,
) -> User:
    """
    Log in an existing user via verified Google claims. Does not create users.

    - Match by google_id first, then by email (link if google_id empty).
    - Reject if email is linked to a different google_id.
    """
    if not google_id:
        raise ValueError("google_id is required")

    email_norm = normalize_email(email)
    user = User.objects.filter(google_id=google_id).select_related("profile").first()

    if user:
        if user.email_normalized != email_norm:
            raise GoogleLoginConflictError(
                "This Google account does not match the email on file."
            )
    else:
        user = User.objects.filter(email_normalized=email_norm).select_related("profile").first()
        if not user:
            raise GoogleLoginNotFoundError(
                "No account found for this Google identity. Please register first."
            )
        if user.google_id and user.google_id != google_id:
            raise GoogleLoginConflictError(
                "This email is already linked to a different Google account."
            )
        if not user.google_id:
            user.google_id = google_id
            _apply_email_verified_from_google(user, email_verified=email_verified)
            user.save()

    if user.status == UserStatus.SUSPENDED:
        raise GoogleLoginSuspendedError("This account has been suspended.")

    _update_profile_from_google(user, name=name, picture=picture)
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


@transaction.atomic
def create_admin_invitation(*, email: str, created_by: User) -> AdminInvitation:
    """
    Create a pending admin invitation and send the invitation email.

    Revokes any existing pending invitations for the same normalized email.
    Raises AdminInvitationUserExistsError if a user account already exists.
    """
    email_norm = normalize_email(email)
    if User.objects.filter(email_normalized=email_norm).exists():
        raise AdminInvitationUserExistsError("A user with this email already exists.")

    now = timezone.now()
    AdminInvitation.objects.filter(
        email_normalized=email_norm,
        status=AdminInvitationStatus.PENDING,
    ).update(
        status=AdminInvitationStatus.REVOKED,
        revoked_at=now,
    )

    invitation = AdminInvitation.objects.create(
        email=email_norm,
        created_by=created_by,
        expires_at=AdminInvitation.default_expires_at(),
    )
    send_admin_invitation_email(invitation)
    return invitation
