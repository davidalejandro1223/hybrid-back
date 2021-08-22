from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import BranchOfficeViewSet, BranchOfficeListAPIView

router = DefaultRouter()
router.register(r'infrastructure', BranchOfficeViewSet, basename='branchoffice')

urlpatterns = [
    path(
        "infrastructure/employee-branch-office",
        BranchOfficeListAPIView.as_view()
    ),
]
urlpatterns+=router.urls
