import pandas as pd

from employee.models import Policy
from infrastructure.models import Contract, Resource, Seat, Area, BranchOffice
from users.models import User
from users.tasks import send_confirmation_email


class EmployeeLoader:
    def __init__(self, excel, user):
        self.user = user
        self.excel = excel

    def execute(self):
        excel_df = pd.read_excel(self.excel)
        for index, data in excel_df.iterrows():
            branch_offices = None
            area = None
            resource = None
            seat = None

            if data["Sucursales"]:
                branch_offices = BranchOffice.objects.filter(
                    company=self.user.get_company(),
                    name__in=data["Sucursales"].split(", ")
                )
                if not branch_offices:
                    return "No se encontraron las sucursales", 400
            
            if data["Área"] and branch_offices:
                area = Area.objects.filter(
                    name=data["Área"],
                    branch_office__in=branch_offices
                ).first()
            else:
                return "No se puede asignar un area sin una sucursal", 400
            
            if data["Recurso"] and area:
                resource = Resource.objects.filter(
                    name = data["Recurso"],
                    area = area
                ).first()
            else:
                return "No se puede asignar un recurso sin un area", 400
            
            if data["Puesto"] and resource:
                seat = Seat.objects.filter(
                    resource = resource,
                    id_in_area = data["Puesto"]
                ).first()
            else:
                return "No se puede asignar un puesto sin un recurso", 400
            
            translated_days = self.convert_language_days(data["Jornada"].split(", "))
            
            minimum_attendance = data["Minimo Dias Asistencia"]
            if not minimum_attendance:
                minimum_attendance = len(translated_days)

            employee = User.objects.create_user(
                first_name = data["Nombres"],
                last_name = data["Apellidos"],
                user_identification = data["N°Identificación"],
                email = data["Correo"],
                is_worker = True,
                is_active = False
            )
            send_confirmation_email(employee)

            contract = Contract(
                employee = employee,
                company = self.user.get_company(),
                job_title = data["Cargo"],
                minimum_attendance = minimum_attendance,
                start_date = data["Fecha Inicio Contrato"],
                end_date = data["Fecha Termino Contrato"],
            )
            contract.save()
            contract.branch_offices.set(branch_offices)

            policy = Policy(
                employee = employee,
                area = area,
                resource = resource,
                seat = seat,
                days_of_the_week = translated_days,
                assigned_by_admin = True
            )
            policy.save()

        return "Trabajadores creados correctamente", 200   

    
    def convert_language_days(self, days):
        days = [day.lower() for day in days]
        equivalent_days = (
            ("lunes", "Monday"),
            ("martes", "Tuesday"),
            ("miércoles", "Wednesday"),
            ("jueves", "Thursday"),
            ("viernes", "Friday"),
            ("sabado", "Saturday"),
            ("domingo", "Sunday"),
        )
        translated_days = []

        for day in equivalent_days:
            if day[0] in days:
                translated_days.append(day[1])
        return translated_days
