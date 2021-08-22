from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from users.models import User
from employee.models import (
	ContagiousHistory,
	Policy
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
	Reserva,
	Resource
)

class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ('email', 'is_staff', 'is_active',)
    list_filter = ('email', 'is_staff', 'is_active',)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Permissions', {'fields': ('is_staff', 'is_active')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'is_staff', 'is_active')}
        ),
    )
    search_fields = ('email',)
    ordering = ('email',)
    

admin.site.register(User, CustomUserAdmin)
admin.site.register(ContagiousHistory)
admin.site.register(Policy)
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
admin.site.register(Resource)
