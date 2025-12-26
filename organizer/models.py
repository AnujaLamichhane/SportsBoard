

# Create your models here.
from django.db import models
from django.contrib.auth import get_user_model


User = get_user_model()

# Define choices for status fields
EVENT_STATUS_CHOICES = [
    ('LIVE', 'Live'),
    ('UPCOMING', 'Upcoming'),
    ('COMPLETED', 'Completed'),
]

APPLICATION_STATUS_CHOICES = [
    ('PENDING', 'Pending'),
    ('APPROVED', 'Approved'),
    ('REJECTED', 'Rejected'),
]

PAYMENT_STATUS_CHOICES = [
    ('PAID', 'Paid'),
    ('PENDING', 'Pending'),
    ('FAILED', 'Failed'),
]

GAME_TYPE_CHOICES = [
    ('MULTI', 'Multi-Sport / Sports Week 🏆'),
    ('FOOTBALL', 'Football ⚽'),
    ('BASKETBALL', 'Basketball 🏀'),
    ('BADMINTON', 'Badminton 🏸'),
    ('VOLLEYBALL', 'Volleyball 🏐'),
    ('KABADDI', 'Kabaddi'),
    ('CRICKET', 'Cricket 🏏'),
    ('FUTSAL', 'Futsal'),
    ('OTHER', 'Others'),
]

class Event(models.Model):
    name = models.CharField(max_length=255)
    organizer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='organized_events')
    date_time = models.DateTimeField()
    location = models.CharField(max_length=255)
    description = models.TextField()
    status = models.CharField(max_length=10, choices=EVENT_STATUS_CHOICES, default='UPCOMING')

    # 🚨 ADD NEW FIELDS 🚨
    game_type = models.CharField(max_length=20, choices=GAME_TYPE_CHOICES, default='FOOTBALL')
    game_type_other = models.CharField(max_length=100, blank=True, null=True, verbose_name="Specify Other Game")
    photo = models.ImageField(upload_to='event_photos/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return self.name


class TicketType(models.Model):
    """Stores different ticket tiers (e.g., VIP, Standard) for an Event."""
    event = models.ForeignKey(
        'Event',
        on_delete=models.CASCADE,
        related_name='ticket_tiers'
    )
    name = models.CharField(max_length=50, help_text="e.g., VIP, Standard, Student")
    price = models.DecimalField(max_digits=10, decimal_places=2)
    available_quantity = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.name} - {self.event.name}"


class Application(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    applicant_name = models.CharField(max_length=100)  # Could be a ForeignKey to User if applicants log in
    status = models.CharField(max_length=10, choices=APPLICATION_STATUS_CHOICES, default='PENDING')
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"App for {self.event.name} by {self.applicant_name}"


class TicketSale(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tickets')
    ticket_type = models.ForeignKey(TicketType, on_delete=models.SET_NULL, null=True)

    ticket_code = models.CharField(max_length=50, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    sale_date = models.DateTimeField(auto_now_add=True)
    payment_status = models.CharField(max_length=10, choices=PAYMENT_STATUS_CHOICES, default='PAID')

    def __str__(self):
        return f"Sale {self.ticket_code} - {self.event.name}"


# Add this below your Event model
class Match(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='matches')
    game_type = models.CharField(max_length=20, choices=GAME_TYPE_CHOICES)
    team_a = models.CharField(max_length=100, verbose_name="Team A / Player 1")
    team_b = models.CharField(max_length=100, verbose_name="Team B / Player 2")
    match_time = models.DateTimeField()
    venue = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"{self.team_a} vs {self.team_b} ({self.game_type})"