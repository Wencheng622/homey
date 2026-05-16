from django.urls import path

from users.views import RegisterView, LoginView, GoogleRegisterView

urlpatterns = [
    path("auth/register/", RegisterView.as_view(), name="auth-register"),
    path("auth/login/", LoginView.as_view(), name="auth-login"),
    path("auth/google/register/", GoogleRegisterView.as_view(), name="auth-google-register"),
]
