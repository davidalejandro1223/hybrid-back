from datetime import timedelta, timezone, datetime
from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView

from employee.models import Policy
from users.models import User
from employee.serializers import (
    WritePolicySerializer,
    GetPolicySerializer,
    EmployeeProfileSerializer,
    EmployeeSerializer
)

from employee.tasks import notify_positive_covid
from employee.usecases import EmployeeLoader
from users.models import User
from infrastructure.models import Contract, Reserva
from infrastructure.repositories.contagious_history import ContagiousHistoryRepository
from infrastructure.serializers import ReservasByEmployeeSerializer

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

class NotifyCovidCaseAPI(APIView):
    
    def post(self, request, employee_pk):
        employee = User.objects.get(id=employee_pk)
        repo = ContagiousHistoryRepository()
        last_report = repo.get_contagious_history_by_employee(employee)
        
        try:
            if last_report.pcr_result=='p':
                contract_branch_offices = list(employee.contract_set.first().branch_offices)
                preferred_branch_offices = list(employee.policy_set.first().branch_office_favorited)
                all_branch_offices = contract_branch_offices + preferred_branch_offices
                for branch_office in all_branch_offices:
                    notify = branch_office.notify_branch_office
                    if not notify:
                        continue
                    days_to_review_contagious = branch_office.days_to_review_contagious
                    notify_since = last_report.fecha_reporte - timedelta(days=days_to_review_contagious)
                    
                    reservas_employee = Reserva.objects.filter(
                        start_date__gte = notify_since,
                        branch_office = branch_office,
                        status__in = ['CONFIRMADA'],
                        employee = employee
                    )
                    
                    already_emails_sent = []
                    for reserva_employee in reservas_employee:

                        risk_reservas = Reserva.objects.filter(
                            start_date__lte = reserva_employee.start_date,
                            end_date__gte = reserva_employee.end_date,
                            branch_office = branch_office,
                            status__in = ['ASIGNADA', 'CONFIRMADA']
                        )

                        for reserva in risk_reservas:
                            reserva_employee = reserva.employee
                            if not reserva_employee in already_emails_sent:
                                notify_positive_covid(reserva_employee)
                                already_emails_sent.append(reserva_employee)

                    reservas_to_cancel = Reserva.objects.filter(
                        start_date__gte = timezone.now(),
                        branch_office = branch_office,
                        employee__in = already_emails_sent
                    )
                    reservas_to_cancel.update(status="CANCELADA")
                return Response(date={'status':'Los empleados fueron notificados y sus reservas canceladas'}, status=200)            
            else:
                return Response(data={'status':"El ultimo reporte del usuario no indica PCR positivo"}, status=200)
        except AttributeError:
            return Response(data={'status':"El usuario no tiene reporte por covid"}, status=200)

class UpdateReservaStatus(APIView):
    serializer_class = ReservasByEmployeeSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, reserva_pk):
        try:
            reserva = Reserva.objects.get(id=reserva_pk)
        except:
            return Response(data={"status": f"No existe la reserva con id {reserva_pk}"}, status=400)
        
        if not request.user == reserva.employee: 
            return Response(data={"status": "No puede modificar una reserva de otra persona"}, status=400)
        
        action = request.query_params["action"]
        if action == "CONFIRMADA":
            now = datetime.now()
            confirm_window = reserva.start_date - timedelta(minutes=5)
            if confirm_window > now:
                return Response(data={"status": "Solo se puede confirmar una reserva 5 minutos antes de su inicio"}, status=400)
        reserva.status = action
        reserva.save()

        return Response(data={"status": f"Reserva {action.capitalize()}"}, status=200)

