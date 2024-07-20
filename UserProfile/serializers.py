from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserProfile

class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "password"]

class TokenRefreshRequestSerializer(serializers.Serializer):
    refresh = serializers.CharField()

class SignUpRequestSerializer(serializers.Serializer):
    password = serializers.CharField()
    username = serializers.CharField()
    nickname = serializers.CharField()
    profilepic_id = serializers.IntegerField()

class UserProfileSerializer(ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = UserProfile
        fields = "__all__"

