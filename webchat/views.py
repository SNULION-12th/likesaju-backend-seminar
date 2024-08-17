# from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action

from .models import ChatRoom, Message
from .schemas import list_message_docs
from .serializers import MessageSerializer

# 시원 추가
from django.contrib.auth import get_user_model
from django.utils import timezone  # timezone 가져오기
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from UserProfile.models import UserProfile
User = get_user_model()  # User 모델 가져오기

class ChatRoomViewSet(viewsets.ViewSet):
    @swagger_auto_schema(
        operation_description="Create a new chatroom with specified participants",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'user_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID of the user to be added as a participant'),
            },
            required=['user_id']
        ),
        responses={
            201: openapi.Response(
                description="ChatRoom created successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'id': openapi.Schema(type=openapi.TYPE_STRING, description='ChatRoom ID'),
                        'participants': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    'id': openapi.Schema(type=openapi.TYPE_INTEGER, description='User ID'),
                                    'profile': openapi.Schema(
                                        type=openapi.TYPE_OBJECT,
                                        properties={
                                            'nickname': openapi.Schema(type=openapi.TYPE_STRING, description='User nickname'),
                                            'profilepic': openapi.Schema(
                                                type=openapi.TYPE_OBJECT,
                                                properties={
                                                    'id': openapi.Schema(type=openapi.TYPE_INTEGER, description='Profile picture ID'),
                                                    'image_url': openapi.Schema(type=openapi.TYPE_STRING, description='Profile picture URL'),
                                                }
                                            ),
                                        }
                                    )
                                }
                            )
                        ),
                        'last_message': openapi.Schema(type=openapi.TYPE_STRING, description='Last message in the chatroom'),
                    }
                )
            ),
            400: openapi.Response(
                description="Invalid request data",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'error': openapi.Schema(type=openapi.TYPE_STRING, description='Error message')
                    }
                )
            ),
        }
    )
    def create(self, request):
        
        participant_id = request.data.get('user_id')  # 전달받은 participant의 user_id
        user = request.user if request.user.is_authenticated else None  # 요청을 보낸 사용자

        # 채팅방 생성
        chatroom = ChatRoom.objects.create(
            created_at=timezone.now()
        )

        # User 모델에서 participant와 user를 가져옴
        if participant_id:
            participant = User.objects.filter(id=participant_id).first()  # participant를 찾아서 추가
            if participant:
                chatroom.participants.add(participant)
    
        if user:
            chatroom.participants.add(user)  # 요청한 사용자도 추가

        # 모든 participants 가져오기
        participants = []
        for participant in chatroom.participants.all():
            profile = {
                "nickname": participant.userprofile.nickname if hasattr(participant, 'userprofile') else "default nickname",
                "profilepic": {
                    "id": participant.userprofile.profilepic_id.id if participant.userprofile.profilepic_id else 1,  # 기본값 설정
                    "image_url": "default_image_url"  # 기본값 설정
                }
            }
            participants.append({
                "id": participant.id,
                "profile": profile
            })

        response_data = {
            'id': str(chatroom.id),
            'participants': participants,
            'last_message': ""  # 생성 시점에 last_message는 빈 문자열로 반환
        }

        return Response(response_data, status=status.HTTP_201_CREATED)
    
    # 완료!!
    @swagger_auto_schema(operation_description="Get list of all chatrooms with participants")
    def list(self, request):
        
        # 요청을 보낸 사용자 찾기 (인증된 사용자만)
        user = request.user if request.user.is_authenticated else None
        # ChatRoom이 하나도 없을 경우 
        if not ChatRoom.objects.exists():
            pass

        # 모든 ChatRoom과 그에 속한 participants의 username 목록 반환
        chatrooms = ChatRoom.objects.filter(participants=user) if user else ChatRoom.objects.none()
        result = []      
        for chatroom in chatrooms:
            participants_info = []
            for participant in chatroom.participants.all():
                # UserProfile 정보를 가져옴
                user_profile = UserProfile.objects.get(user=participant)
                
                # profilepic 부분은 임의의 값으로 설정
                profilepic_info = {
                    "id": user_profile.profilepic_id.id if user_profile.profilepic_id else 0, 
                    "image_url": "any value"
                }

                participant_info = {
                    "id": participant.id,
                    "profile": {
                        "nickname": user_profile.nickname,
                        "profilepic": profilepic_info
                    }
                }
                participants_info.append(participant_info)     
            # 마지막 메시지 가져오기
            last_message = chatroom.message.order_by('-timestamp').first()
            last_message_content = last_message.content if last_message else None
            result.append({
                'id': chatroom.id,
                'participants': participants_info,
                'last_message': last_message_content
            })
        return Response(result)

# 완료!
class MessageViewSet(viewsets.ViewSet):
    
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'chat_room_id',
                openapi.IN_QUERY,
                description="chat_room_id",
                type=openapi.TYPE_STRING
            )
        ]
    )
    @list_message_docs
    def list(self, request):
        chat_room_id = request.query_params.get("chat_room_id")  
        # 요청을 보낸 사용자 찾기 (인증된 사용자만)
        user = request.user if request.user.is_authenticated else None
        try:
            chatroom = ChatRoom.objects.get(id=chat_room_id)
        except ChatRoom.DoesNotExist:
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

            # 새로운 ChatRoom 생성
            chatroom, created = ChatRoom.objects.get_or_create(
                id=chat_room_id,
                defaults={
                    'created_at': timezone.now()
                }
            )

            if created:
                # Test User와 요청을 보낸 사용자를 participants에 추가
                chatroom.participants.add(test_user)
                if user:
                    chatroom.participants.add(user)

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
                        chatroom=chatroom,
                        sender=test_user,
                        content=content,
                        timestamp=timezone.now()
                    )

        # 해당 ChatRoom의 모든 메시지 가져오기
        messages = chatroom.message.all()
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data)