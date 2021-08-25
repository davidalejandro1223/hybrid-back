from django.conf.urls import url
from django.urls import path
from rest_framework.generics import RetrieveUpdateDestroyAPIView
from rest_framework.routers import DefaultRouter
from .views import (
    BranchOfficeViewSet,
    BranchOfficeListAPIView,
    BranchOfficeLoaderAPIView,
    AreaLoaderAPIView,
    ContagiousHistoryView,
    #AreaListAPIView,
    ContagiousHistoryCreateAPIView,
    BookingStatusAPIView,
    AttendesByBranchOfficeListAPIView,
    LocationListAPIView,
    CountryListAPIView,
    CreateListAreaAPIView,
    RetrieveUpdateDestroyAreaAPIView,
    ReservasByEmployeeListAPIView,
    CovidReportAPIView,
    LocationsByCompanyAPIView,
    ChangeFaseInLocation,
    AreaViewSet,
)

router = DefaultRouter()
router.register(r"infrastructure/branch-office", BranchOfficeViewSet, basename="branchoffice")
router.register(r"infrastructure/area", AreaViewSet, basename="area")

urlpatterns = [
    path('infrastructure/employee/<int:employee_pk>/contagious_history',ContagiousHistoryView.as_view()),
    path("employee/contagious_history",ContagiousHistoryCreateAPIView.as_view()),
    path("infrastructure/employee-branch-office",BranchOfficeListAPIView.as_view()),
    path("infrastructure/branch-office/<int:branch_office_pk>/attendees-by-branch",AttendesByBranchOfficeListAPIView.as_view()),
    path("infrastructure/employee/<int:employee_pk>/reservas",ReservasByEmployeeListAPIView.as_view()),
    #path("infrastructure/employee-area",AreaListAPIView.as_view()),
    path("infrastructure/branch-office/loader", BranchOfficeLoaderAPIView.as_view()),
    path("infrastructure/areas/loader", AreaLoaderAPIView.as_view()),
    path("infrastructure/branch-office/<int:branch_office_id>/booking-status", BookingStatusAPIView.as_view()),
    path("infrastructure/country", CountryListAPIView.as_view()),
    path("infrastructure/country/<int:country_id>/location", LocationListAPIView.as_view()),
    path("infrastructure/branch-office/<int:branch_office>/area", CreateListAreaAPIView.as_view()),
    path("infrastructure/branch-office/<int:branch_office>/area/<int:pk>", RetrieveUpdateDestroyAreaAPIView.as_view()),
    path("infrastructure/branch-office/<int:branch_office>/covid-report", CovidReportAPIView.as_view()),
    path("infrastructure/company/location", LocationsByCompanyAPIView.as_view()),
    path("infrastructure/company/location/<int:pk>", ChangeFaseInLocation.as_view())
]
urlpatterns += router.urls
