from email.message import EmailMessage
import aiosmtplib
from config import settings

async def send_email(to_email: str, subject: str,plain_text: str, html_content: str = None):
    message = EmailMessage() #email message object
    message["From"] = settings.mail_from
    message["To"] = to_email
    message["Subject"] = subject
    message.set_content(plain_text)

    if html_content:
        message.add_alternative(html_content, subtype="html")

    await aiosmtplib.send(
                message,
                hostname=settings.email_host,
                port=settings.email_port,
                username=settings.email_username if settings.email_username else None,
                password=settings.email_password.get_secret_value() or None,
                use_tls=settings.mail_use_tls,
            )

async def send_password_reset_email(to_email: str, reset_token: str):
    subject = "Password Reset Request"
    reset_link = f"{settings.frontend_url}/reset-password?token={reset_token}"
    plain_text = f"To reset your password, click the following link: {reset_link}"
    html_content = f"""
    <html>
        <body>
            <p>To reset your password, click the following link:</p>
            <a href="{reset_link}">Reset Password</a>
            <p>This link will expire in {settings.reset_token_expire_minutes} minutes.</p>
            <p>If you did not request a password reset, please ignore this email.</p>
            <p>Thank you,</p>
            <p>Your FastAPI Blog Team</p>
        </body>
    </html>
    """
    await send_email(to_email, subject, plain_text, html_content)