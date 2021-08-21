from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from datetime import datetime
User = get_user_model()


class Country(models.Model):
    nombre = models.CharField(max_length=250)


class Location(models.Model):
    LEVELS = [
        ("COMUNA", 'Comuna')
    ]
    FASES = [
        ("FASEI", 'Fase I'),
        ("FASEII", 'Fase II'),
        ("FASEIII", 'Fase III'),
        ("FASEIV", 'Fase IV'),
    ]    
    nombre = models.CharField(max_length=250)
    country = models.ForeignKey(
    	Country,related_name='location_country_id',on_delete=models.CASCADE)
    level = models.CharField(
		max_length=20,
		choices=LEVELS)
    fase = models.CharField(max_length=250)

    """Si cambia de fase una location, cambiarán todas,
    Hay que tomar en cuenta esas validaciones"""

class Company(models.Model):
    name = models.CharField(max_length=250)
    created_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.name}: {self.id}'


class BranchOfficeConfig(models.Model):
	maximun_capacity = models.IntegerField(default=0)
	start_date = models.DateTimeField(
	    blank=True, null=True, verbose_name="hora jornada inicio")
	end_date = models.DateTimeField(
	    blank=True, null=True, verbose_name="hora jornada fin")
	maximun_request_days = models.IntegerField(default=1)
	maximun_request_days_contagious = models.IntegerField(default=14)
	notify_branch_office = models.BooleanField(default=False)
	block_branch_office = models.BooleanField(default=False)
	created_date = models.DateTimeField(auto_now_add=True)


class BranchOffice(models.Model):
    name = models.CharField(max_length=250)
    company = models.ForeignKey(
    	Company,related_name='branchoffice_company_id',on_delete=models.CASCADE)
	#lat = models.DecimalField(max_digits=22, decimal_places=16, blank=False, null=True)
	#lng = models.DecimalField(max_digits=22, decimal_places=16, blank=False, null=True)
	#position = models.PointField(null=True, blank=False)
    address = models.CharField(max_length=250)
    country = models.ForeignKey(
    	Country,related_name='branchoffice_country_id',on_delete=models.CASCADE)
    location = models.ForeignKey(
    	Location,related_name='branchoffice_location_id',on_delete=models.CASCADE)
    branch_office_config = models.ForeignKey(
    	BranchOfficeConfig,related_name='branchoffice_branchofficeconfig_id',on_delete=models.CASCADE)
    created_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.name}: ({self.company})'


class BranchOfficeEmployee(models.Model):
	employee = models.ManyToManyField(User)
	branch_office = models.ManyToManyField(BranchOffice)
	created_date = models.DateTimeField(auto_now_add=True)


class Contract(models.Model):
	employee = models.ManyToManyField(User)
	company = models.ForeignKey(
		Company,related_name='contract_company_id',on_delete=models.CASCADE)
	job_title = models.CharField(max_length=250)
	minimum_attendance = models.IntegerField(default=0)
	start_date = models.DateField(
	    blank=True, null=True, verbose_name="fecha contratación")
	end_date = models.DateField(
	    blank=True, null=True, verbose_name="fecha fin de contratación") 
	#assigned_area = models.ForeignKey(Company,related_name='contract_area_id',on_delete=models.CASCADE)
	created_date = models.DateTimeField(auto_now_add=True)

	def __str__(self):
	    return f'{self.company}: {self.employee} - ({self.job_title})'


class AreaConfig(models.Model):
	maximun_capacity = models.IntegerField(default=0)
	immobile_spaces = models.IntegerField(default=0,verbose_name="Cantidad espacios fijos")
	flexible_spaces = models.IntegerField(default=0,verbose_name="Cantidad espacios flexibles")
	start_date = models.DateTimeField(
	    blank=True, null=True, verbose_name="hora jornada area inicio")
	end_date = models.DateTimeField(
	    blank=True, null=True, verbose_name="hora jornada area fin")
	maximun_request_days_contagious = models.IntegerField(default=14)
	created_date = models.DateTimeField(auto_now_add=True)


class Area(models.Model):
	TIPO = [
	    ("ESCRITORIO", 'Escritorio'),
	    ("SALA DE REUNIÓN", 'Sala de reunión')
	]
	available = models.BooleanField(default=True)
	maximun_capacity = models.IntegerField(default=0)
	tipo = models.CharField(
		max_length=100,
		choices=TIPO)
	branch_area_config = models.ForeignKey(
		AreaConfig,related_name='areaconfig_id',on_delete=models.CASCADE)
	created_date = models.DateTimeField(auto_now_add=True)


class Reserva(models.Model):
	ESTADO = [
	    ("ASIGNADA", 'Asignada'),
	    ("CONFIRMADA", 'Confirmada'),
	    ("CANCELADA", 'Cancelada')	    
	]
	fijo = models.BooleanField(default=False)
	start_date = models.DateTimeField(
	    blank=True, null=True, verbose_name="hora jornada")
	end_date = models.DateTimeField(
	    blank=True, null=True, verbose_name="hora jornada")
	status = models.CharField(
		max_length=100,
		choices=ESTADO)
	employee = models.ManyToManyField(User)
	branch_office = models.ForeignKey(
		BranchOffice,related_name='reserva_branchoffice_id',on_delete=models.CASCADE)
	area = models.ForeignKey(
		Area,related_name='reserva_area_id',on_delete=models.CASCADE)	
	created_date = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return f'{self.status}: {self.start_date} - {self.end_date}, ({self.employee}) ({self.id})'