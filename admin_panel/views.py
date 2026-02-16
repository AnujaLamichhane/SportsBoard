from django.shortcuts import render

# Create your views here.
from django.contrib.auth.decorators import user_passes_test

# @user_passes_test(lambda u: u.is_staff)
def login_view(request):
    return render(request, 'admin_panel/login.html')

def dashboard(request):
    return render(request, 'admin_panel/adashboard.html')

def organizer_requests(request):
    # You can fetch your organizers here:
    # pending_organizers = Organizer.objects.filter(status='pending')
    return render(request, 'admin_panel/organizer_requests.html')

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib import messages

def manage_users(request):
    # Fetch all users except the current superuser (optional)
    users = User.objects.all().order_by('-date_joined')
    
    # Handle search logic
    query = request.GET.get('search','').strip()
    if query:
        users = users.filter(username__icontains=query) | users.filter(email__icontains=query)

    return render(request, 'admin_panel/manage_users.html', {'users': users, 'query': query})

def delete_user(request, user_id):
    if request.method == "POST":
        user = get_object_or_404(User, id=user_id)
        user.delete()
        messages.success(request, f"User {user.username} has been deleted.")
    return redirect('admin_panel:manage_users')