from django.shortcuts import redirect, render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import logout
from organizer.models import Event
from django.shortcuts import render, get_object_or_404

# Create your views here.
def home(request):
    featured_events = Event.objects.filter(
        status__in=['LIVE', 'UPCOMING']
    ).order_by('-created_at') 

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
def cricket(request):
    return HttpResponse("Welcome to cricket page.")
def football(request):
    return HttpResponse("Welcome to football page.")
def volleyball(request):
    return HttpResponse("Welcome to volleyball page.")
def basketball(request):
    return HttpResponse("Welcome to basketball page.")
def badminton(request):
    return HttpResponse("Welcome to badminton page.")
def logout_user(request):
    logout(request)     # <-- THIS clears login
    return redirect("/")
# def event_detail(request, id):
#     event = get_object_or_404(Event, id=id)
#     return render(request, 'homepage/event_detail.html', {'event': event})

