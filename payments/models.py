from django.db import models
from organizer.models import TicketSale


class KhaltiTransaction(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Completed', 'Completed'),
        ('Refunded', 'Refunded'),
        ('Failed', 'Failed'),
    ]

    # Link to the specific Ticket Sale record
    ticket_sale = models.ForeignKey(TicketSale, on_delete=models.CASCADE, related_name='khalti_payments')

    # Khalti Identifiers
    pidx = models.CharField(max_length=255, unique=True, help_text="Unique identifier from Khalti")
    transaction_id = models.CharField(max_length=255, blank=True, null=True, help_text="Khalti's unique transaction ID")

    # Financial Data
    amount = models.DecimalField(max_digits=10, decimal_places=2, help_text="Amount in Paisa")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.ticket_sale.buyer.username} - {self.pidx} ({self.status})"