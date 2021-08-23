from django.urls import path
from .views import (ListCreatePolicy,UpdateDeleteRetrievePolicy,
    EmployeeLoaderView,EmployeeProfileView)

urlpatterns = [
    path('employee/<int:employee_pk>/policy', ListCreatePolicy.as_view()),
    path('employee/<int:employee_pk>/policy/<int:policy_pk>', UpdateDeleteRetrievePolicy.as_view()),
    path('employee/loader', EmployeeLoaderView.as_view()),
    path('employee/<int:employee_pk>/profile', EmployeeProfileView.as_view())
]

