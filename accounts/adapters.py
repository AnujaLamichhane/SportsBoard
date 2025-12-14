# from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
# from django.shortcuts import redirect
#
#
# class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
#     def get_login_redirect_url(self, request):
#         role = getattr(request.user, 'role', 'user')
#         if role == 'organizer':
#             return '/organizer-dashboard/'
#         return '/user-dashboard/'


# # # accounts/adapters.py (Use the save_user method instead)
# #
# from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
# from django.shortcuts import redirect


# class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
#     def get_login_redirect_url(self, request):
#         role = getattr(request.user, 'role', 'user')
#         if role == 'organizer':
#             return '/organizer-dashboard/'
#         return '/user-dashboard/'


from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.contrib.auth.models import Group


class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        # Retrieve the role selected by the user on the login screen
        role = request.session.pop('login_role', None)

        # Only process if this is a new signup
        if role and not sociallogin.is_existing:
            user = sociallogin.user  # The user object is available here before final save

            if role == 'organizer':
                group_name = 'Organizer'
            else:  # Defaults to 'user' or 'athlete'
                group_name = 'Athlete'

            try:
                # Add the user to the correct Django Group
                group = Group.objects.get(name=group_name)
                user.groups.add(group)
            except Group.DoesNotExist:
                print(f"Django Group '{group_name}' does not exist. Please create it in the Admin.")
