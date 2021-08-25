from infrastructure.models import BranchOffice, Contract, Seat
from rest_framework import serializers

from users.models import User
from employee.models import Policy, Resource, ContagiousHistory
from users.serializers import UserSerializer
from infrastructure.serializers import BranchOfficeSerializer
from employee.usecases import GenerateReservasWithPolicy
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

    def create(self, validated_data):
        if validated_data["seat"]:
            seat = Seat.objects.filter(
                    resource__area_id = validated_data["area"],
                    id_in_area = validated_data["seat"].id
                ).first()
            validated_data["seat"]=seat
            validated_data["resource"]=seat.resource
        policy = super().create(validated_data)
        if policy.seat and policy.assigned_by_admin:
            GenerateReservasWithPolicy(policy).execute()
        return policy

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
    is_company_admin = serializers.BooleanField(read_only=True)
    is_worker = serializers.BooleanField(read_only=True)
    favorited_area = serializers.SerializerMethodField(read_only=True,default=None)

    def get_is_infected(self, obj):
        contagious_history = None
        contagious_history = ContagiousHistory.objects.filter(
            employee=obj,pcr_result='P'
        ).last()
        if contagious_history:
            return True
        else:
            return False

    def get_favorited_area(self, obj):
        favorited_area = Policy.objects.filter(
            employee=obj
        ).last()
        if favorited_area and favorited_area.area:
            return favorited_area.area.name


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

