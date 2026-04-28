#
# # accounts/adapters.py
# from allauth.account.adapter import DefaultAccountAdapter
# from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
# from django.contrib.auth.models import Group
# from django.conf import settings
# from django.urls import reverse
#
#
# # --- FIXES THE EMAIL LINKS (Step 3 from your previous plan) ---
# class CustomAccountAdapter(DefaultAccountAdapter):
#     def get_email_confirmation_url(self, request, emailconfirmation):
#         # This forces the link to use your ngrok DOMAIN from settings
#         path = reverse("account_confirm_email", args=[emailconfirmation.key])
#         # return f"https://{settings.DOMAIN}{path}"
#         host = request.get_host()
#         protocol = 'https' if 'ngrok' in host else 'http'
#
#         return f"{protocol}://{host}{path}"
#
# # --- HANDLES GOOGLE ROLE SELECTION (Your current logic) ---
# class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
#     def pre_social_login(self, request, sociallogin):
#         # Retrieve the role from the session
#         role = request.session.pop('login_role', None)
#
#         if role and not sociallogin.is_existing:
#             user = sociallogin.user
#
#             if role == 'organizer':
#                 group_name = 'Organizer'
#             else:
#                 group_name = 'Athlete'
#
#             # Note: We can't use user.groups.add(group) before the user is saved.
#             # We store it as an attribute to save after the user hits the DB.
#             user._selected_group = group_name
#
#     def save_user(self, request, sociallogin, form=None):
#         user = super().save_user(request, sociallogin, form)
#         # Check if we stored a group name during pre_social_login
#         group_name = getattr(sociallogin.user, '_selected_group', None)
#         if group_name:
#             try:
#                 group = Group.objects.get(name=group_name)
#                 user.groups.add(group)
#             except Group.DoesNotExist:
#                 pass
#         return user

# accounts/adapters.py
from django.conf import settings
from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.contrib.auth.models import Group
from django.urls import reverse


class CustomAccountAdapter(DefaultAccountAdapter):
    def get_email_confirmation_url(self, request, emailconfirmation):
        path = reverse("account_confirm_email", args=[emailconfirmation.key])
        # Use HTTPS if on Render, otherwise follow request
        protocol = request.META.get('HTTP_X_FORWARDED_PROTO', 'https' if not settings.DEBUG else 'http')
        host = request.get_host()
        return f"{protocol}://{host}{path}"


class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        # Use .get() instead of .pop() to ensure it stays in session if the login fails midway
        role = request.session.get('login_role')

        if role and not sociallogin.is_existing:
            user = sociallogin.user
            user._selected_group = 'Organizer' if role == 'organizer' else 'Athlete'

    def save_user(self, request, sociallogin, form=None):
        user = super().save_user(request, sociallogin, form)
        group_name = getattr(user, '_selected_group', None)
        if group_name:
            # .get_or_create ensures it works even if you haven't set up Groups in Admin
            group, _ = Group.objects.get_or_create(name=group_name)
            user.groups.add(group)

            # Also update the profile role field
            from accounts.models import Profile
            profile, _ = Profile.objects.get_or_create(user=user)
            profile.role = group_name.upper()
            profile.save()

        return user