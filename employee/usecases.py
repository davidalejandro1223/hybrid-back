from datetime import datetime, timedelta
import pandas as pd

from employee.models import Policy
from infrastructure.models import Contract, Reserva, Resource, Seat, Area, BranchOffice
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
            
            if data["Puesto"] and area:
                seat = Seat.objects.filter(
                    resource__area = area,
                    id_in_area = data["Puesto"]
                ).first()
                resource = seat.resource
            else:
                return "No se puede asignar un puesto sin un area", 400
            
            translated_days = []
            if data["Jornada"]:
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
                minimum_attendance = minimum_attendance or 0,
                start_date = data["Fecha Inicio Contrato"],
                end_date = data["Fecha Termino Contrato"],
            )
            contract.save()
            contract.branch_offices.set(branch_offices)

            if area or resource or seat or translated_days:
                policy = Policy(
                    employee = employee,
                    area = area,
                    resource = resource,
                    seat = seat,
                    days_of_the_week = translated_days,
                    assigned_by_admin = True
                )
                policy.save()
                if policy.seat:
                    GenerateReservasWithPolicy(policy).execute()

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

class GenerateReservasWithPolicy:
    def __init__(self, policy):
        self.policy = policy

    def execute(self):
        area = self.policy.area
        seat = self.policy.seat
        branch_office = area.branch_office
        area_block = area.get_time_blocks()[0]["bloque 1"]
        start_date = datetime.now().replace(
            hour=area_block["start_time"].hour, 
            minute=area_block["start_time"].minute
        
        )
        end_date = datetime.now().replace(
            hour=area_block["end_time"].hour, 
            minute=area_block["end_time"].minute
        
        )
        for i in range(0, 31):
            start_date = start_date + timedelta(days=i)
            end_date = end_date + timedelta(days=i)
            reserva = Reserva(
                fijo=True,
                start_date=start_date,
                end_date= end_date,
                status="ASIGNADA",
                employee=self.policy.employee,
                branch_office=branch_office,
                seat=seat,
                area=area
            )
            reserva.save()

