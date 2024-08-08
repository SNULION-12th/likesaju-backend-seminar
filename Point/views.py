from django.shortcuts import render

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import Point
from .serializers import PointSerializer


# Create your views here.
class PointListView(APIView):
    def get(self, request): # point 리스트 조회
        points = Point.objects.all()
        serializer = PointSerializer(points, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request): # point 생성
        price = request.data.get('price')
        point = request.data.get('point')
        if not price or not point:
            return Response({"detail": "fields missing."}, status=status.HTTP_400_BAD_REQUEST)
        point = Point.objects.create(price=price, point=point)
        serializer = PointSerializer(point)
        return Response(serializer.data, status=status.HTTP_201_CREATED)