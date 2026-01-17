from django.shortcuts import redirect, render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import logout
from organizer.models import Event, Match
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
import json
from django.utils import timezone
from django.db.models import Q


# Create your views here.
def home(request):
    featured_events = Event.objects.filter(
        status__in=['LIVE', 'UPCOMING']
    ).order_by('-created_at') [:3]

    return render(request, 'homepage/home.html',{
        'featured_events': featured_events
    })
    # return HttpResponse("Homepage is working!")


def is_organizer(user):

    if not user.is_authenticated:
        return False
    return user.groups.filter(name='Organizer').exists()

@login_required(login_url='accounts:login')
def handle_athlete_redirect(request):
    return redirect('accounts:user_dashboard')

@login_required(login_url='accounts:login')
def handle_organizer_redirect(request):
    if is_organizer(request.user):
        # Uses the name 'organizer_dashboard' defined in organizer/urls.py
        return redirect('organizer:dashboard')
    else:

        messages.error(request, "You do not have organizer privileges.")
        return redirect('accounts:user_dashboard')

def about(request):
    return render(request, 'homepage/about.html')
def news(request):
    return render(request, 'news/index.html')
# def cricket(request):
#     return HttpResponse("Welcome to cricket page.")
# def football(request):
#     return HttpResponse("Welcome to football page.")
# def volleyball(request):
#     return HttpResponse("Welcome to volleyball page.")
# def basketball(request):
#     return HttpResponse("Welcome to basketball page.")
# def badminton(request):
#     return HttpResponse("Welcome to badminton page.")
# def viewmatch(request):
#     return HttpResponse("Welcome to view matches section.")
def logout_user(request):
    logout(request)     # <-- THIS clears login
    return redirect("/")
# def event_detail(request, id):
#     event = get_object_or_404(Event, id=id)
#     return render(request, 'homepage/event_detail.html', {'event': event})

# def all_events(request):
#     # This extracts every event created by organizers
#     events = Event.objects.all().order_by('-created_at')
#
#     upcoming_events = Event.objects.filter(
#         date_time__gte=timezone.now()
#     ).order_by('date_time')
#
#     # 🚨 NEW: Create a list of date strings for the JavaScript calendar
#     # Format: ['2025-12-26', '2025-12-27']
#     event_dates = [e.date_time.strftime('%Y-%m-%d') for e in upcoming_events]
#
#     return render(request, 'homepage/all_events.html', {
#         'events': events,
#         'upcoming_events': upcoming_events,
#         'event_dates_json': json.dumps(event_dates),
#         'page_title': 'All Matches & Events'
#     })


def all_events(request):
    sport_query = request.GET.get('sport')  # Captured from navbar link

    # Start with all published events
    events = Event.objects.all().order_by('-created_at')

    if sport_query:
        # 1. Finds events where the MAIN game_type is the selected sport
        # 2. OR finds events like "PEC Sports Week" that have matches of that sport
        events = events.filter(
            Q(game_type__iexact=sport_query) |
            Q(matches__game_type__iexact=sport_query)
        ).distinct()

    upcoming_events = Event.objects.filter(
        date_time__gte=timezone.now()
    ).order_by('date_time')
    event_dates = [e.date_time.strftime('%Y-%m-%d') for e in upcoming_events]

    return render(request, 'homepage/all_events.html', {
        'events': events,
        'selected_sport': sport_query,
        'event_dates_json': json.dumps(event_dates),
        'page_title': f"{sport_query.capitalize() if sport_query else 'All'} Matches"
    })


def privacy_policy(request):
    return render(request, 'homepage/privacy.html')
def contact_view(request):
    return render(request, 'homepage/contact.html')
def terms_view(request):
    return render(request, 'homepage/terms.html')