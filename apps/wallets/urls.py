from django.urls.conf import path, include
from rest_framework.routers import DefaultRouter

from apps.wallets.views import DepositView, TransferView, WalletView, WalletLogView

router = DefaultRouter()
router.register(r'deposits', DepositView, basename='deposits')
router.register(r'transfers', TransferView, basename='transfers')
router.register('<wallet_hash>/logs', WalletLogView, basename='logs')

router.register('', WalletView, basename='wallets')
urlpatterns = [
    path('', include(router.urls)),
]
