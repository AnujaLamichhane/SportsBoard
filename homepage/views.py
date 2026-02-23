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
        status__in=['LIVE', 'UPCOMING'],
        date_time__date__gte=timezone.now().date() #
    ).order_by('date_time')[:3]#

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

        # messages.error(request, "You do not have organizer privileges.")
        return redirect('accounts:user_dashboard')

def about(request):
    return render(request, 'homepage/about.html')
def news(request):
    return render(request, 'news/index.html')

def logout_user(request):
    logout(request)     # <-- THIS clears login
    return redirect("/")





def all_events(request):
    # 1. Capture all GET parameters
    sport_query = request.GET.get('sport')
    search_query = request.GET.get('search')
    organizer_status = request.GET.get('organizer') # 'verified' or 'unverified'
    price_type = request.GET.get('price')           # 'paid' or 'free'

    # 2. Optimized Base Queryset
    # select_related fetches the organizer profile in ONE query (Better performance)
    events = Event.objects.all().select_related('organizer__organizer_profile').order_by('-date_time')

    # 3. Filtering Logic
    if sport_query:
        events = events.filter(
            Q(game_type__iexact=sport_query) |
            Q(matches__game_type__iexact=sport_query)
        ).distinct()

    if search_query:
       events = events.filter(
            Q(name__icontains=search_query) |
            Q(matches__game_type__icontains=search_query) |
            Q(matches__team_a__icontains=search_query) |
            Q(matches__team_b__icontains=search_query)
        ).distinct()

    # 🚨 NEW: Filter by Organizer Verification
    if organizer_status == 'verified':
        events = events.filter(organizer__organizer_profile__is_verified=True)
    elif organizer_status == 'unverified':
        events = events.filter(organizer__organizer_profile__is_verified=False)

    # 🚨 NEW: Filter by Price (Paid vs Free)
    if price_type == 'paid':
        # Events that have at least one ticket tier with price > 0
        events = events.filter(ticket_tiers__price__gt=0).distinct()
    elif price_type == 'free':
        # Events with no tickets OR tickets specifically priced at 0
        events = events.filter(Q(ticket_tiers__price=0) | Q(ticket_tiers__isnull=True)).distinct()

    # 4. Calendar Logic (Remains unchanged)
    all_calendar_events = Event.objects.all()
    event_dates = [e.date_time.strftime('%Y-%m-%d') for e in all_calendar_events if e.date_time]
    events_list = []
    for e in all_calendar_events:
        if e.date_time:
            events_list.append({
                'name': e.name,
                'date': e.date_time.strftime('%Y-%m-%d'),
                'formatted_date': e.date_time.strftime('%a, %b %d')
            })

    # 5. Dynamic Page Title
    title = "All Matches & Events"
    if sport_query: title = f"{sport_query.capitalize()} Events"
    if organizer_status == 'verified': title += " (Verified)"

    return render(request, 'homepage/all_events.html', {
        'events': events,
        'search_query': search_query,
        'selected_sport': sport_query,
        'selected_organizer': organizer_status,
        'selected_price': price_type,
        'event_dates_json': json.dumps(event_dates),
        'events_json': json.dumps(events_list),
        'page_title': title
    })


def privacy_policy(request):
    return render(request, 'homepage/privacy.html')
def contact_view(request):
    return render(request, 'homepage/contact.html')
def terms_view(request):
    return render(request, 'homepage/terms.html')
