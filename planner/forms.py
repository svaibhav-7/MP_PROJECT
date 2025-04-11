from django import forms
from .models import StudyPreferences

class StudyPreferencesForm(forms.ModelForm):
    study_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=False
    )
    
    class Meta:
        model = StudyPreferences
        fields = [
            'study_date',
            'start_time',
            'session_length',
            'total_study_time',
            'num_breaks',
            'break_duration',
            'leisure_time'
        ]
        widgets = {
            'start_time': forms.TimeInput(attrs={'type': 'time'}),
            'session_length': forms.NumberInput(attrs={'min': 15, 'max': 180}),
        }