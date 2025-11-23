# #
# # from django.shortcuts import render, redirect
# # from django.contrib.auth import authenticate, login
# # from django.contrib import messages
# # from .forms import CustomAuthenticationForm, CustomUserCreationForm
# # from django.contrib.auth.decorators import login_required
from allauth.socialaccount.providers.google.views import oauth2_login
# #
# #
# # def login_view(request):
# #     if request.method == 'POST':
# #         form = CustomAuthenticationForm(request, data=request.POST)
# #         if form.is_valid():
# #             username = form.cleaned_data.get('username')
# #             password = form.cleaned_data.get('password')
# #             role = form.cleaned_data.get('role')
# #             remember_me = form.cleaned_data.get('remember_me')  # ✅ get the checkbox value
# #             user = authenticate(username=username, password=password)
# #             if user is not None:
# #                 login(request, user)
# #                 if remember_me:
# #                     request.session.set_expiry(1209600)  # 2 weeks
# #                 else:
# #                     request.session.set_expiry(0)  # expires on browser close
# #
# #                 if role == 'organizer':
# #                     return redirect('organizer_dashboard')
# #                 return redirect('user_dashboard')
# #             else:
# #                 messages.error(request, "Invalid username or password.")
# #     else:
# #         form = CustomAuthenticationForm()
# #     return render(request, 'accounts/login.html', {'form': form})
# #
# # def register_view(request):
# #     if request.method == 'POST':
# #         form = CustomUserCreationForm(request.POST)
# #         if form.is_valid():
# #             user = form.save(commit=False)
# #             user.role = form.cleaned_data.get('role')
# #             user.save()
# #             messages.success(request, "Account created successfully! Please login.")
# #             return redirect('login')
# #     else:
# #         form = CustomUserCreationForm()
# #     return render(request, 'accounts/signup.html', {'form': form})
# #
# #

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from .forms import CustomAuthenticationForm, CustomUserCreationForm
from django.contrib.auth.decorators import login_required

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
            role = form.cleaned_data.get('role')
            remember_me = form.cleaned_data.get('remember_me')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                if remember_me:
                    request.session.set_expiry(1209600)
                else:
                    request.session.set_expiry(0)
                if role == 'organizer':
                    return redirect('organizer_dashboard')
                return redirect('user_dashboard')
            else:
                messages.error(request, "Invalid username or password.")
    else:
        form = CustomAuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form})

@login_required
def user_dashboard(request):
    return render(request, 'accounts/user_dashboard.html')


@login_required
def organizer_dashboard(request):
    return render(request, 'accounts/organizer_dashboard.html')


def custom_google_login(request):
    role = request.GET.get('role')
    if role not in ['user', 'organizer']:
        messages.error(request, "Please choose a valid role before signing in.")
        return redirect('login')
    request.session['login_role'] = role
    return oauth2_login(request)

# from django.shortcuts import render, redirect, get_object_or_404
# from django.contrib import messages
# from django.contrib.auth.decorators import login_required, user_passes_test
# from django.db import transaction
# from .models import Event, SelectionForm, FormField
# from .forms import EventCreationForm, TicketTypeFormset, FormFieldFormset
#
#
# # --- Helper function for role checking ---
# def is_organizer(user):
#     return user.is_authenticated and user.role == 'organizer'
#
#
# # --- Existing Organizer Dashboard (Assuming this is defined elsewhere, but good to include context) ---
# @login_required
# @user_passes_test(is_organizer)
# def organizer_dashboard(request):
#     # Example dashboard view logic
#     events = Event.objects.filter(organizer=request.user).order_by('-date_time')
#     context = {'events': events}
#     return render(request, 'organizer/organizer_dashboard.html', context)
#
#
# # --- Existing Event Creation View (Example structure) ---
# @login_required
# @user_passes_test(is_organizer)
# def create_event(request):
#     if request.method == 'POST':
#         form = EventCreationForm(request.POST, request.FILES)
#         if form.is_valid():
#             event = form.save(commit=False)
#             event.organizer = request.user
#             event.save()
#             messages.success(request, f"Event '{event.name}' created successfully!")
#             return redirect('event_details', event_id=event.pk)
#     else:
#         form = EventCreationForm()
#     return render(request, 'organizer/create_event.html', {'form': form})
#
#
# # ----------------------------------------------------------------------
# # NEW VIEW: Dynamic Form Builder
# # ----------------------------------------------------------------------
#
# @login_required
# @user_passes_test(is_organizer)
# def dynamic_form_builder(request, event_id):
#     """
#     Allows the organizer to define the custom application fields for an event.
#     """
#     event = get_object_or_404(Event, pk=event_id, organizer=request.user)
#
#     # Try to get the existing SelectionForm or create a new one if it doesn't exist
#     try:
#         selection_form_instance = event.selection_form
#     except SelectionForm.DoesNotExist:
#         # Create a new SelectionForm linked to the event
#         selection_form_instance = SelectionForm.objects.create(event=event)
#
#     if request.method == 'POST':
#         # Create the formset instance bound to the request data
#         formset = FormFieldFormset(request.POST, request.FILES, instance=selection_form_instance)
#
#         if formset.is_valid():
#             try:
#                 # Use a transaction to ensure all database operations succeed or fail together
#                 with transaction.atomic():
#                     # Save the formset data, which creates/updates/deletes FormField objects
#                     formset.save()
#
#                     # Ensure fields have a sequential 'order' after saving
#                     # This is important for rendering the form correctly later
#                     fields = selection_form_instance.fields.all().order_by('order')
#                     for index, field in enumerate(fields):
#                         if field.order != index:
#                             field.order = index
#                             field.save(update_fields=['order'])
#
#                 messages.success(request, f"Application form fields for '{event.name}' updated successfully.")
#                 return redirect('event_details', event_id=event.pk)
#
#             except Exception as e:
#                 messages.error(request, f"An error occurred while saving the form fields: {e}")
#         else:
#             messages.error(request, "Please correct the errors below.")
#
#     else:
#         # GET request: Load the formset with existing data (or empty forms if new)
#         formset = FormFieldFormset(instance=selection_form_instance)
#
#     context = {
#         'event': event,
#         'formset': formset,
#         'form_title': f"Configure Application Form for: {event.name}",
#     }
#     return render(request, 'organizer/dynamic_form_builder.html', context)