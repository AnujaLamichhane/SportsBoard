# from django.shortcuts import render
#
# # Create your views here.
# from django.contrib.auth.decorators import user_passes_test
#
# from organizer.models import OrganizerProfile
#
#
# # @user_passes_test(lambda u: u.is_staff)
# def login_view(request):
#     return render(request, 'admin_panel/login.html')
#
# def dashboard(request):
#     return render(request, 'admin_panel/adashboard.html')
#
# def organizer_requests(request):
#     # You can fetch your organizers here:
#     profiles = OrganizerProfile.objects.all().order_by('-verification_status')
#
#     # pending_organizers = Organizer.objects.filter(status='pending')
#     return render(request, 'admin_panel/organizer_requests.html', {'profiles': profiles})
#
# from django.shortcuts import render, redirect, get_object_or_404
# from django.contrib.auth.models import User
# from django.contrib import messages
#
#
# def manage_users(request):
#     # Fetch all users except the current superuser (optional)
#     users = User.objects.all().order_by('-date_joined')
#
#     # Handle search logic
#     query = request.GET.get('search','').strip()
#     if query:
#         users = users.filter(username__icontains=query) | users.filter(email__icontains=query)
#
#     return render(request, 'admin_panel/manage_users.html', {'users': users, 'query': query})
#
# def delete_user(request, user_id):
#     if request.method == "POST":
#         user = get_object_or_404(User, id=user_id)
#         user.delete()
#         messages.success(request, f"User {user.username} has been deleted.")
#     return redirect('admin_panel:manage_users')
#
# from organizer.models import OrganizerFeedback
#
# def manage_feedback(request):
#     def manage_feedback(request):
#         """List all feedback, showing unresolved issues first."""
#         feedbacks = OrganizerFeedback.objects.all().order_by('is_resolved', '-created_at')
#         unresolved_count = feedbacks.filter(is_resolved=False).count()
#         return render(request, 'admin_panel/manage_feedback.html', {
#             'feedbacks': feedbacks,
#             'unresolved_count': unresolved_count
#         })
#
# def resolve_feedback(request, pk):
#     """Mark a specific feedback entry as resolved."""
#     feedback = get_object_or_404(OrganizerFeedback, pk=pk)
#     feedback.is_resolved = True
#     feedback.save()
#     messages.success(request, f"Feedback from {feedback.organizer.username} marked as resolved.")
#     return redirect('admin_panel:manage_feedback')
#
#
# def verify_organizer(request, pk, action):
#     """Update verification status based on admin action."""
#     profile = get_object_or_404(OrganizerProfile, pk=pk)
#
#     if action == 'approve':
#         profile.verification_status = 'verified'
#         profile.is_verified = True  # Matches your model's boolean field
#         messages.success(request, f"Organizer {profile.organization_name} has been verified.")
#     elif action == 'reject':
#         profile.verification_status = 'rejected'
#         profile.is_verified = False
#         messages.warning(request, f"Verification for {profile.organization_name} was rejected.")
#
#     profile.save()
#     return redirect('admin_panel:organizer_requests')

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
# Import your transaction model (e.g., KhaltiTransaction)
from organizer.models import KhaltiTransaction ,OrganizerProfile

# --- AUTH & DASHBOARD ---

def login_view(request):
    return render(request, 'admin_panel/login.html')



def calculate_trend(current, previous):
    """Returns the percentage change between current and previous."""
    if previous == 0:
        return 100 if current > 0 else 0
    return int(((current - previous) / previous) * 100)

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
    }

    return render(request, 'admin_panel/adashboard.html', {'stats': stats})
# --- USER MANAGEMENT ---

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

def organizer_requests(request):
    profiles = OrganizerProfile.objects.all().order_by('-verification_status')
    return render(request, 'admin_panel/organizer_requests.html', {'profiles': profiles})


def verify_organizer(request, pk, action):
    profile = get_object_or_404(OrganizerProfile, pk=pk)
    if action == 'approve':
        profile.verification_status = 'verified'
        profile.is_verified = True
        messages.success(request, f"Organizer {profile.organization_name} has been verified.")
    elif action == 'reject':
        profile.verification_status = 'rejected'
        profile.is_verified = False
        messages.warning(request, f"Verification for {profile.organization_name} was rejected.")
    profile.save()
    return redirect('admin_panel:organizer_requests')


# --- FEEDBACK MANAGEMENT (FIXED) ---

def manage_feedback(request):
    """List all feedback, showing unresolved issues first."""
    # FIXED: Removed the nested function 'def manage_feedback'
    feedbacks = OrganizerFeedback.objects.all().order_by('is_resolved', '-created_at')
    unresolved_count = feedbacks.filter(is_resolved=False).count()

    return render(request, 'admin_panel/manage_feedback.html', {
        'feedbacks': feedbacks,
        'unresolved_count': unresolved_count
    })


def resolve_feedback(request, pk):
    """Mark a specific feedback entry as resolved."""
    feedback = get_object_or_404(OrganizerFeedback, pk=pk)
    feedback.is_resolved = True
    feedback.save()
    messages.success(request, f"Feedback from {feedback.organizer.username} marked as resolved.")
    return redirect('admin_panel:manage_feedback')

def manage_sports(request):
    
    all_events = Event.objects.all().select_related('organizer').order_by('-created_at')
    
    context = {
        'sports_data': all_events,
    }
    return render(request, 'admin_panel/sports.html', context)

def reports_view(request):
    # 1. Data for "Events by Sport" Bar Chart
    sport_data = Event.objects.values('game_type').annotate(count=Count('id'))
    # This creates a list of labels and values for Chart.js
    chart_labels = [item['game_type'] for item in sport_data]
    chart_values = [item['count'] for item in sport_data]

    # 2. Data for "Recent Activity"
    # Fetching the latest 5 actions
    recent_activities = [
        {"title": "Pokhara United created 7-A-Side Cup", "time": "2 mins ago", "type": "plus"},
        # In a real app, you'd query an ActivityLog model here
    ]

    context = {
        'labels': chart_labels,
        'values': chart_values,
        'recent_activities': recent_activities,
    }
    
    return render(request, 'admin_panel/reports.html', context)