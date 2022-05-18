from rest_framework import serializers

from communication.models import Message


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['id', 'recipient', 'sender', 'message_content', 'created_at', 'read_at', 'received_at']
        read_only_field = ['created_at']
