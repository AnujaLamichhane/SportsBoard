import requests
from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from django.contrib.auth.decorators import login_required
from organizer.models import TicketSale
from .models import KhaltiTransaction
from .utils import initiate_khalti_payment


@login_required
def init_payment(request, ticket_id):
    """
    Step 1: The 'Glue' view.
    Triggered when a user clicks 'Buy Ticket'.
    """
    # Get the ticket sale record created during checkout
    ticket = get_object_or_404(TicketSale, id=ticket_id, buyer=request.user)

    # Call the utility function that uses your Live Secret Key
    khalti_response = initiate_khalti_payment(ticket)

    if khalti_response.get('pidx'):
        # Create the transaction record as 'Pending'
        KhaltiTransaction.objects.create(
            ticket_sale=ticket,
            pidx=khalti_response['pidx'],
            amount=ticket.price * 100,  # Store in Paisa
            status='Pending'
        )
        # Redirect user to Khalti's payment gateway
        return redirect(khalti_response['payment_url'])

    else:
        # If Khalti fails to initialize (e.g., bad key or network)
        return render(request, 'payments/failed.html', {
            'error': 'Gateway error. Please try again later.'
        })


def payment_callback(request):
    """
    Step 2: Verification View.
    Khalti sends the user back here with a 'pidx'.
    """
    pidx = request.GET.get('pidx')

    # Server-to-Server Verification (Crucial Security)
    verify_url = "https://a.khalti.com/api/v2/epayment/lookup/"
    headers = {
        'Authorization': f'Key {settings.KHALTI_SECRET_KEY}',
        'Content-Type': 'application/json',
    }

    response = requests.post(verify_url, json={'pidx': pidx}, headers=headers)
    data = response.json()

    if data.get('status') == 'Completed':
        # Update Transaction record
        transaction = get_object_or_404(KhaltiTransaction, pidx=pidx)
        transaction.status = 'Completed'
        transaction.transaction_id = data.get('transaction_id')
        transaction.save()

        # Update TicketSale (This triggers your 'PAID' signal/QR logic)
        ticket = transaction.ticket_sale
        ticket.payment_status = 'PAID'
        ticket.save()

        return redirect('payment_success_page')

    return redirect('payment_failed_page')


def payment_success(request):
    """Simple feedback view for successful payment."""
    return render(request, 'payments/success.html')


def payment_failed(request):
    """Simple feedback view for canceled or failed payment."""
    return render(request, 'payments/failed.html')