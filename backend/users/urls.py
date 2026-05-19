from django.urls import path

from users.views import (
    AdminInvitationCreateView,
    RegisterView,
    LoginView,
    LogoutView,
    GoogleRegisterView,
    GoogleLoginView,
)

urlpatterns = [
    path(
        "admin/invitations/",
        AdminInvitationCreateView.as_view(),
        name="admin-invitations-create",
    ),
    path("auth/register/", RegisterView.as_view(), name="auth-register"),
    path("auth/login/", LoginView.as_view(), name="auth-login"),
    path("auth/logout/", LogoutView.as_view(), name="auth-logout"),
    path("auth/google/register/", GoogleRegisterView.as_view(), name="auth-google-register"),
    path("auth/google/login/", GoogleLoginView.as_view(), name="auth-google-login"),
]
