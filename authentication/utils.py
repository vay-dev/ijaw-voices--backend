import secrets
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from django.core.mail import send_mail


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
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Verify Your Email - Ijaw Voices</title>
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                padding: 40px 20px;
                margin: 0;
            }}
            .email-wrapper {{
                max-width: 600px;
                margin: 0 auto;
                background: white;
                border-radius: 16px;
                overflow: hidden;
                box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            }}
            .header {{
                background: linear-gradient(135deg, #2563eb 0%, #1e40af 100%);
                padding: 40px 30px;
                text-align: center;
            }}
            .logo {{
                max-width: 200px;
                height: auto;
                margin-bottom: 10px;
            }}
            .header-title {{
                color: white;
                font-size: 24px;
                font-weight: 600;
                margin: 0;
            }}
            .content {{
                padding: 50px 40px;
                text-align: center;
                background: white;
            }}
            .welcome-text {{
                color: #1f2937;
                font-size: 28px;
                font-weight: 700;
                margin-bottom: 10px;
            }}
            .greeting {{
                color: #6b7280;
                font-size: 16px;
                margin-bottom: 30px;
                line-height: 1.6;
            }}
            .otp-container {{
                background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%);
                border: 2px solid #3b82f6;
                border-radius: 12px;
                padding: 30px;
                margin: 30px 0;
                position: relative;
            }}
            .otp-label {{
                color: #1e40af;
                font-size: 14px;
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 1px;
                margin-bottom: 15px;
            }}
            .otp-code {{
                font-size: 48px;
                font-weight: 700;
                color: #1e3a8a;
                letter-spacing: 8px;
                margin: 15px 0;
                font-family: 'Courier New', monospace;
                user-select: all;
                -webkit-user-select: all;
                -moz-user-select: all;
                -ms-user-select: all;
                cursor: pointer;
                padding: 10px;
                border-radius: 8px;
                background: rgba(255, 255, 255, 0.5);
            }}
            .otp-code:hover {{
                background: rgba(255, 255, 255, 0.8);
            }}
            .copy-instruction {{
                color: #6b7280;
                font-size: 13px;
                margin-top: 15px;
                font-style: italic;
            }}
            .expiry-notice {{
                background: #fef3c7;
                border-left: 4px solid #f59e0b;
                padding: 16px;
                margin: 30px 0;
                border-radius: 8px;
                text-align: left;
            }}
            .expiry-notice p {{
                color: #92400e;
                font-size: 14px;
                line-height: 1.6;
                margin: 0;
            }}
            .expiry-notice strong {{
                color: #78350f;
                font-weight: 700;
            }}
            .security-note {{
                color: #6b7280;
                font-size: 14px;
                line-height: 1.6;
                margin-top: 30px;
                padding: 20px;
                background: #f9fafb;
                border-radius: 8px;
            }}
            .footer {{
                background: #f9fafb;
                padding: 30px 40px;
                text-align: center;
                border-top: 1px solid #e5e7eb;
            }}
            .footer-text {{
                color: #6b7280;
                font-size: 14px;
                line-height: 1.8;
                margin: 0;
            }}
            .social-links {{
                margin: 20px 0;
            }}
            .social-links a {{
                color: #3b82f6;
                text-decoration: none;
                margin: 0 10px;
                font-size: 14px;
            }}
            .copyright {{
                color: #9ca3af;
                font-size: 12px;
                margin-top: 20px;
            }}
            @media only screen and (max-width: 600px) {{
                body {{ padding: 20px 10px; }}
                .content {{ padding: 30px 20px; }}
                .otp-code {{ font-size: 36px; letter-spacing: 4px; }}
                .welcome-text {{ font-size: 24px; }}
            }}
        </style>
    </head>
    <body>
        <div class="email-wrapper">
            <!-- Header with Logo -->
            <div class="header">
                <img src="http://ijaw-voices.duckdns.org/static/images/email-header.png" alt="Ijaw Voices Logo" class="logo">
                <h1 class="header-title">Ijaw Voices</h1>
            </div>

            <!-- Main Content -->
            <div class="content">
                <h2 class="welcome-text">Welcome to Ijaw Voices! 🎉</h2>
                <p class="greeting">
                    Hello <strong>{user.first_name or 'there'}</strong>,<br>
                    We're excited to have you join our community! Just one more step to get started.
                </p>

                <!-- OTP Container -->
                <div class="otp-container">
                    <div class="otp-label">Your Verification Code</div>
                    <div class="otp-code" title="Click to select and copy">{otp}</div>
                    <div class="copy-instruction">👆 Click the code above to select it, then copy (Ctrl+C or Cmd+C)</div>
                </div>

                <!-- Expiry Notice -->
                <div class="expiry-notice">
                    <p>
                        ⏰ <strong>This code will expire in 10 minutes.</strong><br>
                        Please enter it soon to complete your registration.
                    </p>
                </div>

                <!-- Security Note -->
                <div class="security-note">
                    🔒 <strong>Security Note:</strong> If you didn't request this code, please ignore this email.
                    Your account is safe and no action is needed.
                </div>
            </div>

            <!-- Footer -->
            <div class="footer">
                <p class="footer-text">
                    <strong>Happy learning!</strong><br>
                    The Ijaw Voices Team
                </p>
                <div class="social-links">
                    <a href="#">Website</a> •
                    <a href="#">Support</a> •
                    <a href="#">Privacy Policy</a>
                </div>
                <p class="copyright">
                    © {timezone.now().year} Ijaw Voices. All rights reserved.
                </p>
            </div>
        </div>
    </body>
    </html>
    """

    try:
        # Use Django's send_mail with Gmail SMTP
        send_mail(
            subject=subject,
            message=f"Your verification code is: {otp}\n\nThis code will expire in 10 minutes.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )
        print(f"Email sent successfully to {user.email}")
        return otp  # Return for testing/debugging
    except Exception as e:
        # Log the error for debugging
        print(f"Failed to send OTP email to {user.email}: {e}")
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
