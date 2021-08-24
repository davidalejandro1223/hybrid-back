from infrastructure.models import Area, BranchOffice, AreaConfig
import pandas as pd


class AreaLoader:
    def __init__(self, user, excel_file):
        self.user = user
        self.excel_file = excel_file

    def execute(self):
        excel_df = pd.read_excel(self.excel_file)

        for index, data in excel_df.iterrows():
            branch_office = BranchOffice.objects.filter(
                name=data["Sucursal"], company=self.user.get_company()
            ).first()
            if not branch_office:
                return "No existe la sucursal ingresada", 400
            
            area = Area(
                name = data["Nombre"],
                maximun_capacity = data["Capacidad"],
                branch_office = branch_office,
            )
            area.save()
            cont = 1
            for fase in AreaConfig.FASES:
                if cont!=5:
                    immobile_spaces = data[f'Fase {cont} Aforo Puestos Fijos']
                    flexible_spaces = data[f'Fase {cont} Aforo Puestos Flexible']
                else:
                    immobile_spaces = data[f'Sin Fase Aforo Puestos Fijos']
                    flexible_spaces = data[f'Sin Fase Aforo Puestos Flexible']
                
                if not immobile_spaces or not flexible_spaces:
                    continue

                fase_maximun_capacity  = immobile_spaces + flexible_spaces
                area_config = AreaConfig(
                    fase=fase[0],
                    maximun_capacity = fase_maximun_capacity,
                    immobile_spaces = immobile_spaces,
                    flexible_spaces = flexible_spaces,
                    start_date = data["Hora Inicio Jornada"],
                    end_date = data["Hora Fin Jornada"],
                    maximun_request_days_ahead = data["Maximo Días A Solicitar"],
                    area=area
                )
                area_config.save()
                cont+=1

        
        return "Areas cargadas correctamente", 200
