from rest_framework.response import Response
from rest_framework import status, filters
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView, UpdateAPIView
from rest_framework.viewsets import ModelViewSet
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

from infrastructure.models import (Country,Location,Company,BranchOfficeConfig,BranchOffice,
    BranchOfficeEmployee,Contract,AreaConfig,Resource,Area,Reserva
)
from infrastructure.repositories.branch_office import BranchOfficeRepository
from infrastructure.usecases.branch_office import (
    GetBranchOffices
)
from .serializers import (BranchOfficeSerializer, ReservaSerializer)


class BranchOfficeViewSet(ModelViewSet):
    queryset = BranchOffice.objects.all()
    serializer_class = BranchOfficeSerializer


class BranchOfficeListAPIView(ListAPIView):
    serializer_class = BranchOfficeSerializer

    def get_queryset(self):
        employee = self.request.query_params.get("employee_id")
        #company = self.request.query_params.get("company_id")
        repo = BranchOfficeRepository()
        uc_response = GetBranchOffices(
            employee, repo).execute()

        return uc_response