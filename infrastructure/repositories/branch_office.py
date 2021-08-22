from django.utils import timezone
from django.db.models import Q, QuerySet

from infrastructure.models import (Country,Location,Company,BranchOfficeConfig,BranchOffice,
    BranchOfficeEmployee,Contract,AreaConfig,Resource,Area,Reserva
)
from users.models import User

class BranchOfficeRepository:
    def get_branch_office_by_company(
        self, employee: User
    ) -> QuerySet:
        return BranchOffice.objects.filter(
            branchofficeemployee=employee
        )

