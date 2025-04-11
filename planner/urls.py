from django.urls import path
from django.contrib.auth import views as auth_views
from .views import home, register, study_preferences, study_plan

urlpatterns = [
    path('', home, name='home'),
    path('register/', register, name='register'),
    path('preferences/', study_preferences, name='study_preferences'),
    path('plan/', study_plan, name='study_plan'),
]