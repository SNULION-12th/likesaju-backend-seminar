# from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets
from rest_framework.response import Response

from .models import Conversation
from .schemas import list_message_docs
from .serializers import MessageSerializer

# 시원 추가
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema



class MessageViewSet(viewsets.ViewSet):

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'channel_id',
                openapi.IN_QUERY,
                description="channel_id",
                type=openapi.TYPE_STRING
            )
        ]
    )

    @list_message_docs
    def list(self, request):
        channel_id = request.query_params.get("channel_id")

        try:
            conversation = Conversation.objects.get(channel_id=channel_id)
            message = conversation.message.all()
            serializer = MessageSerializer(message, many=True)
            return Response(serializer.data)
        except Conversation.DoesNotExist:
            return Response(["no"])