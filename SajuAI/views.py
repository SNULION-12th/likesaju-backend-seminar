from django.shortcuts import render

# Create your views here.
from langchain_community.chat_models import ChatOpenAI
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

class ChatView(APIView):
    def post(self, request):
        data = request.data
        chat = ChatOpenAI(model="gpt-3.5-turbo-0125")
        response = chat.invoke(data['message'])
        return Response(response, status=status.HTTP_200_OK)
