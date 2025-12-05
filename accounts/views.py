
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from .forms import CustomAuthenticationForm, CustomUserCreationForm
from django.contrib.auth.decorators import login_required
from allauth.socialaccount.providers.google.views import oauth2_login
from django.contrib.auth.models import Group

def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.role = form.cleaned_data.get('role')
            user.save()
            messages.success(request, "Account created successfully! Please login.")
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'accounts/signup.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            # role = form.cleaned_data.get('role')
            remember_me = form.cleaned_data.get('remember_me')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                if remember_me:
                    request.session.set_expiry(1209600)
                else:
                    request.session.set_expiry(0)
                # if role == 'organizer':
                    # return redirect('organizer_dashboard')
                    # return redirect('organizer:dashboard')
                return redirect('accounts:dashboard_redirect')
            else:
                messages.error(request, "Invalid username or password.")
    else:
        form = CustomAuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form})


@login_required
def role_based_redirect(request):

    user = request.user


    if user.groups.filter(name='Organizer').exists():
        return redirect('organizer:dashboard')  # The destination URL name


    if user.groups.filter(name='Athlete').exists():
        return redirect('accounts:user_dashboard')

    # Fallback/Default for any logged-in user who isn't explicitly grouped
    return redirect('accounts:user_dashboard')


# Now, update your existing dashboard view names to be role-specific:



@login_required
def user_dashboard(request):
    return render(request, 'accounts/user_dashboard.html')


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

@login_required
def player_application_view(request):

    context = {
        # 'form': form,
        'page_title': 'Player Application',
    }


    return render(request, 'accounts/player_application_form.html', context)

