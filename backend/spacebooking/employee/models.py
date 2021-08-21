from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from datetime import datetime

from infrastructure.models import (
    Area
)

User = get_user_model()


class ContagiousHistory(models.Model):
    POSITIVE = 'P'
    NEGATIVE = 'N'
    POLARITY_CHOICES = [
        (POSITIVE, 'Positive'),
        (NEGATIVE, 'Negative'),
    ]
    employee = models.ForeignKey(User,related_name='contagioushistory_user_id',on_delete=models.CASCADE)
    pcr_result = models.CharField(
		max_length=1,
		choices=POLARITY_CHOICES
	)
    fecha_sintomas = models.DateField(
        blank=True, null=True, verbose_name="Fecha de Sintomas")
    fecha_reporte = models.DateField(
        blank=True, null=True, verbose_name="Fecha de Reporte")    
    created_date = models.DateTimeField(auto_now_add=True)


class BaseWorkGroup(models.Model):
    name = models.CharField(max_length=250)
    created_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class WorkGroup(models.Model):
    employee = models.ManyToManyField(User)
    work_position = models.ManyToManyField(BaseWorkGroup)
    created_date = models.DateTimeField(auto_now_add=True)


class Policy(models.Model):
    asigned_by_admin = models.BooleanField(default=False)
    employee = models.ForeignKey(User,related_name='policy_user_id',on_delete=models.CASCADE)
    area = models.ForeignKey(Area,related_name='policy_area_id',on_delete=models.CASCADE)
    horario = models.DateTimeField(blank=True, null=True)
    created_date = models.DateTimeField(auto_now_add=True)
