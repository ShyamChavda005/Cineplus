from django.db import models
from django.utils import timezone

# Create your models here.

class Signup(models.Model) :
    name = models.CharField(max_length=100)
    email = models.CharField(max_length=255)
    username = models.CharField(max_length=100)
    password = models.CharField(max_length=255)
    confirmpassword = models.CharField(max_length=255)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name