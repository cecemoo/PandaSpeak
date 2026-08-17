from django.db import models
from . managers import CustomUserManager
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils import timezone


class CustomUser(AbstractBaseUser, PermissionsMixin):
    username = None
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=120)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    is_teacher = models.BooleanField(default=False, verbose_name="Are you a teacher?")
    stripe_account_id = models.CharField(max_length=255, blank=True, null=True)

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email
    

class TermsOfService(models.Model):
    content = models.TextField()
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Terms of Service (Last Updated: {self.last_updated.strftime('%Y-%m-%d')})"


class PrivacyPolicy(models.Model):
    content = models.TextField()
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Privacy Policy (Last Updated: {self.last_updated.strftime('%Y-%m-%d')})"




class PlacementQuestion(models.Model):
    LEVEL_CHOICES = [
        ('level1', 'Level I - Beginner'),
        ('level2', 'Level II - Intermediate'),
        ('level3', 'Level III - Advanced'),
    ]
    ANSWER_CHOICES = [
        ('A', 'A'),
        ('B', 'B'),
        ('C', 'C'),
        ('D', 'D'),
    ]
    level = models.CharField(
        max_length=20,
        choices=LEVEL_CHOICES
    )
    prompt = models.TextField()
    choice_a = models.CharField(max_length=500)
    choice_b = models.CharField(max_length=500)
    choice_c = models.CharField(max_length=500)
    choice_d = models.CharField(max_length=500)

    correct_answer = models.CharField(max_length=1, choices=ANSWER_CHOICES)
    audio = models.FileField(
        upload_to = 'placement_audio/', 
        blank=True,
        null=True
    )
    order = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.get_level_display()} - Question {self.order}"