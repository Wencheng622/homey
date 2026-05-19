from django.core import mail
from django.test import TestCase, override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.middleware.csrf import get_token

from users.models import (
    AdminInvitation,
    AdminInvitationStatus,
    User,
    UserRole,
    UserStatus,
)


@override_settings(
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
)
class AdminInvitationCreateAPITests(TestCase):
    def setUp(self):
        self.client = APIClient(enforce_csrf_checks=True)
        self.url = reverse("admin-invitations-create")
        self.password = "SecurePassword123!"
        self.admin = User.objects.create_user(
            email="admin@example.com",
            password=self.password,
            role=UserRole.ADMIN,
            status=UserStatus.ACTIVE,
            is_email_verified=True,
            is_staff=True,
        )
        self.tenant = User.objects.create_user(
            email="tenant@example.com",
            password=self.password,
            role=UserRole.TENANT,
            status=UserStatus.ACTIVE,
            is_email_verified=True,
        )

    def _csrf_post(self, user: User, payload: dict):
        self.client.force_login(user)
        response=self.client.get("/admin/")
        csrf_token = get_token(response.wsgi_request)
        self.client.cookies["csrftoken"] = csrf_token
 
        return self.client.post(
            self.url,
            payload,
            format="json",
            HTTP_X_CSRFTOKEN=csrf_token,
        )

    def test_unauthenticated_post_403(self):
        response = self.client.post(
            self.url,
            {"email": "newadmin@example.com"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_non_admin_post_403(self):
        response = self._csrf_post(
            self.tenant,
            {"email": "newadmin@example.com"},
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            response.json()["detail"],
            "Only admins can send invitations.",
        )

    def test_admin_post_valid_email_201(self):
        response = self._csrf_post(self.admin, {"email": "newadmin@example.com"})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        body = response.json()
        self.assertEqual(body["email"], "newadmin@example.com")
        self.assertEqual(body["status"], AdminInvitationStatus.PENDING)
        self.assertIn("id", body)
        self.assertIn("expires_at", body)
        self.assertNotIn("token", body)

        invitation = AdminInvitation.objects.get(pk=body["id"])
        self.assertEqual(invitation.created_by, self.admin)

    def test_admin_post_duplicate_registered_email_409(self):
        User.objects.create_user(
            email="existing@example.com",
            password=self.password,
            role=UserRole.TENANT,
        )
        response = self._csrf_post(self.admin, {"email": "existing@example.com"})
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(
            response.json()["detail"],
            "A user with this email already exists.",
        )

    def test_admin_post_invalid_email_400(self):
        response = self._csrf_post(self.admin, {"email": "not-an-email"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.json())

    def test_second_invite_same_email_revokes_prior_and_returns_201(self):
        first = self._csrf_post(self.admin, {"email": "reuse@example.com"})
        self.assertEqual(first.status_code, status.HTTP_201_CREATED)
        first_id = first.json()["id"]

        second = self._csrf_post(self.admin, {"email": "reuse@example.com"})
        self.assertEqual(second.status_code, status.HTTP_201_CREATED)
        second_id = second.json()["id"]
        self.assertNotEqual(first_id, second_id)

        first_invitation = AdminInvitation.objects.get(pk=first_id)
        self.assertEqual(first_invitation.status, AdminInvitationStatus.REVOKED)
        self.assertIsNotNone(first_invitation.revoked_at)

        second_invitation = AdminInvitation.objects.get(pk=second_id)
        self.assertEqual(second_invitation.status, AdminInvitationStatus.PENDING)

    def test_invitation_email_sent_without_token_in_response(self):
        mail.outbox.clear()
        response = self._csrf_post(self.admin, {"email": "mailed@example.com"})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertNotIn("token", response.json())

        self.assertEqual(len(mail.outbox), 1)
        message = mail.outbox[0]
        self.assertEqual(message.to, ["mailed@example.com"])

        invitation = AdminInvitation.objects.get(email="mailed@example.com")
        self.assertIn(invitation.token, message.body)
        self.assertIn("token=", message.body)
