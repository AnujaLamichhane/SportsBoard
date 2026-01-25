from django.urls import path
from . import views

urlpatterns = [
    path('initiate/<int:ticket_id>/', views.init_payment, name='init_payment'),
    # This matches the 'return_url' we sent to Khalti
    path('callback/', views.payment_callback, name='payment_callback'),
    path('success/', views.payment_success, name='payment_success_page'),
    path('failed/', views.payment_failed, name='payment_failed_page'),
]