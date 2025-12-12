from django.db import models

# Create your models here.
class Article(models.Model):
    title = models.CharField(max_length=200)
    summary = models.TextField()
    link = models.URLField()
    source = models.CharField(max_length=50)
    published = models.DateTimeField()
    image_url = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.title