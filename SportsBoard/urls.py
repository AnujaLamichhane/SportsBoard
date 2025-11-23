from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
# from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),

    # Homepage
    path('', include('homepage.urls')),

    # Custom accounts app (your crispy + video login/signup)
    path('accounts/', include(('accounts.urls','accounts'), namespace='accounts')),

    path('accounts/', include('allauth.urls')),
    path('organizer/', include('organizer.urls', namespace='organizer')),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)