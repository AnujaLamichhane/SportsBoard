from django.db import models

# Create your models here.
from django.contrib.auth.models import User

class Sport(models.Model):  # Make sure 'Sport' is capitalized exactly like this
    name = models.CharField(max_length=100)
    organizer = models.ForeignKey(User, on_delete=models.CASCADE)
    # ... other fields ...

    def __str__(self):
        return self.name