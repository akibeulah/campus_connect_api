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


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
