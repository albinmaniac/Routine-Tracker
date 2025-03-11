from django import forms
from tracker.models import CustomUser  
from django.contrib.auth.forms import UserCreationForm
from tracker.models import Habit,HabitTracker,HabitReminder,HabitStats


# User Registration Form
class RegistrationForm(UserCreationForm):
    first_name = forms.CharField(
        max_length=30, 
        required=True, 
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    last_name = forms.CharField(
        max_length=30, 
        required=True, 
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    age = forms.IntegerField(
        required=True, 
        min_value=1, 
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    gender = forms.ChoiceField(
        choices=CustomUser.GENDER_CHOICES, 
        required=True,
        widget=forms.Select(attrs={'class': 'form-control '})  # ✅ Fixed widget error
    )

    class Meta:
        model = CustomUser  
        fields = ["username", "email", "first_name", "last_name", "gender", "age", "password1", "password2"]
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

# User Login Form
class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput()) 






from django import forms
from tracker.models import Habit

class HabitForm(forms.ModelForm):
    class Meta:
        model = Habit
        fields = [
            'name', 'description', 'goal', 'frequency', 'target_value', 
            'completed_value', 'start_date', 'end_date', 'status', 'reminder_time'
        ]
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'reminder_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),  # ✅ New Field
            'frequency': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }


class HabitTrackerForm(forms.ModelForm):
    class Meta:
        model = HabitTracker
        fields = ['date', 'completed', 'progress']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }

