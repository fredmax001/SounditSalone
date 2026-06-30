"""
Email Service Module
====================

Centralized email sending functionality using Hostinger SMTP SSL as primary
transport, with SendGrid as fallback.

All emails use Sound It Salone branding.

From Address: support@sounditsl.com or noreply@sounditentsl.com
"""

import base64
import io
import logging
import smtplib
import ssl
import zipfile
from email import encoders
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Optional
from config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

# Default from email address
DEFAULT_FROM_EMAIL = settings.SMTP_FROM or settings.SENDGRID_FROM_EMAIL or "noreply@sounditentsl.com"
DEFAULT_FROM_NAME = "Sound It Salone"


# ─────────────────────────── Core SMTP Transport ───────────────────────────

def _smtp_send(
    to_email: str,
    subject: str,
    body: str = "",
    html_body: Optional[str] = None,
    from_email: Optional[str] = None,
    attachments: Optional[List[tuple]] = None
) -> bool:
    """Send email via Hostinger SMTP SSL (or any SMTP provider).
    attachments: list of (filename, bytes, mimetype) tuples
    """
    if not settings.SMTP_USER or not settings.SMTP_PASS:
        return False

    sender = from_email or settings.SMTP_FROM or settings.SMTP_USER
    try:
        msg = MIMEMultipart("mixed")
        msg["Subject"] = subject
        msg["From"] = sender
        msg["To"] = to_email

        # Body part
        body_part = MIMEMultipart("alternative")
        if body:
            body_part.attach(MIMEText(body, "plain"))
        if html_body:
            body_part.attach(MIMEText(html_body, "html"))
        msg.attach(body_part)

        # Attachments
        if attachments:
            for filename, file_bytes, mimetype in attachments:
                maintype, subtype = mimetype.split("/", 1) if "/" in mimetype else ("application", "octet-stream")
                part = MIMEBase(maintype, subtype)
                part.set_payload(file_bytes)
                encoders.encode_base64(part)
                part.add_header("Content-Disposition", f'attachment; filename="{filename}"')
                msg.attach(part)

        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT, context=context, timeout=30) as server:
            server.login(settings.SMTP_USER, settings.SMTP_PASS)
            envelope_from = settings.SMTP_USER
            server.sendmail(envelope_from, [to_email], msg.as_string())

        logger.info(f"[SMTP EMAIL SENT] To: {to_email}, Subject: {subject}, Attachments: {len(attachments or [])}")
        return True
    except Exception as e:
        logger.error(f"SMTP send failed: {e}")
        return False


def _sendgrid_send(
    to_email: str,
    subject: str,
    html_content: str,
    from_email: str = DEFAULT_FROM_EMAIL,
    from_name: str = DEFAULT_FROM_NAME,
    text_content: Optional[str] = None
) -> bool:
    """Send email via SendGrid as fallback."""
    try:
        from sendgrid import SendGridAPIClient
        from sendgrid.helpers.mail import Mail, Email, Content, HtmlContent

        api_key = settings.SENDGRID_API_KEY
        if not api_key:
            return False

        message = Mail(
            from_email=Email(from_email, from_name),
            to_emails=to_email,
            subject=subject,
            html_content=HtmlContent(html_content)
        )
        if text_content:
            message.add_content(Content("text/plain", text_content))

        sg = SendGridAPIClient(api_key)
        response = sg.send(message)
        return response.status_code in [200, 201, 202]
    except Exception as e:
        logger.error(f"SendGrid send failed: {e}")
        return False


def _console_log(to_email: str, subject: str, body: str):
    """Dev fallback: log email to console."""
    log_msg = f"[EMAIL LOG — DEV MODE] To: {to_email} | Subject: {subject}"
    logger.info(log_msg)
    print(log_msg)
    preview = f"Body preview: {body[:300]}..."
    logger.info(preview)
    print(preview)


# ─────────────────────────── Public API ───────────────────────────

def send_email(
    to_email: str,
    subject: str,
    html_content: str,
    from_email: str = DEFAULT_FROM_EMAIL,
    from_name: str = DEFAULT_FROM_NAME,
    text_content: Optional[str] = None,
    attachments: Optional[List[tuple]] = None
) -> bool:
    """
    Send an email via Hostinger SMTP SSL → SendGrid fallback → console log.
    All emails use Sound It Salone branding.
    """
    # 1) Try Hostinger SMTP SSL first
    if _smtp_send(to_email, subject, text_content or "", html_content, from_email, attachments):
        return True

    # 2) Fallback to SendGrid (if no attachments, since SendGrid handles them differently)
    if not attachments:
        if _sendgrid_send(to_email, subject, html_content, from_email, from_name, text_content):
            return True

    # 3) Dev fallback
    _console_log(to_email, subject, text_content or html_content or "")
    return False


def send_email_to_multiple(
    to_emails: List[str],
    subject: str,
    html_content: str,
    from_email: str = DEFAULT_FROM_EMAIL,
    from_name: str = DEFAULT_FROM_NAME
) -> dict:
    """Send an email to multiple recipients."""
    results = {'successful': 0, 'failed': 0, 'total': len(to_emails)}
    for email in to_emails:
        if send_email(email, subject, html_content, from_email, from_name):
            results['successful'] += 1
        else:
            results['failed'] += 1
    return results


# ─────────────────────────── HTML Email Wrapper ───────────────────────────

def _email_wrapper(title: str, content_html: str) -> str:
    """Standard HTML email wrapper with Sound It Salone branding."""
    return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        body {{ margin: 0; padding: 0; background: #0a0a0a; font-family: 'Segoe UI', Arial, sans-serif; }}
        .container {{ max-width: 600px; margin: 0 auto; background: #141414; border-radius: 16px; overflow: hidden; }}
        .header {{ background: #FFC107; padding: 24px 32px; text-align: center; }}
        .header h1 {{ margin: 0; color: #000; font-size: 24px; font-weight: 800; }}
        .content {{ padding: 32px; color: #e5e5e5; line-height: 1.6; }}
        .content p {{ margin: 0 0 16px; }}
        .content strong {{ color: #FFC107; }}
        .cta {{ display: inline-block; margin: 16px 0; padding: 14px 28px; background: #FFC107; color: #000; text-decoration: none; border-radius: 12px; font-weight: 700; }}
        .qr-box {{ background: #fff; padding: 20px; border-radius: 12px; text-align: center; margin: 20px 0; }}
        .qr-box img {{ max-width: 240px; height: auto; }}
        .footer {{ padding: 24px 32px; text-align: center; color: #666; font-size: 12px; border-top: 1px solid #222; }}
        .code {{ font-family: 'Courier New', monospace; font-size: 32px; letter-spacing: 6px; color: #FFC107; background: #0a0a0a; padding: 16px 32px; border-radius: 8px; display: inline-block; margin: 12px 0; }}
        @media only screen and (max-width: 600px) {{
            .content {{ padding: 20px; }}
            .code {{ font-size: 24px; letter-spacing: 4px; padding: 12px 20px; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Sound It Salone</h1>
        </div>
        <div class="content">
            {content_html}
        </div>
        <div class="footer">
            <p>Sound It Salone — Your Guide to Sierra Leone Entertainment</p>
            <p>If you need help, contact us at support@sounditsl.com</p>
        </div>
    </div>
</body>
</html>"""


# ─── OTP Email ───

def send_otp_email(to_email: str, otp_code: str, purpose: str = "verification") -> bool:
    """Send OTP verification code via email with Sound It Salone branding."""
    purpose_text = {
        "verification": "verify your email",
        "register": "complete your registration",
        "reset_password": "reset your password",
        "login": "log in to your account",
    }.get(purpose, "verify your email")

    subject = "Your Sound It Salone Verification Code"
    body = f"""Your Sound It Salone verification code is: {otp_code}

This code will expire in 10 minutes.

If you didn't request this code, you can safely ignore this email.

— Sound It Salone Team"""

    html = _email_wrapper(
        subject,
        f"""<p>Your verification code is:</p>
        <div class="code">{otp_code}</div>
        <p>Use this code to <strong>{purpose_text}</strong>.</p>
        <p>This code will expire in <strong>10 minutes</strong>.</p>
        <p style="color:#888; font-size:13px;">If you didn't request this code, you can safely ignore this email.</p>"""
    )
    return send_email(to_email, subject, html, text_content=body)


# ─── Welcome Email ───

def send_welcome_email(to_email: str, first_name: str = "") -> bool:
    """Welcome email for regular users (sent immediately on registration)."""
    name = first_name or "there"
    subject = "Welcome to Sound It Salone 🎉"
    body = f"""Hi {name},

Welcome to Sound It Salone 🎉

We're excited to have you on the platform.

Sound It Salone is your guide to Sierra Leone entertainment. Here's how to get the best experience:

👤 USERS
The mobile version is best for regular users. You can:
• Discover events across Sierra Leone
• Buy tickets securely
• View your QR tickets
• Access event information
• Receive updates and notifications
• Scan into events quickly

For a better mobile experience, you can also add Sound It Salone to your home screen like an app:

📱 On iPhone (Safari):
1. Open the website
2. Tap the Share button
3. Select "Add to Home Screen"

📱 On Android (Chrome):
1. Open the website
2. Tap the 3-dot menu
3. Select "Add to Home Screen"

Thank you for joining Sound It Salone.
We're building a smarter entertainment experience for Sierra Leone.

— Sound It Salone Team"""

    html = _email_wrapper(
        subject,
        f"""<p>Hi {name},</p>
        <p>Welcome to <strong>Sound It Salone</strong> 🎉</p>
        <p>We're excited to have you on the platform.</p>
        <p>Sound It Salone is your guide to Sierra Leone entertainment. Here's how to get the best experience:</p>
        <div style="background:#0a0a0a; padding:20px; border-radius:12px; margin:16px 0;">
            <h3 style="color:#FFC107; margin:0 0 12px;">👤 USERS</h3>
            <p style="margin:0 0 12px;">The mobile version is best for regular users. You can:</p>
            <ul style="margin:0; padding-left:20px; color:#ccc;">
                <li>Discover events across Sierra Leone</li>
                <li>Buy tickets securely</li>
                <li>View your QR tickets</li>
                <li>Access event information</li>
                <li>Receive updates and notifications</li>
                <li>Scan into events quickly</li>
            </ul>
        </div>
        <p>For a better mobile experience, you can also add Sound It Salone to your home screen like an app:</p>
        <div style="background:#0a0a0a; padding:16px; border-radius:12px; margin:12px 0;">
            <p style="margin:0 0 8px; font-weight:600;">📱 On iPhone (Safari):</p>
            <ol style="margin:0; padding-left:20px; color:#ccc;">
                <li>Open the website</li>
                <li>Tap the Share button</li>
                <li>Select "Add to Home Screen"</li>
            </ol>
        </div>
        <div style="background:#0a0a0a; padding:16px; border-radius:12px; margin:12px 0;">
            <p style="margin:0 0 8px; font-weight:600;">📱 On Android (Chrome):</p>
            <ol style="margin:0; padding-left:20px; color:#ccc;">
                <li>Open the website</li>
                <li>Tap the 3-dot menu</li>
                <li>Select "Add to Home Screen"</li>
            </ol>
        </div>
        <a href="https://sounditsl.com" class="cta">Start Exploring</a>
        <p style="margin-top:24px; color:#888;">Thank you for joining Sound It Salone.<br>We're building a smarter entertainment experience for Sierra Leone.</p>
        <p style="color:#888;">— Sound It Salone Team</p>"""
    )
    return send_email(to_email, subject, html, text_content=body)


def send_business_welcome_email(to_email: str, first_name: str = "") -> bool:
    """Welcome email for business/organizer accounts."""
    name = first_name or "there"
    subject = "Your Organizer Account is Approved — Welcome to Sound It Salone!"
    body = f"""Hi {name},

Welcome to Sound It Salone 🎉

We're excited to have you on the platform.

🎟️ ORGANIZERS
For organizers, we highly recommend using a laptop or desktop during setup and event creation.

Desktop gives you full access to:
• Event creation tools
• Ticket management
• Analytics & reports
• Team & vendor management
• Revenue tracking
• Full dashboard controls

Mobile is mainly optimized for:
• Viewing metrics
• Event scanning/check-ins
• Managing quick tasks on the go

Thank you for joining Sound It Salone. We're building a smarter entertainment experience for Sierra Leone.

— Sound It Salone Team"""

    html = _email_wrapper(
        subject,
        f"""<p>Hi {name},</p>
        <p>Welcome to <strong>Sound It Salone</strong> 🎉</p>
        <p>We're excited to have you on the platform.</p>
        <div style="background:#0a0a0a; padding:20px; border-radius:12px; margin:16px 0;">
            <h3 style="color:#FFC107; margin:0 0 12px;">🎟️ ORGANIZERS</h3>
            <p style="margin:0 0 12px;">For organizers, we highly recommend using a <strong>laptop or desktop</strong> during setup and event creation.</p>
            <p style="margin:0 0 8px; font-weight:600;">Desktop gives you full access to:</p>
            <ul style="margin:0 0 16px; padding-left:20px; color:#ccc;">
                <li>Event creation tools</li>
                <li>Ticket management</li>
                <li>Analytics & reports</li>
                <li>Team & vendor management</li>
                <li>Revenue tracking</li>
                <li>Full dashboard controls</li>
            </ul>
            <p style="margin:0 0 8px; font-weight:600;">Mobile is mainly optimized for:</p>
            <ul style="margin:0; padding-left:20px; color:#ccc;">
                <li>Viewing metrics</li>
                <li>Event scanning/check-ins</li>
                <li>Managing quick tasks on the go</li>
            </ul>
        </div>
        <a href="https://sounditsl.com/login" class="cta">Go to Dashboard</a>
        <p style="margin-top:24px; color:#888;">Thank you for joining Sound It Salone.<br>We're building a smarter entertainment experience for Sierra Leone.</p>
        <p style="color:#888;">— Sound It Salone Team</p>"""
    )
    return send_email(to_email, subject, html, text_content=body)


# ─── Password Reset Email ───

def send_password_reset_email(to_email: str, reset_token: str, user_name: str = "") -> bool:
    """Send password reset email with reset link."""
    base_url = settings.BASE_URL or "https://sounditsl.com"
    reset_url = f"{base_url}/reset-password?token={reset_token}"

    subject = "Reset your Sound It Salone password"
    body = (
        f"Hello {user_name or 'there'},\n\n"
        f"You requested a password reset. Click the link below to reset your password:\n\n"
        f"{reset_url}\n\n"
        f"This link will expire in 1 hour.\n\n"
        f"If you didn't request this, you can safely ignore this email.\n\n"
        f"— Sound It Salone Team"
    )
    html = _email_wrapper(
        subject,
        f"""<p>Hello {user_name or 'there'},</p>
        <p>You requested a password reset. Click the link below to reset your password:</p>
        <a href="{reset_url}" class="cta">Reset Password</a>
        <p style="color:#888; margin-top:16px;">This link will expire in 1 hour.</p>
        <p style="color:#888;">If you didn't request this, you can safely ignore this email.</p>"""
    )
    return send_email(to_email, subject, html, text_content=body)


def send_password_changed_confirmation(to_email: str, user_name: str = "") -> bool:
    """Send password changed confirmation."""
    subject = "Your Sound It Salone password was changed"
    body = (
        f"Hello {user_name or 'there'},\n\n"
        f"Your password was successfully changed.\n\n"
        f"If you didn't make this change, please contact support immediately at support@sounditsl.com\n\n"
        f"— Sound It Salone Team"
    )
    html = _email_wrapper(
        subject,
        f"""<p>Hello {user_name or 'there'},</p>
        <p>Your password was successfully changed.</p>
        <p style="color:#888;">If you didn't make this change, please contact support immediately at <a href="mailto:support@sounditsl.com" style="color:#FFC107;">support@sounditsl.com</a></p>"""
    )
    return send_email(to_email, subject, html, text_content=body)


# ─── Ticket Confirmation Email ───

def send_ticket_confirmation(
    to_email: str,
    event_title: str,
    ticket_count: int,
    order_ref: str,
    total_amount: float,
    user_name: str = ""
) -> bool:
    """Send ticket purchase confirmation email."""
    base_url = settings.BASE_URL or "https://sounditsl.com"
    subject = f"🎫 Your Ticket Confirmation - {event_title}"
    body = f"""Hi {user_name or 'there'},

Thank you for your purchase! Your ticket for "{event_title}" has been confirmed.

Ticket Details:
• Event: {event_title}
• Quantity: {ticket_count} ticket(s)
• Total Paid: SLE {total_amount}
• Order Reference: {order_ref}

Please show the QR code in your tickets page at the entrance.

View your tickets: {base_url}/tickets

Need help? Contact us at support@sounditsl.com

© Sound It Salone. All rights reserved."""

    html = _email_wrapper(
        subject,
        f"""<p>Hi {user_name or 'there'},</p>
        <p>Thank you for your purchase! Your ticket for <strong>{event_title}</strong> has been confirmed.</p>
        <div style="background:#0a0a0a; padding:20px; border-radius:12px; margin:16px 0; border-left:4px solid #FFC107;">
            <h3 style="margin-top:0; color:#FFC107;">Ticket Details</h3>
            <p><strong>Event:</strong> {event_title}</p>
            <p><strong>Quantity:</strong> {ticket_count} ticket(s)</p>
            <p><strong>Total Paid:</strong> SLE {total_amount}</p>
            <p><strong>Order Reference:</strong> {order_ref}</p>
        </div>
        <p>Please show the QR code in your tickets page at the entrance.</p>
        <a href="{base_url}/tickets" class="cta">View My Tickets</a>
        <p style="color:#888; font-size:12px; margin-top:24px;">Need help? Contact us at <a href="mailto:support@sounditsl.com" style="color:#FFC107;">support@sounditsl.com</a><br>© Sound It Salone. All rights reserved.</p>"""
    )
    return send_email(to_email, subject, html, text_content=body)


# ─── Contact Form Email ───

import html as html_module


def send_contact_form_email(name: str, from_email: str, subject: str, message: str) -> bool:
    """Send contact form submission to support."""
    safe_name = html_module.escape(name)
    safe_from_email = html_module.escape(from_email)
    safe_subject = html_module.escape(subject)
    safe_message = html_module.escape(message).replace(chr(10), '<br>')

    full_subject = f"[Contact Form] {safe_subject}"
    body = f"From: {name} <{from_email}>\n\nSubject: {subject}\n\n{message}"
    html = _email_wrapper(
        full_subject,
        f"""<h2 style="color:#FFC107;">New Contact Form Submission</h2>
        <p><strong>From:</strong> {safe_name} ({safe_from_email})</p>
        <p><strong>Subject:</strong> {safe_subject}</p>
        <hr style="border-color:#333;">
        <p>{safe_message}</p>
        <hr style="border-color:#333;">
        <p style="color:#666; font-size:12px;">To reply, email: {safe_from_email}</p>"""
    )
    return send_email("support@sounditsl.com", full_subject, html, text_content=body)


# ─── Broadcast Email ───

def send_broadcast_email(to_email: str, subject: str, message: str) -> bool:
    """Send broadcast message to a user."""
    body = message
    html = _email_wrapper(
        subject,
        f"""<h2 style="color:#FFC107;">{subject}</h2>
        <div style="line-height:1.6; color:#e5e5e5;">{message.replace(chr(10), '<br>')}</div>
        <p style="color:#666; font-size:12px; margin-top:24px;">
            You're receiving this because you're a member of Sound It Salone.<br>
            <a href="https://sounditsl.com" style="color:#FFC107;">Visit Sound It Salone</a>
        </p>"""
    )
    return send_email(to_email, subject, html, text_content=body)


# ─── Ticket Approved Email with ZIP attachment ───

def _decode_qr_bytes(qr_data: str) -> bytes:
    """Decode a base64 data URI into raw PNG bytes."""
    try:
        if qr_data.startswith("data:image"):
            qr_data = qr_data.split(",", 1)[-1]
        return base64.b64decode(qr_data)
    except Exception:
        return b""


def send_ticket_approved_email(
    to_email: str,
    first_name: str,
    event_title: str,
    event_date: str,
    event_venue: str,
    tickets: List[dict],
    quantity: int = 1
) -> bool:
    """Send ticket approval email with QR codes bundled in a ZIP attachment."""
    name = first_name or "there"
    safe_title = "".join(c if c.isalnum() else "_" for c in event_title)[:30]
    subject = f"Your tickets for {event_title} are confirmed!"

    ticket_list_text = "\n".join(
        f"• Ticket #{i+1}: {t['ticket_number']}" for i, t in enumerate(tickets)
    )
    body = f"""Hi {name},

Great news! Your ticket order for "{event_title}" has been approved.

Event Details:
• Event: {event_title}
• Date: {event_date}
• Venue: {event_venue}
• Quantity: {quantity} ticket(s)

Your Tickets:
{ticket_list_text}

Please download the attached ZIP file and show each QR code at the entrance (one per person).
You can also view your tickets online: https://sounditsl.com/tickets

— Sound It Salone Team"""

    ticket_rows = "\n".join(
        f"""<tr>
            <td style="padding:10px 16px; border-bottom:1px solid #222; color:#FFC107; font-weight:700;">Ticket #{i+1}</td>
            <td style="padding:10px 16px; border-bottom:1px solid #222; color:#e5e5e5; font-family:monospace;">{t['ticket_number']}</td>
        </tr>"""
        for i, t in enumerate(tickets)
    )

    html = _email_wrapper(
        subject,
        f"""<p>Hi {name},</p>
        <p>Great news! Your ticket order for <strong>{event_title}</strong> has been approved.</p>
        <div style="background:#0a0a0a; padding:16px; border-radius:12px; margin:16px 0;">
            <p style="margin:4px 0;"><strong>Event:</strong> {event_title}</p>
            <p style="margin:4px 0;"><strong>Date:</strong> {event_date}</p>
            <p style="margin:4px 0;"><strong>Venue:</strong> {event_venue}</p>
            <p style="margin:4px 0;"><strong>Quantity:</strong> {quantity} ticket(s)</p>
        </div>
        <p style="margin:0 0 12px; font-weight:600;">Your tickets:</p>
        <table style="width:100%; border-collapse:collapse; margin:0 0 20px;">
            {ticket_rows}
        </table>
        <p style="margin:0 0 16px;">📎 <strong>Download the attached ZIP file</strong> for your QR codes. Show each QR at the entrance (one per person).</p>
        <a href="https://sounditsl.com/tickets" class="cta">View My Tickets</a>
        <p style="margin-top:24px; color:#888;">— Sound It Salone Team</p>"""
    )

    # Build ZIP attachment
    attachments = []
    try:
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
            for i, t in enumerate(tickets):
                qr_bytes = _decode_qr_bytes(t.get("qr_code", ""))
                if qr_bytes:
                    filename = f"ticket_{i+1}_{t['ticket_number']}.png"
                    zf.writestr(filename, qr_bytes)
        zip_buffer.seek(0)
        zip_filename = f"soundit_salone_tickets_{safe_title}.zip"
        attachments.append((zip_filename, zip_buffer.getvalue(), "application/zip"))
    except Exception as e:
        logger.warning(f"Failed to create ticket ZIP: {e}")

    return send_email(to_email, subject, html, text_content=body, attachments=attachments)
