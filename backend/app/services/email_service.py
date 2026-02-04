"""
NutriLens Backend - Email Service

Email sending functionality (stub for now).
"""

from typing import Optional, List

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class EmailService:
    """Service for sending emails."""
    
    def __init__(self):
        self.smtp_host = settings.SMTP_HOST
        self.smtp_port = settings.SMTP_PORT
        self.smtp_user = settings.SMTP_USER
        self.smtp_password = settings.SMTP_PASSWORD
        self.from_email = settings.SMTP_FROM_EMAIL
        self.enabled = bool(self.smtp_user and self.smtp_password)
    
    async def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None,
    ) -> bool:
        """
        Send an email.
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            html_content: HTML email body
            text_content: Plain text fallback
        
        Returns:
            True if sent successfully
        """
        if not self.enabled:
            logger.warning("Email service not configured, skipping send")
            return False
        
        try:
            import smtplib
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart
            
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = self.from_email
            msg["To"] = to_email
            
            if text_content:
                msg.attach(MIMEText(text_content, "plain"))
            msg.attach(MIMEText(html_content, "html"))
            
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)
            
            logger.info(f"Email sent to {to_email}: {subject}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {e}")
            return False
    
    async def send_verification_email(self, to_email: str, token: str) -> bool:
        """Send email verification link."""
        verification_url = f"https://NutriLens.app/verify?token={token}"
        
        html = f"""
        <h1>Welcome to NutriLens!</h1>
        <p>Please verify your email address by clicking the link below:</p>
        <p><a href="{verification_url}">Verify Email</a></p>
        <p>If you didn't create an account, you can ignore this email.</p>
        """
        
        return await self.send_email(
            to_email=to_email,
            subject="Verify your NutriLens account",
            html_content=html,
        )
    
    async def send_password_reset_email(self, to_email: str, token: str) -> bool:
        """Send password reset link."""
        reset_url = f"https://NutriLens.app/reset-password?token={token}"
        
        html = f"""
        <h1>Password Reset Request</h1>
        <p>Click the link below to reset your password:</p>
        <p><a href="{reset_url}">Reset Password</a></p>
        <p>If you didn't request a password reset, you can ignore this email.</p>
        <p>This link will expire in 1 hour.</p>
        """
        
        return await self.send_email(
            to_email=to_email,
            subject="Reset your NutriLens password",
            html_content=html,
        )
