from django.shortcuts import render
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from .models import ProfilePic
from .serializers import ProfilePicSerializer

# Create your views here.

class ProfilePicListView(APIView):
    def post(self, request):
        imagelink = request.data.get("imagelink")
        profilepic = ProfilePic.objects.create(imagelink=imagelink)

        serializer = ProfilePicSerializer(profilepic)

        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    def get(self, request):
        profilepic = ProfilePic.objects.all()
        serializer = ProfilePicSerializer(profilepic, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
