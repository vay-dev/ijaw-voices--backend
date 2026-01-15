import secrets
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
import resend

resend.api_key = settings.RESEND_API_KEY


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
    user.otp_expiry = user.otp_created_at + \
        timedelta(minutes=10)  # 10 min expiry
    user.save(update_fields=["otp_code", "otp_created_at", "otp_expiry"])

    # Email content
    subject = "Your Ijaw Voices Verification Code"

    html_message = f"""
    <!DOCTYPE html>
    <html>
     <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
      body {{ font-family: Arial, Helvetica, sans-serif; margin: 0; padding: 0; background-color: #f4f4f4; }}
      .container {{ max-width: 600px; margin: 0 auto; background: white; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 12px rgba(0,0,0,0.1); }}
      .header {{ background: #1a1a1a; color: white; padding: 20px; text-align: center; }}
      .header h1 {{ margin: 0; font-size: 28px; }}
      .content {{ padding: 30px 24px; text-align: center; }}
      .otp-box {{
        font-size: 48px;
        font-weight: bold;
        letter-spacing: 12px;
        background: #f8f8f8;
        padding: 20px;
        border-radius: 12px;
        margin: 24px 0;
        display: inline-block;
      }}
      .footer {{ background: #f8f8f8; padding: 20px; font-size: 14px; color: #666; text-align: center; }}
      .btn {{
        display: inline-block;
        background: #000;
        color: white;
        padding: 12px 32px;
        text-decoration: none;
        border-radius: 999px;
        margin-top: 16px;
      }}
    </style>
  </head>
  <body>
    <div class="container">
      <!-- Header -->
      <div class="header">
        <h1>Ijaw Voices</h1>
      </div>

      <!-- Main content -->
      <div class="content">
        <h2>Welcome to Ijaw Voices!</h2>
        <p>Hello {user.first_name or 'there'},</p>
        <p>You're almost there! Use this verification code to complete your sign-up:</p>

        <div class="otp-box">{otp}</div>

        <p>This code will expire in <strong>10 minutes</strong>.</p>
        <p>If you didn't request this code, please ignore this email — your account is safe.</p>
      </div>

      <!-- Footer -->
      <div class="footer">
        <p>Happy learning!<br>The Ijaw Voices Team</p>
        <p style="margin-top: 12px; font-size: 12px;">
          © {timezone.now().year} Ijaw Voices. All rights reserved.
        </p>
      </div>
    </div>
  </body>
    </html>
    """

    try:
        # Use Resend API to send email
        params = {{
            "from": settings.DEFAULT_FROM_EMAIL,
            "to": [user.email],
            "subject": subject,
            "html": html_message,
        }}

        resend.Emails.send(params)
        print(f"Email sent successfully to {{user.email}}")
        return otp  # Return for testing/debugging
    except Exception as e:
        # Log the error for debugging
        print(f"Failed to send OTP email to {{user.email}}: {{e}}")
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
