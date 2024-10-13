from django.urls.conf import path, include
from rest_framework.routers import DefaultRouter

from apps.wallets.views import DepositView, TransferView, WalletView

router = DefaultRouter()
router.register(r'deposits', DepositView, basename='deposits')
urlpatterns = [
    path('', include(router.urls)),
]
