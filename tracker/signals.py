from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.timezone import now
from .models import Habit
from tracker.utils import send_habit_email  

@receiver(post_save, sender=Habit)
def habit_notifications(sender, instance, created, **kwargs):
    """✅ Send email notifications when a habit is created or completed (only once per day)."""

    if created:
        send_habit_email(instance.user, instance, "habit_created")  # 📧 Habit created email

    elif instance.status == "completed":
        today = now().date()

        # ✅ Check if the habit was completed today (avoid multiple emails)
        if instance.completed_on != today:
            send_habit_email(instance.user, instance, "habit_completed")  # 🏆 Habit completed email
            instance.completed_on = today  # ✅ Mark as completed today
            instance.save(update_fields=["completed_on"])  # ✅ Avoid full save