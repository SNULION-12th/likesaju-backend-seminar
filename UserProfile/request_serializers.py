from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserProfile

### request serializers for swagger

class SignUpRequestSerializer(serializers.Serializer):
    password = serializers.CharField()
    username = serializers.CharField()

class SignInRequestSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "password"]

class TokenRefreshRequestSerializer(serializers.Serializer):
    refresh = serializers.CharField()