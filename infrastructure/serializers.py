from django.utils import timezone
from django.contrib.auth import get_user_model
from django.db.models import Sum
from rest_framework import serializers

from infrastructure.models import (Country,Location,Company,BranchOfficeConfig,BranchOffice,
    Contract,AreaConfig,Resource,Area,Reserva,
)
from employee.models import (ContagiousHistory)

User = get_user_model()

class BranchOfficeConfigSerializer(serializers.Serializer):
    start_date = serializers.TimeField()
    end_date = serializers.TimeField()
    maximun_request_days_contagious = serializers.IntegerField()
    days_to_review_contagious = serializers.IntegerField()
    notify_branch_office = serializers.BooleanField()
    block_branch_office = serializers.BooleanField(allow_null=True, required=False)
    fase = serializers.CharField(source='branchoffice_set.first.location.get_fase_display', read_only=True)
    fase_capacity = serializers.SerializerMethodField(read_only=True)

    def get_fase_capacity(self, obj):
        branch_office = obj.branchoffice_set.first()
        location = branch_office.location
        areas = Area.objects.filter(branch_office=branch_office)
        areas_config = AreaConfig.objects.filter(
            area__in = areas,
            fase=location.fase
        )
        fase_capacity = areas_config.aggregate(Sum("maximun_capacity"))
        return fase_capacity["maximun_capacity__sum"]
    

class BranchOfficeSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField()
    location = serializers.CharField()
    address = serializers.CharField()
    branch_office_config = BranchOfficeConfigSerializer()
    available_capacity = serializers.IntegerField(read_only=True)
    assigned_capacity = serializers.IntegerField(read_only=True)
    areas = serializers.SerializerMethodField(read_only=True)
    num_areas = serializers.IntegerField(source='area_set.count', read_only=True)
    total_capacity = serializers.SerializerMethodField(read_only=True)

    def get_areas(self,obj):
        areas_resulting = []
        areas = Area.objects.filter(branch_office=obj.id,available=True)
        for area in areas:
            aux = {}
            current_area_capacity = area.maximun_capacity
            areas_reservas_confirmadas = Reserva.objects.filter(
                branch_office=obj.id,status='CONFIRMADA',area=area).count()
            # No se toma en cuenta la política, se hará al reservar 
            if areas_reservas_confirmadas < current_area_capacity:
                aux['id'] = area.id
                aux['name'] = area.name
                aux['time_block_by_time'] = area.get_time_block_by_time(timezone.now().replace(second=0, microsecond=0))
                #aux['time_blocks'] = area.get_time_blocks()
                areas_resulting.append(aux)
        return areas_resulting

    def get_total_capacity(self, obj):
        maximun_capacity = obj.area_set.all().aggregate(Sum("maximun_capacity"))
        return maximun_capacity["maximun_capacity__sum"]

    def create(self, validated_data):
        branch_office_config = BranchOfficeConfig(**validated_data.pop('branch_office_config'))
        branch_office_config.save()
        location = Location.objects.get(id=int(validated_data["location"]))
        validated_data["location"] = location
        validated_data["company"] = self.context["company"]
        branch_office = BranchOffice(**validated_data)
        branch_office.branch_office_config = branch_office_config
        branch_office.save()
        return branch_office
    
    def update(self, instance, validated_data):
        branch_office_config = instance.branch_office_config
        for attr, value in validated_data.pop("branch_office_config").items():
            setattr(branch_office_config, attr, value)
        branch_office_config.save()          
        location = Location.objects.get(id=int(validated_data["location"]))
        validated_data["location"] = location
        validated_data["company"] = self.context["company"]
        validated_data["branch_office_config"] = branch_office_config
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = '__all__'

class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = '__all__'

class AttendesByBranchOfficeSerializer(serializers.Serializer):
    first_name = serializers.CharField(source='employee.first_name')
    last_name = serializers.CharField(source='employee.last_name')


class ReservaSerializer(serializers.Serializer):
    fijo = serializers.BooleanField(read_only=True)
    start_date = serializers.DateTimeField(read_only=True)
    end_date = serializers.DateTimeField(read_only=True)
    status = serializers.CharField(read_only=True)
    branch_office = BranchOfficeSerializer(read_only=True)


class ReservaCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reserva
        exclude = ['created_date','status']


class AttendesByBranchOfficeSerializer(serializers.Serializer):
    first_name = serializers.CharField(source='employee.first_name')
    last_name = serializers.CharField(source='employee.last_name')

class ReservasByEmployeeSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    branch_office_id = serializers.IntegerField(source='branch_office.id')
    start_date = serializers.DateTimeField(read_only=True,format="%Y-%m-%d")
    block_time = serializers.SerializerMethodField(read_only=True)
    turno = serializers.SerializerMethodField(read_only=True)
    branch_office = serializers.CharField(source='branch_office.name')
    total_attendes = serializers.SerializerMethodField(read_only=True)
    area = serializers.CharField(source='area.name')
    branch_office_current_capacity = serializers.SerializerMethodField(read_only=True)
    reservas_confirmadas_sucursal = serializers.SerializerMethodField(read_only=True)
    seat = serializers.CharField(read_only=True,source='seat.id')

    def get_block_time(self,obj):
        duracion_reserva = abs((obj.start_date - obj.end_date).total_seconds())
        inicio_jornada = obj.branch_office.branch_office_config.start_date
        fin_jornada = obj.branch_office.branch_office_config.end_date
        duracion_jornada = fin_jornada.hour - inicio_jornada.hour
        medio_turno_jornada = (duracion_jornada / 2 ) * 3600
        if duracion_reserva <= medio_turno_jornada:
            return "Medio Turno"
        else:
            return "Turno Completo"

    def get_turno(self,obj):
        turno = obj.end_date.strftime("%p")
        if turno == 'AM':
            return "Mañana"
        else:
            return "Tarde"

    def get_total_attendes(self, obj):
        get_attendes = Reserva.objects.filter(
            branch_office=obj.branch_office,
            status='CONFIRMADA'
        )
        get_total_attendes = 0
        for attendes in get_attendes:
            if attendes.start_date.strftime("%d %m %Y") == obj.start_date.strftime("%d %m %Y"):
                get_total_attendes+=1
        return get_total_attendes

    def get_branch_office_current_capacity(self, obj):
        from django.db.models import Count,Sum

        branch_office = obj.branch_office.id
        branch_office_current_capacity = Area.objects.filter(
            branch_office=branch_office
        ).values('maximun_capacity').annotate(
            total=Count('maximun_capacity')
        ).order_by().aggregate(Sum('maximun_capacity'))
        if not branch_office_current_capacity['maximun_capacity__sum']:
            return 0
        return branch_office_current_capacity['maximun_capacity__sum']

    def get_reservas_confirmadas_sucursal(self, obj):
        branch_office = obj.branch_office.id
        reservas_confirmadas_sucursal = Reserva.objects.filter(
            branch_office=branch_office,status='CONFIRMADA'
        ).count()

        return reservas_confirmadas_sucursal


class ContagiousHistoryStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContagiousHistory
        exclude = ['created_date']


class ContagiousHistoryUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContagiousHistory
        fields = ['pcr_result']


# class AreaSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Area
#         fields = ['created_date']


class MinEmployeeSerializer(serializers.Serializer):
    first_name = serializers.CharField()
    last_name = serializers.CharField()

class MinReservaSerializer(serializers.Serializer):
    employee = MinEmployeeSerializer(read_only=True)
    resource = serializers.CharField(source='resource.name')
    seat = serializers.CharField(source='seat.id_in_area')
    start_date = serializers.DateTimeField()
    end_date = serializers.DateTimeField()
    status = serializers.CharField()
    fijo = serializers.BooleanField()

class AreaConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = AreaConfig
        fields = '__all__'

class AreaAlternativeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Area
        fields = ["id"]

class AreaSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(max_length=250)
    available = serializers.BooleanField()
    maximun_capacity = serializers.IntegerField(source='area_config.maximun_capacity')
    assigned_capacity = serializers.IntegerField(required=False)
    area_config = AreaConfigSerializer()
    employees_booked = MinReservaSerializer(many=True, required=False)

class WriteAreaConfigSerializer(serializers.ModelSerializer):
    class Meta:
            model = AreaConfig
            exclude = ["area"]

class WriteAreaSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=250)
    available = serializers.BooleanField()
    maximun_capacity = serializers.IntegerField()
    area_config = WriteAreaConfigSerializer(many=True, write_only=True)

    def create(self, validated_data):
        area_config_data = validated_data.pop("area_config")
        validated_data["branch_office_id"] = self.context["branch_id"]
        area = Area(**validated_data)
        area.save()

        for config in area_config_data:
            config["area"] = area
            area_config = AreaConfig(**config)
            area_config.save()
        
        current_fase = area.branch_office.location.fase
        fase_area_config = area.areaconfig_set.filter(fase=current_fase).first()
        fase_area_config.active = True
        fase_area_config.save()
        
        return area
    
    def update(self, instance, validated_data):
        areas_config_data = validated_data.pop("area_config")
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        areas_config = instance.areaconfig_set.all()
        for area_config_data in areas_config_data:
            fase = area_config_data["fase"]
            area_config = areas_config.get(fase=fase)
            for attr, value in area_config_data.items():
                setattr(area_config, attr, value)
            area_config.save()
        return instance


class MultiAreaSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=250)
    available = serializers.BooleanField()
    maximun_capacity = serializers.IntegerField()
    area_config = WriteAreaConfigSerializer(many=True, source='areaconfig_set')

class BookingStatusSerializer(BranchOfficeSerializer):
    fase = serializers.CharField()
    areas = AreaSerializer(many=True)
