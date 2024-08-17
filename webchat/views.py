# from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action

from .models import Conversation, Message
from .schemas import list_message_docs
from .serializers import MessageSerializer

# 시원 추가
from django.contrib.auth import get_user_model
from django.utils import timezone  # timezone 가져오기
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
User = get_user_model()  # User 모델 가져오기

class ConversationViewSet(viewsets.ViewSet):
    @swagger_auto_schema(
        operation_description="Create a new conversation with specified participants",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'channel_id': openapi.Schema(type=openapi.TYPE_STRING, description='Channel ID for the new conversation'),
                'participants': openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Items(type=openapi.TYPE_STRING),
                    description='List of usernames to be added as participants'
                ),
            },
            required=['channel_id', 'participants']
        ),
        responses={
            201: openapi.Response(
                description="Conversation created successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'channel_id': openapi.Schema(type=openapi.TYPE_STRING),
                        'participants': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Items(type=openapi.TYPE_STRING)
                        ),
                    }
                )
            ),
            400: openapi.Response(
                description="Invalid request data",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'error': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            ),
        }
    )
    def create(self, request):
        channel_id = request.data.get('channel_id')
        participants_usernames = request.data.get('participants', [])

        if not channel_id:
            return Response({"error": "Channel ID is required."}, status=status.HTTP_400_BAD_REQUEST)
        
        # 요청을 보낸 사용자
        user = request.user if request.user.is_authenticated else None

        # Test User 찾기 또는 생성
        test_user, _ = User.objects.get_or_create(
            id=999,
            defaults={
                'username': 'testuser',
                'email': 'test@test.com',
                'password': 'testpassword',
            }
        )
        
        if test_user.password == 'testpassword':
            test_user.set_password('testpassword')
            test_user.save()

        # 참가자들을 사용자 이름으로 검색
        participants = []
        for username in participants_usernames:
            try:
                user_instance = User.objects.get(username=username)
                participants.append(user_instance)
            except User.DoesNotExist:
                # 사용자 이름이 존재하지 않는 경우, 무시하고 계속 진행
                continue

        # 요청 보낸 사용자와 Test User를 참가자로 추가
        if user:
            participants.append(user)
        participants.append(test_user)

        # 채팅방 생성
        conversation, created = Conversation.objects.get_or_create(
            channel_id=channel_id,
            defaults={'created_at': timezone.now()}
        )

        if created:
            # 새로운 채팅방 생성 시, 참가자 추가
            conversation.participants.set(participants)

            # 5개의 테스트 메시지 생성
            messages_content = [
                f"test message 1 for {channel_id}",
                f"test message 2 for {channel_id}",
                f"test message 3 for {channel_id}",
                f"test message 4 for {channel_id}",
                f"test message 5 for {channel_id}"
            ]
            
            for content in messages_content:
                Message.objects.create(
                    conversation=conversation,
                    sender=test_user,
                    content=content,
                    timestamp=timezone.now()
                )

        return Response({
            'channel_id': conversation.channel_id,
            'participants': [p.username for p in participants]
        }, status=status.HTTP_201_CREATED)
    
    @swagger_auto_schema(operation_description="Get list of all conversations with participants")
    def list(self, request):
        # 요청을 보낸 사용자 찾기 (인증된 사용자만)
        user = request.user if request.user.is_authenticated else None

        # Conversation이 하나도 없을 경우 기본 Conversation 5개 생성
        if not Conversation.objects.exists():
            initial_channel_ids = ['test', 'test2', 'test3', 'test4', 'test5']

            # Test User 찾거나 생성
            test_user, _ = User.objects.get_or_create(
                id=999,
                defaults={
                    'username': 'testuser',
                    'email': 'test@test.com',
                    'password': 'testpassword',
                }
            )

            if test_user.password == 'testpassword':
                test_user.set_password('testpassword')
                test_user.save()

            for channel_id in initial_channel_ids:
                conversation = Conversation.objects.create(
                    channel_id=channel_id,
                    created_at=timezone.now()
                )
                # Test User와 요청을 보낸 사용자를 participants에 추가
                conversation.participants.add(test_user)
                if user:
                    conversation.participants.add(user)

                # 5개의 메시지 생성
                messages_content = [
                    "test message 1",
                    "test message 2",
                    "test message 3",
                    "test message 4",
                    "test message 5"
                ]
                
                for content in messages_content:
                    Message.objects.create(
                        conversation=conversation,
                        sender=test_user,
                        content=content,
                        timestamp=timezone.now()
                    )

        # 모든 Conversation과 그에 속한 participants의 username 목록 반환
        conversations = Conversation.objects.all()
        result = []
        for conversation in conversations:
            participants_usernames = conversation.participants.values_list('username', flat=True)
            result.append({
                'channel_id': conversation.channel_id,
                'participants': list(participants_usernames)
            })

        return Response(result)


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
        
        # 요청을 보낸 사용자 찾기 (인증된 사용자만)
        user = request.user if request.user.is_authenticated else None
        
        try:
            conversation = Conversation.objects.get(channel_id=channel_id)
        except Conversation.DoesNotExist:
            # Test User를 찾거나 생성
            test_user, created = User.objects.get_or_create(
                id=999,
                defaults={
                    'username': 'testuser',
                    'email': 'test@test.com',
                    'password': 'testpassword',
                }
            )

            if created:
                test_user.set_password('testpassword')
                test_user.save()

            # 새로운 Conversation 생성
            conversation, created = Conversation.objects.get_or_create(
                channel_id=channel_id,
                defaults={
                    'created_at': timezone.now()
                }
            )

            if created:
                # Test User와 요청을 보낸 사용자를 participants에 추가
                conversation.participants.add(test_user)
                if user:
                    conversation.participants.add(user)

                # 5개의 메시지 생성
                messages_content = [
                    "test message 1",
                    "test message 2",
                    "test message 3",
                    "test message 4",
                    "test message 5"
                ]
                
                for content in messages_content:
                    Message.objects.create(
                        conversation=conversation,
                        sender=test_user,
                        content=content,
                        timestamp=timezone.now()
                    )

        # 해당 Conversation의 모든 메시지 가져오기
        messages = conversation.message.all()
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data)