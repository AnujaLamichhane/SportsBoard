

# Create your models here.
from django.db import models
from django.contrib.auth import get_user_model
from datetime import date
from django.contrib.auth.models import User


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


# from django.db import models
# from django.contrib.auth import get_user_model
# from django.utils import timezone  # Add this import if you need it later, though not strictly used below
#
# User = get_user_model()
#
# # Define choices for status fields
# EVENT_STATUS_CHOICES = [
#     ('LIVE', 'Live'),
#     ('UPCOMING', 'Upcoming'),
#     ('COMPLETED', 'Completed'),
# ]
#
# APPLICATION_STATUS_CHOICES = [
#     ('PENDING', 'Pending'),
#     ('APPROVED', 'Approved'),
#     ('REJECTED', 'Rejected'),
# ]
#
# PAYMENT_STATUS_CHOICES = [
#     ('PAID', 'Paid'),
#     ('PENDING', 'Pending'),
#     ('FAILED', 'Failed'),
# ]
#
# GAME_TYPE_CHOICES = [
#     ('FOOTBALL', 'Football ⚽'),
#     ('BASKETBALL', 'Basketball 🏀'),
#     ('BADMINTON', 'Badminton 🏸'),
#     ('VOLLEYBALL', 'Volleyball 🏐'),
#     ('KABADDI', 'Kabaddi'),
#     ('CRICKET', 'Cricket 🏏'),
#     ('FUTSAL', 'Futsal'),
#     ('OTHER', 'Others'),
# ]
#
#
# class Event(models.Model):
#     name = models.CharField(max_length=255)
#     organizer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='organized_events')
#     date_time = models.DateTimeField()
#     location = models.CharField(max_length=255)
#     description = models.TextField()
#     status = models.CharField(max_length=10, choices=EVENT_STATUS_CHOICES, default='UPCOMING')
#
#     # Existing fields:
#     game_type = models.CharField(max_length=20, choices=GAME_TYPE_CHOICES, default='FOOTBALL')
#     game_type_other = models.CharField(max_length=100, blank=True, null=True, verbose_name="Specify Other Game")
#     photo = models.ImageField(upload_to='event_photos/', blank=True, null=True)
#
#     def __str__(self):
#         return self.name
#
#
# class TicketType(models.Model):
#     """Stores different ticket tiers (e.g., VIP, Standard) for an Event."""
#     event = models.ForeignKey(
#         'Event',
#         on_delete=models.CASCADE,
#         related_name='ticket_tiers'
#     )
#     name = models.CharField(max_length=50, help_text="e.g., VIP, Standard, Student")
#     price = models.DecimalField(max_digits=10, decimal_places=2)
#     available_quantity = models.IntegerField(default=0)
#
#     def __str__(self):
#         return f"{self.name} - {self.event.name}"
#
#
# # --- NEW MODEL: Links form structure to an Event ---
# class SelectionForm(models.Model):
#     """Represents the custom player application form structure attached to an Event."""
#     event = models.OneToOneField(
#         'Event',
#         on_delete=models.CASCADE,
#         related_name='selection_form',
#         help_text="The event this player selection form is for."
#     )
#     is_active = models.BooleanField(default=True)
#
#     def __str__(self):
#         return f"Form for {self.event.name}"
#
#     class Meta:
#         verbose_name = "Selection Form"
#         verbose_name_plural = "Selection Forms"
#
#
# # --- NEW MODEL: Defines the individual fields/questions ---
# class FormField(models.Model):
#     """Represents an individual field defined by the organizer."""
#     FIELD_TYPE_CHOICES = [
#         ('TEXT', 'Text Input (Short Answer)'),
#         ('TEXTAREA', 'Text Area (Long Answer)'),
#         ('NUMBER', 'Number Input'),
#         ('CHOICE', 'Dropdown / Select (Must specify options)'),
#         ('CHECKBOX', 'Checkbox (Yes/No)'),
#     ]
#
#     form = models.ForeignKey(SelectionForm, on_delete=models.CASCADE, related_name='fields')
#     label = models.CharField(max_length=255)
#     field_type = models.CharField(max_length=10, choices=FIELD_TYPE_CHOICES)
#     is_required = models.BooleanField(default=True)
#     # Stored as comma-separated values (e.g., "S,M,L,XL")
#     options = models.TextField(
#         blank=True,
#         null=True,
#         help_text="Comma-separated options for Choice fields (e.g., Option 1, Option 2)"
#     )
#     order = models.IntegerField(default=0)
#
#     def __str__(self):
#         return f"{self.label} ({self.field_type})"
#
#     class Meta:
#         ordering = ['order']
#         verbose_name = "Form Field"
#         verbose_name_plural = "Form Fields"
#
#
# # --- MODIFIED MODEL: Application ---
# class Application(models.Model):
#     event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='applications')  # Added related_name
#
#     # CRITICAL CHANGE 1: Switched from CharField(applicant_name) to ForeignKey(user)
#     user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='applications')
#
#     # CRITICAL CHANGE 2: Added the JSON field to store dynamic answers
#     dynamic_responses = models.JSONField(
#         default=dict,
#         help_text="Stores answers to custom form fields as JSON."
#     )
#
#     status = models.CharField(max_length=10, choices=APPLICATION_STATUS_CHOICES, default='PENDING')
#     submitted_at = models.DateTimeField(auto_now_add=True)
#
#     def __str__(self):
#         return f"App for {self.event.name} by {self.user.username}"
#
#     class Meta:
#         # CRITICAL CHANGE 3: Ensures a user can only apply once per event
#         unique_together = ('event', 'user')
#
#
# class TicketSale(models.Model):
#     event = models.ForeignKey(Event, on_delete=models.CASCADE)
#     ticket_code = models.CharField(max_length=50, unique=True)
#     price = models.DecimalField(max_digits=10, decimal_places=2)
#     sale_date = models.DateTimeField(auto_now_add=True)
#     payment_status = models.CharField(max_length=10, choices=PAYMENT_STATUS_CHOICES, default='PAID')
#
#     def __str__(self):
#         return f"Sale {self.ticket_code} - {self.event.name}"



LEVEL_CHOICES = [
    ('district', 'District Level'),
    ('province', 'Province Level'),
    ('national', 'National Level'),
    ('none', 'None'),
]

CATEGORY_CHOICES = [
    ('male', 'Male'),
    ('female', 'Female'),
]

SPORT_CHOICES = [
    ('cricket', 'Cricket'),
    ('football', 'Football'),
    ('volleyball', 'Volleyball'),
    ('basketball', 'Basketball'),
    ('badminton', 'Badminton'),
    ('other', 'Other'),
]
GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ]


class PlayerSelectionForm(models.Model):
    # Organizer-controlled (LOCKED)
    organizer = models.ForeignKey(User, on_delete=models.CASCADE)

    # New fields for publishing logic
    is_published = models.BooleanField(default=True)
    # created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='organized_events')
    # created_at = models.DateTimeField(auto_now_add=True)

    # Selection Details (Filled by Organizer)
    event_name = models.CharField(max_length=50)
    sports = models.CharField(max_length=30)
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES)
    address = models.CharField(max_length=150)

    # Player info
    full_name = models.CharField(max_length=100,blank=True, null=True)
    dob = models.DateField(blank=True, null=True)
    age = models.CharField(max_length=2,blank=True, null=True)
    gender = models.CharField(max_length=10,choices=GENDER_CHOICES,blank=True, null=True)

    phone = models.CharField(max_length=10,blank=True, null=True)  # Nepal only
    email = models.EmailField(blank=True, null=True)

    temporary_address = models.CharField(max_length=150,blank=True, null=True)
    permanent_address = models.CharField(max_length=150,blank=True, null=True)

    guardian_name = models.CharField(max_length=150)
    guardian_relation = models.CharField(max_length=100)
    guardian_phone = models.CharField(max_length=15)

    citizenship = models.FileField(upload_to='documents/citizenship/',blank=True, null=True)
    certificates = models.FileField(upload_to='documents/certificates/', blank=True,null=True)

    @property
    def calculate_age(self):
        if self.dob:
            today = date.today()
            return today.year - self.dob.year - ((today.month, today.day) < (self.dob.month, self.dob.day))
        return 0
    
    status = models.CharField(
        max_length=20,
        choices=[('pending','Pending'),('selected','Selected'),('rejected','Rejected')],
        default='pending'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        # return self.full_name
        return f"{self.event_name} - {self.full_name or 'Template'}"

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