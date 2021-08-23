from rest_framework.response import Response
from rest_framework import status, filters
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated

from users.models import User
from infrastructure.models import (
    Country,
    Location,
    Company,
    BranchOfficeConfig,
    BranchOffice,
    Contract,
    AreaConfig,
    Resource,
    Area,
    Reserva
)
from employee.models import (
    ContagiousHistory,
    Policy
)
from infrastructure.usecases.area import AreaLoader
from infrastructure.usecases.contagious_history import GetEmployeeStatusContagious
from infrastructure.repositories.branch_office import BranchOfficeRepository
from infrastructure.repositories.contagious_history import ContagiousHistoryRepository
from infrastructure.usecases.branch_office import (
    GetBranchOffices,
    BranchOfficeLoader
)
from .serializers import (
    BranchOfficeSerializer,
    ReservaSerializer,
    ContagiousHistoryStatusSerializer,
    ContagiousHistoryUpdateSerializer,
    AreaSerializer
)


class BranchOfficeViewSet(ModelViewSet):
    serializer_class = BranchOfficeSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return BranchOffice.objects.filter(
            company=self.request.user.get_company()
        )


class BranchOfficeListAPIView(generics.ListAPIView):
    serializer_class = BranchOfficeSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        employee = self.request.query_params.get("employee_id")
        #company = self.request.query_params.get("company_id")
        repo = BranchOfficeRepository(),ContagiousHistoryRepository()
        uc_response = GetBranchOffices(
            employee, repo).execute()

        return uc_response


class ContagiousHistoryCreateAPIView(generics.CreateAPIView):
    serializer_class = ContagiousHistoryStatusSerializer
    permission_classes = [IsAuthenticated]


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


class BranchOfficeLoaderAPIView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user
        excel_file = request.data["excel_file"]
        uc = BranchOfficeLoader(user, excel_file)
        response, status = uc.execute()
        return Response(data={"status":response}, status=status)


class AreaLoaderAPIView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user
        excel_file = request.data["excel_file"]
        uc = AreaLoader(user, excel_file)
        response, status = uc.execute()
        return Response(data={"status":response}, status=status)

