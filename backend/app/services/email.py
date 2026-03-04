"""
Email Service - Gmail SMTP
"""
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


def send_reset_email(to_email: str, reset_token: str) -> bool:
    """
    Send a password reset email via Gmail SMTP.
    
    Args:
        to_email: Recipient email address
        reset_token: The secure reset token
        
    Returns:
        True if email sent successfully, False otherwise
    """
    reset_link = f"{settings.frontend_url}/reset-password?token={reset_token}"
    
    # If SMTP credentials are not configured, log the link instead
    if not settings.smtp_email or not settings.smtp_password:
        logger.warning("SMTP not configured. Logging reset link to console.")
        logger.info("=" * 60)
        logger.info(f"🔑 PASSWORD RESET LINK (for: {to_email})")
        logger.info(f"   {reset_link}")
        logger.info("=" * 60)
        return True
    
    try:
        # Build email
        msg = MIMEMultipart("alternative")
        msg["Subject"] = "NutriLens - Reset Your Password"
        msg["From"] = settings.smtp_email
        msg["To"] = to_email
        
        # Plain text version
        text = f"""
Hello,

You requested a password reset for your NutriLens account.

Click the link below to reset your password:
{reset_link}

This link will expire in 30 minutes.

If you didn't request this, please ignore this email.

— NutriLens Team
"""
        
        # HTML version
        html = f"""
<div style="font-family: 'Inter', Arial, sans-serif; max-width: 600px; margin: 0 auto; background: #0a0a0a; color: #ffffff; border-radius: 16px; overflow: hidden;">
    <div style="padding: 40px 32px; text-align: center; background: linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 100%);">
        <h1 style="margin: 0 0 8px; font-size: 28px; font-weight: 700; color: #ffffff;">
            Nutri<span style="color: #A7EFC1;">Lens</span>
        </h1>
        <p style="margin: 0; color: #9ca3af; font-size: 14px;">Password Reset Request</p>
    </div>
    <div style="padding: 40px 32px;">
        <p style="color: #d1d5db; font-size: 16px; line-height: 1.6; margin: 0 0 24px;">
            You requested a password reset for your account. Click the button below to set a new password.
        </p>
        <div style="text-align: center; margin: 32px 0;">
            <a href="{reset_link}" 
               style="display: inline-block; background: #A7EFC1; color: #000000; font-weight: 700; font-size: 16px; padding: 14px 32px; border-radius: 12px; text-decoration: none;">
                Reset Password
            </a>
        </div>
        <p style="color: #6b7280; font-size: 13px; line-height: 1.5; margin: 24px 0 0;">
            This link will expire in <strong>30 minutes</strong>.<br>
            If you didn't request a password reset, you can safely ignore this email.
        </p>
    </div>
    <div style="padding: 20px 32px; border-top: 1px solid #1f2937; text-align: center;">
        <p style="margin: 0; color: #4b5563; font-size: 12px;">&copy; 2024 NutriLens. All rights reserved.</p>
    </div>
</div>
"""
        
        msg.attach(MIMEText(text, "plain"))
        msg.attach(MIMEText(html, "html"))
        
        # Send via Gmail SMTP
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
            server.starttls()
            server.login(settings.smtp_email, settings.smtp_password)
            server.sendmail(settings.smtp_email, to_email, msg.as_string())
        
        logger.info(f"Password reset email sent to {to_email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send reset email to {to_email}: {e}")
        # Fallback: log the link so the feature still works
        logger.info("=" * 60)
        logger.info(f"🔑 FALLBACK - PASSWORD RESET LINK (for: {to_email})")
        logger.info(f"   {reset_link}")
        logger.info("=" * 60)
        return False
