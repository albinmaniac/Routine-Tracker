from celery import shared_task
from django.utils.timezone import now, localdate

@shared_task
def send_habit_reminders(habit_id=None):
    """✅ Sends reminders for due habits and creates notifications."""
    print("🔔 Running send_habit_reminders task...")  

    from tracker.utils import send_habit_email
    from tracker.models import Habit, Notification  

    today = localdate()  # ✅ Get today's date

    if habit_id:
        habits = Habit.objects.filter(id=habit_id)
    else:
        habits = Habit.objects.filter(
            reminder_time__lte=now(),
            reminder_sent=False
        ).exclude(last_completed_date=today)  # ✅ Skip habits already completed today

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
    print("⚠️ Running send_pending_habit_alerts task...")  

    from tracker.models import Habit
    from tracker.utils import send_habit_email
    today = localdate()

    pending_habits = Habit.objects.filter(
        status__in=["active", "paused"],  
        reminder_time__lt=now()  
    ).exclude(last_completed_date=today)  # ✅ Exclude habits completed today

    if not pending_habits.exists():
        print("⚠️ No pending habits found.")
        return "No pending habits."

    for habit in pending_habits:
        print(f"⚠️ Sending pending habit email for: {habit.name}")
        send_habit_email(habit.user, habit, email_type="pending_habit")

    print("✅ Pending habit emails sent successfully.")
    return f"{pending_habits.count()} pending habit emails sent."


@shared_task
def reset_habit_reminders():
    """✅ Resets reminder_sent to False every day at midnight."""
    print("🔄 Resetting habit reminders...")  

    from tracker.models import Habit
    Habit.objects.all().update(reminder_sent=False)  # ✅ Reset for all habits

    print("✅ Habit reminders reset.")
    return "Habit reminders reset."