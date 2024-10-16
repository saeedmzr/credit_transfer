from django.urls.conf import path, include
from rest_framework.routers import DefaultRouter

from apps.crypto.views import CryptoView
from apps.wallets.views import DepositView, TransferView, WalletView

router = DefaultRouter()
router.register(r'', CryptoView, basename='crypto')
urlpatterns = [
    path('', include(router.urls)),
]
