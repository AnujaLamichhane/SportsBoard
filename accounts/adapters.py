from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.shortcuts import redirect


class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def get_login_redirect_url(self, request):
        role = getattr(request.user, 'role', 'user')
        if role == 'organizer':
            return '/organizer-dashboard/'
        return '/user-dashboard/'
