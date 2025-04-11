from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login as auth_login
from django.http import JsonResponse
import json
from .models import StudyPreferences
from .forms import StudyPreferencesForm
from datetime import timedelta, time
from pulp import *

def home(request):
    return render(request, "home.html")

def register(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)  # Log the user in after registration
            return redirect("home")
    else:
        form = UserCreationForm()
    return render(request, "registration/register.html", {"form": form})

@login_required
def study_preferences(request):
    user = request.user
    preferences, created = StudyPreferences.objects.get_or_create(user=user)

    if request.method == "POST":
        form = StudyPreferencesForm(request.POST, instance=preferences)
        if form.is_valid():
            study_prefs = form.save(commit=False)
            
            # Handle subjects from frontend
            subjects = json.loads(request.POST.get('subjects', '[]'))
            study_prefs.subjects = subjects
            
            # Handle priorities if you have drag-sorting
            priorities = json.loads(request.POST.get('priorities', '[]'))
            study_prefs.priorities = priorities
            
            study_prefs.save()
            return JsonResponse({'success': True})
        
        return JsonResponse({
            'success': False,
            'errors': form.errors.as_json()
        })

    # Initialize form with existing data
    form = StudyPreferencesForm(instance=preferences)
    return render(request, 'study_preferences.html', {
        'form': form,
        'saved_subjects': preferences.subjects or []
    })

@login_required
def study_plan(request):
    user = request.user
    try:
        prefs = StudyPreferences.objects.get(user=user)
        subjects = prefs.subjects or []
        priorities = prefs.priorities or []
    except StudyPreferences.DoesNotExist:
        return redirect('study_preferences')

    if not subjects:
        return render(request, 'study_plan.html', {
            'error': 'No subjects configured',
            'study_slots': []
        })

    # Get time preferences
    if isinstance(prefs.start_time, str):
        hours, minutes = map(int, prefs.start_time.split(':'))
        start_time = time(hours, minutes)
    else:
        start_time = prefs.start_time

    start_minutes = start_time.hour * 60 + start_time.minute
    session_mins = prefs.session_length
    total_mins = int(prefs.total_study_time * 60)
    break_mins = prefs.break_duration
    num_breaks = prefs.num_breaks
    
    # Calculate total available study time (excluding breaks)
    available_study_time = total_mins - (num_breaks * break_mins)
    
    # Convert priorities to a dictionary if it's a list
    priority_dict = {}
    if isinstance(priorities, list):
        # If priorities is a list of [subject, priority_value] pairs
        for item in priorities:
            if isinstance(item, list) and len(item) >= 2:
                priority_dict[item[0]] = item[1]
    elif isinstance(priorities, dict):
        priority_dict = priorities
    
    # Set default priorities if not specified
    for subject in subjects:
        if subject not in priority_dict:
            priority_dict[subject] = 5
    
    # Create a PuLP problem
    prob = LpProblem("Study_Schedule_Optimization", LpMaximize)
    
    # Create decision variables: minutes allocated to each subject
    # Using "continuous" variables allows for fractional minutes that we'll round later
    study_vars = LpVariable.dicts("StudyTime", subjects, lowBound=session_mins, cat='Continuous')
    
    # Objective function: maximize sum of (priority * minutes) for each subject
    prob += lpSum([priority_dict[subject] * study_vars[subject] for subject in subjects]), "Maximize priority-weighted study time"
    
    # Constraint: total study time equals available time
    prob += lpSum([study_vars[subject] for subject in subjects]) == available_study_time, "Total study time constraint"
    
    # Solve the problem
    prob.solve(PULP_CBC_CMD(msg=False))
    
    if LpStatus[prob.status] != 'Optimal':
        return render(request, 'study_plan.html', {
            'error': 'Could not generate an optimal study plan. Please adjust your preferences.',
            'study_slots': []
        })
    
    # Extract solution
    subject_minutes = {subject: round(value(study_vars[subject])) for subject in subjects}
    
    # Adjust for rounding errors
    total_allocated = sum(subject_minutes.values())
    if total_allocated != available_study_time:
        # Find subject with highest allocation to adjust
        max_subject = max(subject_minutes, key=subject_minutes.get)
        subject_minutes[max_subject] += (available_study_time - total_allocated)
    
    # Generate study slots with breaks
    study_slots = []
    current_time = start_minutes
    
    # Calculate break intervals
    break_points = []
    if num_breaks > 0:
        study_segment = available_study_time / (num_breaks + 1)
        for i in range(1, num_breaks + 1):
            break_points.append(start_minutes + int(i * study_segment) + ((i-1) * break_mins))
    
    # Create schedule by allocating sessions based on optimal time distribution
    remaining_minutes = {subject: subject_minutes[subject] for subject in subjects}
    subject_list = sorted(subjects, key=lambda x: -priority_dict[x])  # Sort by priority (high to low)
    
    while any(remaining_minutes.values()):
        # Check if we need a break before next session
        if break_points and current_time >= break_points[0]:
            # Add a break
            end_time = current_time + break_mins
            study_slots.append({
                'time': f"{current_time // 60:02d}:{current_time % 60:02d} to {end_time // 60:02d}:{end_time % 60:02d}",
                'subject': 'Break',
                'activity': 'Take a break',
                'duration': break_mins
            })
            current_time = end_time
            break_points.pop(0)
            continue
        
        # Find next subject to allocate time to (highest priority with remaining time)
        next_subject = None
        for subject in subject_list:
            if remaining_minutes[subject] > 0:
                next_subject = subject
                break
        
        if not next_subject:
            break  # No more subjects with remaining time
        
        # Determine session length
        session_duration = min(session_mins, remaining_minutes[next_subject])
        
        # Add study session
        end_time = current_time + session_duration
        study_slots.append({
            'time': f"{current_time // 60:02d}:{current_time % 60:02d} to {end_time // 60:02d}:{end_time % 60:02d}",
            'subject': next_subject,
            'activity': 'Study',
            'duration': session_duration,
            'priority': priority_dict.get(next_subject, 5)
        })
        
        current_time = end_time
        remaining_minutes[next_subject] -= session_duration
        
        # If less than minimum session time remains, redistribute to not waste time
        if 0 < remaining_minutes[next_subject] < session_mins:
            # Find subject with highest priority that can use this time
            for subject in subject_list:
                if subject != next_subject and remaining_minutes[subject] >= session_mins:
                    remaining_minutes[subject] += remaining_minutes[next_subject]
                    remaining_minutes[next_subject] = 0
                    break
    
    # Add any remaining breaks
    for break_point in break_points:
        end_time = current_time + break_mins
        study_slots.append({
            'time': f"{current_time // 60:02d}:{current_time % 60:02d} to {end_time // 60:02d}:{end_time % 60:02d}",
            'subject': 'Break',
            'activity': 'Take a break',
            'duration': break_mins
        })
        current_time = end_time
    
    # Sort study slots by time
    study_slots.sort(key=lambda x: int(x['time'].split(' to ')[0].replace(':', '')))
    
    return render(request, 'study_plan.html', {
        'study_slots': study_slots,
        'total_duration': total_mins,
        'optimization_result': {
            'subject_allocations': [{'subject': subject, 'minutes': subject_minutes[subject]} for subject in subjects],
            'solver_status': LpStatus[prob.status]
        }
    })