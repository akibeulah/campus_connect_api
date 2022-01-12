import secrets

import environ
import os
import datetime
from uuid import uuid4
import jwt
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from pos.models import Transaction, POS
from pos.serializers import POSRegistrationSerializer, BasicTransactionSerializer
from user.models import User

env = environ.Env(
    PRIVATE_KEY_5=(str, "")
)


class POSAdminManagement(viewsets.ViewSet):

    def create(self, request):
        serializer = POSRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            if user:
                json = serializer.data
                return Response(json, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ConsumerTransactionAPI(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        queryset = Transaction.objects.filter(consumer=request.user).order_by('-created_at')
        serializer = BasicTransactionSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class POSTransactionsAPI(viewsets.ViewSet):
    @action(detail=False, methods=['get'], url_path='pos_identification')
    def pos_identification(self, request):
        user = find_user(request.data['auth_type'], request.data['auth_token'])

        if user == "":
            return Response({"message": "User not found!"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({
                "first_name": User.objects.filter(biometrics_password=request.data['biometrics_password']).first_name,
                "last_name": User.objects.filter(biometrics_password=request.data['biometrics_password']).last_name,
                "username": User.objects.filter(biometrics_password=request.data['biometrics_password']).username
            }, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], url_path='pos_debit_transaction')
    def pos_debit_transaction(self, request):
        user = find_user(request.data['auth_type'], request.data['auth_token'])

        if user == "":
            return Response({"message": "User not found!"}, status=status.HTTP_400_BAD_REQUEST)

        if request.data['auth_token'] == "BIOMETRICS":
            if not user.biometrics_enabled:
                return Response({"message": "Fingerprint Authentication Disabled"})

        if request.data['auth_token'] == "RFID":
            if user.rfid_auth_enabled:
                if user.rfid_auth_pin != request.data['auth_token_pin']:
                    user.rfid_auth_attempts += 1
                    if user.rfid_auth_attempts == 3:
                        user.rfid_auth_enabled = False
                        user.save()

                        return Response({"message": "Too Many Failed Attempts, RFID Auth Blocked"})

                    user.save()
                    return Response({"message": "Incorrect Pin, Try Again"})
                else:
                    user.rfid_auth_attempts = 0
                    user.save()
            else:
                return Response({"message": "RFID Authentication Disabled"})

        if user.amount > get_balance(user):
            return Response({"message": "Insufficient Funds for Transaction"})

        transaction = BasicTransactionSerializer({
            "transaction_type": request.data['transaction_type'],
            "transaction_title": request.data['transaction_title'],
            "transaction_amount": request.data['transaction_amount'],
            "transaction_desc": request.data['transaction_desc'],
            "auth_type": request.data['auth_type'],
            "consumer": request.data['consumer'],
            "vendor": request.data['vendor'],
            "pos": request.data['pos']
        })

        if transaction.is_valid():
            transaction.save()
            if transaction:
                return Response({"message": "Transaction Successful"}, status=status.HTTP_200_OK)

        return Response({"message": "Transaction Error, Please Try Again"})


class POSAuthenticationAPI(viewsets.ViewSet):
    def create(self, request):
        pos = POS.objects.get(UID=request.data['UID'])

        if pos:
            if request.data['password'] == request.data['password']:
                pos.token = jwt.encode({
                    'token': secrets.token_hex(32),
                    'exp': datetime.datetime.today() + datetime.timedelta(days=1)
                }, env('PRIVATE_KEY_5'), algorithm="HS256")
                pos.save()

                return Response({'message': "Welcome!", "token": pos.token})

            else:
                return Response({'message': "Wrong Pin"})

        return Response({'message': "POS not registered"})

    @action(detail=False, methods=["get"], url_path='ping')
    def ping_pos(self, request):
        return Response({
            "message": "OK",
            "UID": request.data['UID']
        }, status=status.HTTP_200_OK)


def find_user(auth_type, data):
    if auth_type == "BIOMETRICS":
        try:
            return User.objects.filter(biometrics_password=data)
        except User.DoesNotExist:
            return ""
    elif auth_type == "RFID":
        try:
            return User.objects.filter(rfid_auth_id=data)
        except User.DoesNotExist:
            return ""
    else:
        return ""


def get_balance(user):
    user_balance = 0
    for i in Transaction.objects.filter(consumer=user):
        if i.transaction_type == "IN":
            user_balance += i.amount
        elif i.transaction_type == "OUT":
            user_balance -= i.amount

    return user_balance
