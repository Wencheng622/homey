from datetime import timedelta

from django.db import IntegrityError
from django.test import TestCase
from django.utils import timezone

from users.exceptions import InvalidInvitationTransition
from users.models import (
    AdminInvitation,
    AdminInvitationStatus,
    User,
    UserRole,
    UserStatus,
)


class AdminInvitationModelTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            email="admin@example.com",
            password="SecurePassword123!",
            role=UserRole.ADMIN,
            status=UserStatus.ACTIVE,
            is_email_verified=True,
        )

    def _create_invitation(self, email: str = "invite@example.com", **kwargs):
        defaults = {
            "email": email,
            "created_by": self.admin,
            "expires_at": AdminInvitation.default_expires_at(),
        }
        defaults.update(kwargs)
        return AdminInvitation.objects.create(**defaults)

    def test_token_generated_on_create(self):
        invitation = self._create_invitation()
        self.assertTrue(invitation.token)
        self.assertGreater(len(invitation.token), 20)

    def test_tokens_are_unique(self):
        first = self._create_invitation(email="first@example.com")
        second = self._create_invitation(email="second@example.com")
        self.assertNotEqual(first.token, second.token)

    def test_email_normalized_on_save(self):
        invitation = self._create_invitation(email="  NewAdmin@Example.COM  ")
        invitation.refresh_from_db()
        self.assertEqual(invitation.email, "newadmin@example.com")
        self.assertEqual(invitation.email_normalized, "newadmin@example.com")

    def test_is_expired_and_is_valid(self):
        future = self._create_invitation(
            expires_at=timezone.now() + timedelta(days=1),
        )
        self.assertFalse(future.is_expired())
        self.assertTrue(future.is_valid())

        past = self._create_invitation(
            email="past@example.com",
            expires_at=timezone.now() - timedelta(minutes=1),
        )
        self.assertTrue(past.is_expired())
        self.assertFalse(past.is_valid())

    def test_mark_accepted(self):
        invitation = self._create_invitation()
        invitee = User.objects.create_user(
            email="invitee@example.com",
            password="SecurePassword123!",
            role=UserRole.ADMIN,
            status=UserStatus.ACTIVE,
        )
        invitation.mark_accepted(invitee)
        invitation.refresh_from_db()
        self.assertEqual(invitation.status, AdminInvitationStatus.ACCEPTED)
        self.assertEqual(invitation.accepted_user, invitee)
        self.assertIsNotNone(invitation.accepted_at)

    def test_mark_rejected(self):
        invitation = self._create_invitation()
        invitation.mark_rejected()
        invitation.refresh_from_db()
        self.assertEqual(invitation.status, AdminInvitationStatus.REJECTED)
        self.assertIsNotNone(invitation.rejected_at)

    def test_mark_revoked(self):
        invitation = self._create_invitation()
        invitation.mark_revoked()
        invitation.refresh_from_db()
        self.assertEqual(invitation.status, AdminInvitationStatus.REVOKED)
        self.assertIsNotNone(invitation.revoked_at)

    def test_mark_expired(self):
        invitation = self._create_invitation(
            expires_at=timezone.now() - timedelta(minutes=1),
        )
        invitation.mark_expired()
        invitation.refresh_from_db()
        self.assertEqual(invitation.status, AdminInvitationStatus.EXPIRED)

    def test_mark_accepted_raises_when_not_pending(self):
        invitation = self._create_invitation()
        invitation.mark_rejected()
        invitee = User.objects.create_user(
            email="other@example.com",
            password="SecurePassword123!",
            role=UserRole.ADMIN,
        )
        with self.assertRaises(InvalidInvitationTransition):
            invitation.mark_accepted(invitee)

    def test_mark_rejected_raises_when_expired(self):
        invitation = self._create_invitation(
            expires_at=timezone.now() - timedelta(minutes=1),
        )
        with self.assertRaises(InvalidInvitationTransition):
            invitation.mark_rejected()

    def test_only_one_pending_per_email(self):
        self._create_invitation(email="dup@example.com")
        with self.assertRaises(IntegrityError):
            self._create_invitation(email="dup@example.com")

    def test_multiple_non_pending_same_email_allowed(self):
        first = self._create_invitation(email="reuse@example.com")
        first.mark_revoked()
        second = self._create_invitation(email="reuse@example.com")
        self.assertEqual(second.status, AdminInvitationStatus.PENDING)

    def test_default_expires_at_uses_settings(self):
        from django.conf import settings

        before = timezone.now()
        expires = AdminInvitation.default_expires_at()
        after = timezone.now()
        expected_min = before + timedelta(seconds=settings.ADMIN_INVITATION_EXPIRY_SECONDS)
        expected_max = after + timedelta(seconds=settings.ADMIN_INVITATION_EXPIRY_SECONDS)
        self.assertGreaterEqual(expires, expected_min)
        self.assertLessEqual(expires, expected_max)
