from django.contrib.auth.models import User
from rest_framework import serializers

from .models import Message


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['id', 'title', 'read', ]


class MessageDetailSerializer(serializers.ModelSerializer):
    sender = serializers.ReadOnlyField(source='sender.username')
    recipient = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = Message
        fields = ['id', 'title', 'body', 'sender', 'recipient', ]


class UserSerializer(serializers.ModelSerializer):
    sender_messages = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    recipient_messages = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'sender_messages', 'recipient_messages']
