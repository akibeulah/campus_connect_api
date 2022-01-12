import jwt

import environ
import os


from pos.models import POS, Transaction
from rest_framework import serializers

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
        fields = ['transaction_type', 'transaction_title', 'transaction_amount', 'transaction_desc', 'auth_type',
                  'consumer', 'vendor',
                  'pos', 'created_at', ]
