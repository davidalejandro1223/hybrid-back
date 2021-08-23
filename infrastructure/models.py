from django.db import models
from datetime import datetime, timedelta, time
from users.models import User
import math

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
	
	def get_time_block_by_time(self, check_datetime):
		area_config = self.areaconfig_set.filter(active=True).order_by('-created_date').first()
		start_time = timedelta(hours=area_config.start_date.hour, minutes=area_config.start_date.minute)
		end_time = timedelta(hours=area_config.end_date.hour, minutes=area_config.end_date.minute)
		cant_hours = (end_time - start_time).seconds/3600
		block_time = cant_hours / 4
		delta = timedelta(hours=block_time)
		for i in range(0,4):
			start_block = start_time + (delta*i)
			end_block = start_block + delta
			
			start_minutes, start_hours = math.modf(start_block.seconds/3600)
			start_hours = int(start_hours)
			start_minutes = int(start_minutes * 60)

			end_minutes, end_hours = math.modf(end_block.seconds/3600)
			end_hours = int(end_hours)
			end_minutes = int(end_minutes * 60)

			start_datetime = datetime.combine(check_datetime.date(), time(hour=start_hours, minute=start_minutes))
			end_datetime = datetime.combine(check_datetime.date(), time(hour=end_hours, minute=end_minutes))

			if check_datetime > start_datetime and check_datetime < end_datetime:
				return start_datetime.time(), end_datetime.time()
		return None
	
	def get_time_blocks(self):
		time_blocks = []
		area_config = self.areaconfig_set.filter(active=True).order_by('-created_date').first()
		start_time = timedelta(hours=area_config.start_date.hour, minutes=area_config.start_date.minute)
		end_time = timedelta(hours=area_config.end_date.hour, minutes=area_config.end_date.minute)
		cant_hours = (end_time - start_time).seconds/3600

		time_blocks.append({
				"bloque 1":{"start_time":area_config.start_date, "end_time":area_config.end_date}
			})
		
		block_time = cant_hours / 2
		delta = timedelta(hours=block_time)
		for i in range(0,2):
			start_block = start_time + (delta*i)
			end_block = start_block + delta
			
			start_minutes, start_hours = math.modf(start_block.seconds/3600)
			start_hours = int(start_hours)
			start_minutes = int(start_minutes * 60)

			end_minutes, end_hours = math.modf(end_block.seconds/3600)
			end_hours = int(end_hours)
			end_minutes = int(end_minutes * 60)

			start_datetime =  time(hour=start_hours, minute=start_minutes)
			end_datetime =  time(hour=end_hours, minute=end_minutes)
			
			time_blocks.append({
				f"bloque {i+2}":{"start_time":start_datetime, "end_time":end_datetime}
			})

		block_time = cant_hours / 4
		delta = timedelta(hours=block_time)
		for i in range(0,4):
			start_block = start_time + (delta*i)
			end_block = start_block + delta
			
			start_minutes, start_hours = math.modf(start_block.seconds/3600)
			start_hours = int(start_hours)
			start_minutes = int(start_minutes * 60)

			end_minutes, end_hours = math.modf(end_block.seconds/3600)
			end_hours = int(end_hours)
			end_minutes = int(end_minutes * 60)

			start_datetime =  time(hour=start_hours, minute=start_minutes)
			end_datetime =  time(hour=end_hours, minute=end_minutes)
			time_blocks.append({
				f"bloque {i+4}":{"start_time":start_datetime.time(), "end_time":end_datetime.time()}
			})
		return time_blocks
	
	@property
	def area_config(self):
		return self.areaconfig_set.filter(active=True).order_by('-created_date').first()

	def __str__(self):
		return f'{self.name}: {self.available} - {self.maximun_capacity}'

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
		return f'{self.area.name}-{self.fase}: {self.active} - {self.maximun_capacity}'
			

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