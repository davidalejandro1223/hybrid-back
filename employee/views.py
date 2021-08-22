from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from employee.models import Policy
from employee.serializers import WritePolicySerializer, GetPolicySerializer


class ListCreatePolicy(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        pk_employee = self.kwargs["employee_pk"]
        if pk_employee == self.request.user.pk or self.request.user.is_company_admin:
            return Policy.objects.filter(employee=self.request.user)

    def get_serializer_class(self):
        if self.request.method == "POST":
            return WritePolicySerializer
        if self.request.method == "GET":
            return GetPolicySerializer

class UpdateDeleteRetrievePolicy(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]

    def get_object(self):
        pk_employee = self.kwargs["employee_pk"]
        pk_policy = self.kwargs["policy_pk"]
        if pk_employee == self.request.user.pk or self.request.user.is_company_admin:
            return Policy.objects.get(id=pk_policy)
        
    def get_serializer_class(self):
        if self.request.method == "PUT":
            return WritePolicySerializer
        if self.request.method == "GET":
            return GetPolicySerializer

