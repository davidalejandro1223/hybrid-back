from django.db import models
from datetime import datetime, timedelta
from users.models import User

class Country(models.Model):
	nombre = models.CharField(max_length=250)

	def __str__(self):
		return self.nombre

class Location(models.Model):
	FASES = [
		("FASEI", 'Fase I'),
		("FASEII", 'Fase II'),
		("FASEIII", 'Fase III'),
		("FASEIV", 'Fase IV'),
		("FASEV", 'Fase V'),
		("Sin fase", "Sin fase")
	]    
	LEVELS = [
        ("COMUNA", 'Comuna')
    ]
	fase = models.CharField(max_length=250,choices=FASES)
	nombre = models.CharField(max_length=250)
	country = models.ForeignKey(
    	Country,related_name='location_country_id',on_delete=models.CASCADE)
	admnistrative_level = models.CharField(
		max_length=20,
		choices=LEVELS)

	def __str__(self):
		return self.nombre


class Company(models.Model):
    name = models.CharField(max_length=250)
    created_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.name} ({self.id})'


class BranchOfficeConfig(models.Model):
	start_date = models.TimeField(
	    blank=True, null=True, verbose_name="hora jornada inicio")
	end_date = models.TimeField(
	    blank=True, null=True, verbose_name="hora jornada fin")
	maximun_request_days_contagious = models.IntegerField(default=14)
	days_to_review_contagious = models.IntegerField()
	notify_branch_office = models.BooleanField(default=False)
	block_branch_office = models.BooleanField(default=False)
	created_date = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return f"{self.branchoffice_set.first()} config"


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
    	BranchOfficeConfig,on_delete=models.CASCADE)
    created_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.name} ({self.company})'


class Contract(models.Model):
	employee = models.ForeignKey(User, on_delete=models.CASCADE)
	company = models.ForeignKey(
		Company,related_name='contract_company_id',on_delete=models.CASCADE)
	job_title = models.CharField(max_length=250)
	minimum_attendance = models.IntegerField(default=0)
	start_date = models.DateField(
	    blank=True, null=True, verbose_name="fecha contratación")
	end_date = models.DateField(
	    blank=True, null=True, verbose_name="fecha fin de contratación") 
	#assigned_area = models.ForeignKey(Company,related_name='contract_area_id',on_delete=models.CASCADE)
	branch_offices = models.ManyToManyField(BranchOffice)
	created_date = models.DateTimeField(auto_now_add=True)

	def __str__(self):
	    return f'{self.company}: {self.employee} - ({self.job_title})'


class Area(models.Model):
	name = models.CharField(max_length=250)
	available = models.BooleanField(default=True)
	maximun_capacity = models.IntegerField(default=0)
	branch_office = models.ForeignKey(BranchOffice, on_delete=models.CASCADE)
	created_date = models.DateTimeField(auto_now_add=True)
	
	def get_time_block_by_time(self, datetime):
		area_config = self.areaconfig_set.filter(active=True).order_by('-created_date').first()
		start_time = area_config.start_date
		end_time = area_config.end_date
		cant_hours = end_time - start_time
		block_time = cant_hours / 4
		delta = timedelta(hours=block_time)
		for i in range(0,4):
			start_block = start_time + (delta*i)
			end_block = start_time + (start_block + delta)
			if datetime.time() > start_block and datetime.time() < end_block:
				return start_block, end_block
		return None
	
	def get_time_blocks(self):
		time_blocks = []
		area_config = self.areaconfig_set.filter(active=True).order_by('-created_date').first()
		start_time = area_config.start_date
		end_time = area_config.end_date
		cant_hours = end_time - start_time
		block_time = cant_hours / 4
		delta = timedelta(hours=block_time)
		for i in range(0,4):
			start_block = start_time + (delta*i)
			end_block = start_time + (start_block + delta)
			time_blocks.append({
				f"bloque{i+1}":{"start_time":start_block, "end_time":end_block}
			})
		return time_blocks

class AreaConfig(models.Model):
	FASES = [
		("FASEI", 'Fase I'),
		("FASEII", 'Fase II'),
		("FASEIII", 'Fase III'),
		("FASEIV", 'Fase IV'),
		("FASEV", 'Fase V'),
		("Sin fase", "Sin fase")
	]    
	fase = models.CharField(max_length=250,choices=FASES)
	maximun_capacity = models.IntegerField(default=0)
	immobile_spaces = models.IntegerField(default=0,verbose_name="Cantidad espacios fijos")
	flexible_spaces = models.IntegerField(default=0,verbose_name="Cantidad espacios flexibles")
	start_date = models.TimeField(
	    blank=True, null=True, verbose_name="hora jornada area inicio")
	end_date = models.TimeField(
	    blank=True, null=True, verbose_name="hora jornada area fin")
	active = models.BooleanField(default=False)
	area = models.ForeignKey(Area, models.CASCADE)
	maximun_request_days_ahead = models.IntegerField(default=8)	
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
	    blank=True, null=True, verbose_name="fecha y hora inicio jornada")
	end_date = models.DateTimeField(
	    blank=True, null=True, verbose_name="fecha y hora fin jornada")
	status = models.CharField(
		max_length=100,
		choices=ESTADO)
	employee = models.ForeignKey(User, on_delete=models.CASCADE)
	branch_office = models.ForeignKey(
		BranchOffice,related_name='reserva_branchoffice_id',on_delete=models.CASCADE)
	area = models.ForeignKey(
		Area,related_name='reserva_area_id',on_delete=models.CASCADE)	
	resource = models.ForeignKey(Resource, on_delete=models.CASCADE)
	seat = models.ForeignKey(Seat, on_delete=models.CASCADE, null=True)
	created_date = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return f'{self.status}: {self.start_date} - {self.end_date}, ({self.employee}) ({self.id})'