from infrastructure.models import BranchOffice, Contract
from rest_framework import serializers

from employee.models import Policy, Resource
from users.serializers import UserSerializer
from infrastructure.serializers import BranchOfficeSerializer

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

class ContractSerializer(serializers.Serializer):
    job_title = serializers.CharField()
    minimum_attendance = serializers.IntegerField()
    start_date = serializers.DateField()
    end_date = serializers.DateField()
    active = serializers.BooleanField(read_only=True)
    branch_offices = BranchOfficeSerializer(allow_null=True, many=True,)

class EmployeeSerializer(UserSerializer):
    policy = GetPolicySerializer(allow_null=True, required=False, source='policy_user_id.first')
    contract = ContractSerializer(allow_null=True, required=False, source='contract_set.first')

    def create(self, validated_data):
        employee = super().create(validated_data)
        branch_offices_ids = [x["id"] for x in validated_data["contract_set"]["first"]["branch_offices"]]
        branch_offices = BranchOffice.objects.filter(id__in=branch_offices_ids)

        contract = Contract(
            employee = employee,
            company = self.context["company"],
            job_title = validated_data["contract_set"]["first"]["job_title"],
            minimum_attendance = validated_data["contract_set"]["first"]["minimum_attendance"],
            start_date = validated_data["contract_set"]["first"]["start_date"],
            end_date = validated_data["contract_set"]["first"]["end_date"]
        )
        contract.save()
        contract.branch_offices.set(branch_offices)
        return employee
    
    def update(self, instance, validated_data):
        branch_offices_ids = [x["id"] for x in validated_data["contract_set"]["first"]["branch_offices"]]
        branch_offices = BranchOffice.objects.filter(id__in=branch_offices_ids)
        
        for attr, value in validated_data.items():
            if attr != "contract_set":
                setattr(instance, attr, value)
        instance.save()
        
        contract = instance.contract_set.first()
        for attr, value in validated_data["contract_set"]["first"].items():
            if attr != "branch_offices":
                setattr(contract, attr, value)
        
        contract.branch_offices.set(branch_offices)
        contract.save()
        return instance

