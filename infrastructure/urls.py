from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import BranchOfficeViewSet, BranchOfficeListAPIView, BranchOfficeLoaderAPIView

router = DefaultRouter()
router.register(r'infrastructure', BranchOfficeViewSet, basename='branchoffice')

urlpatterns = [
    path(
        "infrastructure/employee-branch-office",
        BranchOfficeListAPIView.as_view()
    ),
    path(
        "infrastructure/branch-office/loader",
        BranchOfficeLoaderAPIView.as_view()
    )
]
urlpatterns+=router.urls
