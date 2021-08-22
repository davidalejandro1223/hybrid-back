from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import PermissionsMixin
# Create your models here.

from .managers import CustomUserManager

class User(AbstractUser):
    username = None
    
    user_identification = models.CharField(max_length=128)
    cellphone_number = models.CharField(verbose_name="Numero telefono", max_length=15, null=True, blank=True)
    email = models.EmailField(unique=True)
    is_company_admin = models.BooleanField(verbose_name="Administrador de la empresa", default=False)
    is_worker = models.BooleanField(verbose_name="Trabajador de la empresa", default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = [
        'first_name', 
        'last_name', 
        'user_identification'
    ]

    objects = CustomUserManager()

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.user_identification}"