"""
URL configuration for routine project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from tracker import views

urlpatterns = [
    path('admin/', admin.site.urls),

     path('signup/',views.SignupView.as_view(),name="register"),

    path('',views.SignInView.as_view(),name="login"),

    path('signout/',views.SignoutView.as_view(),name="signout"),

    path('dashboard/', views.DashboardView.as_view(),name="dashboard"),

    path('createhabit/',views.CreateHabitView.as_view(),name="createhabit"),

    path('habits/',views.HabitListView.as_view(),name="habits"),

    path('habits/<int:pk>/', views.HabitDetailView.as_view(), name='habit-detail'),

    path('habits/<int:pk>/edit/', views.HabitUpdateView.as_view(), name='habit-update'),

    path('habits/<int:pk>/delete/', views.HabitDeleteView.as_view(), name='habit-delete'),

    path("track-habit/<int:habit_id>/", views.HabitTrackingView.as_view(), name="track-habit"),

    path('sts/', views.HabitStatisticsView.as_view(), name="habit-statistics"),
    
    path("habit/<int:habit_id>/stats/",views.HabitStatsView.as_view(), name="habit-stats"),

    path("badges/", views.BadgeView.as_view(), name="badge-list"),

    path("calendar/", views.CalendarView.as_view(), name="calendar"),


    path("calendar/<int:year>/<int:month>/", views.CalendarView.as_view(), name="calendar_with_date"),


]
