"""
Email Service for SquigLeague

Handles sending verification emails and notifications
"""

import os
from typing import Optional
import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


# ═══════════════════════════════════════════════
# EMAIL CONFIGURATION
# ═══════════════════════════════════════════════


def get_smtp_config() -> dict:
    """Get SMTP configuration from environment"""
    return {
        "hostname": os.getenv("SMTP_HOST", "localhost"),
        "port": int(os.getenv("SMTP_PORT", "1025")),
        "username": os.getenv("SMTP_USER", ""),
        "password": os.getenv("SMTP_PASSWORD", ""),
        "use_tls": os.getenv("SMTP_USE_TLS", "false").lower() == "true",
        "from_email": os.getenv("SMTP_FROM_EMAIL", "noreply@squigleague.local"),
        "from_name": os.getenv("SMTP_FROM_NAME", "SquigLeague"),
    }


# ═══════════════════════════════════════════════
# EMAIL TEMPLATES
# ═══════════════════════════════════════════════


def get_verification_email_html(username: str, verification_url: str) -> str:
    """HTML template for email verification"""
    return f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background-color: #4a5568; color: white; padding: 20px; text-align: center; }}
        .content {{ background-color: #f7fafc; padding: 30px; }}
        .button {{ display: inline-block; background-color: #48bb78; color: white; padding: 12px 24px; text-decoration: none; border-radius: 4px; margin: 20px 0; }}
        .footer {{ font-size: 12px; color: #718096; padding: 20px; text-align: center; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Welcome to SquigLeague!</h1>
        </div>
        <div class="content">
            <h2>Verify Your Email Address</h2>
            <p>Hi {username},</p>
            <p>Thanks for registering with SquigLeague! To complete your registration and start creating matchups, please verify your email address.</p>
            <p style="text-align: center;">
                <a href="{verification_url}" class="button">Verify Email Address</a>
            </p>
            <p>Or copy and paste this link into your browser:</p>
            <p style="word-break: break-all; color: #4299e1;">{verification_url}</p>
            <p><strong>This link expires in 24 hours.</strong></p>
            <p>If you didn't create this account, you can safely ignore this email.</p>
        </div>
        <div class="footer">
            <p>This is an automated email from SquigLeague. Please do not reply.</p>
        </div>
    </div>
</body>
</html>
"""


def get_verification_email_text(username: str, verification_url: str) -> str:
    """Plain text template for email verification"""
    return f"""
Welcome to SquigLeague!

Hi {username},

Thanks for registering with SquigLeague! To complete your registration and start creating matchups, please verify your email address.

Verification Link:
{verification_url}

This link expires in 24 hours.

If you didn't create this account, you can safely ignore this email.

---
SquigLeague - Warhammer Matchup & Tournament System
This is an automated email. Please do not reply.
"""


# ═══════════════════════════════════════════════
# EMAIL SENDING
# ═══════════════════════════════════════════════


async def send_email(
    to_email: str,
    subject: str,
    html_body: str,
    text_body: str,
) -> bool:
    """
    Send email via SMTP
    
    Args:
        to_email: Recipient email address
        subject: Email subject line
        html_body: HTML email content
        text_body: Plain text email content
        
    Returns:
        True if email sent successfully, False otherwise
    """
    config = get_smtp_config()
    
    # Create message
    message = MIMEMultipart("alternative")
    message["From"] = f"{config['from_name']} <{config['from_email']}>"
    message["To"] = to_email
    message["Subject"] = subject
    
    # Attach both text and HTML versions
    text_part = MIMEText(text_body, "plain")
    html_part = MIMEText(html_body, "html")
    message.attach(text_part)
    message.attach(html_part)
    
    try:
        # Send email
        await aiosmtplib.send(
            message,
            hostname=config["hostname"],
            port=config["port"],
            username=config["username"] if config["username"] else None,
            password=config["password"] if config["password"] else None,
            use_tls=config["use_tls"],
        )
        return True
    except Exception as e:
        print(f"ERROR: Failed to send email to {to_email}: {e}")
        return False


async def send_verification_email(
    username: str,
    email: str,
    verification_token: str,
) -> bool:
    """
    Send email verification link to new user
    
    Args:
        username: User's chosen username
        email: User's email address
        verification_token: Unique verification token
        
    Returns:
        True if email sent successfully
    """
    base_url = os.getenv("BASE_URL", "http://localhost")
    verification_url = f"{base_url}/squire/verify-email?token={verification_token}"
    
    subject = "Verify your SquigLeague account"
    html_body = get_verification_email_html(username, verification_url)
    text_body = get_verification_email_text(username, verification_url)
    
    return await send_email(email, subject, html_body, text_body)


async def send_password_reset_email(
    username: str,
    email: str,
    reset_token: str,
) -> bool:
    """
    Send password reset link (future implementation)
    
    Args:
        username: User's username
        email: User's email address
        reset_token: Unique password reset token
        
    Returns:
        True if email sent successfully
    """
    base_url = os.getenv("BASE_URL", "http://localhost")
    reset_url = f"{base_url}/squire/reset-password?token={reset_token}"
    
    subject = "Reset your SquigLeague password"
    
    html_body = f"""
<!DOCTYPE html>
<html>
<body>
    <h2>Password Reset Request</h2>
    <p>Hi {username},</p>
    <p>We received a request to reset your password. Click the link below to set a new password:</p>
    <p><a href="{reset_url}">Reset Password</a></p>
    <p>This link expires in 1 hour.</p>
    <p>If you didn't request this, please ignore this email.</p>
</body>
</html>
"""
    
    text_body = f"""
Password Reset Request

Hi {username},

We received a request to reset your password. Visit this link to set a new password:
{reset_url}

This link expires in 1 hour.

If you didn't request this, please ignore this email.
"""
    
    return await send_email(email, subject, html_body, text_body)
