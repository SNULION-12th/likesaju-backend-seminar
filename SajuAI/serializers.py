from rest_framework.serializers import ModelSerializer
from rest_framework import serializers

class AIRequestSerializer(serializers.Serializer):
  data = serializers.CharField()