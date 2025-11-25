from django.db import models
from django.contrib.auth import get_user_model



# Create your models here.
class Sponsor(models.Model):
     user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE, related_name='sponsor_profile')
     organization_name = models.CharField(max_length=255)
     website = models.URLField(blank=True, null=True)
     contact_number = models.CharField(max_length=20, blank=True, null=True)

     def __str__(self):
         return self.organization_name

