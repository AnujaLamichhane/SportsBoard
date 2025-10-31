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
from django.shortcuts import redirect


@receiver(user_logged_in)
def after_google_login(request, user, **kwargs):
    role = request.session.pop('login_role', None)
    if role:
        user.role = role
        user.save()
