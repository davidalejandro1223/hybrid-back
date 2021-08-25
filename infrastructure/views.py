import io
from rest_framework.response import Response
from rest_framework import status, filters
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from datetime import datetime, timedelta
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from wsgiref.util import FileWrapper
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
from infrastructure.tasks import send_email, send_cancel_email_by_fase

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
    permission_classes = [IsAuthenticated]

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
        branch_office = BranchOffice.objects.get(id=branch_office)
        now = datetime.now().replace(second=0, microsecond=0)
        full_reservas = Reserva.objects.filter(
            start_date__lte=now,
            branch_office=branch_office
        )
        
        employees = full_reservas.distinct("employee").values_list("employee", flat=True)
        employees = User.objects.filter(id__in=employees)
        
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

        list_risk_reservas = []
        for employee in employees:
            last_report = ContagiousHistoryRepository().get_last_contagious_history(employee)
            try:
                if last_report.pcr_result =='P':
                    days_to_review_contagious = branch_office.days_to_review_contagious
                    notify_since = last_report.fecha_reporte - timedelta(days=days_to_review_contagious)
                    reservas_infected_employee = Reserva.objects.filter(
                        start_date__gte = notify_since,
                        branch_office = branch_office,
                        status__in = ['CONFIRMADA', 'ASIGNADA'],
                        employee = employee
                    )
                    
                    for reserva_employee in reservas_infected_employee:
                        risk_reservas = Reserva.objects.filter(
                            start_date__lte = reserva_employee.start_date,
                            end_date__gte = reserva_employee.end_date,
                            branch_office = branch_office,
                            status__in = ['ASIGNADA', 'CONFIRMADA']
                        )
                        for reserva in risk_reservas:
                            list_risk_reservas.append({
                                "Contagiado": employee,
                                "Fecha sintomas": last_report.fecha_sintomas,
                                "Fecha PCR positivo": last_report.fecha_reporte,
                                "Trabajador": reserva.employee,
                                "Fecha de contacto (inicio)": reserva.start_date,
                                "Fecha de contacto (fin)": reserva.end_date,
                                "Sucursal":reserva.branch_office,
                                "Area": reserva.area,
                                "Puesto": reserva.puesto
                            })
            except:
                pass
        
        df_infected = pd.DataFrame(list_risk_reservas)
        buffer = io.BytesIO()
        writer =  pd.ExcelWriter(buffer)
        df_reservas.to_excel(writer, sheet_name="Reservas")
        df_infected.to_excel(writer, sheet_name="Trazabilidad")
        writer.save()
        buffer.seek(0)
        
        response = HttpResponse(buffer, content_type='application/msexcel')
        response['Content-Disposition'] = 'attachment; filename="reporte-covid.xlsx"'
        return response

class LocationsByCompanyAPIView(generics.ListAPIView):
    serializer_class = LocationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        company = self.request.user.get_company()
        return Location.objects.filter(branchoffice_location_id__company=company).distinct()

class ChangeFaseInLocation(generics.UpdateAPIView):
    serializer_class = LocationSerializer
    permission_classes = [IsAuthenticated]
    queryset = Location.objects.all()
    
    def put(self, request, pk):
        response = super().put(request, pk)
        location = self.get_object()
        branch_offices = BranchOffice.objects.filter(
            location = location,
            company = self.request.user.get_company()
        )
        cancel_since = datetime.now().replace(hour=23, minute=50)

        for branch_office in branch_offices:
            
            current_area_config = AreaConfig.objects.filter(
                area__in=branch_office.area_set.all(),
                active=True
            ).update(active=False)
            new_area_config = AreaConfig.objects.filter(
                area__in=branch_office.area_set.all(),
                fase=location.fase
            ).update(active=True)
            
            policies = Policy.objects.filter(
                branch_office_favorited=branch_office,
                assigned_by_admin=True
            )
            if len(policies)>branch_office.current_immobile_spaces:
                policies.update(assigned_by_admin=False)

            cancel_reservas = Reserva.objects.filter(
                start_date__gte=cancel_since,
                branch_office = branch_office,
                status__in =["ASIGNADA", "CONFIRMADA"]
            )
            cancel_reservas.update(status="CANCELADA")

            for reserva in cancel_reservas:
                send_cancel_email_by_fase(reserva.employee)

        return response
