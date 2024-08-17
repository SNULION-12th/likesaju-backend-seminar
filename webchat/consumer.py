from asgiref.sync import async_to_sync
from channels.generic.websocket import JsonWebsocketConsumer
from django.contrib.auth import get_user_model
from .models import Conversation, Message
User = get_user_model()

class WebChatConsumer(JsonWebsocketConsumer):
    groups = ["broadcast"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = None

    def connect(self):
        self.user = self.scope["user"]
        if self.user.is_authenticated:
            self.user = User.objects.get(id=self.user.id)
        else:
            # 사용자가 인증되지 않은 경우, testuser를 설정
            self.user, _ = User.objects.get_or_create(
                id=999,
                defaults={
                    'username': 'testuser',
                    'email': 'test@test.com',
                    'password': 'testpassword',
                }
            )

        self.accept()

        # 사용자가 참가자로 포함된 모든 채팅방을 가져와서 그룹에 추가
        conversations = Conversation.objects.filter(participants=self.user)
        for conversation in conversations:
            async_to_sync(self.channel_layer.group_add)(
                conversation.channel_id,
                self.channel_name
            )

    def receive_json(self, content):
        sender = self.user
        if not sender:
            # 사용자가 없으면 testuser를 설정
            sender, _ = User.objects.get_or_create(
                id=999,
                defaults={
                    'username': 'testuser',
                    'email': 'test@test.com',
                    'password': 'testpassword',
                }
            )

        message = content.get("message")
        channel_id = content.get("channel_id")

        # 채팅방을 가져오거나 새로 생성
        conversation, created = Conversation.objects.get_or_create(channel_id=channel_id)

        if created:
            # 채팅방이 새로 생성되었으면 self.user와 testuser를 참가자로 설정
            test_user, _ = User.objects.get_or_create(
                id=999,
                defaults={
                    'username': 'testuser',
                    'email': 'test@test.com',
                    'password': 'testpassword',
                }
            )
            if self.user:
                conversation.participants.add(self.user)
            conversation.participants.add(test_user)

            # 5개의 테스트 메시지를 생성
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
                    content=content
                )

        # 새 메시지를 생성하고, 그룹에 전송
        new_message = Message.objects.create(conversation=conversation, sender=sender, content=message)
        async_to_sync(self.channel_layer.group_send)(
            channel_id,
            {
                "type": "chat.message",
                "new_message": {
                    "id": new_message.id,
                    "sender": new_message.sender.username,
                    "content": new_message.content,
                    "timestamp": new_message.timestamp.isoformat(),
                },
            }
        )

    def chat_message(self, event):
        self.send_json(event["new_message"])

    def disconnect(self, close_code):
        # 사용자가 참가자로 포함된 모든 채팅방에서 그룹을 제거
        conversations = Conversation.objects.filter(participants=self.user)
        for conversation in conversations:
            async_to_sync(self.channel_layer.group_discard)(
                conversation.channel_id,
                self.channel_name
            )
        super().disconnect(close_code)
