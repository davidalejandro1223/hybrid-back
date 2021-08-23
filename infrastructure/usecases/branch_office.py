from datetime import timedelta, date

import pandas as pd
from django.db.models import QuerySet
from django.shortcuts import get_object_or_404

from infrastructure.repositories.branch_office import BranchOfficeRepository
from infrastructure.repositories.contagious_history import ContagiousHistoryRepository
from users.models import User
from infrastructure.models import (
    Company,
    BranchOfficeConfig,
    BranchOffice,
    Country,
    Location,
)
from users.models import User


class GetBranchOffices:
    def __init__(
        self,
        employee: User,
        #company: Company,
        repo: [BranchOfficeRepository,ContagiousHistoryRepository]
    ):
        self.employee = employee
        #self.company = company
        self.repository = repo

    def execute(self) -> QuerySet:

        employee = get_object_or_404(
            User,is_active=True,is_worker=True,id=int(self.employee)
        )

        available_branch_offices = self.repository[0].get_branch_office_by_employee(
            self.employee
        )

        if available_branch_offices:
            contagious_history_date = self.repository[1].get_contagious_date_by_employee(
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

        return available_branch_offices


class BranchOfficeLoader:
    def __init__(self, user, excel_file):
        self.user = user
        self.excel_file = excel_file
    
    def execute(self):
        excel_df = pd.read_excel(self.excel_file)

        for index, data in excel_df.iterrows():
            country, created = Country.objects.get_or_create(
                nombre = data["País"]
            )
            
            location = Location.objects.filter(
                nombre = data["Locación"],
                country = country
            ).first()
            
            if not location:
                return "No existe la locación determinada", 400
            
            branch_office_config = BranchOfficeConfig(
                start_date = data["Hora Inicio Jornada"],
                end_date = data["Hora Fin Jornada"],
                maximun_request_days_contagious = data["Dias a revisar en caso contagio"],
                notify_branch_office = True if data["Notificar sucursal en caso contagio"] == "s" else False
            )
            branch_office_config.save()
            
            branch_office = BranchOffice(
                name = data["Nombre"],
                company = self.user.get_company(),
                address = data["Dirección"],
                location = location,
                branch_office_config = branch_office_config,
            )
            branch_office.save()
        
        return "Sucursales creadas satisfactoriamente", 200
