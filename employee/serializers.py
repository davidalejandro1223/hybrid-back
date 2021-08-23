from rest_framework import serializers

from users.models import User
from employee.models import Policy, Resource, ContagiousHistory

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
    branch_office_favorited = serializers.CharField(max_length=250)
    created = serializers.DateTimeField()
    updated = serializers.DateTimeField()


class WritePolicySerializer(serializers.ModelSerializer):
    days_of_the_week = serializers.ListField(
        child=serializers.CharField(max_length=200)
    )
    class Meta:
        model = Policy
        exclude = ['created', 'updated']


class EmployeeProfileSerializer(serializers.Serializer):
    first_name = serializers.CharField(read_only=True)
    last_name = serializers.CharField(read_only=True)
    email = serializers.EmailField(read_only=True)
    user_identification = serializers.CharField(read_only=True)
    cellphone_number = serializers.CharField(read_only=True)
    mobility_permit = serializers.FileField(read_only=True)
    policy = GetPolicySerializer(source='policy_user_id.first')
    is_infected = serializers.SerializerMethodField(read_only=True)

    def get_is_infected(self, obj):
        contagious_history = None
        contagious_history = ContagiousHistory.objects.filter(
            employee=obj,pcr_result='P'
        ).last()
        if contagious_history:
            return True
        else:
            return False