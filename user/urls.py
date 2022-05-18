from rest_framework.routers import DefaultRouter
from user.views import UserAdminManagement, ConsumerAccountManagement

app_name = 'user'

router = DefaultRouter()
router.register('', UserAdminManagement, basename='user_admin_management')
router.register('consumer_account_management', ConsumerAccountManagement, basename='consumer_account_management')
urlpatterns = router.urls
