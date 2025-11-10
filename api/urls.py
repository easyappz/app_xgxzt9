from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    HelloView,
    RegisterView,
    LoginView,
    LogoutView,
    ProfileView
)

urlpatterns = [
    path("hello/", HelloView.as_view(), name="hello"),
    path("auth/register/", RegisterView.as_view(), name="register"),
    path("auth/login/", LoginView.as_view(), name="login"),
    path("auth/logout/", LogoutView.as_view(), name="logout"),
    path("auth/profile/", ProfileView.as_view(), name="profile"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]
