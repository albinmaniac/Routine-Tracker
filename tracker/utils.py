from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

def send_habit_email(user, habit, email_type="reminder"):
    """✅ Sends habit-related emails (creation, reminders, pending, completion)"""

    email_templates = {
        "habit_created": {
            "subject": f"🎯 New Habit Created: {habit.name}",
            "template": "habit_created_email.html",
        },
        "reminder": {
            "subject": f"⏳ Habit Reminder: {habit.name}",
            "template": "habit_reminder_email.html",
        },
        "pending_habit": {
            "subject": f"⚠️ Pending Habit: {habit.name}",
            "template": "pending_habit_email.html",
        },
        "habit_completed": {
            "subject": f"🏆 Habit Completed: {habit.name}",
            "template": "habit_completed_email.html",
        },
    }

    # ✅ Validate email type
    if email_type not in email_templates:
        logger.warning(f"Invalid email type: {email_type}")
        return

    subject = email_templates[email_type]["subject"]
    template_name = email_templates[email_type]["template"]

    context = {
        "user_name": user.get_full_name() or user.username,
        "habit_name": habit.name,
        "habit_url": f"https://yourwebsite.com/habits/{habit.id}/track",
    }

    html_message = render_to_string(template_name, context)
    plain_message = strip_tags(html_message)

    try:
        send_mail(
            subject,
            plain_message,
            settings.DEFAULT_FROM_EMAIL,  # ✅ Use Django settings
            [user.email],
            html_message=html_message,
        )
        logger.info(f"📧 Email sent: {email_type} to {user.email}")
    except Exception as e:
        logger.error(f"❌ Email sending failed: {str(e)}")