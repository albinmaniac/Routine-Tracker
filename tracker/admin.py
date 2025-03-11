from django.contrib import admin
from .models import CustomUser, Habit, HabitTracker, HabitStats
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from .models import CustomUser, Habit, HabitTracker, HabitStats


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'first_name', 'last_name', 'age', 'gender')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'user'  # Automatically set role as 'user' for new registrations
        if commit:
            user.save()
        return user

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'first_name', 'last_name', 'age', 'gender', 'role')

@admin.register(CustomUser)
class CustomUserAdmin(BaseUserAdmin):
    add_form = CustomUserCreationForm  
    form = CustomUserChangeForm        

    list_display = ('username', 'email', 'first_name', 'last_name', 'age', 'gender', 'role', 'is_staff', 'is_active')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    list_filter = ('role', 'gender', 'is_staff', 'is_active')

    # Modify fieldsets properly to avoid duplication
    fieldsets = list(BaseUserAdmin.fieldsets)  # Convert tuple to list for modification
    fieldsets[1] = (fieldsets[1][0], {'fields': ('first_name', 'last_name', 'email', 'gender')})  # Modify the 'Personal info' section
    fieldsets.append(
        ('Additional Info', {'fields': ('age', 'role')})  # Add new fields without duplication
    )

    # Modify add_fieldsets properly
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'first_name', 'last_name', 'age', 'gender', 'password1', 'password2'),
        }),
    )

    
@admin.register(Habit)
class HabitAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'frequency', 'start_date', 'end_date')
    search_fields = ('name', 'user__username')
    list_filter = ('frequency', 'start_date', 'end_date')

@admin.register(HabitTracker)
class HabitTrackerAdmin(admin.ModelAdmin):
    list_display = ('habit', 'date', 'completed', 'progress')
    list_filter = ('completed', 'date')

@admin.register(HabitStats)
class HabitStatsAdmin(admin.ModelAdmin):
    list_display = ('habit', 'streak', 'completion_rate')







