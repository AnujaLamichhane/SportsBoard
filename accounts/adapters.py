

# from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
# from django.shortcuts import redirect

#
#
#

#
#
#

# from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
# from django.contrib.auth.models import Group
#
# class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
#     def pre_social_login(self, request, sociallogin):
#         # Retrieve the role selected by the user on the login screen
#
#         role = request.session.pop('login_role', None)
#
#         # Only process if this is a new signup
#         if role and not sociallogin.is_existing:
#             user = sociallogin.user  # The user object is available here before final save
#
#             if role == 'organizer':
#                 group_name = 'Organizer'
#             else:  # Defaults to 'user' or 'athlete'
#
#                 role = request.session.pop('login_role', None)
#
#         # Only process if this is a new signup
#         if role and not sociallogin.is_existing:
#             user = sociallogin.user # The user object is available here before final save
#
#             if role == 'organizer':
#                 group_name = 'Organizer'
#             else: # Defaults to 'user' or 'athlete'
#
#                 group_name = 'Athlete'
#
#             try:
#                 # Add the user to the correct Django Group
#                 group = Group.objects.get(name=group_name)
#                 user.groups.add(group)
#             except Group.DoesNotExist:
#
#                 print(f"Django Group '{group_name}' does not exist. Please create it in the Admin.")
#
#                 print(f"Django Group '{group_name}' does not exist. Please create it in the Admin.")
#

# accounts/adapters.py
from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.contrib.auth.models import Group
from django.conf import settings
from django.urls import reverse


# --- FIXES THE EMAIL LINKS (Step 3 from your previous plan) ---
class CustomAccountAdapter(DefaultAccountAdapter):
    def get_email_confirmation_url(self, request, emailconfirmation):
        # This forces the link to use your ngrok DOMAIN from settings
        path = reverse("account_confirm_email", args=[emailconfirmation.key])
        # return f"https://{settings.DOMAIN}{path}"
        host = request.get_host()
        protocol = 'https' if 'ngrok' in host else 'http'

        return f"{protocol}://{host}{path}"

# --- HANDLES GOOGLE ROLE SELECTION (Your current logic) ---
class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        # Retrieve the role from the session
        role = request.session.pop('login_role', None)

        if role and not sociallogin.is_existing:
            user = sociallogin.user

            if role == 'organizer':
                group_name = 'Organizer'
            else:
                group_name = 'Athlete'

            # Note: We can't use user.groups.add(group) before the user is saved.
            # We store it as an attribute to save after the user hits the DB.
            user._selected_group = group_name

    def save_user(self, request, sociallogin, form=None):
        user = super().save_user(request, sociallogin, form)
        # Check if we stored a group name during pre_social_login
        group_name = getattr(sociallogin.user, '_selected_group', None)
        if group_name:
            try:
                group = Group.objects.get(name=group_name)
                user.groups.add(group)
            except Group.DoesNotExist:
                pass
        return user
