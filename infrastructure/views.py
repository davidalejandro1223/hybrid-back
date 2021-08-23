from rest_framework.response import Response
from rest_framework import status, filters
from rest_framework import generics
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from infrastructure.models import (Country,Location,Company,BranchOfficeConfig,BranchOffice,
    Contract,AreaConfig,Resource,Area,Reserva
)
from users.models import User
from infrastructure.repositories.branch_office import BranchOfficeRepository
from infrastructure.repositories.contagious_history import ContagiousHistoryRepository
from infrastructure.usecases.branch_office import GetBranchOffices
from infrastructure.usecases.contagious_history import GetEmployeeStatusContagious
from .serializers import (BranchOfficeSerializer,ReservaSerializer,
    ContagiousHistoryStatusSerializer,ContagiousHistoryUpdateSerializer)
from employee.models import ContagiousHistory,Policy

class BranchOfficeViewSet(ModelViewSet):
    queryset = BranchOffice.objects.all()
    serializer_class = BranchOfficeSerializer
    permission_classes = [IsAuthenticated]


class BranchOfficeListAPIView(generics.ListAPIView):
    serializer_class = BranchOfficeSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        employee = self.request.query_params.get("employee_id")
        #company = self.request.query_params.get("company_id")
        repo = BranchOfficeRepository()
        uc_response = GetBranchOffices(
            employee, repo).execute()

        return uc_response


class ContagiousHistoryView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == "PUT":
            return ContagiousHistoryUpdateSerializer
        if self.request.method == "GET":
            return ContagiousHistoryStatusSerializer

    def get_object(self):
        employee = self.kwargs["employee_pk"]
        repo = ContagiousHistoryRepository()
        uc_response = GetEmployeeStatusContagious(
            employee, repo).execute()
        return uc_response
