#
# from django.contrib import admin
# from django.urls import path, include
# from django.conf import settings
# from django.conf.urls.static import static
# from django.views.generic.base import RedirectView # For redirecting root URL
#
#
#
# urlpatterns = [
#     path('admin/', admin.site.urls),
#     path('', include('homepage.urls')),
# path('accounts/', include('allauth.urls')), # This will include allauth's own login/signup/social URLs
#     # You might want to remove 'django.contrib.auth.urls' if allauth is handling all auth.
# #     path('accounts/', include('accounts.urls')),
# #     path('accounts/', include('django.contrib.auth.urls')),
# # # Optional: Redirect root URL to login page
#     path('', RedirectView.as_view(url='/accounts/login/', permanent=True)),
# ]
#
# if settings.DEBUG:
#     urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
#     urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),

    # Homepage
    path('', include('homepage.urls')),

    # Custom accounts app (your crispy + video login/signup)
    path('accounts/', include('accounts.urls')),

    path('accounts/', include('allauth.urls')),

]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)