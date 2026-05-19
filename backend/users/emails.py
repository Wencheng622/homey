from __future__ import annotations

from django.conf import settings
from django.core.mail import send_mail

from users.models import AdminInvitation


def send_admin_invitation_email(invitation: AdminInvitation) -> None:
    base_url = settings.ADMIN_INVITATION_FRONTEND_URL.rstrip("/")
    invite_link = f"{base_url}?token={invitation.token}"
    subject = "You have been invited to join Homey as an admin"
    message = (
        f"You have been invited to create an admin account for Homey.\n\n"
        f"Accept your invitation by visiting:\n{invite_link}\n\n"
        f"This link expires on {invitation.expires_at.isoformat()}."
    )
    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[invitation.email],
        fail_silently=False,
    )
