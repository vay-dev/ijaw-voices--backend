import uuid
from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
    BaseUserManager,
)
from django.utils import timezone
from datetime import timedelta
import secrets


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True")

        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    avatar_id = models.CharField(
        max_length=255, blank=True, null=True
    )  ## provided by frontend
    is_verified = models.BooleanField(default=False)

    otp_code = models.CharField(max_length=4, blank=True, null=True)
    otp_created_at = models.DateTimeField(null=True, blank=True)
    otp_expiry = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email

    def generate_otp(self):
        """Generate 6-digit OTP and set expiry(5 mins)"""
        import random

        self.otp_code = f"{secrets.randbelow(1000000):06d}"
        self.otp_created_at = timezone.now()
        self.otp_expiry = self.otp_created_at + timedelta(minutes=10)
        self.save(update_fields=["otp_code", "otp_created_at", "otp_expiry"])

    def is_otp_valid(self, code):
        """Check if provided OTP is correct and not expired"""
        if not self.otp_code or not self.otp_expiry:
            return False, "No OTP found. Please request a new verification code."
        if timezone.now() > self.otp_expiry:
            return False, "OTP has expired. Please request a new verification code."
        if self.otp_code == code:
            return True, "OTP is valid."
        return False, "Invalid verification code."

    def clear_otp(self):
        """Invalidate OTP after successful validation"""
        self.otp_code = None
        self.otp_created_at = None
        self.otp_expiry = None
        self.save(update_fields=["otp_code", "otp_created_at", "otp_expiry"])
