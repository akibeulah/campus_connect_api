from rest_framework.routers import DefaultRouter
from pos.views import POSAdminManagement, ConsumerTransactionAPI, POSTransactionsAPI, POSAuthenticationAPI

app_name = 'pos'

router = DefaultRouter()
router.register('pos_admin_management', POSAdminManagement, basename='pos_admin_management')
router.register('pos_authentication_api', POSAuthenticationAPI, basename='pos_authentication_api')
router.register('consumer_transaction_management', ConsumerTransactionAPI, basename='consumer_transaction_management')
router.register('pos_transactions_api', POSTransactionsAPI, basename='pos_transactions_api')
urlpatterns = router.urls
