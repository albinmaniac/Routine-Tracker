from celery import shared_task
from django.utils.timezone import now

@shared_task
def send_habit_reminders(habit_id=None):
    """✅ Sends reminders for due habits and creates notifications."""
    print("🔔 Running send_habit_reminders task...")  

    from tracker.utils import send_habit_email
    from tracker.models import Habit, Notification  # ✅ Import Notification model

    if habit_id:
        habits = Habit.objects.filter(id=habit_id)
    else:
        habits = Habit.objects.filter(reminder_time__lte=now(), reminder_sent=False)

    if not habits.exists():
        print("⚠️ No habits found for reminders.")
        return "No habits to remind"
    
    for habit in habits:
        print(f"📩 Sending reminder for: {habit.name}")
        send_habit_email(habit.user, habit, email_type="reminder")

        # ✅ Mark as Sent
        habit.reminder_sent = True
        habit.save()

        # ✅ Create a Notification for the user
        Notification.objects.create(
            user=habit.user,
            message=f"Reminder: It's time for your habit - {habit.name}"
        )
    
    print("✅ Habit reminders sent successfully.")
    return f"{habits.count()} reminders sent"


@shared_task
def send_pending_habit_alerts():
    """✅ Sends emails for habits that are overdue (not completed on time)."""
    print("⚠️ Running send_pending_habit_alerts task...")  # Debugging

    from tracker.models import Habit
    from tracker.utils import send_habit_email
    pending_habits = Habit.objects.filter(
        status__in=["active", "paused"],  # ✅ Habit is still pending
        reminder_time__lt=now()  # ✅ The habit is overdue
    )

    if not pending_habits.exists():
        print("⚠️ No pending habits found.")
        return "No pending habits."

    for habit in pending_habits:
        print(f"⚠️ Sending pending habit email for: {habit.name}")
        send_habit_email(habit.user, habit, email_type="pending_habit")

    print("✅ Pending habit emails sent successfully.")
    return f"{pending_habits.count()} pending habit emails sent."