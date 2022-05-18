from rest_framework.routers import DefaultRouter

from communication.views import MessagesAPI

app_name = 'communication'

router = DefaultRouter()

router.register('messages_api', MessagesAPI, basename='messages_api')

urlpatterns = router.urls