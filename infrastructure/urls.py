from django.conf.urls import url
from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import (
    BranchOfficeViewSet,
    BranchOfficeListAPIView,
    BranchOfficeLoaderAPIView,
    AreaLoaderAPIView,
    #BookingStatusAPIView,
    ContagiousHistoryView
)

router = DefaultRouter()
router.register(r"infrastructure/branch-office", BranchOfficeViewSet, basename="branchoffice")

urlpatterns = [
    path('infrastructure/employee/<int:employee_pk>/contagious_history',ContagiousHistoryView.as_view()),
    path("infrastructure/employee-branch-office",BranchOfficeListAPIView.as_view()),
    path("infrastructure/branch-office/loader", BranchOfficeLoaderAPIView.as_view()),
    path("infrastructure/areas/loader", AreaLoaderAPIView.as_view()),
    #path("infrastructure/branch-office/<int:branch_office_id>/booking-status", BookingStatusAPIView.as_view())
]
urlpatterns += router.urls
