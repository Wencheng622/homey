from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from users.models import User, UserRole, UserStatus


class PasswordResetAPITests(APITestCase):
    def setUp(self):
        self.url = reverse("auth-password-reset")
        User.objects.create_user(
            email="resetme@example.com",
            password="OldPassword123!",
            role=UserRole.TENANT,
            status=UserStatus.ACTIVE,
            is_email_verified=True,
        )

    def test_password_reset_200(self):
        response = self.client.post(
            self.url,
            {
                "email": "resetme@example.com",
                "password": "NewPassword456!",
                "password_confirm": "NewPassword456!",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user = User.objects.get(email="resetme@example.com")
        self.assertTrue(user.check_password("NewPassword456!"))

    def test_password_reset_mismatch_400(self):
        response = self.client.post(
            self.url,
            {
                "email": "resetme@example.com",
                "password": "NewPassword456!",
                "password_confirm": "Different456!",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_reset_unknown_email_400(self):
        response = self.client.post(
            self.url,
            {
                "email": "unknown@example.com",
                "password": "NewPassword456!",
                "password_confirm": "NewPassword456!",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
