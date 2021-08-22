from rest_framework import serializers

from employee.models import Policy, Resource

class MinAreaSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField(max_length=250)


class MinResourceSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField(max_length=250)
    tipo = serializers.ChoiceField(choices=Resource.TIPO)
    reservable = serializers.BooleanField()
    compartible = serializers.BooleanField()


class GetPolicySerializer(serializers.Serializer):
    id = serializers.IntegerField()
    area = MinAreaSerializer(allow_null=True)
    resource = MinResourceSerializer(allow_null=True)
    seat = serializers.IntegerField(source="seat.id_in_area", allow_null=True)
    days_of_the_week = serializers.ListField(
        child=serializers.CharField(max_length=200),
        source='get_days_of_the_week_verbose'
    )
    assigned_by_admin = serializers.BooleanField()
    created = serializers.DateTimeField()
    updated = serializers.DateTimeField()

class WritePolicySerializer(serializers.ModelSerializer):
    days_of_the_week = serializers.ListField(
        child=serializers.CharField(max_length=200)
    )
    class Meta:
        model = Policy
        exclude = ['created', 'updated']

