from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from apps.main.models import User



# Create your models here.
class Sponsor(models.Model):
     user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE, related_name='sponsor_profile')
     organization_name = models.CharField(max_length=255)
     contact_number = models.CharField(max_length=20, blank=True, null=True)
     website = models.URLField(blank=True, null=True)
     email = models.EmailField(blank=True, null=True)
     name=models.CharField(max_length=255, blank=True, null=True)
     description = models.TextField(blank=True, null=True)

     def __str__(self):
         return self.organization_name


    

class Scholarship(models.Model):
    sponsor = models.ForeignKey(User, on_delete=models.CASCADE, related_name="scholarships")
    title = models.CharField(max_length=255)
    description = models.TextField()
    criteria = models.TextField(help_text="GPA requirements, region, etc.")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    deadline = models.DateField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    requirements=models.TextField(blank=True,null=True)
    category=models.CharField(max_length=100,blank=True,null=True)
    

    def __str__(self):
        return self.title    
