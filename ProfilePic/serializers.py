from rest_framework.serializers import ModelSerializer
from rest_framework import serializers

from .models import ProfilePic

class ProfilePicSerializer(ModelSerializer):
    class Meta:
        model = ProfilePic
        fields = "__all__"