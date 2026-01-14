from django.db import models

# Create your models here.

# class Match(models.Model):
#     title = models.CharField(max_length=200)
#     match_type = models.CharField(max_length=100)
#     date = models.DateField()
#     time = models.TimeField()
#     venue = models.CharField(max_length=200)
#     is_free = models.BooleanField(default=True)
#     tickets_available = models.BooleanField(default=False)
#     highlights = models.TextField(blank=True, null=True)
#     image = models.ImageField(upload_to='matches/')

#     def __str__(self):
#         return self.title
class Event(models.Model):
    title = models.CharField(max_length=200)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    description = models.TextField()
    sport = models.CharField(max_length=100)
    is_published = models.BooleanField(default=True)

    def __clist__(self):
        return self.title