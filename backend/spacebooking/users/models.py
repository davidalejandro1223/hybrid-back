from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.

class User(AbstractUser):
    user_identification = models.CharField(max_length=128)
    cellphone_number = models.CharField(max_length=15)
    email = models.EmailField(unique=True)
    is_company_admin = models.BooleanField(verbose_name="Administrador de la empresa", default=False)
    is_worker = models.BooleanField(verbose_name="Trabajador de la empresa", default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

