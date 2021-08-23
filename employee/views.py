from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from employee.models import Policy
from users.models import User
from employee.serializers import (
    WritePolicySerializer,
    GetPolicySerializer,
    EmployeeProfileSerializer,
    EmployeeSerializer
)

from employee.usecases import EmployeeLoader
from users.models import User
from infrastructure.models import Contract

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

class EmployeeLoaderView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        excel = request.data["excel_file"]
        user = request.user
        uc = EmployeeLoader(excel, user)
        response, status = uc.execute()
        return Response(data={'status': response}, status=status)

class GetEmployeesAPIView(ModelViewSet):
    serializer_class = EmployeeSerializer
    
    def get_queryset(self):
        return User.objects.filter(contract__company=self.request.user.get_company())

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["company"] = self.request.user.get_company()
        return context

class EmployeeProfileView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = EmployeeProfileSerializer

    def get_object(self):
        pk_employee = self.kwargs["employee_pk"]
        employee = get_object_or_404(
            User,is_active=True,is_worker=True,pk=pk_employee
        )
        return User.objects.get(id=pk_employee)
