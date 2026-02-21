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


# --- AUTH & DASHBOARD ---

def login_view(request):
    return render(request, 'admin_panel/login.html')


def dashboard(request):
    # Fetch only the profiles that are waiting for verification
    pending_profiles = OrganizerProfile.objects.filter(verification_status='pending').order_by('-user__date_joined')

    # You might also want some stats for your dashboard cards
    context = {
        'profiles': pending_profiles,
        'total_users': User.objects.count(),
        'pending_count': pending_profiles.count(),
    }
    return render(request, 'admin_panel/adashboard.html', context)
    # return render(request, 'admin_panel/adashboard.html')


# --- USER MANAGEMENT ---

def manage_users(request):
    users = User.objects.all().order_by('-date_joined')
    query = request.GET.get('search', '').strip()
    if query:
        users = users.filter(username__icontains=query) | users.filter(email__icontains=query)
    return render(request, 'admin_panel/manage_users.html', {'users': users, 'query': query})


def delete_user(request, user_id):
    if request.method == "POST":
        user = get_object_or_404(User, id=user_id)
        user.delete()
        messages.success(request, f"User {user.username} has been deleted.")
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