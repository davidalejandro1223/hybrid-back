from django.contrib import admin
from django.contrib.admin.models import UserAdmin

from users.models import User
# Register your models here.
admin.site.register(User, UserAdmin)