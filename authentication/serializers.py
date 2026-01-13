# authentication/serializers.py
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from .models import CustomUser
from .utils import generate_and_send_otp
import re


class UserSerializer(serializers.ModelSerializer):
    """
    Full user details returned after successful verification
    """

    class Meta:
        model = CustomUser
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "avatar_id",
            "is_verified",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "is_verified", "created_at", "updated_at"]


class RegisterSerializer(serializers.ModelSerializer):
    """
    Registration input serializer
    Creates unverified user and sends OTP
    """

    password = serializers.CharField(
        write_only=True,
        required=True,
        style={"input_type": "password"},
        min_length=6,
        error_messages={"min_length": "Password must be at least 6 characters long."},
    )

    class Meta:
        model = CustomUser
        fields = [
            "email",
            "password",
            "first_name",
            "last_name",
            "avatar_id",
        ]

    def validate_email(self, value):
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("This email is already registered.")
        return value

    def validate_password(self, value):
        """
        Custom password validation:
        - At least 6 characters (already enforced by min_length)
        - At least one uppercase letter
        - At least one special character
        """
        if not re.search(r"[A-Z]", value):
            raise serializers.ValidationError(
                "Password must contain at least one uppercase letter."
            )

        if not re.search(r'[!@#$%^&*()_+\-=\[\]{}|;:\'",.<>?/`~]', value):
            raise serializers.ValidationError(
                "Password must contain at least one special character."
            )

        return value

    def create(self, validated_data):
        # Create user (unverified)
        user = CustomUser.objects.create_user(
            email=validated_data["email"],
            password=validated_data["password"],
            first_name=validated_data.get("first_name", ""),
            last_name=validated_data.get("last_name", ""),
            avatar_id=validated_data.get("avatar_id", None),
        )

        # Generate and send OTP
        otp = generate_and_send_otp(user)

        if not otp:
            raise serializers.ValidationError(
                "Failed to send verification code. Please try again later."
            )

        return user


class VerifyOTPSerializer(serializers.Serializer):
    """
    OTP verification input
    """

    user_id = serializers.UUIDField()
    code = serializers.CharField(max_length=6, min_length=6)  # ← Changed to 6 digits?

    def validate(self, attrs):
        try:
            user = CustomUser.objects.get(id=attrs["user_id"])
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError({"user_id": "User not found."})

        is_valid, message = user.is_otp_valid(
            attrs["code"]
        )  # ← Now expects tuple (bool, str)

        if not is_valid:
            raise serializers.ValidationError(
                {"code": message}
            )  # ← Correct error raising

        attrs["user"] = user
        return attrs

    def validate_code(self, value):
        if not value.isdigit():
            raise serializers.ValidationError("Code must contain only digits.")
        return value

    def save(self):
        user = self.validated_data["user"]

        user.is_verified = True
        user.clear_otp()
        user.save(update_fields=["is_verified"])

        refresh = RefreshToken.for_user(user)

        return {
            "user": user,
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        }


# Login


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(
        required=True, write_only=True, style={"input_type": "password"}
    )

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError(
                {"email": "No account found with this email."}
            )

        if not user.check_password(password):
            raise serializers.ValidationError({"password": "Incorrect password."})

        if not user.is_verified:
            raise serializers.ValidationError(
                {"email": "Account is not verified. Please check your email."}
            )

        if not user.is_active:
            raise serializers.ValidationError("This account has been disabled.")

        attrs["user"] = user
        return attrs


# Password Reset – Request


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

    def validate_email(self, value):
        if not CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("No user with this email address.")
        return value


# Password Reset – Confirm (set new password)


class PasswordResetConfirmSerializer(serializers.Serializer):
    token = serializers.CharField(required=True)  # usually from email
    new_password = serializers.CharField(
        required=True, min_length=6, write_only=True, style={"input_type": "password"}
    )

    def validate_new_password(self, value):
        # Same password rules as registration
        if not re.search(r"[A-Z]", value):
            raise serializers.ValidationError(
                "Password must contain at least one uppercase letter."
            )
        if not re.search(r'[!@#$%^&*()_+\-=\[\]{}|;:\'",.<>?/`~]', value):
            raise serializers.ValidationError(
                "Password must contain at least one special character."
            )
        return value
