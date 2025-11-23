

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