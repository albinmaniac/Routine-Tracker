from django.contrib.auth.models import AbstractUser
from django.db import models
from datetime import timedelta
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.db import models
from django.utils.timezone import now, localtime, timedelta
from tracker.utils import send_habit_email
from tracker.utils import send_habit_email
from tracker.tasks import send_habit_reminders  # ✅ Correct Celery task import

# Custom User Model
class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('user', 'User'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')
    age = models.PositiveIntegerField(null=True, blank=True)
    GENDER_CHOICES=(

        ("male","male"),
        ("female","female")

    )

    gender=models.CharField(max_length=10,choices=GENDER_CHOICES,default='male')


    def is_admin(self):
        return self.role == 'admin'

    def is_user(self):
        return self.role == 'user'
    
    def __str__(self):
        return f"{self.username} ({self.role.capitalize()})"



class Habit(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='habits')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    goal = models.CharField(max_length=100, null=True)
    
    frequency = models.CharField(max_length=50, choices=[
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly')
    ])
    
    target_value = models.FloatField(default=0.0, blank=True, null=True)
    completed_value = models.FloatField(default=0.0)
    
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    reminder_time = models.DateTimeField(null=True, blank=True)
    reminder_sent = models.BooleanField(default=False)

    STATUS_CHOICES = [
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('paused', 'Paused'),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')

    def progress_percentage(self):
        """✅ Calculate habit completion percentage"""
        if self.target_value and self.target_value > 0:
            return int((self.completed_value / self.target_value) * 100)
        return 0

    def update_status(self):
        """✅ Auto-update status & send completion email"""
        old_status = self.status  # Store previous status

        if self.progress_percentage() >= 100:
            self.status = 'completed'
        elif self.completed_value > 0:
            self.status = 'active'
        else:
            self.status = 'paused'

        # ✅ Only send "Habit Completed" email when it transitions from non-completed to completed
        if old_status != 'completed' and self.status == 'completed':
            send_habit_email(self.user, self, email_type="habit_completed")  

    def schedule_reminder(self):
        """✅ Schedule reminders if habit is pending"""
        now_time = localtime()

        # ✅ If a reminder time is set, schedule it
        if self.reminder_time and self.reminder_time > now_time:
            send_habit_reminders.apply_async((self.id,), eta=self.reminder_time)

        # ✅ If habit is still incomplete before midnight, send a reminder at 23:59
        end_of_day = now_time.replace(hour=23, minute=59, second=0)
        if self.status != 'completed' and now_time < end_of_day:
            send_habit_reminders.apply_async((self.id,), eta=end_of_day)

    def save(self, *args, **kwargs):
        """✅ Override save to update status & trigger emails"""
        new_habit = self.pk is None  # Check if it's a new habit
        old_instance = None

        if not new_habit:
            old_instance = Habit.objects.filter(pk=self.pk).first()

        self.update_status()  # Update status before saving
        super().save(*args, **kwargs)  # Call original save method

        # ✅ Send email when a new habit is created
        if new_habit:
            send_habit_email(self.user, self, email_type="habit_created")  

        # ✅ Schedule reminders if reminder_time is set or changed
        if new_habit or (old_instance and old_instance.reminder_time != self.reminder_time):
            self.schedule_reminder()

        # ✅ Send "Pending Habit" email at the end of the day if habit is still not completed
        if old_instance and old_instance.status == "active" and self.status != "completed":
            end_of_day = localtime().replace(hour=23, minute=59, second=0)
            from tracker.tasks import send_habit_email_task  
            send_habit_email_task.apply_async((self.user.id, self.id, "pending_habit"), eta=end_of_day)

    def __str__(self):
        return f"{self.name} ({self.progress_percentage()}%)"



class HabitTracker(models.Model):
    habit = models.ForeignKey(Habit, on_delete=models.CASCADE, related_name='trackers')
    date = models.DateField()
    completed = models.BooleanField(default=False)
    progress = models.FloatField(default=0.0, blank=True, null=True)  
    value_done = models.FloatField(default=0.0, blank=True, null=True)  

    class Meta:
        unique_together = ('habit', 'date')

    def save(self, *args, **kwargs):
    # ✅ Auto-calculate progress
        if self.completed:
            self.progress = 100.0
        elif self.habit.target_value and self.value_done is not None and self.habit.target_value > 0:
            self.progress = (self.value_done / self.habit.target_value) * 100
        else:
            self.progress = 0.0

        super().save(*args, **kwargs)  # ✅ Save HabitTracker first

        # ✅ Update HabitStats **only if progress changes**
        habit_stats, created = HabitStats.objects.get_or_create(habit=self.habit)
        habit_stats.update_stats()

    def __str__(self):
        return f"{self.habit.name} - {self.date} - {self.progress:.2f}%"

#==================

class HabitStats(models.Model):
    habit = models.OneToOneField(Habit, on_delete=models.CASCADE, related_name='stats')
    streak = models.PositiveIntegerField(default=0)
    best_streak = models.PositiveIntegerField(default=0)
    completion_rate = models.FloatField(default=0.0)
    total_completions = models.PositiveIntegerField(default=0)
    weekly_completions = models.PositiveIntegerField(default=0)  # ✅ Correctly track weekly completions

    def update_stats(self):
        tracked_entries = self.habit.trackers.order_by('-date')
        today = timezone.now().date()
        expected_date = today
        streak = 0
        best_streak = self.best_streak

        # ✅ 1️⃣ Calculate Current Streak (Consecutive Completed Days)
        for entry in tracked_entries.filter(completed=True):
            if entry.date == expected_date:
                streak += 1
                expected_date -= timedelta(days=1)
            else:
                break  

        best_streak = max(best_streak, streak)

        # ✅ 2️⃣ Calculate Completion Rate
        total_entries = tracked_entries.count()
        completed_entries = tracked_entries.filter(completed=True).count()
        completion_rate = (completed_entries / total_entries) * 100 if total_entries > 0 else 0.0

        # ✅ 3️⃣ Calculate Weekly Completions (Last 7 Days)
        one_week_ago = today - timedelta(days=7)
        weekly_completions = tracked_entries.filter(date__gte=one_week_ago, completed=True).count()

        # ✅ 4️⃣ Update Habit Stats
        self.streak = streak
        self.best_streak = best_streak
        self.completion_rate = completion_rate
        self.total_completions = completed_entries
        self.weekly_completions = weekly_completions  # 🔥 Store Weekly Completions
        self.save()

        # ✅ 5️⃣ Assign Badges (if applicable)
        self.assign_badges()

    def assign_badges(self):
        """Placeholder method for badge assignment"""
        pass

    def __str__(self):
        return (
            f"{self.habit.name} - {self.completion_rate:.2f}% Completion - "
            f"Streak: {self.streak} days (Best: {self.best_streak}) - "
            f"Weekly Completions: {self.weekly_completions}"
        )

# Habit Reminders (For Multiple Reminders)
class HabitReminder(models.Model):
    habit = models.ForeignKey(Habit, on_delete=models.CASCADE, related_name='reminders')
    reminder_time = models.TimeField()  # Store exact time of reminder
    is_active = models.BooleanField(default=True)  # Enable/Disable reminders

    def __str__(self):
        return f"Reminder for {self.habit.name} at {self.reminder_time}"


#===============





class Notification(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="notifications")
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)

    def __str__(self):
        return f"Notification for {self.user.username} at {self.timestamp}"
    
    
