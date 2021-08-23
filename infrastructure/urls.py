from django.conf.urls import url
from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import (BranchOfficeViewSet, BranchOfficeListAPIView,
    ContagiousHistoryView)

router = DefaultRouter()
router.register(r'infrastructure', BranchOfficeViewSet, basename='branchoffice')

urlpatterns = [
    path(
        'infrastructure/employee/<int:employee_pk>/contagious_history',
        ContagiousHistoryView.as_view(),
    ),
    path(
        "infrastructure/employee-branch-office",
        BranchOfficeListAPIView.as_view()
    ),
]
urlpatterns+=router.urls
