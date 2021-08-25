from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from datetime import datetime

from infrastructure.models import (
    Area,
    Resource,
    Seat,
    BranchOffice
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

class Policy(models.Model):
    
    DAYS_OF_THE_WEEK = (
        ('Mon. ', 'Monday'),
        ('Tue. ', 'Tuesday'),
        ('Wed. ', 'Wednesday'),
        ('Thu. ', 'Thursday'),
        ('Fri. ', 'Friday'),
        ('Sat. ', 'Saturday'),
        ('Sun. ', 'Sunday')
    )

    assigned_by_admin = models.BooleanField(default=False)
    employee = models.ForeignKey(User,related_name='policy_user_id',on_delete=models.CASCADE)
    area = models.ForeignKey(Area,related_name='policy_area_id',on_delete=models.CASCADE, blank=True, null=True)
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE, blank=True, null=True)
    seat = models.ForeignKey(Seat, on_delete=models.CASCADE, blank=True, null=True)
    days_of_the_week = models.CharField(verbose_name="dias de asistencia", max_length=50, blank=True, null=True)
    branch_office_favorited = models.ForeignKey(BranchOffice, on_delete=models.CASCADE, blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def get_days_of_the_week(self):
        days_list = self.days_of_the_week.split(" ")
        days_filter = list(filter(lambda x: x[0].strip() in days_list, self.DAYS_OF_THE_WEEK))
        return days_filter
    
    def get_days_of_the_week_verbose(self):
        verbose_days = []
        for days in self.get_days_of_the_week():
            verbose_days.append(days[1])
        return verbose_days
    
    def set_days_of_the_week(self, days_list):
        if isinstance(days_list, str):
            return days_list
        days_str = ""
        for day in days_list:
            day_abr = list(filter(lambda x: x[1]==day, self.DAYS_OF_THE_WEEK))[0][0]
            days_str+=day_abr
        self.days_of_the_week = days_str
        return self.days_of_the_week
    
    def save(self, *args, **kwargs):
        self.set_days_of_the_week(self.days_of_the_week)
        super().save()
