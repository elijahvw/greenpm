"""
Green PM - Notification Service
"""
import logging
from typing import Optional, Dict, Any, List
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content
from twilio.rest import Client as TwilioClient
from jinja2 import Environment, FileSystemLoader
import os

from src.core.config import settings
from src.models.user import User

logger = logging.getLogger(__name__)

class NotificationService:
    def __init__(self):
        # Initialize SendGrid
        self.sendgrid_client = None
        if settings.SENDGRID_API_KEY:
            try:
                self.sendgrid_client = SendGridAPIClient(api_key=settings.SENDGRID_API_KEY)
            except Exception as e:
                logger.error(f"Failed to initialize SendGrid: {e}")
        
        # Initialize Twilio
        self.twilio_client = None
        if settings.TWILIO_ACCOUNT_SID and settings.TWILIO_AUTH_TOKEN:
            try:
                self.twilio_client = TwilioClient(
                    settings.TWILIO_ACCOUNT_SID,
                    settings.TWILIO_AUTH_TOKEN
                )
            except Exception as e:
                logger.error(f"Failed to initialize Twilio: {e}")
        
        # Initialize Jinja2 for email templates
        template_dir = os.path.join(os.path.dirname(__file__), '..', 'templates', 'email')
        self.jinja_env = Environment(loader=FileSystemLoader(template_dir))

    async def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None,
        from_email: str = "noreply@greenpm.com"
    ) -> bool:
        """Send email using SendGrid"""
        if not self.sendgrid_client:
            logger.warning("SendGrid not configured, skipping email")
            return False

        try:
            message = Mail(
                from_email=Email(from_email),
                to_emails=To(to_email),
                subject=subject,
                html_content=Content("text/html", html_content)
            )
            
            if text_content:
                message.content = [
                    Content("text/plain", text_content),
                    Content("text/html", html_content)
                ]

            response = self.sendgrid_client.send(message)
            
            if response.status_code in [200, 201, 202]:
                logger.info(f"Email sent successfully to {to_email}")
                return True
            else:
                logger.error(f"Failed to send email: {response.status_code} - {response.body}")
                return False

        except Exception as e:
            logger.error(f"Error sending email: {e}")
            return False

    async def send_sms(self, to_phone: str, message: str) -> bool:
        """Send SMS using Twilio"""
        if not self.twilio_client or not settings.TWILIO_PHONE_NUMBER:
            logger.warning("Twilio not configured, skipping SMS")
            return False

        try:
            message = self.twilio_client.messages.create(
                body=message,
                from_=settings.TWILIO_PHONE_NUMBER,
                to=to_phone
            )
            
            logger.info(f"SMS sent successfully to {to_phone}: {message.sid}")
            return True

        except Exception as e:
            logger.error(f"Error sending SMS: {e}")
            return False

    def render_email_template(self, template_name: str, context: Dict[str, Any]) -> tuple[str, str]:
        """Render email template"""
        try:
            # Load HTML template
            html_template = self.jinja_env.get_template(f"{template_name}.html")
            html_content = html_template.render(**context)
            
            # Load text template (optional)
            text_content = None
            try:
                text_template = self.jinja_env.get_template(f"{template_name}.txt")
                text_content = text_template.render(**context)
            except:
                pass
            
            return html_content, text_content

        except Exception as e:
            logger.error(f"Error rendering email template {template_name}: {e}")
            return "", ""

    async def send_welcome_email(self, user: User) -> bool:
        """Send welcome email to new user"""
        context = {
            "user_name": user.full_name,
            "user_email": user.email,
            "app_name": settings.APP_NAME,
            "login_url": f"https://app.greenpm.com/login"  # Update with actual URL
        }
        
        html_content, text_content = self.render_email_template("welcome", context)
        
        return await self.send_email(
            to_email=user.email,
            subject=f"Welcome to {settings.APP_NAME}!",
            html_content=html_content,
            text_content=text_content
        )

    async def send_password_reset_email(self, user: User, reset_token: str) -> bool:
        """Send password reset email"""
        context = {
            "user_name": user.full_name,
            "reset_url": f"https://app.greenpm.com/reset-password?token={reset_token}",  # Update with actual URL
            "app_name": settings.APP_NAME
        }
        
        html_content, text_content = self.render_email_template("password_reset", context)
        
        return await self.send_email(
            to_email=user.email,
            subject="Password Reset Request",
            html_content=html_content,
            text_content=text_content
        )

    async def send_lease_signed_notification(self, landlord: User, tenant: User, property_title: str) -> bool:
        """Send lease signed notification to landlord"""
        context = {
            "landlord_name": landlord.full_name,
            "tenant_name": tenant.full_name,
            "property_title": property_title,
            "app_name": settings.APP_NAME,
            "dashboard_url": "https://app.greenpm.com/dashboard"
        }
        
        html_content, text_content = self.render_email_template("lease_signed", context)
        
        return await self.send_email(
            to_email=landlord.email,
            subject="Lease Agreement Signed",
            html_content=html_content,
            text_content=text_content
        )

    async def send_rent_payment_confirmation(self, tenant: User, amount: float, property_title: str) -> bool:
        """Send rent payment confirmation"""
        context = {
            "tenant_name": tenant.full_name,
            "amount": f"${amount:,.2f}",
            "property_title": property_title,
            "app_name": settings.APP_NAME
        }
        
        html_content, text_content = self.render_email_template("payment_confirmation", context)
        
        return await self.send_email(
            to_email=tenant.email,
            subject="Rent Payment Confirmation",
            html_content=html_content,
            text_content=text_content
        )

    async def send_maintenance_request_notification(
        self, 
        landlord: User, 
        tenant: User, 
        request_title: str,
        property_title: str
    ) -> bool:
        """Send maintenance request notification to landlord"""
        context = {
            "landlord_name": landlord.full_name,
            "tenant_name": tenant.full_name,
            "request_title": request_title,
            "property_title": property_title,
            "app_name": settings.APP_NAME,
            "dashboard_url": "https://app.greenpm.com/dashboard"
        }
        
        html_content, text_content = self.render_email_template("maintenance_request", context)
        
        return await self.send_email(
            to_email=landlord.email,
            subject="New Maintenance Request",
            html_content=html_content,
            text_content=text_content
        )

    async def send_application_received_notification(
        self, 
        landlord: User, 
        applicant_name: str, 
        property_title: str
    ) -> bool:
        """Send application received notification to landlord"""
        context = {
            "landlord_name": landlord.full_name,
            "applicant_name": applicant_name,
            "property_title": property_title,
            "app_name": settings.APP_NAME,
            "dashboard_url": "https://app.greenpm.com/dashboard"
        }
        
        html_content, text_content = self.render_email_template("application_received", context)
        
        return await self.send_email(
            to_email=landlord.email,
            subject="New Rental Application",
            html_content=html_content,
            text_content=text_content
        )

    async def send_bulk_notification(
        self,
        users: List[User],
        subject: str,
        template_name: str,
        context: Dict[str, Any],
        notification_type: str = "email"
    ) -> Dict[str, bool]:
        """Send bulk notifications"""
        results = {}
        
        for user in users:
            # Skip if user has disabled this notification type
            if notification_type == "email" and not user.notification_email:
                continue
            if notification_type == "sms" and not user.notification_sms:
                continue
            
            # Personalize context for each user
            user_context = {**context, "user_name": user.full_name}
            
            if notification_type == "email":
                html_content, text_content = self.render_email_template(template_name, user_context)
                success = await self.send_email(
                    to_email=user.email,
                    subject=subject,
                    html_content=html_content,
                    text_content=text_content
                )
            elif notification_type == "sms" and user.phone:
                # For SMS, we'd need a text template
                message = self.render_sms_template(template_name, user_context)
                success = await self.send_sms(user.phone, message)
            else:
                success = False
            
            results[user.email] = success
        
        return results

    def render_sms_template(self, template_name: str, context: Dict[str, Any]) -> str:
        """Render SMS template (simple text templates)"""
        # This would be expanded with actual SMS templates
        templates = {
            "rent_reminder": "Hi {user_name}, your rent payment of ${amount} is due on {due_date}. Pay online at {payment_url}",
            "maintenance_update": "Hi {user_name}, your maintenance request '{request_title}' has been updated to: {status}",
        }
        
        template = templates.get(template_name, "")
        return template.format(**context)