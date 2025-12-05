from django.urls import path
from . import views


app_name = 'accounts'
urlpatterns = [
    path('dashboard-redirect/', views.role_based_redirect, name='dashboard_redirect'),
    path('login/', views.login_view, name='login'),
    path('signup/', views.register_view, name='signup'),
    path('user-dashboard/', views.user_dashboard, name='user_dashboard'),
    # path('organizer-dashboard/', views.organizer_dashboard, name='organizer_dashboard'),
    path('google/custom-login/', views.custom_google_login, name='custom_google_login'),
    path('apply/player/', views.player_application_view, name='player_application'),
# path('apply/<int:event_id>/', views.player_application_view, name='player_apply'),
#     path('google/login/', views.custom_google_login, name='custom_google_login'),

]
