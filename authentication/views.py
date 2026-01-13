# authentication/views.py
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import CreateModelMixin
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.throttling import ScopedRateThrottle  # Explicit for security
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import (
    LoginSerializer,
    PasswordResetConfirmSerializer,
    PasswordResetRequestSerializer,
    RegisterSerializer,
    VerifyOTPSerializer,
    UserSerializer,
)
from .models import CustomUser


class RegisterViewSet(CreateModelMixin, GenericViewSet):
    """
    POST /auth/register/
    Creates unverified user and sends OTP
    """

    queryset = CustomUser.objects.none()  # We override get_queryset anyway
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]  # Secure with scope
    throttle_scope = "register"  # Applies '5/hour' limit

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Response matches your spec
        return Response(
            {
                "success": True,
                "message": "Sign up successful. Please check your email for verification code.",
                "userId": str(user.id),
            },
            status=status.HTTP_201_CREATED,
        )


class VerifyOTPViewSet(GenericViewSet):
    """
    POST /auth/verify/
    Validates OTP → verifies user → issues tokens
    """

    queryset = CustomUser.objects.none()
    serializer_class = VerifyOTPSerializer
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]  # Secure with scope
    throttle_scope = "verify_otp"  # Applies '10/minute' limit

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        result = serializer.save()

        user = result["user"]
        user_data = UserSerializer(user).data

        return Response(
            {
                "success": True,
                "message": "Verification complete",
                "user": user_data,
                "accessToken": result["access"],
                "refreshToken": result["refresh"],
            },
            status=status.HTTP_200_OK,
        )


# Login


class LoginViewSet(GenericViewSet):
    """
    POST /auth/login/
    Returns access + refresh tokens for verified users
    """

    serializer_class = LoginSerializer
    permission_classes = [AllowAny]
    throttle_scope = "login"  # you can add this to throttling later

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data["user"]
        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "success": True,
                "message": "Login successful",
                "user": UserSerializer(user).data,
                "accessToken": str(refresh.access_token),
                "refreshToken": str(refresh),
            }
        )


# Logout (blacklist current refresh token)


class LogoutView(APIView):
    """
    POST /auth/logout/
    Blacklists the current refresh token (requires refresh token in body)
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get("refreshToken")
            if not refresh_token:
                return Response({"error": "Refresh token is required"}, status=400)

            token = RefreshToken(refresh_token)
            token.blacklist()  # Requires BLACKLIST_AFTER_ROTATION = True

            return Response({"success": True, "message": "Logged out successfully"})
        except Exception:
            return Response(
                {"success": False, "message": "Invalid or already blacklisted token"},
                status=400,
            )


# Password Reset – Request & Confirm


class PasswordResetRequestViewSet(CreateModelMixin, GenericViewSet):
    serializer_class = PasswordResetRequestSerializer
    permission_classes = [AllowAny]
    throttle_scope = "password_reset_request"

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # In real app: generate token + send email
        # For MVP: just simulate
        email = serializer.validated_data["email"]
        # Here you would normally: send_reset_email(user, token)

        return Response(
            {
                "success": True,
                "message": "If an account exists with this email, you will receive a password reset link.",
            },
            status=200,
        )


class PasswordResetConfirmViewSet(CreateModelMixin, GenericViewSet):
    serializer_class = PasswordResetConfirmSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # In real app: validate token + set password
        # For MVP: we skip real token check
        # You would normally do: user = get_user_from_token(token)
        # user.set_password(new_password); user.save()

        return Response(
            {"success": True, "message": "Password has been reset successfully."}
        )
