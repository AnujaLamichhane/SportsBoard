import requests
import json
from django.conf import settings


def initiate_khalti_payment(ticket_sale):
    """Sends payment request to Khalti and returns the redirect URL."""
    url = "https://a.khalti.com/api/v2/epayment/initiate/"

    # Khalti standard: amount must be in Paisa (Integer)
    amount_in_paisa = int(ticket_sale.price * 100)

    payload = {
        "return_url": "http://127.0.0.1:8000/payments/callback/",  # Update in production
        "website_url": "http://127.0.0.1:8000/",
        "amount": amount_in_paisa,
        "purchase_order_id": str(ticket_sale.id),
        "purchase_order_name": f"Ticket for {ticket_sale.event.name}",
    }

    headers = {
        'Authorization': f'Key {settings.KHALTI_SECRET_KEY}',
        'Content-Type': 'application/json',
    }

    response = requests.post(url, json=payload, headers=headers)
    return response.json()