from django.shortcuts import render

# Create your views here.
from django.contrib.auth import get_user_model
from rest_framework import serializers
from users.tasks import send_confirmation_email

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        user = User.objects.create_user(
            email = validated_data['email'],
            first_name = validated_data['first_name'],
            last_name = validated_data['last_name'],
            user_identification = validated_data['user_identification'],
            is_worker = True,
            is_active = False
        )
        send_confirmation_email(user)
        return user

    class Meta:
        model = User
        exclude = ('password', )

class ActivateUserSerializer(serializers.Serializer):
    jwt_token = serializers.CharField(max_length=200)
    password = serializers.CharField(max_length=200)
