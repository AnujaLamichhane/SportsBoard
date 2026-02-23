from django.urls import path
from . import views

app_name = 'admin_panel'

urlpatterns = [
    path('', views.login_view, name='login'),
    path('dashboard/', views.dashboard, name='adashboard'),
    path('organizer-requests/', views.organizer_requests, name='organizer_requests'), # Add this
    path('manage-users/', views.manage_users, name='manage_users'),
    path('delete-user/<int:user_id>/', views.delete_user, name='delete_user'),
    path('feedback/', views.manage_feedback, name='manage_feedback'),
    path('feedback/resolve/<int:pk>/', views.resolve_feedback, name='resolve_feedback'),
    # path('verify-organizer/<int:pk>/<str:action>/', views.verify_organizer, name='verify_organizer'),
    path('sports/', views.manage_sports, name='manage_sports'),
    path('reports/', views.reports_view, name='reports'),
path('settings/', views.settings_view, name='settings'),
path('verify/<int:pk>/<str:action>/', views.verify_organizer, name='verify_organizer'),
]