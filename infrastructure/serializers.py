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
