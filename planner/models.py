from django.db import models
from django.contrib.auth.models import User
from datetime import time

class StudyPreferences(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    study_date = models.DateField(null=True, blank=True)
    subjects = models.JSONField(default=list)
    priorities = models.JSONField(default=list)
    session_length = models.PositiveIntegerField(default=45)
    start_time = models.TimeField(default=time(9, 0))
    total_study_time = models.FloatField(default=8)
    num_breaks = models.PositiveIntegerField(default=4)
    break_duration = models.PositiveIntegerField(default=15)
    leisure_time = models.FloatField(default=2)

    def __str__(self):
        return f"Preferences for {self.user.username}"