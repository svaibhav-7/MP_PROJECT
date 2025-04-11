from django.contrib import admin
import planner.models as models


class StudyPreferencesAdmin(admin.ModelAdmin):
    list_display = ("user", "total_study_time", "num_breaks", "break_duration", "leisure_time")
    search_fields = ("user__username",)
    
admin.site.register(models.StudyPreferences)

