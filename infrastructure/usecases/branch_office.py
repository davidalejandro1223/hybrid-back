from typing import Union
import datetime

from django.db.models import QuerySet

from infrastructure.repositories.branch_office import BranchOfficeRepository
from infrastructure.models import (Company,BranchOfficeConfig,BranchOffice,
)
from users.models import User

class GetBranchOffices:
    def __init__(
        self,
        employee: User,
        #company: Company,
        repo: BranchOfficeRepository,
    ):
        self.employee = employee
        #self.company = company
        self.repository = repo

    def execute(self) -> QuerySet:
        available_branch_offices = self.repository.get_branch_office_by_employee(
            self.employee
        )

        return available_branch_offices
