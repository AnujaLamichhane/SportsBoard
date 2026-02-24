from django.urls import path
from . import views

app_name = 'organizer'

urlpatterns = [
    # Dashboard & Discovery
    path('', views.organizer_dashboard, name='dashboard'),
    path('all-events/', views.all_events, name='all_events'),
path('settings/', views.organizer_settings, name='settings'),
path('settings/submit-verification/', views.submit_verification, name='submit_verification'),
path('help/', views.help_feedback, name='help_feedback'),


    # Event CRUD
    path('events/create/', views.create_event, name='event_create'),
    path('events/<int:event_id>/', views.event_detail, name='event_detail'),
    path('events/<int:event_id>/edit/', views.event_edit, name='event_edit'),
    path('events/<int:event_id>/delete/', views.event_delete, name='event_delete'),

    # Player Selection / Trial Forms
    path('selection/create/', views.selection_form_create, name='selection_form_create'),
    path('selection/create/<int:pk>/', views.selection_form_create, name='selection_form_create'),
    path('published_forms/', views.published_forms, name='published_forms'),
    path('published_form/<int:pk>/', views.published_form_detail, name='published_form_detail'),
path('selection-form/preview/<int:pk>/', views.form_preview, name='form_preview'),
    path('applications/', views.review_applications, name='review_applications'),
    path('applications/<int:pk>/<str:action>/', views.update_application_status, name='update_application_status'),
path('applications/review/<int:pk>/', views.review_athlete_profile, name='review_athlete_profile'),



    # Ticketing & Khalti Payment (CRITICAL)
    path('book/<int:event_id>/', views.start_booking_process, name='start_booking'),
    path('payment/initiate/<int:tier_id>/', views.init_payment, name='init_payment'), # Required for HTML
    path('payment/verify/', views.verify_payment, name='verify_payment'),             # Required for Khalti callback
    path('booking/success/<int:sale_id>/', views.booking_success, name='booking_success'),
    path('verify-ticket/', views.verify_ticket_gate, name='verify_ticket_gate'),
    path('applications/pdf/<int:pk>/', views.athlete_pdf_view, name='athlete_pdf_detail'),

]