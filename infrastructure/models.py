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
    nombre = models.CharField(max_length=250)
    country = models.ForeignKey(
    	Country,related_name='location_country_id',on_delete=models.CASCADE)
    admnistrative_level = models.CharField(
		max_length=20,
		choices=LEVELS)


class Company(models.Model):
    name = models.CharField(max_length=250)
    created_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.name}: {self.id}'


class BranchOfficeConfig(models.Model):
	start_date = models.DateTimeField(
	    blank=True, null=True, verbose_name="hora jornada inicio")
	end_date = models.DateTimeField(
	    blank=True, null=True, verbose_name="hora jornada fin")
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
    location = models.ForeignKey(
    	Location,related_name='branchoffice_location_id',on_delete=models.CASCADE)
    branch_office_config = models.ForeignKey(
    	BranchOfficeConfig,related_name='branchoffice_branchofficeconfig_id',on_delete=models.CASCADE)
    created_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.name}: ({self.company})'


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
	branch_offices = models.ManyToManyField(BranchOffice)

	def __str__(self):
	    return f'{self.company}: {self.employee} - ({self.job_title})'


class AreaConfig(models.Model):
	FASES = [
		("FASEI", 'Fase I'),
		("FASEII", 'Fase II'),
		("FASEIII", 'Fase III'),
		("FASEIV", 'Fase IV'),
		("FASEIV", 'Fase V'),
		("Sin fase", "Sin fase")
	]    
	fase = models.CharField(max_length=250,choices=FASES)
	maximun_capacity = models.IntegerField(default=0)
	immobile_spaces = models.IntegerField(default=0,verbose_name="Cantidad espacios fijos")
	flexible_spaces = models.IntegerField(default=0,verbose_name="Cantidad espacios flexibles")
	start_date = models.DateTimeField(
	    blank=True, null=True, verbose_name="hora jornada area inicio")
	end_date = models.DateTimeField(
	    blank=True, null=True, verbose_name="hora jornada area fin")
	maximun_request_days_ahead = models.IntegerField(default=8)	
	created_date = models.DateTimeField(auto_now_add=True)

class Area(models.Model):
	name = models.CharField(max_length=250)
	available = models.BooleanField(default=True)
	maximun_capacity = models.IntegerField(default=0)
	branch_area_config = models.ForeignKey(
		AreaConfig,related_name='area_areaConfig_id',on_delete=models.CASCADE)
	branch_office = models.ForeignKey(BranchOffice, on_delete=models.CASCADE)
	created_date = models.DateTimeField(auto_now_add=True)


	def __str__(self):
		return f'{self.name}: {self.available} - {self.maximun_capacity}'

class Resource(models.Model):
	TIPO = [
	    ("ESCRITORIO IND", 'Escritorio individual'),
	    ("SALA DE REUNIÓN", 'Sala de reunión'),
		("PARQUEADERO", 'Parqueadero'),
		("ESCRITORIO COMP", 'Escritorio compartido')
	]
	name = models.CharField(max_length=250)
	compartible = models.BooleanField(default=False)
	reservable = models.BooleanField(default=False)
	area = models.ForeignKey(Area, on_delete=models.CASCADE)
	tipo = models.CharField(
		max_length=100,
		choices=TIPO)

	def __str__(self):
		return f"{self.name} ({self.area})"

class Seat(models.Model):
	resource = models.ForeignKey(Resource, on_delete=models.CASCADE)
	id_in_area = models.IntegerField(verbose_name="Id del asiento dentro del area")

	def save(self):
		cant_seat_area = len(Seat.objects.filter(resource__area=self.resource.area))
		self.id_in_area = cant_seat_area + 1
		super().save()
	
	def __str__(self):
		return f'{self.resource} - {self.id_in_area}'


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