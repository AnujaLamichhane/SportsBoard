

import hashlib
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.validators import RegexValidator


class Profile(models.Model):
    # Role Definitions
    ROLE_CHOICES = [
        ('ATHLETE', 'Athlete'),
        ('ORGANIZER', 'Organizer'),
        ('ADMIN', 'Admin'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='ATHLETE')

    # --- KYC & Compliance (Nepal IT Standards) ---
    is_verified = models.BooleanField(default=False)
    # Required for Organizers to handle payments/tickets legally
    citizenship_no = models.CharField(max_length=50, blank=True, null=True, help_text="Required for Organizers")
    id_front = models.ImageField(upload_to='kyc/ids/', blank=True, null=True)
    id_back = models.ImageField(upload_to='kyc/ids/', blank=True, null=True)

    # --- General Info ---
    phone_regex = RegexValidator(regex=r'^9\d{9}$', message="Enter a valid 10-digit Nepal phone number.")
    phone_number = models.CharField(validators=[phone_regex], max_length=10, blank=True)
    # phone_number = models.CharField(max_length=15, blank=True)
    image = models.ImageField(default='default.jpg', upload_to='profile_pics')
    bio = models.TextField(max_length=500, blank=True)

    def __str__(self):
        return f'{self.user.username} ({self.role})'

    @property
    def profile_url(self):
        if self.image and self.image.name != 'default.jpg':
            return self.image.url
        email_hash = hashlib.md5(self.user.email.strip().lower().encode('utf-8')).hexdigest()
        return f"https://www.gravatar.com/avatar/{email_hash}?d=identicon"


# Signals remain largely the same, but now ensure the profile is ready for role assignment
@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.get_or_create(user=instance)


@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()

@receiver(post_save, sender=User)
def manage_user_profile(sender, instance, created, **kwargs):
    """Consolidated signal: Handles both creation and saving of Profile."""
    if created:
        Profile.objects.get_or_create(user=instance)
    else:
        # Check if profile exists before saving to prevent crashes
        if hasattr(instance, 'profile'):
            instance.profile.save()