from django.db import models
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.shortcuts import render
from django.contrib.auth.models import BaseUserManager

# Create your models here.

#userManager

class UserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Users must have an email address")

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True")

        return self.create_user(email, password, **extra_fields)

#my models 

class User(AbstractUser):
    ROLE_CHOICES = (
        ('student', 'Student'),
        ('sponsor', 'Sponsor'),
    )
    email= models.EmailField(max_length=150, unique=True)
    username = None
    name=models.CharField(max_length=150)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()


    
    

