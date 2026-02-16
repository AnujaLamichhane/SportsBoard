from django.urls import path
from . import views

app_name = 'admin_panel'

urlpatterns = [
    path('', views.login_view, name='login'),
    path('dashboard/', views.dashboard, name='adashboard'),
    path('organizer-requests/', views.organizer_requests, name='organizer_requests'), # Add this
    path('manage-users/', views.manage_users, name='manage_users'),
    path('delete-user/<int:user_id>/', views.delete_user, name='delete_user'),
]