from django.db import models

# Create your models here.


class NewsFlash(models.Model):
    news = models.TextField()