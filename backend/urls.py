from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from user.views import CustomTokenObtainPairView

urlpatterns = [
    path('admin/', admin.site.urls),
    # Authentication and Authorisation
    path('api/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    # V1
    path('api/v1/user/', include('user.urls', namespace='users_api')),
    path('api/v1/pos/', include('pos.urls', namespace='pos_api')),
]
