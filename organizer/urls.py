# from django.urls import path
# from . import views
#
#
# app_name = 'organizer'
#
# urlpatterns = [
#     path('', views.organizer_dashboard, name='dashboard'),
#     path('events/create/', views.create_event, name='event_create'),
#     path('events/<int:event_id>/', views.event_detail, name='event_detail'),
#     path('selection/create/', views.selection_form_create, name='selection_form_create'),
#     path('events/<int:event_id>/edit/', views.event_edit, name='event_edit'),  # NEW
#     path('events/<int:event_id>/delete/', views.event_delete, name='event_delete'),
#     path('events/<int:event_id>/', views.event_detail, name='event_detail'),
#     path('book/<int:event_id>/', views.start_booking_process, name='start_booking'),
# ]


from django.urls import path
from . import views

app_name = 'organizer'

urlpatterns = [
    # Dashboard & Creation
    path('', views.organizer_dashboard, name='dashboard'),
    path('events/create/', views.create_event, name='event_create'),
    # path('selection/create/', views.selection_form_create, name='selection_form_create'),

    # Event Management
    path('events/<int:event_id>/', views.event_detail, name='event_detail'),
    path('events/<int:event_id>/edit/', views.event_edit, name='event_edit'),
    path('events/<int:event_id>/delete/', views.event_delete, name='event_delete'),

    # Booking & Tickets
    path('book/<int:event_id>/', views.start_booking_process, name='start_booking'),
    path('selection/create/', views.selection_form_create, name='selection_form_create'),
    path('selection/create/<int:pk>/', views.selection_form_create, name='selection_form_create'),
    path('booking/success/<int:sale_id>/', views.booking_success, name='booking_success'), # ADDED THIS
]