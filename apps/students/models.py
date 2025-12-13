from django.db import models


from django.contrib.auth import get_user_model
from django.utils import timezone
from apps.main.models import User



# Create your models here.
class Student(models.Model):
     user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE, related_name='student_profile')  
     admn_number= models.CharField(max_length=20, blank=True, null=True)  
     email = models.EmailField(blank=True, null=True)
     phone=models.CharField(max_length=20, blank=True, null=True)
     schoolLevel=models.CharField(max_length=100, blank=True, null=True)
     name=models.CharField(max_length=255, blank=True, null=True)
     familyIncome= models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True) 
     guardianName=models.CharField(max_length=255, blank=True, null=True)
     guardianPhone=models.CharField(max_length=20, blank=True, null=True)
     address=models.TextField(blank=True, null=True)
     dob=models.DateField(blank=True, null=True)
     

     def __str__(self):
         return self.organization_name