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

# ✅ Add periodic task directly (Runs every 15 minutes)
@app.on_after_finalize.connect
def setup_periodic_tasks(sender, **kwargs):
    from tracker.tasks import send_habit_reminder

    sender.add_periodic_task(
        crontab(minute="*/15"),  # Runs every 15 minutes
        send_habit_reminder.s(),
        name="Send Habit Reminders every 15 minutes"
    )