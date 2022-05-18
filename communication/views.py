from datetime import date

from django.db.models import Q
from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from communication.models import Message
from pos.serializers import MessageSerializer
from user.models import User


class MessagesAPI(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def create(self, request):
        message = MessageSerializer(data=request.data)

        if message.is_valid():
            sent_message = message.save()

            if sent_message:
                return Response(status=status.HTTP_201_CREATED)

        return Response(status=status.HTTP_400_BAD_REQUEST)

    def list(self, request):
        queryset = Message.objects.filter(Q(sender=request.user.id) | Q(recipient=request.user.id)).order_by('-created_at')
        serializers = MessageSerializer(queryset, many=True)
        return Response({'messages': serializers.data}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], url_path='read_messages')
    def read_messages(self, request):
        all_user_messages = Message.objects.filter(recipient=request.user.id)

        messages = [mes for mes in all_user_messages if mes.sender is not request.data['sender']]
        for message in messages:
            message.received_at = date.today()
            message.read_at = date.today()
            message.save()

        queryset = Message.objects.filter(Q(sender=request.user.id) | Q(recipient=request.user.id)).order_by(
            '-created_at')
        serializers = MessageSerializer(queryset, many=True)
        return Response({'messages': serializers.data}, status=status.HTTP_200_OK)
