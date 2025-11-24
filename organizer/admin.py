from django.contrib import admin

# Register your models here.
from .models import Event

admin.site.register(Event)
# class EventAdmin(admin.ModelAdmin):
#     list_display = ('title', 'organizer', 'date')  # show fields you want
#     list_filter = ('organizer', 'date')
#     search_fields = ('title', 'organizer__username')