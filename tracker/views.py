from django.shortcuts import render, redirect,get_object_or_404
from django.views.generic import View
from django.contrib.auth import authenticate, login, logout
from tracker.forms import RegistrationForm, LoginForm,HabitForm,HabitTrackerForm
from tracker.models import CustomUser  
from tracker.models import Habit, HabitTracker, HabitStats
from django.contrib import messages 
import calendar
from datetime import date
from django.utils import timezone  
from django.utils.timezone import now
from django.views.generic import TemplateView
from datetime import timedelta,datetime
from django.db.models import Count,Q


# User Registration View
class SignupView(View):
    template_name = 'register.html'
    form_class = RegistrationForm

    def get(self, request, *args, **kwargs):
        form_instance = self.form_class()
        return render(request, self.template_name, {'form': form_instance})

    def post(self, request, *args, **kwargs):
        form_instance = self.form_class(request.POST)
        if form_instance.is_valid():
            form_instance.save()
            print("Registration complete")
            return redirect("login") 
        return render(request, self.template_name, {'form': form_instance})



class SignInView(View):
    template_name = "login.html"
    form_class = LoginForm

    def get(self, request, *args, **kwargs):
        form_instance = self.form_class()
        return render(request, self.template_name, {'form': form_instance})

    def post(self, request, *args, **kwargs):
        form_instance = self.form_class(request.POST)
        if form_instance.is_valid():
            uname = form_instance.cleaned_data.get("username")
            pwd = form_instance.cleaned_data.get("password")

            user_object = authenticate(request, username=uname, password=pwd)

            if user_object:
                login(request, user_object)
                print(request.user)
                return redirect("dashboard") 
        return render(request, self.template_name, {'form': form_instance})



class SignoutView(View):
    def get(self, request, *args, **kwargs):
        logout(request)
        return redirect("login")  



class DashboardView(View):
    template_name = "index.html"

    def get(self, request, *args, **kwargs):
        user = request.user

        # Admin sees all habits, users see only their own
        if user.is_superuser or (hasattr(user, "role") and user.role == "admin"):
            habits = Habit.objects.all()
        else:
            habits = Habit.objects.filter(user=user)

        stats = HabitStats.objects.filter(habit__in=habits)

        # ✅ **Recalculate Weekly Completions Dynamically**
        week_start = now().date() - timedelta(days=now().date().weekday())  # Monday of this week
        week_end = week_start + timedelta(days=6)  # Sunday of this week

        weekly_completions = HabitTracker.objects.filter(
        habit__in=habits,
        date__range=[week_start, week_end],
        completed=True
        ).count()

        print("🚀 Weekly Completions Count:", weekly_completions)  # Debugging print


                # Compute statistics
        total_habits = habits.count()
        longest_streak = max((stat.best_streak for stat in stats), default=0)


        # ✅ Ensure progress_percentage does not exceed 100%
        max_offset = 251.2  # Maximum stroke length

        for habit in habits:
            if callable(habit.progress_percentage):  
                progress_percentage = habit.progress_percentage()
            else:
                progress_percentage = habit.progress_percentage

            progress_percentage = min(float(progress_percentage), 100)  # Cap at 100
            habit.stroke_dashoffset = max(0, max_offset - (progress_percentage / 100 * max_offset))  # Scale properly

            print(f"Habit: {habit.name}, Progress: {progress_percentage}, Stroke Offset: {habit.stroke_dashoffset}")  # Debug


        # 📅 **Calendar Data Generation**
        today = now().date()
        first_day, num_days = calendar.monthrange(today.year, today.month)
        
        # 🔥 **Fix the first weekday so Sunday = 0**
        first_weekday = (calendar.weekday(today.year, today.month, 1) + 1) % 7

        blank_days = range(first_weekday)  # Empty slots before the first day
        calendar_days = []

        for day in range(1, num_days + 1):
            date = today.replace(day=day)
            routines = habits.filter(created_at__date=date)  # Adjust based on your model
            calendar_days.append({
                "date": date,
                "has_routines": routines.exists(),
                "routine_count": routines.count(),
            })

        return render(request, self.template_name, {
            "habits": habits,  # ✅ Now contains stroke_dashoffset
            "total_habits": total_habits,
            "longest_streak": longest_streak,
            "total_weekly_completions": weekly_completions,  # ✅ Now dynamically calculated
            "today": today,  # ✅ Add today’s date
            "blank_days": blank_days,  # ✅ Empty days for calendar alignment
            "calendar_days": calendar_days,  # ✅ Calendar data
        })



# ####=======Habit Crud Session============



class CreateHabitView(View):

    template_name = 'create_habit.html' 

    def get(self, request, *args, **kwargs):

        form = HabitForm()

        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):

        form = HabitForm(request.POST)
        if form.is_valid():

            habit = form.save(commit=False)

            habit.user = request.user 

            habit.save()

            return redirect('dashboard') 
        return render(request, self.template_name, {'form': form})
    



class HabitListView(View):
    template_name = "habits.html"

    def get(self, request, *args, **kwargs):
        habits = Habit.objects.filter(user=request.user)

        # ✅ Call `update_status()` only when necessary
        for habit in habits:
            habit.update_status()  

        return render(request, self.template_name, {"habits": habits})
    

from django.utils import timezone

class HabitDetailView(View):
    template_name = "habit_detail.html"

    def get(self, request, pk, *args, **kwargs):
        habit = get_object_or_404(Habit, pk=pk, user=request.user)
        habit_stats, created = HabitStats.objects.get_or_create(habit=habit)

        today = timezone.now().date()
        today_tracker, created = HabitTracker.objects.get_or_create(habit=habit, date=today)
        
        if created:
            today_tracker.completed = False
            today_tracker.value_done = 0.0
            today_tracker.save()
            
            habit.completed_value = 0.0
            habit.save()

        progress = today_tracker.progress  # Get today's progress

        # ✅ Ensure progress is capped at 100%
        progress_percentage = min(float(progress), 100)

        # ✅ Correct stroke-dashoffset calculation
        max_offset = 251.2  # Full circumference
        habit.stroke_dashoffset = max(0, max_offset - (progress_percentage / 100 * max_offset))

        return render(request, self.template_name, {
            "habit": habit,
            "habit_stats": habit_stats
        })
    
    # def post(self, request, pk, *args, **kwargs):
    #     habit = get_object_or_404(Habit, pk=pk, user=request.user)
    #     completed = request.POST.get("completed") == "true"  # Convert to boolean

    #     # ✅ Get today's tracker or create a new one
    #     tracker, created = HabitTracker.objects.get_or_create(habit=habit, date=timezone.now().date())

    #     # ✅ Update completion status & progress
    #     tracker.completed = completed
    #     tracker.value_done = habit.target_value if completed else 0.0  # 100% if checked, 0% if unchecked
    #     tracker.save()  # ✅ Auto-calls `save()` with progress update

    #     # ✅ Update habit progress
    #     habit.completed_value = habit.target_value if completed else 0.0  # 100% or reset to 0

    #     # ✅ Update `end_date` only if completed
    #     if completed:
    #         habit.end_date = timezone.now().date()  # Set today's date
    #     elif habit.trackers.filter(completed=True).exists():
    #         # If there are previous completions, keep the last completed date
    #         habit.end_date = habit.trackers.filter(completed=True).latest('date').date
    #     else:
    #         habit.end_date = None  # Reset if no completion history

    #     habit.save()

    #     return redirect("habit-detail", pk=habit.pk)
    def post(self, request, pk, *args, **kwargs):
        habit = get_object_or_404(Habit, pk=pk, user=request.user)

        # ✅ Get today's tracker
        tracker, created = HabitTracker.objects.get_or_create(habit=habit, date=timezone.now().date())

        # ✅ Prevent multiple changes
        if tracker.completed:  
            return redirect("habit-detail", pk=habit.pk)  # Ignore if already completed

        # ✅ Mark as completed
        tracker.completed = True
        tracker.value_done = habit.target_value  
        tracker.save()

        # ✅ Update habit progress
        habit.completed_value = habit.target_value  
        habit.end_date = timezone.now().date()  
        habit.save()

        return redirect("habit-detail", pk=habit.pk)

class HabitUpdateView(View):
    template_name = "habit_update.html"
    form_class = HabitForm

    def get(self, request, pk, *args, **kwargs):

        habit = get_object_or_404(Habit, pk=pk, user=request.user) 

        form = self.form_class(instance=habit)

        return render(request, self.template_name, {"form": form, "habit": habit})

    def post(self, request, pk, *args, **kwargs):

        habit = get_object_or_404(Habit, pk=pk, user=request.user)

        form = self.form_class(request.POST, instance=habit)
        
        if form.is_valid():

            form.save()
            
            return redirect("habit-detail", pk=habit.pk) 
        
        return render(request, self.template_name, {"form": form, "habit": habit})
    

class HabitDeleteView(View):

    template_name = "habit_delete.html"

    def get(self, request, pk, *args, **kwargs):

        habit = get_object_or_404(Habit, pk=pk, user=request.user)

        return render(request, self.template_name, {"habit": habit})

    def post(self, request, pk, *args, **kwargs):

        habit = get_object_or_404(Habit, pk=pk, user=request.user)

        habit.delete()

        return redirect("habits")  
    


#======== Habit tracking CRUD ========


class HabitTrackingView(View):
    template_name = "track_habit.html"

    def get(self, request, habit_id, *args, **kwargs):
        habit = get_object_or_404(Habit, id=habit_id, user=request.user)
        form = HabitTrackerForm()

        tracked_entries = HabitTracker.objects.filter(habit=habit).order_by("-date")[:10]

        return render(request, self.template_name, {
            "habit": habit,
            "form": form,
            "tracked_entries": tracked_entries
        })

    def post(self, request, habit_id, *args, **kwargs):
        habit = get_object_or_404(Habit, id=habit_id, user=request.user)
        form = HabitTrackerForm(request.POST)

        if form.is_valid():
            tracker_entry = form.save(commit=False)
            tracker_entry.habit = habit  


            if HabitTracker.objects.filter(habit=habit, date=tracker_entry.date).exists():
                messages.error(request, "You have already tracked this habit for today.")
                return redirect("track-habit", habit_id=habit.id)  # Prevents duplicate entry
            
            tracker_entry.save()
            messages.success(request, "Habit tracked successfully!")  # Success message
            return redirect("track-habit", habit_id=habit.id)  
        
        tracked_entries = HabitTracker.objects.filter(habit=habit).order_by("-date")

        return render(request, self.template_name, {
            "habit": habit, 
            "form": form, 
            "tracked_entries": tracked_entries
        })
    

class HabitStatisticsView(View):
    template_name = "index.html"

    def get(self, request, *args, **kwargs):
        habits = HabitTracker.objects.all()  # Fetch all habits

        # Compute statistics
        total_habits = habits.count()  # Total number of habits
        longest_streak = max((habit.habit_stats.best_streak for habit in habits), default=0)  # Max streak
        total_weekly_completions = sum(habit.habit_stats.weekly_completions for habit in habits)  # Total weekly completions


        context = {
            "total_habits": total_habits,
            "longest_streak": longest_streak,
            "total_weekly_completions": total_weekly_completions,
        }

        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):

        habit_id = request.POST.get("habit_id")
        if habit_id:
            habit = Habit.objects.get(id=habit_id)

            habit.habit_stats.total_completions += 1
            habit.habit_stats.save()

        return redirect("habit-statistics")  # Redirect back to the page

class HabitStatsView(View):
    template_name = "habit_stats.html"

    def get(self, request, habit_id, *args, **kwargs):
        habit = get_object_or_404(Habit, id=habit_id, user=request.user)
        habit_stats, created = HabitStats.objects.get_or_create(habit=habit)

        return render(request, self.template_name, {
            "habit": habit,
            "habit_stats": habit_stats,
        })
    



    


import calendar
from datetime import datetime
from django.utils.timezone import now
from django.views.generic import TemplateView
from .models import Habit

class CalendarView(TemplateView):
    template_name = "calendar.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = now().date()
        year, month = today.year, today.month

        # Get the first weekday of the month (0 = Monday, 6 = Sunday)
        first_weekday, num_days = calendar.monthrange(year, month)

        print(f"DEBUG: {year}-{month} starts on weekday index {first_weekday} (0=Monday)")

        # Adjust blank days based on the correct calendar format
        blank_days = range((first_weekday + 1) % 7)

        # Store habits by date
        habits_by_date = {}
        habits = Habit.objects.filter(start_date__year=year, start_date__month=month)
        for habit in habits:
            date_key = habit.start_date
            if date_key not in habits_by_date:
                habits_by_date[date_key] = {"routine_count": 0}
            habits_by_date[date_key]["routine_count"] += 1

        # Create list of days in the month
        calendar_days = []
        for day in range(1, num_days + 1):
            date = datetime(year, month, day).date()
            calendar_days.append({
                "date": date,
                "has_routines": date in habits_by_date,
                "routine_count": habits_by_date.get(date, {}).get("routine_count", 0),
            })

        # Pass data to template
        context["today"] = today
        context["calendar_days"] = calendar_days
        context["blank_days"] = blank_days  # Corrected blank days calculation

        return context
    

from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from tracker.models import Notification
from django.middleware.csrf import get_token

@login_required
def get_notifications(request):
    """✅ Fetch unread notifications for the logged-in user"""
    notifications = Notification.objects.filter(user=request.user, read=False).order_by('-timestamp')
    data = [
        {
            "id": notification.id,
            "message": notification.message,
            "timestamp": notification.timestamp.strftime('%Y-%m-%d %H:%M'),
            "read": notification.read
        }
        for notification in notifications
    ]
    return JsonResponse({"notifications": data})

@login_required
@require_POST  # Ensures only POST requests are allowed
def mark_notification_as_read(request, notification_id):
    """✅ Marks a notification as read"""
    try:
        notification = Notification.objects.get(id=notification_id, user=request.user)
        notification.read = True
        notification.save()
        return JsonResponse({"success": True})
    except Notification.DoesNotExist:
        return JsonResponse({"error": "Notification not found"}, status=404)
    
@login_required
def get_csrf_token(request):
    """✅ Returns a CSRF token for AJAX requests"""
    return JsonResponse({"csrfToken": get_token(request)})

