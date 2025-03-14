import os
from celery import Celery
from celery.schedules import crontab

# Set the default Django settings module for Celery
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "routine.settings")

app = Celery("routine")

# Load task modules from all registered Django app configs
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

# Optional: Debug Task
@app.task(bind=True)
def debug_task(self):
    print(f"Request: {self.request!r}")

# ✅ Add periodic tasks (Scheduled Execution)
@app.on_after_finalize.connect
def setup_periodic_tasks(sender, **kwargs):
    from tracker.tasks import (
        send_habit_reminders,
        send_pending_habit_alerts,
        reset_habit_reminders
    )

    # ✅ Send habit reminders every day at 8 AM
    sender.add_periodic_task(
        crontab(hour=8, minute=0),
        send_habit_reminders.s(),
        name="Send Habit Reminders at 8 AM"
    )

    # ✅ Send pending habit alerts every day at 8 PM
    sender.add_periodic_task(
        crontab(hour=20, minute=0),
        send_pending_habit_alerts.s(),
        name="Send Pending Habit Emails at 8 PM"
    )

    # ✅ Reset reminders every day at midnight
    sender.add_periodic_task(
        crontab(hour=0, minute=0),
        reset_habit_reminders.s(),
        name="Reset Habit Reminders at Midnight"
    )