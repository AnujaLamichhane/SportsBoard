
from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator
from datetime import date
from django.utils import timezone

User = get_user_model()

# --- CHOICES ---
EVENT_STATUS_CHOICES = [('LIVE', 'Live'), ('UPCOMING', 'Upcoming'), ('COMPLETED', 'Completed')]
APPLICATION_STATUS_CHOICES = [('PENDING', 'Pending'), ('APPROVED', 'Approved'), ('REJECTED', 'Rejected')]
PAYMENT_STATUS_CHOICES = [('INITIATED', 'Initiated'), ('PAID', 'Paid'), ('FAILED', 'Failed')]
GAME_TYPE_CHOICES = [
    ('MULTI', 'Sports Week 🏆'), ('FOOTBALL', 'Football ⚽'),
    ('BASKETBALL', 'Basketball 🏀'), ('BADMINTON', 'Badminton 🏸'),
    ('VOLLEYBALL', 'Volleyball 🏐'), ('CRICKET', 'Cricket 🏏'), ('OTHER', 'Others')
]
LEVEL_CHOICES = [('district', 'District'), ('province', 'Province'), ('national', 'National'), ('none', 'None')]
GENDER_CHOICES = [('male', 'Male'), ('female', 'Female'), ('other', 'Other')]
BLOOD_GROUP_CHOICES = [
    ('A+', 'A+'), ('A-', 'A-'), ('B+', 'B+'), ('B-', 'B-'),
    ('O+', 'O+'), ('O-', 'O-'), ('AB+', 'AB+'), ('AB-', 'AB-'),
]

EXPERIENCE_LEVEL_CHOICES = [
    ('beginner', 'Beginner (School/College)'),
    ('club', 'Club Level'),
    ('district', 'District Level'),
    ('provincial', 'Provincial Level'),
    ('national', 'National/Professional'),
]

# --- 1. CORE EVENT MODELS ---

class Event(models.Model):

    name = models.CharField(max_length=255)
    organizer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='organized_events')
    date_time = models.DateTimeField()
    location = models.CharField(max_length=255)
    description = models.TextField()
    status = models.CharField(max_length=10, choices=EVENT_STATUS_CHOICES, default='UPCOMING')
    game_type = models.CharField(max_length=20, choices=GAME_TYPE_CHOICES, default='FOOTBALL')
    game_type_other = models.CharField(max_length=100, blank=True, null=True)  # Add this line
    photo = models.ImageField(upload_to='event_photos/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    @property
    def is_past(self):
        """Returns True if the event date has already passed."""
        return self.date_time < timezone.now()

    def get_effective_status(self):
        """Returns COMPLETED if the date has passed, otherwise the database status."""
        if self.is_past:
            return 'COMPLETED'
        return self.status

    @property
    def has_paid_tickets(self):
        return self.ticket_tiers.exists()
        # return TicketType.objects.filter(match__event=self).exists()


class Match(models.Model):
    """Specific matches within a Sports Week or Tournament."""
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='matches')
    game_type = models.CharField(max_length=20, choices=GAME_TYPE_CHOICES, default='FOOTBALL')
    team_a = models.CharField(max_length=100, verbose_name="Team A / Player 1")
    team_b = models.CharField(max_length=100, verbose_name="Team B / Player 2")
    match_time = models.DateTimeField()
    venue = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"{self.team_a} vs {self.team_b} ({self.event.name})"


# --- 2. TICKETING & PAYMENTS (KHALTI READY) ---

class TicketType(models.Model):
    # Change 'match' to 'event'
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='ticket_tiers')
    name = models.CharField(max_length=50, help_text="e.g., VIP, Standard")
    price = models.DecimalField(max_digits=10, decimal_places=2)
    available_quantity = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.name} - {self.event.name}"

class KhaltiTransaction(models.Model):
    """Tracks the payment lifecycle before a ticket is issued."""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ticket_type = models.ForeignKey(TicketType, on_delete=models.CASCADE)
    pidx = models.CharField(max_length=255, unique=True, help_text="Khalti Payment ID")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='INITIATED')
    created_at = models.DateTimeField(auto_now_add=True)


class TicketSale(models.Model):
    """The final proof of purchase."""
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tickets')
    transaction = models.OneToOneField(KhaltiTransaction, on_delete=models.CASCADE, related_name='final_ticket')
    ticket_code = models.CharField(max_length=50, unique=True)
    is_used = models.BooleanField(default=False)  # For gate scanning
    bought_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Ticket {self.ticket_code} for {self.transaction.user.username}"


# --- 3. PLAYER SELECTION & APPLICATIONS ---

class PlayerSelectionForm(models.Model):
    """Template created by Organizers for Athletes to fill out."""
    organizer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='templates')
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='registration_forms', null=True, blank=True)
    applicant = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='submissions')

    # Event Info (Mirrored from Template)
    event_name = models.CharField(max_length=255, blank=True)
    sports = models.CharField(max_length=100, blank=True)
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES)
    address = models.CharField(max_length=255, blank=True, help_text="Event Venue Address")

    # Player Personal Info
    full_name = models.CharField(max_length=100, blank=True, null=True)
    dob = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True, null=True)

    # Address & Guardian Info (NEW - Required for your Form Layout)
    temporary_address = models.CharField(max_length=255, blank=True)
    permanent_address = models.CharField(max_length=255, blank=True)
    guardian_name = models.CharField(max_length=100, blank=True)
    guardian_relation = models.CharField(max_length=50, blank=True)
    guardian_phone = models.CharField(max_length=15, blank=True)

    blood_group = models.CharField(max_length=5, choices=BLOOD_GROUP_CHOICES, blank=True, null=True)
    experience_level = models.CharField(max_length=20, choices=EXPERIENCE_LEVEL_CHOICES, default='beginner')
    previous_experience_details = models.TextField(blank=True, help_text="List major tournaments or clubs")
    medical_conditions = models.BooleanField(default=False, help_text="Do you have any medical conditions?")
    medical_details = models.TextField(blank=True, help_text="If yes, please specify")

    # Identity Verification
    citizenship_number = models.CharField(max_length=50, blank=True, null=True)

    certificates = models.FileField(upload_to='documents/certs/', blank=True, null=True)
    citizenship = models.FileField(upload_to='documents/citizenship/', blank=True, null=True)



    # Status
    is_published = models.BooleanField(default=True)
    status = models.CharField(max_length=20, choices=APPLICATION_STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.event.name} - {self.full_name or 'Template'}"

    @property
    def age(self):
        if self.dob:
            today = date.today()
            return today.year - self.dob.year - ((today.month, today.day) < (self.dob.month, self.dob.day))
        return 0

