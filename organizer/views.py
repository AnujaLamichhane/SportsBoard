from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Sum, Count, Q
from django.shortcuts import render, redirect, get_object_or_404  # Ensure get_object_or_404 is imported
from .models import Event, Application, TicketSale, TicketType  # Ensure all models are imported
from .forms import EventCreationForm, TicketTypeFormset  # Ensure forms are imported
from .forms import EventCreationForm, TicketTypeFormset, MatchFormset  # Ensure forms are imported
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.conf import settings
from .models import PlayerSelectionForm
from .forms import PlayerSelectionCrispyForm
from django.core.mail import send_mail
import uuid
from django.db.models import Q  #


def is_organizer_check(user):
    # return user.is_staff
    return user.is_authenticated and user.groups.filter(name='Organizer').exists()


# --- Existing organizer_dashboard view (omitted for brevity, but it's fine) ---
@login_required(login_url='/accounts/login/')
@user_passes_test(is_organizer_check, login_url='/')
def organizer_dashboard(request):

    organizer_events = Event.objects.filter(organizer=request.user)
    # --- 1. Top Card Statistics (Aggregations) ---
    paid_sales = TicketSale.objects.filter(
        event__in=organizer_events,
        payment_status='PAID'
    )

    total_revenue = paid_sales.aggregate(Sum('price'))['price__sum'] or 0

    # NEW STATISTIC: Total Events
    total_events = organizer_events.count()

    # upcoming_count = organizer_events.filter(status='UPCOMING').count()

    upcoming_count = organizer_events.filter(status='UPCOMING').count()

    # Note: Ensure you have the 'Application' model imported
    # pending_applications = Application.objects.filter(
    #     event__in=organizer_events,
    #     status='PENDING'
    # ).count()

    # CORRECTED LOGIC: Pending Applications = Total Forms Filled (with PENDING status)
    pending_applications = Application.objects.filter(
        event__in=organizer_events,
        status='PENDING'  # Assuming 'PENDING' is the status for a newly filled form
    ).count()

    tickets_sold = TicketSale.objects.filter(
        event__in=organizer_events
    ).count()

    # --- 2. Recent Events and Sales ---
    # recent_events = organizer_events.order_by('-date_time')[:5]

    recent_events = organizer_events.prefetch_related('matches', 'ticket_tiers').order_by('-date_time')[:5]

    recent_sales = TicketSale.objects.filter(
        event__in=organizer_events
    ).order_by('-sale_date')[:5]

    recent_applications = Application.objects.filter(
        event__in=organizer_events
    ).order_by('-submitted_at')[:5]

    # --- 3. Chart Data (Tickets Sold by Event) ---
    sales_data_for_chart = paid_sales.values('event__name').annotate(
        sales_count=Count('id')
    )

    # 🚨 CONTEXT MUST BE DEFINED BEFORE BEING RETURNED 🚨
    context = {
        'total_revenue': total_revenue,
        'total_events': total_events,
        'upcoming_count': upcoming_count,
        'pending_applications': pending_applications,
        'tickets_sold': tickets_sold,
        'recent_events': recent_events,
        'recent_sales': recent_sales,
        'recent_applications': recent_applications,
        'sales_data_json': list(sales_data_for_chart),
    }
    return render(request, 'organizer/organizer_dashboard.html', context)



# @login_required
# @user_passes_test(is_organizer_check, login_url='/')
# def create_event(request):
#     form = EventCreationForm()
#     formset = TicketTypeFormset(instance=None)
#     match_formset = MatchFormset(instance=None)
#
#     if request.method == 'POST':
#         form = EventCreationForm(request.POST, request.FILES)
#
#         if form.is_valid():
#             event = form.save(commit=False)
#             event.organizer = request.user
#             event.save()
#
#             formset = TicketTypeFormset(request.POST, request.FILES, instance=event)
#             match_formset = MatchFormset(request.POST, request.FILES, instance=event)
#
#             # Check matches first
#             if match_formset.is_valid():
#                 match_formset.save()
#
#                 # Check tickets. If valid, save them.
#                 # If they are empty/invalid but matches are fine, we still treat it as a success (Free Event)
#                 if formset.is_valid():
#                     formset.save()
#
#                 # messages.success(request, "Tournament Created Successfully!")
#                 return redirect('organizer:dashboard')
#         else:
#             # Re-bind formsets to show errors if main form is invalid
#             formset = TicketTypeFormset(request.POST, request.FILES)
#             match_formset = MatchFormset(request.POST, request.FILES)
#
#     context = {
#         'form': form,
#         'formset': formset,
#         'match_formset': match_formset,
#         'page_title': 'Create New Event'
#     }
#     return render(request, 'organizer/event_create.html', context)

# def selection_form_create(request):
    # This page will contain logic to select an event and configure player fields
    # For now, it's a simple placeholder
    # context = {'page_title': 'Configure Player Selection Form'}
    # return render(request, 'organizer/selection_form_create.html', context)


@login_required
@user_passes_test(is_organizer_check, login_url='/')
def create_event(request):
    if request.method == 'POST':
        form = EventCreationForm(request.POST, request.FILES)
        # STEP A: Add prefix='tickets' and prefix='matches'
        formset = TicketTypeFormset(request.POST, request.FILES, prefix='tickets')
        match_formset = MatchFormset(request.POST, request.FILES, prefix='matches')

        if form.is_valid():
            event = form.save(commit=False)
            event.organizer = request.user
            event.save()

            # STEP B: Re-bind with instance and the SAME prefix
            match_formset = MatchFormset(request.POST, request.FILES, instance=event, prefix='matches')
            formset = TicketTypeFormset(request.POST, request.FILES, instance=event, prefix='tickets')

            # Validate matches now that they are linked to the event ID
            if match_formset.is_valid():
                match_formset.save()

                if formset.is_valid():
                    formset.save()

                messages.success(request, "Event created successfully!")
                return redirect('organizer:dashboard')
    else:
        form = EventCreationForm()
        # STEP C: Set prefixes for the empty forms on page load
        formset = TicketTypeFormset(prefix='tickets')
        match_formset = MatchFormset(prefix='matches')

    context = {
        'form': form,
        'formset': formset,
        'match_formset': match_formset,
        'page_title': 'Create New Event'
    }
    return render(request, 'organizer/event_create.html', context)





@login_required
@user_passes_test(is_organizer_check, login_url='/')
def event_edit(request, event_id):
    event = get_object_or_404(Event, pk=event_id, organizer=request.user)

    if request.method == 'POST':
        form = EventCreationForm(request.POST, request.FILES, instance=event)
        formset = TicketTypeFormset(request.POST, request.FILES, instance=event)
        match_formset = MatchFormset(request.POST, request.FILES, instance=event)

        if form.is_valid() and match_formset.is_valid():
            form.save()
            match_formset.save()

            if formset.is_valid():
                formset.save()

            messages.success(request, f"Event '{event.name}' updated successfully!")
            return redirect('organizer:event_detail', event_id=event.pk)
    else:
        form = EventCreationForm(instance=event)
        formset = TicketTypeFormset(instance=event)
        match_formset = MatchFormset(instance=event)

    context = {
        'form': form,
        'formset': formset,
        'match_formset': match_formset,  # Don't forget this!
        'page_title': f'Edit Event: {event.name}',
        'event': event
    }
    return render(request, 'organizer/event_create.html', context)


# --- NEW: Delete Event Function ---
@login_required
@user_passes_test(is_organizer_check, login_url='/')
def event_delete(request, event_id):
    # Ensure the event exists and belongs to the current organizer
    event = get_object_or_404(Event, pk=event_id, organizer=request.user)

    if request.method == 'POST':
        event_name = event.name
        event.delete()
        messages.success(request, f"Event '{event_name}' deleted successfully.")
        return redirect('organizer:dashboard')

    # For a GET request, we render a confirmation page (recommended for safety)
    return render(request, 'organizer/event_confirm_delete.html', {'event': event})
#
def all_events(request):
    # Get the search term from the URL (e.g., ?search=Rara)
    search_query = request.GET.get('search', '')
    
    if search_query:
        # Filter events where name OR location contains the search term
        events = Event.objects.filter(
            Q(name__icontains=search_query) | 
            Q(location__icontains=search_query)
        ).order_by('-date_time')
    else:
        # If no search, show everything
        events = Event.objects.all().order_by('-date_time')
        
    return render(request, 'organizer/all_events.html', {
        'events': events,
        'search_query': search_query # Pass it back to keep it in the input box
    })
#
def event_detail(request, event_id):
    """
    Handles both public viewing and secured organizer management access for an event.
    """
    
    # 1. PUBLIC ACCESS: Fetch the event details (no organizer check needed here)
    event = get_object_or_404(
        Event.objects.prefetch_related('ticket_tiers','matches'),
        pk=event_id
    )

    matches = event.matches.all().order_by('match_time')

    context = {
        'event': event,
        'page_title': event.name,
        'is_organizer': False, # Default flag for template logic
        'ticket_tiers': event.ticket_tiers.all(),
        # Other necessary public context
        'matches': matches,
    }

    # 2. ORGANIZER DASHBOARD LOGIC (Secured)
    # Check if the user is authenticated AND the current user is the event's organizer
    if request.user.is_authenticated and event.organizer == request.user:
        
        # Set flag to true to display management sections in the template
        context['is_organizer'] = True 
        
        # --- Calculate and add SECURE STATS to context ---
        
        applications = event.application_set.all()
        paid_sales = event.ticketsale_set.filter(payment_status='PAID') 

        # Financial & Sales Stats
        total_revenue_result = paid_sales.aggregate(total=Sum('price'))
        context['total_revenue'] = total_revenue_result['total'] if total_revenue_result['total'] else 0
        context['total_tickets_sold'] = paid_sales.count()
        
        total_capacity_result = event.ticket_tiers.aggregate(total_qty=Sum('available_quantity'))
        context['total_capacity'] = total_capacity_result['total_qty'] if total_capacity_result['total_qty'] else 0

        # Application Stats
        context['pending_applications_count'] = applications.filter(status='PENDING').count()
        context['total_applications_count'] = applications.count()
        
        context['recent_applications'] = applications.order_by('-submitted_at')[:5]
        context['recent_sales'] = paid_sales.order_by('-sale_date')[:5]

    return render(request, 'organizer/event_detail.html', context)

@login_required(login_url=settings.LOGIN_URL)
def start_booking_process(request, event_id):
    event = get_object_or_404(Event, pk=event_id)

    # Check if there are even tickets to book
    if not event.ticket_tiers.exists():
        messages.info(request, "This is a free event. No booking required!")
        return redirect('organizer:event_detail', event_id=event.id)

    if request.method == 'POST':
        tier_id = request.POST.get('ticket_tier')
        full_name = request.POST.get('full_name')

        # Get the specific ticket tier
        tier = get_object_or_404(TicketType, id=tier_id, event=event)

        # 1. Check Availability
        if tier.available_quantity > 0:
            # 2. Create the Sale
            sale = TicketSale.objects.create(
                event=event,
                buyer=request.user,
                ticket_type=tier,
                ticket_code=str(uuid.uuid4())[:8].upper(),
                price=tier.price,
                payment_status='PENDING'
            )

            # 3. Reduce Quantity
            tier.available_quantity -= 1
            tier.save()

            messages.success(request, "Booking initiated! Please present your ticket code at the venue.")
            return redirect('organizer:booking_success', sale_id=sale.id)
        else:
            messages.error(request, "Sorry, this ticket tier just sold out!")

    return render(request, 'organizer/booking_form.html', {'event': event})

# @login_required(login_url=settings.LOGIN_URL)
# def selection_form_create(request,pk=None):
#     form_instance = get_object_or_404(PlayerSelectionForm, pk=pk) if pk else None
#     is_player = request.user != form_instance.organizer if form_instance else False
#     if request.method == 'POST':
#         form = PlayerSelectionCrispyForm(
#             request.POST, 
#             request.FILES, 
#             instance=form_instance, 
#             is_player=is_player
#         )
#         if form.is_valid():
#             application = form.save(commit=False)
            
#             if not is_player:
#                 # Organizer path: Save configuration and publish
#                 application.organizer = request.user
#                 application.is_published = True
#                 application.save()
#                 messages.success(request, "Selection form configured and published!")
#                 return redirect('organizer:dashboard')
#             else:
#                 # Player path: Submit the mandatory fields
#                 application.pk = None 
#                 application.is_published = False
#                 application.status = 'pending'
#                 application.save()
#                 # Trigger Notification Logic Here
#                 messages.success(request, "Application submitted successfully!")
#                 return redirect('home')
#     else:
#         form = PlayerSelectionCrispyForm(instance=form_instance, is_player=is_player)
#     context = {
#         'form': form,
#         'is_player': is_player,
#         # 'page_title': 'Configure Player Selection Form'
#         'page_title': 'Apply for Trial' if is_player else 'Configure Form',
#     }

#     return render(request,'organizer/selection_form_create.html' ,context)



@login_required
def selection_form_create(request, pk=None):
    # 1. Fetch the template if pk exists
    form_instance = get_object_or_404(PlayerSelectionForm, pk=pk) if pk else None
    
    # 2. Logic: Is the current user an Organizer?
    is_org = is_organizer_check(request.user)
    is_player = not is_org # If not an organizer, they are a player/applicant

    if is_player and not pk:
        messages.error(request, "Please select a trial to apply.")
        return redirect('accounts:user_dashboard')

    # 3. Get the template (the form created by the organizer)
    # We use applicant__isnull=True to ensure we are grabbing a TEMPLATE, not someone's submission
    if pk:
        form_instance = get_object_or_404(PlayerSelectionForm, pk=pk)
    else:
        form_instance = None
    if request.method == 'POST':
        form = PlayerSelectionCrispyForm(
            request.POST, 
            request.FILES, 
            # instance=form_instance if is_org else None, # Players shouldn't overwrite the instance
            instance=None if is_player else form_instance,
            is_player=is_player
        )
        
        if form.is_valid():
            application = form.save(commit=False)
            
            if is_org:
                # Path: Organizer creating/editing the template
                application.organizer = request.user
                application.is_published = True
                application.save()
                messages.success(request, "Selection form configured and published!")
                return redirect('organizer:dashboard')
            else:
                # Path: Player submitting an application
                # We link this submission to the template (form_instance)
                application.pk = None # Force creation of a NEW record
                application.applicant = request.user
                application.parent_form = form_instance
                application.organizer = form_instance.organizer # The org who created it

                application.event_name = form_instance.event_name
                application.sports = form_instance.sports
                application.level = form_instance.level
                application.address = form_instance.address

                application.is_published = False # Responses stay private
                application.status = 'pending'
                application.save()
                
                messages.success(request, "Application submitted successfully!")
                return redirect('accounts:user_dashboard')
        else:
            print(form.errors)
    else:
        # GET Request: Pre-fill the form with template data for the player to see
        form = PlayerSelectionCrispyForm(instance=form_instance, is_player=is_player)

    context = {
        'form': form,
        'is_player': is_player,
        'page_title': 'Apply for Trial' if is_player else 'Configure Form',
    }
    
    return render(request, 
        'organizer/athlete_apply_form.html' if is_player else 'organizer/selection_form_create.html', 
        context
    )
    # Use the logic we built earlier to decide which layout to show
    # if is_player:
    #     return render(request, 'organizer/athlete_apply_form.html', context)
    # return render(request, 'organizer/selection_form_create.html', context)



# def send_status_email(application, status_type):
#     """Helper function to send emails based on status change."""
#     subject = f"Update on your Player Selection: {application.sports}"
    
#     messages_dict = {
#         "received": "We have received your application and it is currently pending review.",
#         "selected": "Congratulations! You have been SELECTED for the next round.",
#         "denied": "We regret to inform you that your application was not selected at this time."
#     }
    
#     message = f"Hello {application.full_name},\n\n{messages_dict.get(status_type)}\n\nBest regards,\nSportsBoard Team"
    
#     send_mail(
#         subject,
#         message,
#         settings.DEFAULT_FROM_EMAIL,
#         [application.email],
#         fail_silently=True,
#     )
# # def publish_event(request, event_id):
# #     event = get_object_or_404(PlayerSelectionForm, id=event_id, created_by=request.user)
# #     event.is_published = True
# #     event.save()
# #     messages.success(request, "Event is now live for users!")
# #     return redirect('organizer_dashboard')




@login_required
def booking_success(request, sale_id):
    # Ensure the user can only see their own ticket
    sale = get_object_or_404(TicketSale, id=sale_id, buyer=request.user)
    return render(request, 'organizer/booking_success.html', {'sale': sale})

#
@login_required
def published_forms(request):
    # Fetch forms that are published, ordered by newest first
    # Adjust 'is_published' to match your actual boolean field name
    forms = PlayerSelectionForm.objects.filter(is_published=True).order_by('-created_at')
    
    return render(request, 'organizer/published_form.html', {'forms': forms})
#
@login_required
def published_form_detail(request, pk):
    # Fetch the PlayerSelectionForm model
    form_data = get_object_or_404(PlayerSelectionForm, pk=pk, organizer=request.user)
    
    context = {
        'form_data': form_data,
        'page_title': 'Published Form Details'
    }
    return render(request, 'organizer/published_form_detail.html', context)