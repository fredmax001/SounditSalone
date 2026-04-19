"""
Email Service Module
====================

Centralized email sending functionality using SendGrid.
All emails from the platform go through this service.

From Address: support@example.com
"""

from typing import List, Optional
from config import get_settings
import logging

logger = logging.getLogger(__name__)
settings = get_settings()

# Default from email address
DEFAULT_FROM_EMAIL = "support@example.com"
DEFAULT_FROM_NAME = "Sound It Entertainment"


def send_email(
    to_email: str,
    subject: str,
    html_content: str,
    from_email: str = DEFAULT_FROM_EMAIL,
    from_name: str = DEFAULT_FROM_NAME,
    text_content: Optional[str] = None
) -> bool:
    """
    Send an email using SendGrid
    
    Args:
        to_email: Recipient email address
        subject: Email subject
        html_content: HTML content of the email
        from_email: Sender email address (default: support@example.com)
        from_name: Sender name (default: Sound It Entertainment)
        text_content: Plain text content (optional)
    
    Returns:
        bool: True if sent successfully, False otherwise
    """
    try:
        from sendgrid import SendGridAPIClient
        from sendgrid.helpers.mail import Mail, Email, Content, HtmlContent
        
        api_key = settings.SENDGRID_API_KEY
        if not api_key:
            logger.error("SendGrid API key not configured")
            print(f"[EMAIL] Would send to {to_email}: {subject}")
            print(f"[EMAIL] HTML: {html_content[:200]}...")
            return False
        
        # Create the email
        message = Mail(
            from_email=Email(from_email, from_name),
            to_emails=to_email,
            subject=subject,
            html_content=HtmlContent(html_content)
        )
        
        # Add plain text content if provided
        if text_content:
            message.add_content(Content("text/plain", text_content))
        
        # Send the email
        sg = SendGridAPIClient(api_key)
        response = sg.send(message)
        
        if response.status_code in [200, 201, 202]:
            logger.info(f"Email sent successfully to {to_email}")
            print(f"[EMAIL SENT] To: {to_email}, Subject: {subject}")
            return True
        else:
            logger.error(f"SendGrid error: {response.status_code} - {response.body}")
            return False
            
    except Exception as e:
        logger.error(f"Failed to send email: {e}")
        print(f"[EMAIL ERROR] To: {to_email}, Error: {e}")
        return False


def send_email_to_multiple(
    to_emails: List[str],
    subject: str,
    html_content: str,
    from_email: str = DEFAULT_FROM_EMAIL,
    from_name: str = DEFAULT_FROM_NAME
) -> dict:
    """
    Send an email to multiple recipients
    
    Returns:
        dict: {'successful': count, 'failed': count, 'total': count}
    """
    results = {'successful': 0, 'failed': 0, 'total': len(to_emails)}
    
    for email in to_emails:
        if send_email(email, subject, html_content, from_email, from_name):
            results['successful'] += 1
        else:
            results['failed'] += 1
    
    return results


import html as html_module

def send_contact_form_email(name: str, from_email: str, subject: str, message: str) -> bool:
    """
    Send contact form submission to support@example.com
    """
    safe_name = html_module.escape(name)
    safe_from_email = html_module.escape(from_email)
    safe_subject = html_module.escape(subject)
    safe_message = html_module.escape(message).replace(chr(10), '<br>')
    html_content = f"""
    <h2>New Contact Form Submission</h2>
    <hr>
    <p><strong>From:</strong> {safe_name} ({safe_from_email})</p>
    <p><strong>Subject:</strong> {safe_subject}</p>
    <hr>
    <h3>Message:</h3>
    <p>{safe_message}</p>
    <hr>
    <p style="color: #666; font-size: 12px;">
        This email was sent from the Sound It contact form.<br>
        To reply, please email: {safe_from_email}
    </p>
    """
    
    return send_email(
        to_email="support@example.com",
        subject=f"[Contact Form] {subject}",
        html_content=html_content,
        from_email=from_email,
        from_name=name
    )


def send_broadcast_email(to_email: str, subject: str, message: str) -> bool:
    """
    Send broadcast message to a user
    """
    html_content = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <div style="background: linear-gradient(135deg, #D4FF00, #b8e600); padding: 30px; text-align: center;">
            <h1 style="color: #000; margin: 0;">Sound It</h1>
            <p style="color: #333; margin: 10px 0 0 0;">Entertainment Platform</p>
        </div>
        <div style="background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px;">
            <h2 style="color: #333;">{subject}</h2>
            <div style="line-height: 1.6; color: #555;">
                {message.replace(chr(10), '<br>')}
            </div>
            <hr style="margin: 30px 0; border: none; border-top: 1px solid #ddd;">
            <p style="color: #666; font-size: 12px; text-align: center;">
                You're receiving this because you're a member of Sound It Entertainment.<br>
                <a href="http://localhost:3000" style="color: #D4FF00;">Visit Sound It</a>
            </p>
        </div>
    </div>
    """
    
    return send_email(
        to_email=to_email,
        subject=subject,
        html_content=html_content
    )


def send_password_reset_email(to_email: str, reset_token: str, user_name: str = "") -> bool:
    """
    Send password reset email with reset link
    """
    reset_url = f"http://localhost:3000/reset-password?token={reset_token}"
    
    html_content = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <div style="background: linear-gradient(135deg, #D4FF00, #b8e600); padding: 30px; text-align: center;">
            <h1 style="color: #000; margin: 0;">Sound It</h1>
        </div>
        <div style="background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px;">
            <h2 style="color: #333;">Password Reset Request</h2>
            <p>Hi {user_name or 'there'},</p>
            <p>We received a request to reset your password. Click the button below to create a new password:</p>
            <div style="text-align: center; margin: 30px 0;">
                <a href="{reset_url}" 
                   style="background: #D4FF00; color: #000; padding: 15px 30px; text-decoration: none; 
                          border-radius: 5px; font-weight: bold; display: inline-block;">
                    Reset Password
                </a>
            </div>
            <p style="color: #666;">Or copy and paste this link into your browser:</p>
            <p style="word-break: break-all; color: #0066cc;">{reset_url}</p>
            <hr style="margin: 30px 0; border: none; border-top: 1px solid #ddd;">
            <p style="color: #666; font-size: 12px;">
                This link will expire in 1 hour.<br>
                If you didn't request this, please ignore this email.<br>
                Need help? Contact us at <a href="mailto:support@example.com">support@example.com</a>
            </p>
        </div>
    </div>
    """
    
    return send_email(
        to_email=to_email,
        subject="Reset Your Sound It Password",
        html_content=html_content
    )


def send_password_changed_confirmation(to_email: str, user_name: str = "") -> bool:
    """
    Send confirmation email after password change
    """
    html_content = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <div style="background: linear-gradient(135deg, #D4FF00, #b8e600); padding: 30px; text-align: center;">
            <h1 style="color: #000; margin: 0;">Sound It</h1>
        </div>
        <div style="background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px;">
            <h2 style="color: #333;">Password Changed Successfully</h2>
            <p>Hi {user_name or 'there'},</p>
            <p>Your password has been changed successfully.</p>
            <p>If you didn't make this change, please contact us immediately at 
               <a href="mailto:support@example.com">support@example.com</a></p>
            <hr style="margin: 30px 0; border: none; border-top: 1px solid #ddd;">
            <p style="color: #666; font-size: 12px;">
                <a href="http://localhost:3000/login" style="color: #D4FF00;">Login to your account</a>
            </p>
        </div>
    </div>
    """
    
    return send_email(
        to_email=to_email,
        subject="Your Sound It Password Has Been Changed",
        html_content=html_content
    )


def send_ticket_confirmation(to_email: str, event_title: str, ticket_count: int, 
                             order_ref: str, total_amount: float, user_name: str = "") -> bool:
    """
    Send ticket purchase confirmation email
    """
    html_content = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <div style="background: linear-gradient(135deg, #D4FF00, #b8e600); padding: 30px; text-align: center;">
            <h1 style="color: #000; margin: 0;">🎉 Your Ticket is Confirmed!</h1>
        </div>
        <div style="background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px;">
            <p>Hi {user_name or 'there'},</p>
            <p>Thank you for your purchase! Your ticket for <strong>{event_title}</strong> has been confirmed.</p>
            
            <div style="background: #fff; padding: 20px; border-radius: 8px; margin: 20px 0; 
                        border-left: 4px solid #D4FF00;">
                <h3 style="margin-top: 0;">Ticket Details</h3>
                <p><strong>Event:</strong> {event_title}</p>
                <p><strong>Quantity:</strong> {ticket_count} ticket(s)</p>
                <p><strong>Total Paid:</strong> SLE {total_amount}</p>
                <p><strong>Order Reference:</strong> {order_ref}</p>
            </div>
            
            <p>Please show the QR code in your tickets page at the entrance.</p>
            
            <div style="text-align: center; margin: 30px 0;">
                <a href="http://localhost:3000/tickets" 
                   style="background: #D4FF00; color: #000; padding: 12px 30px; text-decoration: none; 
                          border-radius: 5px; font-weight: bold; display: inline-block;">
                    View My Tickets
                </a>
            </div>
            
            <hr style="margin: 30px 0; border: none; border-top: 1px solid #ddd;">
            <p style="color: #666; font-size: 12px; text-align: center;">
                Need help? Contact us at <a href="mailto:support@example.com">support@example.com</a><br>
                © 2024 Sound It Entertainment. All rights reserved.
            </p>
        </div>
    </div>
    """
    
    return send_email(
        to_email=to_email,
        subject=f"🎫 Your Ticket Confirmation - {event_title}",
        html_content=html_content
    )
