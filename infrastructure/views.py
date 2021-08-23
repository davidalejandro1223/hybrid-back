from rest_framework.response import Response
from rest_framework import status, filters
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView, UpdateAPIView, CreateAPIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

from infrastructure.models import (Country,Location,Company,BranchOfficeConfig,BranchOffice,
    Contract,AreaConfig,Resource,Area,Reserva
)
from infrastructure.repositories.branch_office import BranchOfficeRepository
from infrastructure.usecases.branch_office import (
    GetBranchOffices,
    BranchOfficeLoader
)
from .serializers import (BranchOfficeSerializer, ReservaSerializer)


class BranchOfficeViewSet(ModelViewSet):
    queryset = BranchOffice.objects.all()
    serializer_class = BranchOfficeSerializer
    permission_classes = [IsAuthenticated]


class BranchOfficeListAPIView(ListAPIView):
    serializer_class = BranchOfficeSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        employee = self.request.query_params.get("employee_id")
        #company = self.request.query_params.get("company_id")
        repo = BranchOfficeRepository()
        uc_response = GetBranchOffices(
            employee, repo).execute()

        return uc_response

class BranchOfficeLoaderAPIView(CreateAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user
        excel_file = request.data["excel_file"]
        uc = BranchOfficeLoader(user, excel_file)
        response, status = uc.execute()
        return Response(data={"status":response}, status=status)
