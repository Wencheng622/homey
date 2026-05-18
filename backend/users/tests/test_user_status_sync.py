from django.test import TestCase

from users.models import User, UserRole, UserStatus


class UserStatusEmailVerifiedSyncTests(TestCase):
    def test_active_status_sets_is_email_verified_true(self):
        user = User.objects.create_user(
            email="active@example.com",
            password="SecurePassword123!",
            role=UserRole.TENANT,
            status=UserStatus.ACTIVE,
            is_email_verified=False,
        )
        self.assertTrue(user.is_email_verified)

    def test_active_status_sync_on_save_with_update_fields(self):
        user = User.objects.create_user(
            email="promote@example.com",
            password="SecurePassword123!",
            role=UserRole.TENANT,
            status=UserStatus.EMAIL_UNVERIFIED,
            is_email_verified=False,
        )
        user.status = UserStatus.ACTIVE
        user.save(update_fields=["status", "updated_at"])
        user.refresh_from_db()
        self.assertTrue(user.is_email_verified)

    def test_email_unverified_status_clears_is_email_verified(self):
        user = User.objects.create_user(
            email="unverified@example.com",
            password="SecurePassword123!",
            role=UserRole.TENANT,
            status=UserStatus.EMAIL_UNVERIFIED,
            is_email_verified=True,
        )
        self.assertFalse(user.is_email_verified)

    def test_suspended_status_does_not_clear_is_email_verified(self):
        user = User.objects.create_user(
            email="suspended@example.com",
            password="SecurePassword123!",
            role=UserRole.TENANT,
            status=UserStatus.ACTIVE,
            is_email_verified=True,
        )
        user.status = UserStatus.SUSPENDED
        user.save(update_fields=["status", "updated_at"])
        user.refresh_from_db()
        self.assertTrue(user.is_email_verified)
