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

            area_config = AreaConfig(
                fase=data["Fase actual"],
                maximun_capacity = data["Aforo maximo actual"],
                immobile_spaces = data["Puestos Fijos"],
                flexible_spaces = data["Puestos Flexibles"],
                start_date = data["Hora Inicio Jornada"],
                end_date = data["Hora Fin Jornada"],
                maximun_request_days_ahead = data["Maximo Días A Solicitar"]
            )
            area_config.save()

            area = Area(
                name = data["Nombre"],
                maximun_capacity = data["Aforo"],
                branch_office = branch_office,
                branch_area_config = area_config,
            )
            area.save()
        
        return "Areas cargadas correctamente", 200
