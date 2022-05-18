from django.db import IntegrityError
from rest_framework import filters
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView

from user.models import User
from user.serializers import UserSerializer, UserRegistrationSerializer, CustomTokenObtainPairSerializer


class UserViewSet(viewsets.ModelViewSet):
    http_method_names = ['get']
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated,)
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['updated']
    ordering = ['-updated']

    def get_queryset(self):
        if self.request.user.is_superuser:
            return User.objects.all()

    def get_object(self):
        lookup_field_value = self.kwargs[self.lookup_field]

        obj = User.objects.get(lookup_field_value)
        self.check_object_permissions(self.request, obj)

        return obj


class UserAdminManagement(viewsets.ViewSet):
    # permission_classes = (IsAdminUser, )

    @action(detail=False, methods=['post'], url_path="bulk_create_users")
    def bulk_create_users(self, request):
        errors = {}
        file = request.FILES['CSV'].read().decode("utf-8")
        csv_data = file.split("\n")
        ln = 0

        for row in csv_data:
            try:
                if ln != 0:
                    data = row.split(",")
                    u = {'username': data[0], 'email': data[2], 'first_name': data[3], 'last_name': data[4],
                         'password': data[1]}
                    serializer = UserRegistrationSerializer(data=u)
                    if serializer.is_valid():
                        serializer.save()
                ln += 1

            except (TypeError, IntegrityError, IndexError) as e:
                errors[data[0]] = str(e)

        ln += 1

        if len(errors) != 0:
            return Response({
                'message': 'There were some errors while creating users',
                "errors": str(errors)
            }, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'e': str(errors)}, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'], url_path="create_user")
    def create_user(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            if user:
                json = serializer.data
                return Response(json, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ConsumerAccountManagement(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['patch'], url_path='reset_password')
    def reset_password(self, request):
        user = User.objects.get(username=request.user)
        valid = user.check_password(request.data['pwd'])

        if valid:
            user.set_password(request.data['new_pwd'])
            user.save()
            return Response({'message': "Password Successfully Updated!"}, status=status.HTTP_200_OK)
        else:
            return Response({'message': "Something went wrong, please try again!"}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['patch'], url_path='update_enabled_auth')
    def update_enabled_auth(self, request):
        user = User.objects.get(username=request.user)
        if request.data['type'] == 'fingerprint':
            if user.biometrics_auth:
                user.biometrics_auth = False
            else:
                user.biometrics_auth = True
            user.save()
            return Response(
                {
                    'message': "Biometrics Authentications turned on" if user.biometrics_auth else "Biometrics Authentications turned off",
                    "biometrics_enabled": user.biometrics_auth,
                    "rfid_auth_enabled": user.rfid_auth_enabled,
                    "limit_charges": user.limit_charges,
                    "pos_enabled": user.pos_enabled,
                    "atm_enabled": user.atm_enabled,
                },
                status=status.HTTP_200_OK)
        elif request.data['type'] == 'rfid':
            if user.rfid_auth_enabled:
                user.rfid_auth_enabled = False
            else:
                user.rfid_auth_enabled = True
            user.save()
            return Response(
                {
                    'message': "RFID Authentications turned on" if user.rfid_auth_enabled else "RFID Authentications turned off",
                    "biometrics_enabled": user.biometrics_auth,
                    "rfid_auth_enabled": user.rfid_auth_enabled,
                    "limit_charges": user.limit_charges,
                    "pos_enabled": user.pos_enabled,
                    "atm_enabled": user.atm_enabled,
                },
                status=status.HTTP_200_OK)
        elif request.data['type'] == 'pos_enabled':
            if user.pos_enabled:
                user.pos_enabled = False
            else:
                user.pos_enabled = True
            user.save()
            return Response(
                {
                    'message': "POS transactions turned on" if user.pos_enabled else "POS transactions turned off",
                    "biometrics_enabled": user.biometrics_auth,
                    "rfid_auth_enabled": user.rfid_auth_enabled,
                    "limit_charges": user.limit_charges,
                    "pos_enabled": user.pos_enabled,
                    "atm_enabled": user.atm_enabled,
                },
                status=status.HTTP_200_OK)
        elif request.data['type'] == 'limit_charges':
            if user.limit_charges:
                user.limit_charges = False
            else:
                user.limit_charges = True
            user.save()
            return Response(
                {
                    'message': "Transaction limits turned on" if user.limit_charges else "Transaction limits turned off",
                    "biometrics_enabled": user.biometrics_auth,
                    "rfid_auth_enabled": user.rfid_auth_enabled,
                    "limit_charges": user.limit_charges,
                    "pos_enabled": user.pos_enabled,
                    "atm_enabled": user.atm_enabled,
                },
                status=status.HTTP_200_OK)
        elif request.data['type'] == 'atm_enabled':
            if user.atm_enabled:
                user.atm_enabled = False
            else:
                user.atm_enabled = True
            user.save()
            return Response(
                {
                    'message': "ATM transactions turned on" if user.rfid_auth_enabled else "ATM transactions turned off",
                    "biometrics_enabled": user.biometrics_auth,
                    "rfid_auth_enabled": user.rfid_auth_enabled,
                    "limit_charges": user.limit_charges,
                    "pos_enabled": user.pos_enabled,
                    "atm_enabled": user.atm_enabled,
                },
                status=status.HTTP_200_OK)
        else:
            return Response({'message': "Something went wrong, please try again!"}, status=status.HTTP_400_BAD_REQUEST)


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
