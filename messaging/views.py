import datetime

from django.contrib.auth.models import User
from rest_framework import generics, permissions
from rest_framework_csv.renderers import CSVRenderer

from . import serializers
from .models import Message
from .permissions import IsSenderOrReadOnly
from .throttles import MessageCreateThrottle


class UserList(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = serializers.UserSerializer


class UserDetail(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = serializers.UserSerializer


class MessageListCsvRenderer(CSVRenderer):
    header = ['id', 'title', 'body', 'read', 'sent', 'created']


class MessageList(generics.ListAPIView):
    serializer_class = serializers.MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.query_params.get('outgoing'):
            queryset = Message.objects.filter(sender=self.request.user)
        else:
            queryset = Message.objects.filter(recipient=self.request.user)
        return queryset


class MessageListCsv(MessageList):
    renderer_classes = (MessageListCsvRenderer,)


class MessageCreate(generics.CreateAPIView):
    serializer_class = serializers.MessageDetailSerializer
    permission_classes = [permissions.IsAuthenticated]
    throttle_classes = [MessageCreateThrottle]

    def get_queryset(self):
        return Message.objects.filter(sender=self.request.user)

    def perform_create(self, serializer):
        serializer.save(sender=self.request.user)


class MessageDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Message.objects.all()
    serializer_class = serializers.MessageDetailSerializer
    permission_classes = [permissions.IsAuthenticated, IsSenderOrReadOnly]

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(updated=datetime.datetime.now())
        return super().update(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if not instance.read and self.request.user == instance.recipient:
            serializer = self.get_serializer(instance, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save(updated=datetime.datetime.now(), read=True)
        return super().retrieve(request, *args, **kwargs)
