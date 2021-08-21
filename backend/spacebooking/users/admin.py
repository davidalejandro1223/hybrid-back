from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from users.models import User
from employee.models import (
	ContagiousHistory,
	BaseWorkGroup,
	WorkGroup
)
from infrastructure.models import (
	Country,
	Location,
	Company,
	BranchOfficeConfig,
	BranchOffice,
	BranchOfficeEmployee,
	Contract,
	AreaConfig,
	Area,
	Reserva
)

admin.site.register(User, UserAdmin)
admin.site.register(ContagiousHistory)
admin.site.register(BaseWorkGroup)
admin.site.register(WorkGroup)
admin.site.register(Country)
admin.site.register(Location)
admin.site.register(Company)
admin.site.register(BranchOfficeConfig)
admin.site.register(BranchOffice)
admin.site.register(BranchOfficeEmployee)
admin.site.register(Contract)
admin.site.register(AreaConfig)
admin.site.register(Area)
admin.site.register(Reserva)
