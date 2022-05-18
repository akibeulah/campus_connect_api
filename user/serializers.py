from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from user.models import User


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['username'] = user.username
        token['user_id'] = user.id
        token['email'] = user.email
        token['first_name'] = user.first_name
        token['last_name'] = user.last_name
        token['is_admin'] = user.is_admin
        token['is_staff'] = user.is_staff
        token['is_vendor'] = user.is_vendor
        # token['consumer_transactions'] = BasicTransactionSerializer(Transaction.objects.filter(consumer=user),
        #                                                             many=True).data
        # token['vendor_transactions'] = BasicTransactionSerializer(Transaction.objects.filter(vendor=user),
        #                                                           many=True).data
        token['biometrics_auth'] = user.biometrics_auth
        token['rfid_auth'] = user.rfid_auth
        token['biometrics_enabled'] = user.biometrics_enabled
        token['rfid_auth_enabled'] = user.rfid_auth_enabled
        token['limit_charges'] = user.limit_charges
        token['daily_transaction_limit'] = user.daily_transaction_limit
        token['pos_enabled'] = user.pos_enabled
        token['atm_enabled'] = user.atm_enabled
        return token


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'is_active', 'is_vendor', 'is_admin',
                  'created_at']
        read_only_field = ['username', 'email', 'is_active', 'is_vendor', 'is_admin', 'created_at']


class UserMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'is_active', 'is_vendor', 'is_admin']


class UserRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password']

    def create(self, validated_data):
        password = validated_data.pop('password', None)

        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance


class UserAuthSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['rfid_auth_enabled', 'biometrics_enabled']
