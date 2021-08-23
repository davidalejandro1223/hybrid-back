from django.urls import path
from .views import (ListCreatePolicy,UpdateDeleteRetrievePolicy,
    EmployeeLoaderView,EmployeeProfileView,GetEmployeesAPIView)

from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r"employee", GetEmployeesAPIView, basename="employees")

urlpatterns = [
    path('employee/<int:employee_pk>/policy', ListCreatePolicy.as_view()),
    path('employee/<int:employee_pk>/policy/<int:policy_pk>', UpdateDeleteRetrievePolicy.as_view()),
    path('employee/loader', EmployeeLoaderView.as_view()),
    path('employee/<int:employee_pk>/profile', EmployeeProfileView.as_view())
]
urlpatterns += router.urls

