from datetime import timedelta, date

from django.db.models import QuerySet
from django.shortcuts import get_object_or_404

from infrastructure.repositories.branch_office import BranchOfficeRepository
from infrastructure.models import (Company,BranchOfficeConfig,BranchOffice)
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

        employee = get_object_or_404(
            User,is_active=True,is_worker=True,id=int(self.employee)
        )

        available_branch_offices = self.repository.get_branch_office_by_employee(
            self.employee
        )

        contagious_history_date = self.repository.get_contagious_history_by_employee(
            self.employee
        )

        if contagious_history_date:
            branch_offices_without_risk = [] 
            for branch_office in available_branch_offices:
                config_days = branch_office.branch_office_config.maximun_request_days_contagious
                risk_days = contagious_history_date + timedelta(days=config_days)

                # Aún está en riesgo de contagio para esta sucursal
                if risk_days > date.today():
                    continue
                else:
                    branch_offices_without_risk.append(branch_office)
            return branch_offices_without_risk
        else:
            return available_branch_offices

