
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Sum,  Q
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.conf import settings
from django.template.loader import get_template
from django.urls import reverse
from django.db import transaction ,IntegrityError
from django.core.mail import send_mail
import uuid
import requests
import json
from decimal import Decimal
from django.utils import timezone
from xhtml2pdf import pisa

# Consolidated Model Imports (Removed 'Application')
from .models import Event, TicketSale, TicketType, PlayerSelectionForm ,KhaltiTransaction ,Match ,OrganizerProfile \
    ,OrganizerFeedback

# Consolidated Form Imports
from .forms import (
    EventCreationForm,
    TicketTypeFormset,
    MatchFormset,
    PlayerSelectionCrispyForm,
    OrganizerSettingsForm
)


def is_organizer_check(user):
    # return user.is_staff
    return user.is_authenticated and user.groups.filter(name='Organizer').exists()


@login_required(login_url='/accounts/login/')
@user_passes_test(is_organizer_check, login_url='/')
def organizer_dashboard(request):
    organizer_events = Event.objects.filter(organizer=request.user)
    now = timezone.now()

    # NEW: Fetch or create organizer profile for branding/settings
    profile, created = OrganizerProfile.objects.get_or_create(user=request.user)

    # Check for rejection status to trigger the alert
    is_rejected = profile.verification_status == 'rejected'
    # --- PROFILE COMPLETION LOGIC ---
    # Define fields that you consider "essential" for a complete profile
    essential_fields = [
        profile.organization_name,
        profile.organization_logo,
        profile.khalti_merchant_id,
        profile.contact_phone,
        profile.bio
    ]

    filled_count = sum(1 for field in essential_fields if field)
    completion_percentage = int((filled_count / len(essential_fields)) * 100)
    # --------------------------------


    paid_sales = TicketSale.objects.filter(
        transaction__ticket_type__event__in=organizer_events,  # Changed 'match__event' to 'event'
        transaction__status='PAID'
    ).select_related('transaction__ticket_type__event')

    total_revenue = paid_sales.aggregate(Sum('transaction__amount'))['transaction__amount__sum'] or 0

    pending_applications = PlayerSelectionForm.objects.filter(
        event__in=organizer_events,
        status='PENDING'
    ).count()

    sales_data = []  # Fetch your real data here
    sales_data_json = json.dumps(sales_data)
    # upcoming_count = organizer_events.filter(date_time__gt=timezone.now()).count()
    upcoming_count = organizer_events.filter(date_time__gt=now).count()
    context = {
        'profile': profile,
        'is_rejected': is_rejected,
        'completion_percentage': completion_percentage,  # Pass this to template
        'total_revenue': total_revenue,
        'total_revenue': total_revenue,
        'total_events': organizer_events.count(),
        'tickets_sold': paid_sales.count(),
        'recent_sales': paid_sales.order_by('-bought_at')[:5],  # Consolidated
        'recent_events': organizer_events.order_by('-date_time')[:5],
        'pending_applications': pending_applications,
        'sales_data_json': sales_data_json,
        'upcoming_count': upcoming_count
    }
    return render(request, 'organizer/organizer_dashboard.html', context)




@login_required
@user_passes_test(is_organizer_check, login_url='/')
def create_event(request):
    if request.method == 'POST':
        form = EventCreationForm(request.POST, request.FILES)
        match_formset = MatchFormset(request.POST, request.FILES, prefix='matches')
        ticket_formset = TicketTypeFormset(request.POST, request.FILES, prefix='tickets')

        if form.is_valid() and match_formset.is_valid():
            # 1. Save Event
            event = form.save(commit=False)
            event.organizer = request.user
            event.save()

            # 2. Save Matches
            matches = match_formset.save(commit=False)
            for match in matches:
                match.event = event
                match.save()

            # 3. Save Tickets (Directly linked to Event)
            # Only process if 'isFreeEvent' checkbox is NOT checked
            is_free = request.POST.get('isFreeEvent') == 'on'

            if not is_free and ticket_formset.is_valid():
                tickets = ticket_formset.save(commit=False)
                for ticket in tickets:
                    ticket.event = event  # Direct link to Event
                    ticket.save()

            messages.success(request, "Tournament Created Successfully!")
            return redirect('organizer:dashboard')
    else:
        form = EventCreationForm()
        match_formset = MatchFormset(prefix='matches')
        ticket_formset = TicketTypeFormset(prefix='tickets')

    return render(request, 'organizer/event_create.html', {
        'form': form,
        'match_formset': match_formset,
        'formset': ticket_formset,
        'page_title': 'Create New Event',
        # 'GOOGLE_MAPS_API_KEY': settings.GOOGLE_MAPS_API_KEY,

    })

@login_required
@user_passes_test(is_organizer_check, login_url='/')
def event_edit(request, event_id):
    # 1. Fetch the existing event
    event = get_object_or_404(Event, pk=event_id, organizer=request.user)

    if request.method == 'POST':
        # 2. Bind data to the instance
        form = EventCreationForm(request.POST, request.FILES, instance=event)

        # IMPORTANT: Pass instance=event to these formsets
        match_formset = MatchFormset(request.POST, request.FILES, instance=event, prefix='matches')
        ticket_formset = TicketTypeFormset(request.POST, request.FILES, instance=event, prefix='tickets')

        if form.is_valid() and match_formset.is_valid() and ticket_formset.is_valid():
            form.save()
            match_formset.save()
            ticket_formset.save()

            # messages.success(request, f"Event '{event.name}' updated successfully!")
            return redirect('organizer:event_detail', event_id=event.pk)
    else:
        # 3. For GET requests, load the existing data using instance=event
        form = EventCreationForm(instance=event)
        match_formset = MatchFormset(instance=event, prefix='matches')
        ticket_formset = TicketTypeFormset(instance=event, prefix='tickets')

    context = {
        'form': form,
        'match_formset': match_formset,
        'formset': ticket_formset,  # This is your ticket tier formset
        'event': event,
        'page_title': f'Edit Event: {event.name}'
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
        # messages.success(request, f"Event '{event_name}' deleted successfully.")
        return redirect('organizer:dashboard')

    # For a GET request, we render a confirmation page (recommended for safety)
    return render(request, 'organizer/event_confirm_delete.html', {'event': event})


def all_events(request):
    search_query = request.GET.get('search', '')
    now = timezone.now()

    # 1. Start with all events for this organizer
    base_events = Event.objects.filter(organizer=request.user)

    # 2. Apply search filter to the base queryset if a query exists
    if search_query:
        base_events = base_events.filter(
            Q(name__icontains=search_query) |
            Q(location__icontains=search_query)
        ).distinct()

    # 3. Split the ALREADY FILTERED base_events into two lists
    active_events = base_events.filter(date_time__gte=now).order_by('date_time')
    past_events = base_events.filter(date_time__lt=now).order_by('-date_time')

    # 4. Background maintenance: Update status in DB
    base_events.filter(date_time__lt=now).exclude(status='COMPLETED').update(status='COMPLETED')

    return render(request, 'organizer/all_events.html', {
        'active_events': active_events,
        'past_events': past_events,
        'events': base_events,  # This ensures {% for event in events %} still works
        'search_query': search_query,
        'now': now
    })


def event_detail(request, event_id):
    event = get_object_or_404(Event.objects.prefetch_related('matches' ,'ticket_tiers'), pk=event_id)
    matches = event.matches.all().order_by('match_time')

    context = {'event': event, 'matches': matches, 'is_organizer': False}

    if request.user.is_authenticated and event.organizer == request.user:
        context['is_organizer'] = True



        paid_sales = TicketSale.objects.filter(
            transaction__ticket_type__event=event,  # Remove 'match__'
            transaction__status='PAID'
        )

        total_revenue_result = paid_sales.aggregate(total=Sum('transaction__amount'))
        context['total_revenue'] = total_revenue_result['total'] or 0
        context['total_tickets_sold'] = paid_sales.count()

        # Use registration_forms related_name from your model
        applications = event.registration_forms.all()
        context['total_applications_count'] = applications.count()

    return render(request, 'organizer/event_detail.html', context)


@login_required(login_url=settings.LOGIN_URL)
def start_booking_process(request, event_id):
    event = get_object_or_404(Event, pk=event_id)

    # 1. Handle Free Event (No TicketTypes created by Organizer)
    if not event.ticket_tiers.exists():
        messages.info(request, "Registration for this free event is currently handled on-site.")
        return redirect('organizer:event_detail', event_id=event.id)

    if request.method == 'POST':
        tier_id = request.POST.get('ticket_tier')
        tier = get_object_or_404(TicketType, id=tier_id, event=event)

        if tier.price == 0:
            # Atomic check for free ticket capacity
            if tier.available_quantity > 0:
                with transaction.atomic():
                    # Create a placeholder transaction for the free ticket
                    free_txn = KhaltiTransaction.objects.create(
                        user=request.user,
                        ticket_type=tier,
                        pidx=f"FREE-{uuid.uuid4().hex[:10]}",
                        amount=0,
                        status='PAID'
                    )
                    sale = TicketSale.objects.create(
                        buyer=request.user,
                        transaction=free_txn,
                        ticket_code=f"FREE-{uuid.uuid4().hex[:8].upper()}"
                    )
                    tier.available_quantity -= 1
                    tier.save()
                return redirect('organizer:booking_success', sale_id=sale.id)
            else:
                messages.error(request, "No more free spots available!")
                return redirect('organizer:event_detail', event_id=event.id)

        # Proceed to paid logic
        return redirect('organizer:init_payment', tier_id=tier.id)



@login_required
def selection_form_create(request, pk=None):
    # 1. Get the template if applying, or instance if editing
    template_form = get_object_or_404(PlayerSelectionForm, pk=pk) if pk else None

    is_org = request.user.groups.filter(name='Organizer').exists()
    is_player = not is_org

    if is_player and template_form and template_form.deadline:
        if timezone.now() > template_form.deadline:
            messages.error(request, "Sorry, the registration deadline for this form has passed.")
            return redirect('accounts:user_dashboard')


    if request.method == 'POST':
        # Organizer edits existing template OR Athlete submits new data
        form = PlayerSelectionCrispyForm(
            request.POST,
            request.FILES,
            instance=template_form if is_org else None,
            is_player=is_player
        )

        if form.is_valid():
            application = form.save(commit=False)

            if is_org:
                # ORGANIZER SAVING/PUBLISHING
                application.organizer = request.user
                application.is_published = True  # CRITICAL: This makes it show up for players
                application.status = 'OPEN'
                application.save()
                messages.success(request, "Trial form has been published!")
                return redirect('organizer:dashboard')
            else:
                # PLAYER SUBMITTING
                # Check for double submission
                if PlayerSelectionForm.objects.filter(applicant=request.user, event_name=template_form.event_name,
                                                      is_published=False).exists():
                    messages.warning(request, "Application already submitted.")
                    return redirect('accounts:user_dashboard')

                application.applicant = request.user
                application.organizer = template_form.organizer
                # Link context from template

                if template_form.event:
                    application.event = template_form.event

                application.event_name = template_form.event_name
                application.sports = template_form.sports
                application.level = template_form.level
                application.is_published = False  # Athletes don't publish their private data
                application.status = 'PENDING'
                application.save()

                messages.success(request, "Application submitted successfully!")
                return redirect('accounts:user_dashboard')
        else:
            # Debugging: If form fails, show why in terminal
            print(form.errors)
            messages.error(request, "Please correct the errors below.")
    else:
        # GET request: Show empty form for Org, or template-filled form for Player
        form = PlayerSelectionCrispyForm(instance=template_form, is_player=is_player)

    return render(request,
                  'organizer/athlete_apply_form.html' if is_player else 'organizer/selection_form_create.html',
                  {'form': form, 'is_player': is_player})


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

@login_required
def published_form_detail(request, pk):
    # 1. Fetch the original template created by the organizer
    form_data = get_object_or_404(PlayerSelectionForm, pk=pk, organizer=request.user)

    # 2. Fetch the submissions (the actual athlete applications)
    # We filter by is_published=False (submissions) and match the event name
    submissions = PlayerSelectionForm.objects.filter(
        event_name=form_data.event_name,
        is_published=False
    ).select_related('applicant')

    context = {
        'form_data': form_data,
        'submissions': submissions,  # Add this to the context
        'page_title': 'Published Form Details'
    }
    return render(request, 'organizer/published_form_detail.html', context)




def init_payment(request, tier_id):
    tier = get_object_or_404(TicketType, id=tier_id)
    url = "https://a.khalti.com/api/v2/epayment/initiate/"

    # DYNAMIC: This ensures ngrok works for the callback
    return_url = request.build_absolute_uri(reverse('organizer:verify_payment'))
    amount_in_paisa = int(tier.price * Decimal('100'))  # Precise multiplication
    payload = json.dumps({
        "return_url": return_url,
        "website_url": request.build_absolute_uri('/'),
        "amount": amount_in_paisa,
        "purchase_order_id": str(uuid.uuid4())[:10],
        "purchase_order_name": f"Ticket: {tier.name}",
    })
    request.session['pending_tier_id'] = tier.id



    headers = {
        'Authorization': f'Key {settings.KHALTI_SECRET_KEY}',
        'Content-Type': 'application/json',
    }

    try:
        response = requests.post(url, headers=headers, data=payload)
        # Check if response is actually JSON before decoding
        if response.status_code == 200:
            resp_dict = response.json()
            from .models import KhaltiTransaction
            KhaltiTransaction.objects.create(
                user=request.user,
                ticket_type=tier,
                pidx=resp_dict['pidx'],
                amount=tier.price,
                status='INITIATED',
            )
            return redirect(resp_dict['payment_url'])
        else:
            print(f"Khalti API Error: {response.text}")  # Log the real error
            messages.error(request, f"Khalti Error: {response.status_code}. Check your API keys.")
    except Exception as e:
        print(f"Payment Request Exception: {e}")
        messages.error(request, "Could not connect to Khalti Payment Gateway.")

    return redirect('organizer:event_detail', event_id=tier.event.id)





def verify_payment(request):
    pidx = request.GET.get('pidx')

    # 1. Server-to-Server Verification
    url = "https://a.khalti.com/api/v2/epayment/lookup/"
    headers = {
        'Authorization': f'Key {settings.KHALTI_SECRET_KEY}',
        'Content-Type': 'application/json',
    }

    try:
        resp = requests.post(url, headers=headers, json={"pidx": pidx})
        data = resp.json()
    except Exception as e:
        messages.error(request, "Connection to Khalti failed. Please contact support.")
        return redirect('organizer:dashboard')

    # 2. Process Successful Payment
    if data.get('status') == 'Completed':
        try:
            with transaction.atomic():
                # Lock the record to prevent race conditions (double-tap/refresh)
                payment_record = get_object_or_404(
                    KhaltiTransaction.objects.select_for_update(),
                    pidx=pidx
                )

                # Check if this transaction was already processed
                if payment_record.status == 'PAID':
                    try:
                        # Attempt to find the existing ticket associated with this txn
                        sale = TicketSale.objects.get(transaction=payment_record)
                        return redirect('organizer:booking_success', sale_id=sale.id)
                    except TicketSale.DoesNotExist:
                        # Logic error fallback: Payment is PAID but no ticket exists?
                        # We proceed to create the ticket below.
                        pass

                # Update Payment Status
                payment_record.status = 'PAID'
                payment_record.save()

                # Atomic Inventory Check
                tier = payment_record.ticket_type
                if tier.available_quantity > 0:
                    tier.available_quantity -= 1
                    tier.save()
                else:
                    # Rare edge case: Sold out during the payment window
                    messages.error(
                        request,
                        "Payment successful, but tickets sold out. Please contact us for a refund."
                    )
                    return redirect('organizer:dashboard')

                # 3. Issue Ticket with Collision Protection
                # We use a loop to ensure that if a UUID hex collision occurs, we try again.
                sale = None
                max_retries = 5
                attempts = 0

                while not sale and attempts < max_retries:
                    try:
                        attempts += 1
                        ticket_code = f"SH-{uuid.uuid4().hex[:10].upper()}"
                        sale = TicketSale.objects.create(
                            transaction=payment_record,
                            buyer=payment_record.user,
                            ticket_code=ticket_code
                        )
                    except IntegrityError:
                        if attempts == max_retries:
                            raise  # Crash safely if we fail 5 times (mathematically impossible)
                        continue

            messages.success(request, "Payment Verified! Your ticket is ready.")
            return redirect('organizer:booking_success', sale_id=sale.id)

        except Exception as e:
            # General fallback for database or logic errors
            messages.error(request, "A system error occurred during ticket issuance. Please contact support.")
            return redirect('organizer:dashboard')

    # 4. Handle Failed/Canceled Payments
    messages.error(request, f"Payment failed or was canceled. (Status: {data.get('status')})")
    return redirect('organizer:dashboard')

@login_required
@user_passes_test(is_organizer_check, login_url='/')
def review_applications(request):
    """Lists all trial submissions for events owned by this organizer."""
    # We find forms where is_published=False (athlete submissions)
    # and the organizer matches the logged-in user.
    applications = PlayerSelectionForm.objects.filter(
        organizer=request.user,
        is_published=False
    ).order_by('-created_at')

    return render(request, 'organizer/review_applications.html', {
        'applications': applications,
        'page_title': 'Athlete Applications'
    })


@login_required
@user_passes_test(is_organizer_check, login_url='/')
def update_application_status(request, pk, action):
    application = get_object_or_404(PlayerSelectionForm, pk=pk, organizer=request.user)

    valid_statuses = ['APPROVED', 'REJECTED', 'PENDING']
    action_upper = action.upper()

    if action_upper in valid_statuses:
        application.status = action_upper
        application.save()

        # --- EMAIL LOGIC START ---
        if action_upper in ['APPROVED', 'REJECTED'] and application.email:
            subject = f"Update on your Application for {application.event_name}"

            if action_upper == 'APPROVED':
                message = f"Congratulations {application.full_name}!\n\nYour application for {application.event_name} has been APPROVED. Please check the dashboard for further instructions."
            else:
                message = f"Hello {application.full_name},\n\nWe regret to inform you that your application for {application.event_name} was not selected at this time."

            try:
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [application.email],
                    fail_silently=False,
                )
            except Exception as e:
                messages.warning(request, "Status updated, but email failed to send. Check your SMTP settings.")
        # --- EMAIL LOGIC END ---

        messages.success(request, f"Application for {application.full_name} is now {application.status}.")
    else:
        messages.error(request, "Invalid status update.")

    return redirect('organizer:review_applications')



@login_required
@user_passes_test(is_organizer_check)
def verify_ticket_gate(request):
    ticket_code = request.GET.get('ticket_code')
    ticket = None
    error = None

    # 1. ALWAYS calculate the headcount and history (outside the IF block)
    # This ensures the numbers show up as soon as you open the page
    total_checked_in = TicketSale.objects.filter(
        transaction__ticket_type__event__organizer=request.user,
        is_used=True
    ).count()

    # recent_checkins = TicketSale.objects.filter(
    #     transaction__ticket_type__event__organizer=request.user,
    #     is_used=True
    # ).order_by('-id')[:5]  # Get last 5 successful entries

    if ticket_code:
        try:
            # 2. Search for the ticket
            ticket = TicketSale.objects.get(
                ticket_code__iexact=ticket_code.strip(),
                transaction__ticket_type__event__organizer=request.user
            )

            # 3. Handle the "Grant Entry" button click
            if request.method == "POST" and not ticket.is_used:
                ticket.is_used = True
                ticket.checked_in_at = timezone.now()
                ticket.save()
                messages.success(request, f"Entry Granted for {ticket.buyer.username}!")
                # Refresh the count/history after a successful check-in
                return redirect(f"{request.path}?ticket_code={ticket_code}")

        except TicketSale.DoesNotExist:
            # THIS triggers your error box for random/fake codes
            error = "Invalid Ticket Code. Access Denied."

    return render(request, 'organizer/verify_ticket.html', {
        'ticket': ticket,
        'error': error,
        'total_checked_in': total_checked_in,
        # 'recent_checkins': recent_checkins,
        'ticket_code': ticket_code
    })






@login_required
@user_passes_test(is_organizer_check)
def form_preview(request, pk):
    # Fetch the template the organizer created
    template_form = get_object_or_404(PlayerSelectionForm, pk=pk, organizer=request.user)

    # Initialize form in preview mode
    form = PlayerSelectionCrispyForm(instance=template_form, is_player=True, preview_mode=True)

    return render(request, 'organizer/athlete_apply_form.html', {
        'form': form,
        'is_player': False,
        'is_preview': True,
        'page_title': f"Preview: {template_form.event_name}"
    })


@login_required
@user_passes_test(is_organizer_check, login_url='/')
def review_athlete_profile(request, pk):
    # Ensure the application exists and belongs to this organizer
    application = get_object_or_404(PlayerSelectionForm, pk=pk, organizer=request.user, is_published=False)

    context = {
        'application': application,
        'page_title': f"Review: {application.full_name or application.applicant.username}"
    }
    return render(request, 'organizer/review_athlete_profile.html', context)


@login_required
@user_passes_test(is_organizer_check)
def organizer_settings(request):
    # Get the profile or create one
    profile, created = OrganizerProfile.objects.get_or_create(user=request.user)

    # 1. Define fields for completion calculation
    essential_fields_list = [
        profile.organization_name,
        profile.organization_logo,
        profile.contact_email,
        profile.contact_phone,
        profile.address,
        profile.bio,
        profile.certificate
    ]
    completed = len([f for f in essential_fields_list if f])
    completion_percentage = int((completed / len(essential_fields_list)) * 100)

    if request.method == 'POST':
        form = OrganizerSettingsForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            # Save the profile data first
            profile = form.save()

            # --- RE-APPLICATION LOGIC START ---
            # If the user is on the final tab and clicks "Save",
            # we check if they are eligible to move from 'rejected' or 'none' to 'pending'
            current_tab = request.GET.get('tab')
            if current_tab == 'submit-request-tab':
                # Re-verify all required fields including Khalti ID which is on this tab
                verification_check_fields = [
                    profile.organization_name, profile.organization_logo,
                    profile.contact_phone, profile.contact_email,
                    profile.address, profile.certificate,
                    profile.khalti_merchant_id, profile.bio
                ]

                if all(verification_check_fields):
                    # Reset status to pending so Admin can see it again
                    profile.verification_status = 'pending'
                    profile.save()
                    messages.success(request, "Application re-submitted for verification!")
                    return redirect('organizer:dashboard')
                else:
                    messages.warning(request,
                                     "Settings saved, but some required fields are still missing for verification.")
            else:
                messages.success(request, "Settings updated successfully!")
            # --- RE-APPLICATION LOGIC END ---

            # Redirect specifically to the SUBMIT tab after saving
            base_url = reverse('organizer:settings')
            return redirect(f"{base_url}?tab=submit-request-tab")
    else:
        form = OrganizerSettingsForm(instance=profile)

    return render(request, 'organizer/settings.html', {
        'form': form,
        'profile': profile,
        'completion_percentage': completion_percentage,
        'page_title': 'Account & Organizer Settings'
    })




# @login_required
# @user_passes_test(is_organizer_check)
# def organizer_settings(request):
#     # Get the profile or create one
#     profile, created = OrganizerProfile.objects.get_or_create(user=request.user)
#
#     # 1. Define fields for completion calculation
#     essential_fields = [
#         profile.organization_name,
#         profile.organization_logo,
#         profile.contact_email,
#         profile.contact_phone,
#         profile.address,
#         profile.bio,
#         profile.certificate
#     ]
#     completed = len([f for f in essential_fields if f])
#     completion_percentage = int((completed / len(essential_fields)) * 100)
#
#     if request.method == 'POST':
#         form = OrganizerSettingsForm(request.POST, request.FILES, instance=profile)
#         if form.is_valid():
#             form.save()
#             messages.success(request, "Settings updated successfully!")
#
#             # 2. Redirect specifically to the SUBMIT tab after saving
#             # This ensures that after 'Save & Continue', the user sees the Submit button
#             base_url = reverse('organizer:settings')
#             return redirect(f"{base_url}?tab=submit-request-tab")
#     else:
#         form = OrganizerSettingsForm(instance=profile)
#
#     return render(request, 'organizer/settings.html', {
#         'form': form,
#         'profile': profile,
#         'completion_percentage': completion_percentage,
#         'page_title': 'Account & Organizer Settings'
#     })




@login_required
@user_passes_test(is_organizer_check)
def help_feedback(request):
    if request.method == 'POST':
        subject = request.POST.get('subject')
        f_type = request.POST.get('feedback_type')
        message = request.POST.get('message')

        OrganizerFeedback.objects.create(
            organizer=request.user,
            subject=subject,
            feedback_type=f_type,
            message=message
        )
        messages.success(request, "Your feedback has been submitted! We will get back to you soon.")
        return redirect('organizer:dashboard')

    return render(request, 'organizer/help_feedback.html')


@login_required
@user_passes_test(is_organizer_check)
def submit_verification(request):
    profile = get_object_or_404(OrganizerProfile, user=request.user)
    # If they were rejected, allow them to reset to 'none' to try again
    if profile.verification_status == 'rejected' and request.GET.get('action') == 'reset':
        profile.verification_status = 'none'
        profile.save()
        messages.info(request, "Profile status reset. You can now update your details.")
        return redirect('organizer:settings')
    # Check if 100% complete before allowing submission
    essential_fields = [
        profile.organization_name, profile.organization_logo,
        profile.contact_phone,
        profile.contact_email,
        profile.address,
        profile.certificate,

        profile.khalti_merchant_id, profile.bio
    ]

    if all(essential_fields):
        profile.verification_status = 'pending'
        profile.save()
        messages.success(request, "Verification request sent to Admin!")
    else:
        messages.error(request, "Please fill all details before submitting.")

    return redirect('organizer:settings')
from django.utils import timezone # Add this import

def athlete_pdf_view(request, pk):
    application = get_object_or_404(PlayerSelectionForm, pk=pk)
    template_path = 'organizer/athlete_detail_pdf.html'

    # Add 'today' to the context
    context = {
        'application': application,
        'today': timezone.now()
    }

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="athlete_{application.full_name}.pdf"'

    template = get_template(template_path)
    html = template.render(context)

    # Note: If you want to show the Profile Photo in the PDF,
    # you MUST use the link_callback we discussed earlier.
    pisa_status = pisa.CreatePDF(html, dest=response)

    if pisa_status.err:
       return HttpResponse('Error generating PDF')
    return response