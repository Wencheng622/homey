from unittest.mock import patch

from django.conf import settings
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from users.models import User, UserRole, UserStatus
from users.services import GoogleTokenVerificationError


def mock_google_claims(**overrides):
    claims = {
        "google_id": "google-sub-login",
        "email": "googlelogin@example.com",
        "name": "Google Login User",
        "picture": "https://example.com/avatar.jpg",
        "email_verified": True,
    }
    claims.update(overrides)
    return claims


class GoogleLoginAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse("auth-google-login")

    def _session_cookie_name(self) -> str:
        return settings.SESSION_COOKIE_NAME

    def _post(self, payload, mock_return=None):
        with patch("users.views.verify_google_id_token") as mock_verify:
            if mock_return is not None:
                if isinstance(mock_return, Exception):
                    mock_verify.side_effect = mock_return
                else:
                    mock_verify.return_value = mock_return
            response = self.client.post(self.url, payload, format="json")
        return response

    def test_google_login_invalid_token_400(self):
        response = self._post(
            {"id_token": "bad-token"},
            mock_return=GoogleTokenVerificationError("Invalid or expired Google ID token."),
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("id_token", response.json())

    def test_google_login_no_user_401(self):
        response = self._post(
            {"id_token": "valid-token"},
            mock_return=mock_google_claims(email="unknown@example.com", google_id="sub-unknown"),
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn("detail", response.json())

    def test_google_login_matching_google_id_200_and_session(self):
        user = User.objects.create_user(
            email="googlelogin@example.com",
            password=None,
            google_id="google-sub-login",
            role=UserRole.TENANT,
            status=UserStatus.ACTIVE,
            is_email_verified=True,
        )
        user.profile.display_name = "Old"
        user.profile.save()

        response = self._post(
            {"id_token": "valid-token"},
            mock_return=mock_google_claims(),
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        body = response.json()
        self.assertEqual(body["email"], "googlelogin@example.com")
        self.assertEqual(body["name"], "Google Login User")

        cookie = response.cookies.get(self._session_cookie_name())
        self.assertIsNotNone(cookie)

        user.refresh_from_db()
        self.assertEqual(user.profile.display_name, "Google Login User")
        self.assertEqual(user.profile.avatar_url, "https://example.com/avatar.jpg")

    def test_google_login_links_email_without_google_id(self):
        user = User.objects.create_user(
            email="linkme@example.com",
            password="SecurePassword123!",
            google_id=None,
            role=UserRole.LANDLORD,
            status=UserStatus.EMAIL_UNVERIFIED,
            is_email_verified=False,
        )

        response = self._post(
            {"id_token": "valid-token"},
            mock_return=mock_google_claims(
                email="linkme@example.com",
                google_id="new-google-sub",
            ),
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(response.cookies.get(self._session_cookie_name()))

        user.refresh_from_db()
        self.assertEqual(user.google_id, "new-google-sub")
        self.assertEqual(user.role, UserRole.LANDLORD)
        self.assertTrue(user.is_email_verified)
        self.assertEqual(user.status, UserStatus.ACTIVE)

    def test_google_login_different_google_id_409(self):
        User.objects.create_user(
            email="conflict@example.com",
            password=None,
            google_id="existing-google-id",
            role=UserRole.TENANT,
            status=UserStatus.ACTIVE,
            is_email_verified=True,
        )
        response = self._post(
            {"id_token": "valid-token"},
            mock_return=mock_google_claims(
                email="conflict@example.com",
                google_id="other-google-id",
            ),
        )
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertIn("detail", response.json())

    def test_google_login_suspended_403(self):
        User.objects.create_user(
            email="suspended@example.com",
            password=None,
            google_id="suspended-sub",
            role=UserRole.TENANT,
            status=UserStatus.SUSPENDED,
            is_email_verified=True,
        )
        response = self._post(
            {"id_token": "valid-token"},
            mock_return=mock_google_claims(
                email="suspended@example.com",
                google_id="suspended-sub",
            ),
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
