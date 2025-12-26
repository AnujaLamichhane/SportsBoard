# from allauth.account.signals import user_logged_in
# from django.dispatch import receiver
# from django.shortcuts import redirect
#
#
# @receiver(user_logged_in)
# def after_google_login(request, user, **kwargs):
#     role = request.session.pop('login_role', None)
#     if role:
#         # Assuming you have a 'role' field in your user model or related profile
#         user.role = role
#         user.save()
#
#         # Redirect based on role
#         if role == 'organizer':
#             return redirect('organizer_dashboard')
#         else:
#             return redirect('user_dashboard')

from allauth.account.signals import user_logged_in
from django.dispatch import receiver
# from django.shortcuts import redirect
from .models import Profile
from django.db.models.signals import post_save
from django.contrib.auth.models import User

@receiver(user_logged_in)
def after_google_login(request, user, **kwargs):
    role = request.session.pop('login_role', None)
    if role:
        user.role = role
        user.save()

@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        # Use get_or_create to prevent "IntegrityError" if profile already exists
        Profile.objects.get_or_create(user=instance)

@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
        """Ensures the profile is saved whenever the user is saved."""
        instance.profile.save()