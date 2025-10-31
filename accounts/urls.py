# from django.urls import path
#
# from . import views
#
#
#
# urlpatterns = [
#
#
#     path('login/', views.login_view, name='login'),
#     path('signup/', views.register_view, name='signup'),
#
#     path('user-dashboard/', views.user_dashboard, name='user_dashboard'),
#     path('organizer-dashboard/', views.organizer_dashboard, name='organizer_dashboard'),
#     path('google/custom-login/', views.custom_google_login, name='custom_google_login'),
#
#
#
# ]
#
from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('signup/', views.register_view, name='signup'),
    path('user-dashboard/', views.user_dashboard, name='user_dashboard'),
    path('organizer-dashboard/', views.organizer_dashboard, name='organizer_dashboard'),
    path('google/custom-login/', views.custom_google_login, name='custom_google_login'),
]
