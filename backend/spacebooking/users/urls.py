from django.urls import path
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken import views
from .views import UserViewSet, ActivateUser

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')

urlpatterns = [
    path('users/activate-account', ActivateUser.as_view()),
    path('users/login', views.obtain_auth_token)
]
urlpatterns+=router.urls