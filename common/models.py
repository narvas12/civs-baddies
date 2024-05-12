from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils.translation import gettext_lazy as _
from .managers import RatingManager

   

class Rating(models.Model):
    id = models.BigAutoField(primary_key=True, editable=False) 
    rating_type = models.IntegerField(null=True, blank=True)
    description = models.CharField(
        max_length=255, verbose_name=_("Rating Description")
    )
    date_created = models.DateTimeField(auto_now_add=True)
    
    objects = RatingManager()
    
    

   

