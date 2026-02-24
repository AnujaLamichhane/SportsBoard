
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.http import HttpResponse
from django.contrib import messages
from .forms import CustomAuthenticationForm, CustomUserCreationForm,UserEditForm,ProfileForm
from django.contrib.auth.decorators import login_required
from allauth.socialaccount.providers.google.views import oauth2_login
from allauth.account.utils import complete_signup
from allauth.account.models import EmailAddress
from django.contrib.auth.models import Group
from django.conf import settings
from django.views.decorators.csrf import csrf_protect
from organizer.models import Event, TicketSale,PlayerSelectionForm
from accounts.models import Profile, Feedback
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.shortcuts import get_object_or_404


@csrf_protect
def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user= form.save() #
            # user = form.save(commit=False)
            role_selected = form.cleaned_data.get('role')
            profile, created = Profile.objects.get_or_create(user=user) #
            profile.role = role_selected
            profile.save()

            

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

    # 1. Tickets (Purchased via Khalti)
    user_apps = TicketSale.objects.filter(transaction__user=request.user).select_related(
        'transaction__ticket_type__event'
    )

    # 2. My Applications (Forms the user HAS filled out)
    # We want is_published=True because the form itself must be live,
    # but it must belong to the current user (applicant).
    # my_submissions = PlayerSelectionForm.objects.filter(
    #     applicant=request.user,
    #     is_published=True
    # )

    my_submissions = PlayerSelectionForm.objects.filter(
        applicant=request.user,
        is_published=False  # Submissions by athletes are False
    )


    # 3. Available Trials (Forms the user HAS NOT filled out yet)
    # Get IDs of forms the user already applied to so we can hide them
    applied_event_names = my_submissions.values_list('event_name', flat=True)

    available_forms = PlayerSelectionForm.objects.filter(
        is_published=True
    ).exclude(event_name__in=applied_event_names)

    context = {
        'user': request.user,
        'profile': profile,
        'total_joined': user_apps.count(),
        'user_apps': user_apps,
        'available_forms': available_forms,  # New trials
        'my_submissions': my_submissions,  # Completed apps
        'applied_count': my_submissions.count(),
        # new 2/19
        'pending_count': my_submissions.filter(status__iexact='Pending').count(), # Case-insensitive
        'shortlisted_count': my_submissions.filter(status__iexact='Approved').count(),
        'profile_strength': profile.get_profile_strength(),
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

@login_required
def edit_profile(request):
    if request.method == 'POST':
        # 1. Initialize forms with current instances
        form = UserEditForm(request.POST, request.FILES, instance=request.user)
        profile_form = ProfileForm(request.POST, request.FILES, instance=request.user.profile)

        if form.is_valid() and profile_form.is_valid():
            new_email = form.cleaned_data.get('email')
            old_email = request.user.email  # The email CURRENTLY in the database

            # 2. Save Profile first (Images, bio, etc.)
            profile_form.save()

            if new_email != old_email:
                # 3. CRITICAL: Save User info (Names) but DO NOT save the new email yet
                # We save everything EXCEPT the email field to the User model
                user = form.save(commit=False)
                user.email = old_email  # Force it back to the old one
                user.save() 

                # 4. Trigger Allauth to handle the new email in the background
                # This sends the link and keeps the new email 'unverified'
                EmailAddress.objects.add_email(
                    request, user, new_email, confirm=True
                )
                
                messages.warning(request, f"Profile updated! To change your email to {new_email}, please verify it via the link sent to your inbox.")
            else:
                # No email change? Just save the form as usual
                form.save()
                messages.success(request, "Profile updated successfully!")
                
            return redirect('accounts:edit_profile')
    else:   
        form = UserEditForm(instance=request.user)
        profile_form = ProfileForm(instance=request.user.profile)
    
    return render(request, 'accounts/edit_profile.html', {'form': form , 'profile_form': profile_form})
@login_required
def my_trials(request):
    query = request.GET.get('q')
    profile, created = Profile.objects.get_or_create(user=request.user)

    applications = PlayerSelectionForm.objects.filter(
        applicant=request.user,
        is_published=False
    )

    if query:
        applications = applications.filter(event_name__icontains=query)

    context = {
        'applications': applications,
        'query': query,
        'applied_count': applications.count(),
        'pending_count': applications.filter(status__iexact='Pending').count(),
        'shortlisted_count': applications.filter(status__iexact='Approved').count(),
        'profile_strength': profile.get_profile_strength(),
    }

    return render(request, 'accounts/my_trials.html', context)

def download_trial_pdf(request, pk):
    # Fetch the specific submission based on ID and current user
    sub = get_object_or_404(PlayerSelectionForm, pk=pk)
    
    template_path = 'accounts/trial_pdf_template.html'
    context = {
        'sub': sub,
        'event_exists': sub.event is not None
        }
    
    # Create a Django response object with PDF content type
    response = HttpResponse(content_type='application/pdf')
    # CHANGED: 'inline' opens it in the browser tab first
    response['Content-Disposition'] = f'inline; filename="Trial_Application_{pk}.pdf"'
    
    try:
        template = get_template(template_path)
        html = template.render(context)
        pisa_status = pisa.CreatePDF(html, dest=response)
        
        if pisa_status.err:
            return HttpResponse(f'PDF Error: {pisa_status.err}', status=500)
        return response
    except Exception as e:
        # This will show you the exact error in the browser instead of a 500
        return HttpResponse(f"System Error: {str(e)}", status=500)
    
def trial_detail_view(request, pk):
    # Fetch the specific application
    sub = get_object_or_404(PlayerSelectionForm, pk=pk,applicant=request.user)
    # Render a web page that looks like the PDF preview
    return render(request, 'accounts/trial_detail_preview.html', {
        'sub': sub,
        'active_tab': 'my_trials'
    })

@login_required
def available_trials_view(request):
    # 1. Fetch search query
    search_query = request.GET.get('search', '')
    total_published = PlayerSelectionForm.objects.filter(is_published=True)
    # 2. Get names of trials the user has already applied for (is_published=False)
    applied_event_names = PlayerSelectionForm.objects.filter(
        applicant=request.user,
        is_published=False
    ).values_list('event_name', flat=True)
    
    # 3. FIX: Use 'is_published=True' instead of 'is_active'
    # available_forms = PlayerSelectionForm.objects.filter(
    #     is_published=True
    # ).exclude(event_name__in=applied_event_names)
    available_forms = total_published.exclude(event_name__in=applied_event_names)
    
    # 4. Expired/Unavailable: Published trials that are now closed
    # We use .filter(is_published=False) excluding the user's own submissions
    expired_count = PlayerSelectionForm.objects.filter(is_published=False).exclude(applicant=request.user).count()
    # 4. Search logic
    if search_query:
        available_forms = available_forms.filter(event_name__icontains=search_query)

    # 5. Get submissions for sidebar count
    my_submissions = PlayerSelectionForm.objects.filter(
        applicant=request.user,
        is_published=False
    )

    context = {
        'available_forms': available_forms,
        'my_submissions': my_submissions,
        'search_query': search_query,
        'total_count': total_published.count(), # Returns '2' as seen in edit
        'available_count': available_forms.count(),
        'expired_count': expired_count,
    }
    
    return render(request, 'accounts/available_trial.html', context)
@login_required
def feedback_view(request):
    if request.method == 'POST':
        # Capture data from the merged form
        rating = request.POST.get('rating',0)
        subject = request.POST.get('subject')
        category = request.POST.get('category')
        message = request.POST.get('message')

        if not rating or not subject or not message:
            messages.error(request, "Please provide a rating, subject, and a detailed message.")
            # Return to the form with existing data so they don't lose progress
            return render(request, 'accounts/feedback.html', {
                'active_tab': 'feedback',
                'form_data': request.POST 
            })
        # Save to database
        Feedback.objects.create(
            user=request.user,
            # email=request.user.email,
            rating=rating,
            subject=subject,
            category=category,
            message=message
        )
        
        messages.success(request, "Feedback submitted successfully! We will get back to you soon.")
        return redirect('accounts:user_dashboard')
    
    return render(request, 'accounts/feedback.html', {'active_tab': 'feedback'})