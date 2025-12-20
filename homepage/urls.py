from django.urls import path
from . import views

app_name = 'homepage'
urlpatterns = [
    path('viewevents/', views.all_events, name='view_events'),
    path('', views.home, name='home'),
    path('go-athlete/', views.handle_athlete_redirect, name='go_athlete'),
    path('about/', views.about, name='about'),
    path('go-organizer/', views.handle_organizer_redirect, name='go_organizer'),
    path('cricket/', views.cricket, name='cricket'),
    path('football/', views.football, name='football'),
    path('volleyball/', views.volleyball, name='volleyball'),
    path('basketball/', views.basketball, name='basketball'),
    path('badminton/', views.badminton, name='badminton'),
    path('logout/', views.logout_user, name='logout'),
    # path('event/<int:id>/', views.event_detail, name='event_detail'),

   ]


