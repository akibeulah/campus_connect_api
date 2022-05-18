import environ
import jwt
from rest_framework import serializers

from communication.models import Message
from pos.models import POS, Transaction, POSHandovers, Remittance
from user.serializers import UserMessageSerializer

env = environ.Env(
    PRIVATE_KEY_5=(str, "")
)


class POSSerializer(serializers.ModelSerializer):
    class Meta:
        model = POS
        fields = ['id', 'UID', 'is_active', 'user', 'created_at']
        read_only_field = ['is_active', 'created_at']


class POSRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = POS
        fields = ['id', 'UID', 'is_active', 'password', 'created_at']

    def create(self, validated_data):
        password = validated_data.pop('password', None)

        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.password = jwt.encode({"pass: ": password}, env('PRIVATE_KEY_5'), algorithm="HS256")
        instance.save()
        return instance


class BasicTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['id', 'transaction_type', 'transaction_title', 'transaction_amount', 'transaction_desc', 'auth_type',
                  'consumer', 'vendor',
                  'pos', 'created_at', ]


class POSTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['transaction_type', 'transaction_title', 'transaction_amount', 'transaction_desc', 'auth_type',
                  'consumer', 'vendor',
                  'pos']


class ReverseTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['transaction_type', 'transaction_title', 'transaction_amount', 'transaction_desc', 'auth_type',
                  'consumer', 'vendor']


class BasicPOSHandoverSerializer(serializers.ModelSerializer):
    class Meta:
        model = POSHandovers
        fields = ['vendor', 'request_type', 'request_desc']


class POSHandoverSerializer(serializers.ModelSerializer):
    class Meta:
        model = POSHandovers
        fields = ['vendor', 'request_type', 'request_desc', 'request_made_at', 'request_approval',
                  'pos', 'collected_at', 'returned_at', 'updated_at']


class RemittanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Remittance
        fields = ['vendor', 'request_approval', 'created_at']


class MessageSerializer(serializers.ModelSerializer):
    sender = UserMessageSerializer(read_only=True)
    class Meta:
        model = Message
        fields = ['id', 'recipient', 'sender', 'message_content', 'created_at', 'read_at', 'received_at']
        read_only_field = ['created_at']
