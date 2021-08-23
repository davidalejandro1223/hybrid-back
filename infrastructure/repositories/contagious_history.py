import datetime

from django.utils import timezone
from django.db.models import Q, QuerySet, CharField, DateField

from infrastructure.models import (Country,Location,Company,BranchOfficeConfig,BranchOffice,
    Contract,AreaConfig,Resource,Area,Reserva
)
from users.models import (User)
from employee.models import (ContagiousHistory)

class ContagiousHistoryRepository:
    def get_contagious_history_by_employee(
        self, employee: User
    ) -> QuerySet:

        return ContagiousHistory.objects.filter(
            employee=employee,pcr_result='P'
        ).last()

    def get_contagious_date_by_employee(
        self, employee: User
    ) -> DateField:

        contagious_result = ContagiousHistory.objects.filter(
            employee=employee
        ).last()

        if contagious_result:
            return contagious_result.fecha_sintomas
