from django.db import models

# Create your models here.
from django.contrib.auth.models import User

class Sport(models.Model):  # Make sure 'Sport' is capitalized exactly like this
    name = models.CharField(max_length=100)
    organizer = models.ForeignKey(User, on_delete=models.CASCADE)
    # ... other fields ...

    def __str__(self):
        return self.name

class SiteSettings(models.Model):

    # -------- General ----------
    site_name = models.CharField(max_length=150, default="SportsBoard")
    support_email = models.EmailField(default="support@sportsboard.com")
    maintenance_mode = models.BooleanField(default=False)

    # -------- Platform ----------
    commission = models.PositiveIntegerField(default=10)
    max_duration = models.PositiveIntegerField(default=24)

    # -------- Security ----------
    admin_session_timeout = models.PositiveIntegerField(default=120)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "Global Site Settings"

    @classmethod
    def load(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj