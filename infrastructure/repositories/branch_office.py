from django.utils import timezone
from django.db.models import Q, QuerySet

from infrastructure.models import (Country,Location,Company,BranchOfficeConfig,BranchOffice,
    Contract,AreaConfig,Resource,Area,Reserva
)
from users.models import User

class BranchOfficeRepository:
    def get_branch_office_by_employee(
        self, employee: User
    ) -> QuerySet:

        branch_offices =  Contract.objects.filter(
            employee=int(employee)
        ).values_list("branch_offices", flat=True)

        return BranchOffice.objects.filter(
            id__in=branch_offices)

