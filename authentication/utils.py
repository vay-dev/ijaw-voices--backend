import random
import secrets
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import timedelta


def generate_and_send_otp(user):
    """
    Generates a 4-digit OTP, saves it to the user with expiry,
    and sends it via email.
    Returns the OTP (for testing/logging) or None on failure.
    """
    # Generate 4-digit code
    otp = f"{secrets.randbelow(1000000):06d}"

    # Set OTP fields
    user.otp_code = otp
    user.otp_created_at = timezone.now()
    user.otp_expiry = user.otp_created_at + timedelta(minutes=10)  # 10 min expiry
    user.save(update_fields=["otp_code", "otp_created_at", "otp_expiry"])

    # Email content
    subject = "Your Language App Verification Code"
    message = (
        f"Hello {user.first_name or 'there'},\n\n"
        f"Your verification code is: **{otp}**\n\n"
        "This code will expire in 10 minutes.\n"
        "If you didn't request this, please ignore this email.\n\n"
        "Happy learning!\n"
        "The Language App Team"
    )

    html_message = f"""
    <html>
      <body>
        <h2>Welcome to Language App!</h2>
        <p>Hello {user.first_name or 'there'},</p>
        <p>Your verification code is:</p>
        <h1 style="letter-spacing: 8px; font-size: 36px; font-weight: bold;">{otp}</h1>
        <p>This code will expire in <strong>10 minutes</strong>.</p>
        <p>If you didn't sign up, please ignore this email.</p>
        <br>
        <p>Happy learning!<br>The Language App Team</p>
      </body>
    </html>
    """

    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,  # For dev, better to see errors
        )
        return otp  # Return for testing/debugging
    except Exception as e:
        # In production, you might want to log this instead of raising
        print(f"Failed to send OTP email to {user.email}: {str(e)}")
        return None


def verify_otp(user, code):
    """
    Simple helper to check OTP validity.
    Returns (is_valid: bool, message: str)
    """
    if not user.otp_code:
        return False, "No verification code was generated for this account."

    if timezone.now() > user.otp_expiry:
        return False, "This verification code has expired. Please request a new one."

    if user.otp_code != code:
        return False, "Invalid verification code."

    # All good
    return True, "Verification successful"
