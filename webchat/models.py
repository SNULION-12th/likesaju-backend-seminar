from django.db import models

# Create your models here.
from django.contrib.auth.models import User
from django.db import models
from django.contrib.auth import get_user_model


class Conversation(models.Model):
    channel_id = models.CharField(max_length=255)
    participants = models.ManyToManyField(get_user_model())
    created_at = models.DateTimeField(auto_now_add=True)


class Message(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name="message")
    sender = models.ForeignKey( User, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
