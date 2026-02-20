from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView #12/23 change
from django.views.decorators.csrf import csrf_exempt #


app_name = 'accounts'
urlpatterns = [
    path('dashboard-redirect/', views.role_based_redirect, name='dashboard_redirect'),
    path('login/', views.login_view, name='login'),
    path('signup/', views.register_view, name='signup'),
    path('user-dashboard/', views.user_dashboard, name='user_dashboard'),
    # path('organizer-dashboard/', views.organizer_dashboard, name='organizer_dashboard'),
    path('google/custom-login/', views.custom_google_login, name='custom_google_login'),
    # path('apply/player/', views.player_application_view, name='player_application'),
# path('apply/<int:event_id>/', views.player_application_view, name='player_apply'),
#     path('google/login/', views.custom_google_login, name='custom_google_login'),
    path('logout/', csrf_exempt(LogoutView.as_view()), name='logout'), # 12/23 change
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('my-trials/', views.my_trials, name='my_trials'),
    path('my-trials/download/<int:pk>/', views.download_trial_pdf, name='download_trial_pdf'),
    path('my-trials/view/<int:pk>/', views.trial_detail_view, name='trial_detail_view'),
    path('available-trials/', views.available_trials_view, name='available_trials'),
    path('feedback/', views.feedback_view, name='feedback'),
]
