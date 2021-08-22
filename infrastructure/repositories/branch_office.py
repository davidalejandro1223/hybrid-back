from django.utils import timezone
from django.db.models import Q, QuerySet

from infrastructure.models import (Country,Location,Company,BranchOfficeConfig,BranchOffice,
    BranchOfficeEmployee,Contract,AreaConfig,Resource,Area,Reserva
)
from users.models import User

class BranchOfficeRepository:
    def get_branch_office_by_employee(
        self, employee: User
    ) -> QuerySet:
        contracts =  Contract.objects.filter(
            employee=employee
        ).values_list("branch_offices", flat=True)


