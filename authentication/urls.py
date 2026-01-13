from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    LoginViewSet,
    LogoutView,
    PasswordResetConfirmViewSet,
    PasswordResetRequestViewSet,
    RegisterViewSet,
    VerifyOTPViewSet,
)

router = DefaultRouter()
router.register(r"register", RegisterViewSet, basename="register")
router.register(r"verify", VerifyOTPViewSet, basename="verify")

# Using router for consistency
router.register(r"login", LoginViewSet, basename="login")
router.register(
    r"password/reset/request",
    PasswordResetRequestViewSet,
    basename="password-reset-request",
)
router.register(
    r"password/reset/confirm",
    PasswordResetConfirmViewSet,
    basename="password-reset-confirm",
)

urlpatterns = [
    path("", include(router.urls)),
    path("refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("logout/", LogoutView.as_view(), name="logout"),
]
