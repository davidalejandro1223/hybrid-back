from rest_framework.response import Response
from rest_framework import status, filters
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from datetime import datetime
from django.shortcuts import get_object_or_404
import pandas as pd
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
    BranchOfficeLoader,
    GetBranchOfficeBookingStatus
)
from .serializers import (
    BranchOfficeSerializer,
    ReservaSerializer,
    ContagiousHistoryStatusSerializer,
    ContagiousHistoryUpdateSerializer,
    AreaSerializer,
    BookingStatusSerializer,
    AttendesByBranchOfficeSerializer,
    LocationSerializer,
    CountrySerializer,
    WriteAreaSerializer,
    MultiAreaSerializer,
    ReservasByEmployeeSerializer
)
from infrastructure.tasks import send_email

class BranchOfficeViewSet(ModelViewSet):
    serializer_class = BranchOfficeSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return BranchOffice.objects.filter(
            company=self.request.user.get_company()
        )
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["company"] = self.request.user.get_company()
        return context

class LocationListAPIView(generics.ListAPIView):
    serializer_class = LocationSerializer
    permissions_classes = [IsAuthenticated]

    def get_queryset(self):
        country = self.kwargs['country_id']
        return Location.objects.filter(country_id=country)

class CountryListAPIView(generics.ListAPIView):
    serializer_class = CountrySerializer
    permission_classes = [IsAuthenticated]
    queryset = Country.objects.all()

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

class AttendesByBranchOfficeListAPIView(generics.ListAPIView):
    serializer_class = AttendesByBranchOfficeSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        pk_branch_office = self.kwargs["branch_office_pk"]
        branch_office = get_object_or_404(
            BranchOffice,id=pk_branch_office
        )
        attendes = Reserva.objects.filter(
            branch_office=branch_office,status='CONFIRMADA')
        return attendes

class ReservasByEmployeeListAPIView(generics.ListAPIView):
    serializer_class = ReservasByEmployeeSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        pk_employee = self.kwargs["employee_pk"]
        employee = get_object_or_404(
            User,id=pk_employee
        )
        reservas = Reserva.objects.filter(
            status='ASIGNADA',
            employee=employee
        ).order_by('-start_date')
        return reservas


class ContagiousHistoryCreateAPIView(generics.CreateAPIView):
    serializer_class = ContagiousHistoryStatusSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        pk_employee = request.data["employee"]
        employee = get_object_or_404(
            User,id=pk_employee
        )
        company = employee.get_company()
        admin = Contract.objects.filter(
            company=company,employee__is_company_admin=True
        ).first().employee
        data = {}
        data["sender"] = employee
        data["admin"] = admin
        data["reported_date"] = request.data["fecha_reporte"]
        data["template_file"] = 'covid_admin_notification.html'
        data["message_description"] = 'Notificación Covid'
        data["subject"] = f'{employee.first_name} {employee.last_name} ha reportado Covid'
        send_email(data)
        return Response(data={"msj": "Email enviado"}, status=status.HTTP_200_OK)


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

class BookingStatusAPIView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, branch_office_id):
        uc = GetBranchOfficeBookingStatus(branch_office_id, datetime.now().replace(second=0, microsecond=0))
        data = uc.execute()
        serializer = BookingStatusSerializer(data)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

# class AreasViewSet(ModelViewSet):
#     permission_classes = [IsAuthenticated]

#     def get_queryset(self):
#         company = self.request.user.get_company()
#         return Area.objects.filter(branch_office__company=company)
    
#     def get_serializer_class(self):
#         if self.request.method in ['PUT','POST']:
#             return WriteAreaSerializer
#         return AreaSerializer

class CreateListAreaAPIView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Area.objects.filter(branch_office_id=self.kwargs["branch_office"])

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return WriteAreaSerializer
        return AreaSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["branch_id"] = self.kwargs["branch_office"]
        return context

class RetrieveUpdateDestroyAreaAPIView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Area.objects.filter(branch_office_id=self.kwargs["branch_office"])
    
    def get_serializer_class(self):
        if self.request.method =='PUT':
            return WriteAreaSerializer
        return MultiAreaSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["branch_id"] = self.kwargs["branch_office"]
        return context 

class CovidReportAPIView(APIView):
    def get(self, request, branch_office):
        now = datetime.now().replace(second=0, microsecond=0)
        full_reservas = Reserva.objects.filter(
            start_date__lte=now,
            branch_office_id=branch_office
        )
        
        employees = full_reservas.distinct("employee").values("employee")
        
        data_full_reservas = full_reservas.values(
            "employee__first_name",
            "employee__last_name",
            "start_date",
            "end_date",
            "branch_office__name",
            "area__name",
            "seat__id_in_area",
            "status",
        )
        
        df_reservas = pd.DataFrame(list(data_full_reservas))
        df_reservas.columns = [
                "Nombres Trabajador", 
                "Apellidos Trabajador",
                "Fecha inicio reserva",
                "Fecha fin reserva",
                "Sucursal",
                "Area",
                "Puesto",
                "Estado"
        ]
        pass