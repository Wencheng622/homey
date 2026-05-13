from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.utils.translation import gettext_lazy as _

from users.models import Profile, User


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    """Admin uses all_objects so soft-deleted users remain visible."""

    ordering = ("email",)
    list_display = (
        "email",
        "role",
        "status",
        "is_email_verified",
        "is_staff",
        "is_active",
        "deleted_at",
        "date_joined",
    )
    list_filter = ("role", "status", "is_staff", "is_superuser", "is_active", "is_email_verified")
    search_fields = ("email", "email_normalized", "google_id")
    readonly_fields = ("id", "created_at", "updated_at", "date_joined", "last_login", "email_normalized")

    def get_queryset(self, request):
        return self.model.all_objects.all()

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (_("Google"), {"fields": ("google_id",)}),
        (_("Permissions"), {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        (_("Role & status"), {"fields": ("role", "status", "is_email_verified", "deleted_at")}),
        (_("Important dates"), {"fields": ("last_login", "date_joined", "created_at", "updated_at")}),
        (_("Identifiers"), {"fields": ("id", "email_normalized")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "password1", "password2", "role", "status", "is_staff", "is_superuser"),
            },
        ),
    )


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "display_name", "locale", "created_at")
    search_fields = ("user__email", "display_name", "phone_number")
    raw_id_fields = ("user",)
