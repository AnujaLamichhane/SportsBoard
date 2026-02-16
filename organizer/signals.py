import uuid
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import TicketSale


@receiver(post_save, sender=TicketSale)
def generate_ticket_ref(sender, instance, **kwargs):
    """Triggers only when payment_status changes to PAID."""
    if instance.payment_status == 'PAID' and not instance.ticket_code:
        # Generate a unique human-readable code
        ref = f"TIX-{uuid.uuid4().hex[:8].upper()}"

        # Use .update() to avoid re-triggering the post_save signal
        TicketSale.objects.filter(pk=instance.pk).update(ticket_code=ref)