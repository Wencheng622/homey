from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from users.models import User, UserRole, UserStatus


class RegisterAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse("auth-register")

    def test_register_201_creates_user_and_profile(self):
        payload = {
            "email": "user@example.com",
            "password": "SecurePassword123!",
            "role": UserRole.TENANT,
            "name": "Alice Chen",
        }
        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        body = response.json()
        self.assertEqual(body["email"], "user@example.com")
        self.assertEqual(body["role"], UserRole.TENANT)
        self.assertEqual(body["status"], UserStatus.EMAIL_UNVERIFIED)
        self.assertIs(body["is_email_verified"], False)
        self.assertEqual(body["name"], "Alice Chen")
        self.assertIn("id", body)
        self.assertIn("created_at", body)

        user = User.objects.select_related("profile").get(email="user@example.com")
        self.assertEqual(user.status, UserStatus.EMAIL_UNVERIFIED)
        self.assertTrue(user.has_usable_password())
        self.assertNotEqual(user.password, "SecurePassword123!")
        self.assertEqual(user.profile.display_name, "Alice Chen")

    def test_register_duplicate_email_400(self):
        User.objects.create_user(
            email="dup@example.com",
            password="SecurePassword123!",
            role=UserRole.TENANT,
            status=UserStatus.EMAIL_UNVERIFIED,
        )
        response = self.client.post(
            self.url,
            {
                "email": "Dup@Example.com",
                "password": "SecurePassword123!",
                "role": UserRole.LANDLORD,
                "name": "Bob",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.json())

    def test_register_invalid_password_400(self):
        response = self.client.post(
            self.url,
            {
                "email": "new@example.com",
                "password": "short",
                "role": UserRole.TENANT,
                "name": "Test",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password", response.json())

    def test_register_invalid_role_400(self):
        response = self.client.post(
            self.url,
            {
                "email": "guest@example.com",
                "password": "SecurePassword123!",
                "role": "guest",
                "name": "Test",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("role", response.json())

    def test_register_admin_403(self):
        response = self.client.post(
            self.url,
            {
                "email": "admin@example.com",
                "password": "SecurePassword123!",
                "role": UserRole.ADMIN,
                "name": "Admin",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_register_missing_name_400(self):
        response = self.client.post(
            self.url,
            {
                "email": "noname@example.com",
                "password": "SecurePassword123!",
                "role": UserRole.TENANT,
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("name", response.json())

    def test_register_blank_name_400(self):
        response = self.client.post(
            self.url,
            {
                "email": "blank@example.com",
                "password": "SecurePassword123!",
                "role": UserRole.TENANT,
                "name": "   ",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
