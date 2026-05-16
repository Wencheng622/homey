from unittest.mock import patch

from django.test import TestCase, override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from users.models import User, UserRole, UserStatus
from users.services import GoogleTokenVerificationError


def mock_google_claims(**overrides):
    claims = {
        "google_id": "google-sub-123",
        "email": "user@gmail.com",
        "name": "Test User",
        "picture": "https://example.com/photo.jpg",
        "email_verified": True,
    }
    claims.update(overrides)
    return claims


@override_settings(GOOGLE_CLIENT_ID="test-client-id")
class GoogleRegisterAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse("auth-google-register")

    def _post(self, payload, mock_return=None):
        with patch("users.views.verify_google_id_token") as mock_verify:
            if mock_return is not None:
                if isinstance(mock_return, Exception):
                    mock_verify.side_effect = mock_return
                else:
                    mock_verify.return_value = mock_return
            response = self.client.post(self.url, payload, format="json")
        return response, mock_verify

    def test_google_register_invalid_role_400(self):
        response, mock_verify = self._post(
            {"id_token": "fake-token", "role": "guest"},
            mock_return=mock_google_claims(),
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("role", response.json())
        mock_verify.assert_not_called()

    def test_google_register_invalid_token_400(self):
        response, _ = self._post(
            {"id_token": "bad-token", "role": UserRole.TENANT},
            mock_return=GoogleTokenVerificationError("Invalid or expired Google ID token."),
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("id_token", response.json())

    def test_google_register_new_user_201(self):
        claims = mock_google_claims()
        response, _ = self._post(
            {"id_token": "valid-token", "role": UserRole.TENANT},
            mock_return=claims,
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        body = response.json()
        self.assertEqual(body["email"], claims["email"])
        self.assertEqual(body["role"], UserRole.TENANT)
        self.assertEqual(body["status"], UserStatus.ACTIVE)
        self.assertIs(body["is_email_verified"], True)
        self.assertEqual(body["name"], claims["name"])
        self.assertEqual(body["message"], "Registration successful. Please log in.")
        self.assertIn("id", body)
        self.assertIn("created_at", body)

        user = User.objects.select_related("profile").get(email=claims["email"])
        self.assertEqual(user.google_id, claims["google_id"])
        self.assertEqual(user.profile.display_name, claims["name"])
        self.assertEqual(user.profile.avatar_url, claims["picture"])

    def test_google_register_links_existing_email_without_google_id(self):
        existing = User.objects.create_user(
            email="existing@example.com",
            password="SecurePassword123!",
            role=UserRole.LANDLORD,
            status=UserStatus.EMAIL_UNVERIFIED,
        )
        existing.profile.display_name = "Old Name"
        existing.profile.save()

        claims = mock_google_claims(email="existing@example.com")
        response, _ = self._post(
            {"id_token": "valid-token", "role": UserRole.TENANT},
            mock_return=claims,
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        existing.refresh_from_db()
        self.assertEqual(existing.google_id, claims["google_id"])
        self.assertEqual(existing.role, UserRole.LANDLORD)
        self.assertEqual(existing.profile.display_name, claims["name"])
        self.assertEqual(existing.profile.avatar_url, claims["picture"])

    def test_google_register_existing_google_id_409(self):
        User.objects.create_user(
            email="linked@example.com",
            password=None,
            google_id="existing-google-id",
            role=UserRole.TENANT,
            status=UserStatus.ACTIVE,
            is_email_verified=True,
        )
        claims = mock_google_claims(email="linked@example.com", google_id="other-google-id")
        response, _ = self._post(
            {"id_token": "valid-token", "role": UserRole.TENANT},
            mock_return=claims,
        )
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertIn("detail", response.json())

    def test_google_register_does_not_set_cookie(self):
        response, _ = self._post(
            {"id_token": "valid-token", "role": UserRole.TENANT},
            mock_return=mock_google_claims(),
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertNotIn("set-cookie", {k.lower() for k in response.headers})

    def test_google_register_password_unusable(self):
        claims = mock_google_claims(email="nopass@example.com")
        response, _ = self._post(
            {"id_token": "valid-token", "role": UserRole.TENANT},
            mock_return=claims,
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = User.objects.get(email=claims["email"])
        self.assertFalse(user.has_usable_password())
