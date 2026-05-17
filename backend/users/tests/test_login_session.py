from django.conf import settings
from django.test import TestCase, override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from users.models import User, UserRole, UserStatus


class LoginSessionCookieTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.login_url = reverse("auth-login")
        self.logout_url = reverse("auth-logout")
        User.objects.create_user(
            email="sessionuser@example.com",
            password="SecurePassword123!",
            role=UserRole.TENANT,
            status=UserStatus.ACTIVE,
            is_email_verified=True,
        )

    def _session_cookie_name(self) -> str:
        return settings.SESSION_COOKIE_NAME

    def test_login_sets_session_cookie_http_only_and_max_age(self):
        response = self.client.post(
            self.login_url,
            {"email": "sessionuser@example.com", "password": "SecurePassword123!"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["email"], "sessionuser@example.com")

        cookie = response.cookies.get(self._session_cookie_name())
        self.assertIsNotNone(cookie)
        self.assertEqual(cookie["max-age"], settings.SESSION_COOKIE_AGE)
        output_lower = cookie.output().lower()
        self.assertIn("httponly", output_lower)

    @override_settings(
        DEBUG=False,
        ALLOWED_HOSTS=["testserver"],
        SESSION_COOKIE_SECURE=True,
    )
    def test_login_session_cookie_secure_when_configured(self):
        response = self.client.post(
            self.login_url,
            {"email": "sessionuser@example.com", "password": "SecurePassword123!"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        cookie = response.cookies.get(self._session_cookie_name())
        self.assertIsNotNone(cookie)
        self.assertIn("secure", cookie.output().lower())

    def test_logout_requires_authenticated_session(self):
        self.client.post(
            self.login_url,
            {"email": "sessionuser@example.com", "password": "SecurePassword123!"},
            format="json",
        )
        out = self.client.post(self.logout_url, {}, format="json")
        self.assertEqual(out.status_code, status.HTTP_204_NO_CONTENT)

        second = self.client.post(self.logout_url, {}, format="json")
        self.assertEqual(second.status_code, status.HTTP_403_FORBIDDEN)

    def test_google_register_does_not_set_session_cookie(self):
        from unittest.mock import patch

        from users.services import GoogleTokenVerificationError

        url = reverse("auth-google-register")
        with patch("users.views.verify_google_id_token") as mock_verify:
            mock_verify.side_effect = GoogleTokenVerificationError("bad")
            response = self.client.post(
                url,
                {"id_token": "x", "role": UserRole.TENANT},
                format="json",
            )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        with patch("users.views.verify_google_id_token") as mock_verify:
            mock_verify.return_value = {
                "google_id": "sub-nosession",
                "email": "gmailnosession@example.com",
                "name": "G User",
                "picture": "https://example.com/a.jpg",
                "email_verified": True,
            }
            response = self.client.post(
                url,
                {"id_token": "valid-token", "role": UserRole.TENANT},
                format="json",
            )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertNotIn(self._session_cookie_name(), response.cookies)
