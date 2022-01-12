from rest_framework.routers import DefaultRouter
from user.views import UserAdminManagement

app_name = 'user'

router = DefaultRouter()
router.register('', UserAdminManagement, basename='user_admin_management')
urlpatterns = router.urls
