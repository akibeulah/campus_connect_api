import datetime
import secrets

import environ
import jwt
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from communication.models import Message
from pos.models import Transaction, POS, POSHandovers, Remittance
from pos.serializers import POSRegistrationSerializer, BasicTransactionSerializer, POSTransactionSerializer, \
    ReverseTransactionSerializer, BasicPOSHandoverSerializer, POSHandoverSerializer, RemittanceSerializer, \
    MessageSerializer
from user.models import User

env = environ.Env(
    PRIVATE_KEY_5=(str, "")
)


class POSAdminManagement(viewsets.ViewSet):

    def create(self, request):  # Creating POS
        serializer = POSRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            pos = serializer.save()
            if pos:
                json = serializer.data
                return Response(json, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ConsumerTransactionAPI(viewsets.ViewSet):  # Consumer Web App Requests and Transactions
    permission_classes = [IsAuthenticated]  # Class wide endpoint authorization

    def list(self, request):  # List all one user's transactions
        queryset = Transaction.objects.filter(consumer=request.user).order_by('-created_at')
        serializer = BasicTransactionSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class VendorTransactionAPI(viewsets.ViewSet):  # Consumer Web App Requests and Transactions
    permission_classes = [IsAuthenticated]  # Class wide endpoint authorization

    def list(self, request):  # List all one user's transactions
        queryset = Transaction.objects.filter(vendor=request.user).order_by('-created_at')
        serializer = BasicTransactionSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # def auth_permissions(self, request):

    @action(detail=False, methods=['post'], url_path='reverse_transaction_from_vendor')
    def reverse_transaction_from_vendor(self, request):
        transaction = Transaction.objects.get(id=request.data['transaction_id'])

        if transaction.reversed:
            queryset = Transaction.objects.filter(vendor=request.user).order_by('-created_at')
            serializer = BasicTransactionSerializer(queryset, many=True)
            return Response({"message": "Transaction already reversed", "transactions": serializer.data}, status=status.HTTP_200_OK)
        else:
            reversal_transaction = ReverseTransactionSerializer(data={
                'transaction_type': "IN",
                'transaction_title': "reversal of NGN" + transaction.transaction_amount + " from " + transaction.vendor.username,
                'transaction_amount': transaction.transaction_amount,
                'transaction_desc': request.data['desc'],
                'auth_type': "SYSTEM",
                'consumer': User.objects.get(username=transaction.consumer).id,
                'vendor': User.objects.get(username=transaction.vendor).id,
            })

            if reversal_transaction.is_valid():
                transaction.reversed = True
                transaction.save()
                rev_trans = reversal_transaction.save()

                mes = MessageSerializer(data={
                    'recipient': request.user.id,
                    'sender': 1,
                    'message_content': "Hello " + request.user.username + ", \n\nA refund request has been processed on your account for a transactions of NGN" + transaction.transaction_amount + " just now.\nPlease reach out if this transaction was not started by you. \nThanks,\nCampus Connect Team"
                })

                if mes.is_valid():
                    rev_trans_mes = mes.save()

                    if rev_trans and rev_trans_mes:
                        queryset = Transaction.objects.filter(vendor=request.user).order_by('-created_at')
                        serializer = BasicTransactionSerializer(queryset, many=True)
                        return Response({"message": "Transaction reversed successfully!", "transactions": serializer.data}, status=status.HTTP_200_OK)
                    else:
                        return Response({"message": reversal_transaction.errors}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"message": reversal_transaction.errors}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], url_path='request_remittance')
    def request_remittance(self, request):
        data = {'vendor': request.user.id}

        try:
            chk = Remittance.objects.filter(vendor=request.user.id).order_by('-created_at')[0]

            if not chk.request_approval == "APPROVED":
                return Response({'message': "Remittance Already Submitted"}, status=status.HTTP_201_CREATED)
        except IndexError:
            pass

        serializer = RemittanceSerializer(data=data)

        if serializer.is_valid():
            req = serializer.save()
            mes = MessageSerializer(data={
                'recipient': request.user.id,
                'sender': 1,
                'message_content': "Hello " + request.user.username + ", \n\nA remittance request has been processed on your account just now.\nPlease reach out if this request was not placed by you and look into changing your passwords. \nThanks,\nCampus Connect Team"
            })


            if mes.is_valid():
                req_mes = mes.save()
                if req and req_mes:
                    return Response({'message': "Remittance Request Submitted"}, status=status.HTTP_201_CREATED)

        return Response(serializer.error, status=status.HTTP_400_BAD_REQUEST)


class POSTransactionsAPI(viewsets.ViewSet):  # POS Transactions
    @action(detail=False, methods=['post'], url_path='pos_identification')
    def pos_identification(self, request):
        # Identify user from RFID card or Biometrics
        # Requires auth_type [RFID or BIOMETRICS], and auth_token which is the token used for the validation
        user = find_user(request.data['auth_type'], request.data['auth_token'])

        if user == "":
            return Response({"message": "User not found!", "code": 0}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({
                "first_name": user.first_name,
                "last_name": user.last_name,
                "username": user.username, "code": 1
            }, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], url_path='pos_debit_transaction')
    def pos_debit_transaction(self, request):
        # Debit transaction
        # Requires auth_type [RFID or BIOMETRICS], and auth_token which is the token used for the validation

        user = find_user(request.data['auth_type'], request.data['auth_token'])

        if user == "":  # Fetch user and return error if User not found
            return Response({"message": "User not found!"}, status=status.HTTP_400_BAD_REQUEST)

        if request.data['auth_type'] == "BIOMETRICS":  # If user found via biometrics
            if not user.biometrics_enabled:  # Check if biometric_authentication is enabled
                return Response({"message": "Fingerprint Authentication Disabled", "code": 0})

        if request.data['auth_type'] == "RFID":  # If user found via RFID
            if user.rfid_auth_enabled:  # Check if RFID is enabled
                if user.rfid_auth_pin != request.data['auth_token_pin']:  # Check if passed in matches account RFID pin
                    user.rfid_auth_attempts += 1
                    if user.rfid_auth_attempts == 3:  # Disable RFID if pin failed multiple times
                        user.rfid_auth_enabled = False
                        user.save()

                        return Response({"message": "Too Many Failed Attempts, RFID Auth Blocked", "code": 0})

                    user.save()
                    return Response({"message": "Incorrect Pin, Try Again", "code": 0})
                else:
                    user.rfid_auth_attempts = 0  # Reset RFID attempts on any correct attempt
                    user.save()
            else:
                return Response({"message": "RFID Authentication Disabled", "code": 0})

        if float(request.data['transaction_amount']) > get_balance(user):
            return Response({"message": "Insufficient Funds for Transaction", "code": 0})

        transaction = POSTransactionSerializer(data=request.data)

        pos = POS.objects.get(UID=request.data['pos'])

        if pos.token == request.data['pos_auth'] and pos.is_active:
            if transaction.is_valid():
                transaction.save()
                if transaction:
                    return Response({"message": "Transaction Successful", "code": 1}, status=status.HTTP_200_OK)
            else:
                return Response({"message": transaction.errors, "code": 0}, status=status.HTTP_400_BAD_REQUEST)

        else:
            return Response({"message": "POS auth failed, turn over to vendor", "code": 0},
                            status=status.HTTP_400_BAD_REQUEST)

        return Response({"message": "Transaction Error, Please Try Again", "code": 0},
                        status=status.HTTP_400_BAD_REQUEST)


class POSHandoverRequestManagement(viewsets.ViewSet):
    def list(self, request):
        queryset = POSHandovers.objects.filter(vendor=request.user).order_by('-request_made_at')
        serializer = POSHandoverSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request):
        data = {
            'vendor': request.user.id,
            'request_type': request.data['request_type'],
            'request_desc': request.data['request_desc'],
        }

        pos_handover = BasicPOSHandoverSerializer(data=data)

        if pos_handover.is_valid():
            handover = pos_handover.save()
            queryset = POSHandovers.objects.filter(vendor=request.user).order_by('-request_made_at')
            serializer = POSHandoverSerializer(queryset, many=True)

            if handover:
                return Response({
                    'message': "POS Request Made!",
                    'handover': serializer.data
                })
        print(pos_handover.errors)
        return Response(pos_handover.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'], url_path='vendor_pos_handover')
    def vendor_pos_handover(self, request):
        queryset = POSHandovers.objects.filter(vendor=request.user).order_by('-request_made_at')
        serializer = POSHandoverSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


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

    @action(detail=False, methods=["post"], url_path='ping')
    def ping_pos(self, request):
        try:
            pos = POS.objects.filter(token=request.data['token'])[0]
        except IndexError:
            return Response({'code': 0, 'message': "POS not found"})

        return Response({
            "message": "OK",
            'code': 1
        }, status=status.HTTP_200_OK)


def find_user(auth_type, data):
    if auth_type == "BIOMETRICS":
        try:
            return User.objects.filter(biometrics_password=data)[0]
        except IndexError:
            return ""
    elif auth_type == "RFID":
        try:
            return User.objects.filter(rfid_auth_id=data)[0]
        except IndexError:
            return ""
    elif auth_type == "USERNAME":
        try:
            return User.objects.filter(rfid_auth_id=data)[0]
        except IndexError:
            return ""
    else:
        return ""


def get_balance(user):
    user_balance = 0
    for i in Transaction.objects.filter(consumer=user):
        if i.transaction_type == "IN":
            user_balance += float(i.transaction_amount)
        elif i.transaction_type == "OUT":
            user_balance -= float(i.transaction_amount)

    return user_balance
