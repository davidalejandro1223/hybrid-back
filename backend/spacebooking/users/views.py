from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.authtoken.views import ObtainAuthToken
from django.conf import settings
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

from .serializers import UserSerializer, ActivateUserSerializer

import jwt

User = get_user_model()
class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    
class ActivateUser(APIView):
    def post(self, request, *args, **kwargs):
        serializer = ActivateUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token = jwt.decode(serializer.validated_data['jwt_token'], settings.SECRET_KEY, algorithms='HS256')
        user = get_object_or_404(User, email=token['user'])
        user.set_password(serializer.validated_data['password'])
        user.is_active = True
        user.save()
        return Response(data={"status": "contraseña asignada correctamente"})