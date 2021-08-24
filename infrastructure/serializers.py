from django.contrib.auth import get_user_model
from rest_framework import serializers

from infrastructure.models import (Country,Location,Company,BranchOfficeConfig,BranchOffice,
    Contract,AreaConfig,Resource,Area,Reserva,
)
from employee.models import (ContagiousHistory)

User = get_user_model()

class BranchOfficeSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField(read_only=True)
    location = serializers.CharField(read_only=True)
    address = serializers.CharField(read_only=True)
    available_capacity = serializers.IntegerField(read_only=True)
    assigned_capacity = serializers.IntegerField(read_only=True)


class AttendesByBranchOfficeSerializer(serializers.Serializer):
    first_name = serializers.CharField(source='employee.first_name')
    last_name = serializers.CharField(source='employee.last_name')


class ReservaSerializer(serializers.Serializer):
    fijo = serializers.BooleanField(read_only=True)
    start_date = serializers.DateTimeField(read_only=True)
    end_date = serializers.DateTimeField(read_only=True)
    status = serializers.CharField(read_only=True)
    branch_office = BranchOfficeSerializer(read_only=True)


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
        #import pdb;pdb.set_trace()
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


class AreaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Area
        fields = ['created_date']


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

class AreaSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField(max_length=250)
    available = serializers.BooleanField()
    maximun_capacity = serializers.IntegerField(source='area_config.maximun_capacity')
    assigned_capacity = serializers.IntegerField()
    area_config = AreaConfigSerializer()
    employees_booked = MinReservaSerializer(many=True)

class BookingStatusSerializer(BranchOfficeSerializer):
    fase = serializers.CharField()
    areas = AreaSerializer(many=True)
