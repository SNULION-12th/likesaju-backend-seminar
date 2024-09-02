# from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action

from .models import ChatRoom, Message
from .schemas import list_message_docs
from .serializers import MessageSerializer
from django.db.models import Count, Q
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
        operation_id="채팅방 생성",
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

        # 요청을 보낸 사용자 찾기 (인증된 사용자만)
        if not request.user.is_authenticated:
            return Response(
                {"detail": "please signin"}, status=status.HTTP_401_UNAUTHORIZED
            )
        user = request.user
        participant_id = request.data.get('user_id')
        if not participant_id:
            return Response({"detail": "user_id is missing."}, status=status.HTTP_400_BAD_REQUEST)
        
        participant_group_ids = list({user.id, participant_id})

        try:
            #유저가 만들고자 하는 채팅방이 이미 존재하는지 확인하여 이미 존재하는 경우 새로 만들지 않고, 해당 채팅방 정보를 전달
            chatroom = ChatRoom.objects.annotate(
                num_participants=Count('participants'),
                num_matching=Count('participants', filter=Q(participants__id__in=participant_group_ids))
            ).get(num_participants=len(participant_group_ids), num_matching=len(participant_group_ids))
            print("chatroom already exists")
            participants = []
            for participant in chatroom.participants.all():
                profile = {
                    "nickname": participant.userprofile.nickname,
                    "profilepic": {
                        "id": participant.userprofile.profilepic_id,
                        "imagelink": participant.userprofile.profilepic_id
                    } if participant.userprofile.profilepic_id else None
                }
                participants.append({
                    "id": participant.id,
                    "profile": profile
                })
        except ChatRoom.DoesNotExist:
            # 채팅방 생성
            chatroom = ChatRoom.objects.create(
                created_at=timezone.now()
            )

            # User 모델에서 participant와 user를 가져옴
            if participant_id:
                participant = User.objects.get(id=participant_id) # participant를 찾아서 추가
                if participant:
                    chatroom.participants.add(participant)
        
            if user:
                chatroom.participants.add(user)  # 요청한 사용자도 추가

            # 모든 participants 가져오기
            participants = []
            for participant in chatroom.participants.all():
                profile = {
                    "nickname": participant.userprofile.nickname,
                    "profilepic": {
                        "id": participant.userprofile.profilepic_id,
                        "imagelink": participant.userprofile.profilepic_id
                    } if participant.userprofile.profilepic_id else None
                }
                participants.append({
                    "id": participant.id,
                    "profile": profile
                })
            print("create new chatroom")

        response_data = {
            'id': chatroom.id,
            'participants': participants,
            'last_message': chatroom.message.all().order_by("-timestamp").first()
        }

        return Response(response_data, status=status.HTTP_201_CREATED)
    
    # 완료!!
    @swagger_auto_schema(operation_description="Get list of all chatrooms with participants")
    def list(self, request):
        
        # 요청을 보낸 사용자 찾기 (인증된 사용자만)
        if not request.user.is_authenticated:
            return Response(
                {"detail": "please signin"}, status=status.HTTP_401_UNAUTHORIZED
            )
        user = request.user
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
                    "id": user_profile.profilepic_id, 
                    "imagelink": user_profile.profilepic_id
                } if user_profile.profilepic_id else None

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
        if not request.user.is_authenticated:
            return Response(
                {"detail": "please signin"}, status=status.HTTP_401_UNAUTHORIZED
            )
        chatroom = ChatRoom.objects.get(id=chat_room_id)
            

        # 해당 ChatRoom의 모든 메시지 가져오기
        messages = chatroom.message.all()
        print(messages)
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data)