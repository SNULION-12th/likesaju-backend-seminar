from asgiref.sync import async_to_sync
from rest_framework import status
from channels.generic.websocket import JsonWebsocketConsumer
from django.contrib.auth import get_user_model
from .models import ChatRoom, Message
from django.db.models import Count, Q
from django.utils import timezone

User = get_user_model()
user_channel_name_dict = {}
class WebChatConsumer(JsonWebsocketConsumer):
    groups = ["broadcast"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = None

    def connect(self):
        self.user = self.scope["user"]
        if not self.user.is_authenticated:
            self.close()  # WebSocket 연결을 종료
            return
        user_channel_name_dict[self.user.id] = self.channel_name
        self.accept()
        print("accepted")

        # 사용자가 참가자로 포함된 모든 채팅방을 가져와서 그룹에 추가
        chatrooms = ChatRoom.objects.filter(participants=self.user)
        for chatroom in chatrooms:
            async_to_sync(self.channel_layer.group_add)(
                str(chatroom.id),  # 문자열로 변환
                self.channel_name
            )

    def receive_json(self, content):
        sender = self.scope["user"]
        print(content)
        message = content.get("message")
        chat_room_id = content.get("chat_room_id", None) #채팅창에서 메시지 전송
        participant_id = content.get("participant_id", None) #공유하기에서 메시지 전송

        if chat_room_id:
            # 채팅방을 가져옴
            chatroom = ChatRoom.objects.get(id=chat_room_id)

            # 새 메시지를 생성하고, 그룹에 전송
            new_message = Message.objects.create(chatroom=chatroom, sender=sender, content=message)
            for participant in chatroom.participants.all():
                channel_name = user_channel_name_dict.get(participant.id, None)
                if channel_name:
                    async_to_sync(self.channel_layer.group_add)( #유저가 접속하기 전에 만들어진 채팅방이 아니면, group에 포함되어있지 않으므로 추가
                        str(chatroom.id),  # 문자열로 변환
                        channel_name
                    )
                    
            async_to_sync(self.channel_layer.group_send)(
                str(chat_room_id),  # 문자열로 변환
                {
                    "type": "chat_message",
                    "new_message": {
                        "id": new_message.id,
                        "sender": new_message.sender.id,
                        "chatroom": chat_room_id,
                        "content": new_message.content,
                        "timestamp": new_message.timestamp.isoformat(),
                    },
                }
            )
        if participant_id:
            print(sender.id, participant_id)
            participant_group_ids = list({sender.id, participant_id})
            try:
                #유저가 만들고자 하는 채팅방이 이미 존재하는지 확인하여 이미 존재하는 경우 새로 만들지 않고, 해당 채팅방에 메시지 전달
                chatroom = ChatRoom.objects.annotate(
                    num_participants=Count('participants'),
                    num_matching=Count('participants', filter=Q(participants__id__in=participant_group_ids))
                ).get(num_participants=len(participant_group_ids), num_matching=len(participant_group_ids))
            except:
                chatroom = ChatRoom.objects.create(
                    created_at=timezone.now()
                )
                participant = User.objects.get(id=participant_id) # participant를 찾아서 추가
                chatroom.participants.add(participant)
                chatroom.participants.add(sender)
            
            new_message = Message.objects.create(chatroom=chatroom, sender=sender, content=message)
            for participant in chatroom.participants.all(): #유저가 접속하기 전에 만들어진 채팅방이 아니면, group에 포함되어있지 않으므로 추가
                channel_name = user_channel_name_dict.get(participant.id, None)
                if channel_name:
                    print(participant.id, channel_name)
                    async_to_sync(self.channel_layer.group_add)(
                        str(chatroom.id),  # 문자열로 변환
                        channel_name
                    )
                    
            async_to_sync(self.channel_layer.group_send)(
                str(chatroom.id),  # 문자열로 변환
                {
                    "type": "chat_message",
                    "new_message": {
                        "id": new_message.id,
                        "sender": new_message.sender.id,
                        "chatroom": chatroom.id,
                        "content": new_message.content,
                        "timestamp": new_message.timestamp.isoformat(),
                    },
                }
            )


    def chat_message(self, event):
        self.send_json(event["new_message"])
        print(event)

    def disconnect(self, close_code):
        # 사용자가 참가자로 포함된 모든 채팅방에서 그룹을 제거
        chatrooms = ChatRoom.objects.filter(participants=self.user)
        for chatroom in chatrooms:
            async_to_sync(self.channel_layer.group_discard)(
                str(chatroom.id),  # 문자열로 변환
                self.channel_name
            )
        super().disconnect(close_code)