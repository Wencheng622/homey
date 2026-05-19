from rest_framework.permissions import BasePermission

from users.models import UserRole


class IsAdminRole(BasePermission):
    message = "Only admins can send invitations."

    def has_permission(self, request, view) -> bool:
        user = request.user
        return (
            bool(user and user.is_authenticated)
            and getattr(user, "role", None) == UserRole.ADMIN
        )
