
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from .forms import CustomAuthenticationForm, CustomUserCreationForm
from django.contrib.auth.decorators import login_required
from allauth.socialaccount.providers.google.views import oauth2_login
from django.contrib.auth.models import Group
from allauth.account.utils import complete_signup
from django.conf import settings
from django.views.decorators.csrf import csrf_protect
from organizer.models import Event, Application,PlayerSelectionForm
from accounts.models import Profile


@csrf_protect
def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            role_selected = form.cleaned_data.get('role')
            user.role = role_selected
            user.save()

            

            if role_selected == 'organizer':
                group, created = Group.objects.get_or_create(name='Organizer')
                user.groups.add(group)
            else:
                group, created = Group.objects.get_or_create(name='Athlete')
                user.groups.add(group)

            # messages.success(request, "Account created successfully! Please login.")
            # return redirect('accounts:login')

            return complete_signup(
                request,
                user,
                settings.ACCOUNT_EMAIL_VERIFICATION,
                settings.ACCOUNT_SIGNUP_REDIRECT_URL
            )

    else:
        form = CustomUserCreationForm()
        
    return render(request, 'accounts/signup.html', {'form': form})


# def login_view(request):
#     if request.method == 'POST':
#         form = CustomAuthenticationForm(request, data=request.POST)
#         if form.is_valid():
#             username = form.cleaned_data.get('username')
#             password = form.cleaned_data.get('password')
#             # role = form.cleaned_data.get('role')
#             remember_me = form.cleaned_data.get('remember_me')
#             user = authenticate(username=username, password=password)
#             if user is not None:
#                 login(request, user)
#                 if remember_me:
#                     request.session.set_expiry(1209600)
#                 else:
#                     request.session.set_expiry(0)
#                 # if role == 'organizer':
#                     # return redirect('organizer_dashboard')
#                     # return redirect('organizer:dashboard')
#                 return redirect('accounts:dashboard_redirect')
#             else:
#                 messages.error(request, "Invalid username or password.")
#     else:
#         form = CustomAuthenticationForm()
#     return render(request, 'accounts/login.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            # 1. Capture the role selected by the user in the login form
            selected_role = form.cleaned_data.get('role')
            remember_me = form.cleaned_data.get('remember_me')

            user = authenticate(username=username, password=password)

            if user is not None:
                # 2. Check the user's actual group membership
                is_organizer = user.groups.filter(name__iexact='Organizer').exists()
                is_athlete = user.groups.filter(name__iexact='Athlete').exists()

                # 3. Validation Logic: Block mismatched roles with an alert
                if selected_role == 'organizer' and not is_organizer:
                    messages.error(request,
                                   f"Access Denied. '{username}' is registered as an Athlete. Please select the correct role.")
                    return render(request, 'accounts/login.html', {'form': form})

                elif selected_role == 'athlete' and not is_athlete:
                    messages.error(request,
                                   f"Access Denied. '{username}' is registered as an Organizer. Please select the correct role.")
                    return render(request, 'accounts/login.html', {'form': form})

                # 4. If everything is correct, log the user in
                login(request, user)
                request.session.set_expiry(1209600 if remember_me else 0)
                return redirect('accounts:dashboard_redirect')
            else:
                messages.error(request, "Invalid username or password.")
    else:
        form = CustomAuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form})




# @login_required
# def role_based_redirect(request):
#     user = request.user
#
#     # 1. Debugging: Check the terminal to see what group this user actually has
#     print(f"DEBUG: User {user.username} is in groups: {user.groups.all()}")
#
#     # 2. Check for Organizer group (Case-insensitive check is safer)
#     if user.groups.filter(name__iexact='Organizer').exists():
#         return redirect('organizer:dashboard')
#
#     # 3. Check for Athlete group
#     if user.groups.filter(name__iexact='Athlete').exists():
#         return redirect('accounts:user_dashboard')
#
#     # 4. Fallback (If no groups found, send to default user dashboard)
#     return redirect('accounts:user_dashboard')


@login_required
def role_based_redirect(request):
    user = request.user
    # Capture whether they clicked 'athlete' or 'organizer' card
    clicked_role = request.GET.get('role_type')

    # 1. Handle Organizer Group
    if user.groups.filter(name__iexact='Organizer').exists():
        # if clicked_role == 'athlete':
        #     messages.info(request, "Note: You are logged in as an Organizer, so you've been sent to your management dashboard.")
        return redirect('organizer:dashboard')

    # 2. Handle Athlete Group
    if user.groups.filter(name__iexact='Athlete').exists():
        # if clicked_role == 'organizer':
        #     # They are an athlete trying to enter the organizer dashboard
        #     messages.warning(request, "Access denied. You must have an Organizer account.")
            return redirect('accounts:user_dashboard')
    return redirect('accounts:user_dashboard')

    # 3. Fallback: If logged in but no group assigned yet
    messages.warning(request, "Please contact support to assign a role to your account.")
    return redirect('accounts:user_dashboard')


@login_required
def user_dashboard(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    # 1. Look for all Applications where the applicant_name matches the username
    # We use username because that's the unique string we have for "menaka"
    user_apps = Application.objects.filter(applicant_name=request.user.username)

    # 2. Extract the event IDs from those applications
    event_ids = user_apps.values_list('event_id', flat=True)

    # 3. Get the actual Event objects to display on the dashboard
    joined_events = Event.objects.filter(id__in=event_ids)
    available_forms = PlayerSelectionForm.objects.filter(is_published=True) #
    my_submissions = PlayerSelectionForm.objects.filter( #
        email=request.user.email, 
        is_published=False
    )
    # user_apps = PlayerSelectionForm.objects.filter(email=request.user.email)#
    context = {
        'user': request.user,
        'profile': profile,
        'joined_events': joined_events,
        'total_joined': joined_events.count(),
        'title': 'User Dashboard',
        'user_apps': user_apps, # Passing apps to see statuses 
        'available_forms': available_forms,#
        'my_submissions': my_submissions,
    }
    return render(request, 'accounts/user_dashboard.html', context)

@login_required
def organizer_dashboard(request):
    return render(request, 'organizer/organizer_dashboard.html')


def custom_google_login(request):
    role = request.GET.get('role')
    if role not in ['user', 'organizer']:
        messages.error(request, "Please choose a valid role before signing in.")
        return redirect('login')
    request.session['login_role'] = role
    return oauth2_login(request)






