from typing import Union
import datetime

from django.db.models import QuerySet

from infrastructure.repositories.branch_office import BranchOfficeRepository
from infrastructure.models import (
    Company,
    BranchOfficeConfig,
    BranchOffice,
    Country,
    Location,
)
from users.models import User

import pandas as pd

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

        return 

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



