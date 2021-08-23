from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.

from .managers import CustomUserManager

class User(AbstractUser):
    username = None
    
    user_identification = models.CharField(max_length=128)
    cellphone_number = models.CharField(verbose_name="Numero telefono", max_length=15, null=True, blank=True)
    email = models.EmailField(unique=True)
    is_company_admin = models.BooleanField(verbose_name="Administrador de la empresa", default=False)
    is_worker = models.BooleanField(verbose_name="Trabajador de la empresa", default=False)
    mobility_permit = models.FileField(verbose_name="Pase de movilidad", blank=True, null=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = [
        'first_name', 
        'last_name', 
        'user_identification'
    ]

    objects = CustomUserManager()

    def get_company(self):
        return self.contract_set.order_by("-end_date").first().company

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.user_identification}"