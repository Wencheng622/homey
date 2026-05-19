from django.urls import path

from users.views import (
    RegisterView,
    LoginView,
    LogoutView,
    PasswordResetView,
    GoogleRegisterView,
    GoogleLoginView,
)

urlpatterns = [
    path("auth/register/", RegisterView.as_view(), name="auth-register"),
    path("auth/login/", LoginView.as_view(), name="auth-login"),
    path("auth/password/reset/", PasswordResetView.as_view(), name="auth-password-reset"),
    path("auth/logout/", LogoutView.as_view(), name="auth-logout"),
    path("auth/google/register/", GoogleRegisterView.as_view(), name="auth-google-register"),
    path("auth/google/login/", GoogleLoginView.as_view(), name="auth-google-login"),
]
