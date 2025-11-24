from django.urls import path
from . import views


urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('cricket/', views.cricket, name='cricket'),
    path('football/', views.football, name='football'),
    path('volleyball/', views.volleyball, name='volleyball'),
    path('basketball/', views.basketball, name='basketball'),
    path('badminton/', views.badminton, name='badminton'),
   ]

# from django.urls import path
# from . import views

# urlpatterns = [
#     path('', views.home, name='home'),
#     path('match/<int:match_id>/', views.match_detail, name='match_detail'),
# ]
