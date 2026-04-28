from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Profile, Feedback


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'role', 'is_verified', 'phone_number']
    list_filter = ['role', 'is_verified']
    search_fields = ['user__username', 'user__email']
    list_editable = ['role', 'is_verified']


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ['user', 'subject', 'category', 'is_resolved', 'created_at']
    list_filter = ['category', 'is_resolved']
    search_fields = ['user__username', 'subject']
    list_editable = ['is_resolved']