
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from organizer.models import OrganizerProfile, OrganizerFeedback
from organizer.models import Event,GAME_TYPE_CHOICES
from django.db.models import Count
from django.utils import timezone
from datetime import timedelta
from django.db.models import Sum
from django.contrib.admin.models import LogEntry, CHANGE
from django.contrib.contenttypes.models import ContentType
# from django.contrib.admin.models import LogEntry
# Import your transaction model (e.g., KhaltiTransaction)
from organizer.models import KhaltiTransaction ,OrganizerProfile
from django.contrib import messages
from django.shortcuts import render, redirect
from .models import SiteSettings
from .forms import SiteSettingsForm
from functools import wraps
from django.shortcuts import render, redirect
from accounts.models import Feedback as UserFeedback
# --- AUTH & DASHBOARD ---



from django.contrib.auth import authenticate, login

from django.contrib.auth import authenticate, login

def admin_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_superuser:
            return redirect('admin_panel:login')
        return view_func(request, *args, **kwargs)
    return wrapper


def login_view(request):
    if request.user.is_authenticated and request.user.is_superuser:
        return redirect('admin_panel:adashboard')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()

        user = authenticate(request, username=username, password=password)

        if user is not None and user.is_superuser:
            login(request, user)
            return redirect('admin_panel:adashboard')
        else:
            messages.error(request, 'Invalid Admin credentials. Access Denied.')

    return render(request, 'admin_panel/login.html')






def calculate_trend(current, previous):
    """Returns the percentage change between current and previous."""
    if previous == 0:
        return 100 if current > 0 else 0
    return int(((current - previous) / previous) * 100)

@admin_required
def dashboard(request):
    now = timezone.now()
    last_30 = now - timedelta(days=30)
    prev_30 = now - timedelta(days=60)

    # --- 1. Total Events & Trend ---
    total_events = Event.objects.count()
    ev_current = Event.objects.filter(created_at__gte=last_30).count()
    ev_prev = Event.objects.filter(created_at__range=(prev_30, last_30)).count()
    event_trend = calculate_trend(ev_current, ev_prev)

    # --- 2. Active Users & Trend ---
    active_users = User.objects.filter(is_active=True).count()
    u_current = User.objects.filter(date_joined__gte=last_30).count()
    u_prev = User.objects.filter(date_joined__range=(prev_30, last_30)).count()
    user_trend = calculate_trend(u_current, u_prev)

    # --- 3. Pending Requests & Trend ---
    pending_reqs = OrganizerProfile.objects.filter(verification_status='pending').count()
    req_current = OrganizerProfile.objects.filter(user__date_joined__gte=last_30).count()
    req_prev = OrganizerProfile.objects.filter(user__date_joined__range=(prev_30, last_30)).count()
    req_trend = calculate_trend(req_current, req_prev)
    pending_profiles = OrganizerProfile.objects.filter(verification_status='pending').order_by('-user__date_joined')
    # --- 4. Total Revenue & Trend ---
    total_rev = KhaltiTransaction.objects.aggregate(total=Sum('amount'))['total'] or 0
    rev_current = KhaltiTransaction.objects.filter(created_at__gte=last_30).aggregate(total=Sum('amount'))['total'] or 0
    rev_prev = KhaltiTransaction.objects.filter(created_at__range=(prev_30, last_30)).aggregate(total=Sum('amount'))['total'] or 0
    rev_trend = calculate_trend(rev_current, rev_prev)


    # Formatting Revenue
    revenue_display = f"{total_rev / 1000:.1f}k" if total_rev >= 1000 else str(total_rev)

    stats = {
        'total_events': total_events,
        'event_trend': event_trend,
        'active_users': active_users,
        'user_trend': user_trend,
        'pending_requests': pending_reqs,
        'req_trend': req_trend,
        'total_revenue': revenue_display,
        'rev_trend': rev_trend,
        'profiles': pending_profiles,
    }

    return render(request, 'admin_panel/adashboard.html', stats)
# --- USER MANAGEMENT ---

@admin_required
def manage_users(request):
    # Get all users initially
    users = User.objects.all().order_by('-date_joined')
    
    # Get parameters from the URL
    query = request.GET.get('search', '').strip()
    user_type = request.GET.get('user_type', '')

    # Apply Search Filter
    if query:
        users = users.filter(username__icontains=query) | users.filter(email__icontains=query)

    # Apply Type Filter (Organizer vs Athlete/User)
    if user_type == 'organizer':
        # Filter users who HAVE an organizer_profile (isnull=False)
        users = users.filter(organizer_profile__isnull=False)
    elif user_type == 'athlete':
        # Filter users who DO NOT have an organizer_profile and are not staff
        users = users.filter(organizer_profile__isnull=True, is_staff=False)

    return render(request, 'admin_panel/manage_users.html', {
        'users': users, 
        'query': query,
        'user_type': user_type
    })

@admin_required
def delete_user(request, user_id):
    user_to_delete = get_object_or_404(User, id=user_id)
    
    # Check if the target user is an Admin
    if user_to_delete.is_superuser or user_to_delete.is_staff:
        messages.error(request, "Safety Protocol: Administrator accounts cannot be deleted.")
        return redirect('admin_panel:manage_users')

    user_to_delete.delete()
    messages.success(request, "User deleted successfully.")
    return redirect('admin_panel:manage_users')


# --- ORGANIZER VERIFICATION ---
@admin_required
def organizer_requests(request):
    profiles = OrganizerProfile.objects.all().order_by('-verification_status')
    return render(request, 'admin_panel/organizer_requests.html', {'profiles': profiles})


@admin_required
def verify_organizer(request, pk, action):
    profile = get_object_or_404(OrganizerProfile, pk=pk)

    if action == 'approve':
        profile.verification_status = 'verified'
        profile.is_verified = True
        status_msg = "Approved"
    elif action == 'reject':
        profile.verification_status = 'rejected'
        profile.is_verified = False
        status_msg = "Rejected"
    else:
        return redirect('admin_panel:organizer_requests')

    profile.save()

    # Create the Manual Log Entry
    if request.user.is_authenticated:
        LogEntry.objects.log_action(
            user_id=request.user.id,
            content_type_id=ContentType.objects.get_for_model(profile).pk,
            object_id=profile.pk,
            object_repr=f"{profile.organization_name} ({status_msg})",
            action_flag=CHANGE,
            change_message=f"Admin {status_msg} this organizer request."
        )

    messages.success(request, f"Organizer {profile.organization_name} has been {action}d.")
    return redirect('admin_panel:organizer_requests')


# --- FEEDBACK MANAGEMENT (FIXED) ---


@admin_required
def manage_feedback(request):
    """List all feedback from both Organizers and Athletes."""
    query = request.GET.get('search', '').strip()

    org_feedbacks = OrganizerFeedback.objects.all().order_by('is_resolved', '-created_at')
    user_feedbacks = UserFeedback.objects.all().order_by('is_resolved', '-created_at')

    if query:
        org_feedbacks = org_feedbacks.filter(subject__icontains=query) | org_feedbacks.filter(
            organizer__username__icontains=query)
        user_feedbacks = user_feedbacks.filter(subject__icontains=query) | user_feedbacks.filter(
            user__username__icontains=query)

    unresolved_count = (
            org_feedbacks.filter(is_resolved=False).count() +
            user_feedbacks.filter(is_resolved=False).count()
    )

    return render(request, 'admin_panel/manage_feedback.html', {
        'org_feedbacks': org_feedbacks,
        'user_feedbacks': user_feedbacks,
        'unresolved_count': unresolved_count,
        'query': query
    })

@admin_required
def resolve_feedback(request, user_type, pk):
    """Mark feedback as resolved based on user type."""
    if user_type == 'organizer':
        feedback = get_object_or_404(OrganizerFeedback, pk=pk)
    else:
        feedback = get_object_or_404(UserFeedback, pk=pk)

    feedback.is_resolved = True
    feedback.save()
    messages.success(request, f"Feedback from {user_type} marked as resolved.")
    return redirect('admin_panel:manage_feedback')

@admin_required
def manage_sports(request):
    # Use timezone-aware 'now' since date_time is a DateTimeField
    now = timezone.now()
    all_events = Event.objects.all().select_related('organizer').order_by('-created_at')

    for event in all_events:
        # If the event time is in the past, it's completed
        if event.date_time < now:
            event.calculated_status = 'completed'
        # Since you don't have a separate 'start' and 'end',
        # we'll mark it 'ongoing' if it's within a 3-hour window of the start time
        elif event.date_time <= now <= (event.date_time + timedelta(hours=3)):
            event.calculated_status = 'ongoing'
        # Otherwise, it's in the future
        else:
            event.calculated_status = 'upcoming'

    context = {
        'sports_data': all_events,
    }
    return render(request, 'admin_panel/sports.html', context)


@admin_required
def reports_view(request):
    # 1. Events by Sport Chart
    sport_data = Event.objects.values('game_type').annotate(count=Count('id'))
    chart_labels = [item['game_type'] for item in sport_data]
    chart_values = [item['count'] for item in sport_data]

    # 2. User Distribution Chart
    athletes = User.objects.filter(organizer_profile__isnull=True, is_staff=False).count()
    organizers = OrganizerProfile.objects.count()

    # 3. Feedback Resolution Logic
    total_feedback = OrganizerFeedback.objects.count()
    resolved_feedback = OrganizerFeedback.objects.filter(is_resolved=True).count()
    resolved_percentage = int((resolved_feedback / total_feedback) * 100) if total_feedback > 0 else 0

    # Add these two lines to get the data for the new cards
    total_events = Event.objects.count()
    total_rev = KhaltiTransaction.objects.aggregate(total=Sum('amount'))['total'] or 0
    revenue_display = f"{total_rev / 1000:.1f}k" if total_rev >= 1000 else str(total_rev)

    # 4. Real Recent Activity (Using Django Admin Logs)
    logs = LogEntry.objects.all().select_related('user', 'content_type').order_by('-action_time')[:6]
    recent_activities = []
    for log in logs:
        recent_activities.append({
            "title": f"{log.get_action_flag_display()}: {log.object_repr}",
            "time": log.action_time,
            "user": log.user.username
        })

    context = {
        'labels': chart_labels,
        'values': chart_values,
        'user_dist_labels': ['Athletes', 'Organizers'],
        'user_dist_values': [athletes, organizers],
        'total_events': total_events,
        'total_revenue': revenue_display,
        'resolved_percentage': resolved_percentage,
        'verified_count': OrganizerProfile.objects.filter(verification_status='verified').count(),
        'recent_activities': recent_activities,
    }
    return render(request, 'admin_panel/reports.html', context)

@admin_required
def settings_view(request):

    settings = SiteSettings.load()

    if request.method == "POST":
        form = SiteSettingsForm(request.POST, instance=settings)

        if form.is_valid():
            form.save()
            messages.success(request, "Settings updated successfully!")
            return redirect("admin_panel:settings")

    else:
        form = SiteSettingsForm(instance=settings)

    return render(request,
                  "admin_panel/settings.html",
                  {"form": form})