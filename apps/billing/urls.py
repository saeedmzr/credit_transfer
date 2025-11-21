from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.billing.views import WalletTransactionViewSet, ChargeViewSet, TransferViewSet, WalletViewSet

router = DefaultRouter()
router.register(r"transactions", WalletTransactionViewSet, basename="transaction")
router.register(r"charges", ChargeViewSet, basename="charge")
router.register(r"transfers", TransferViewSet, basename="transfer")
router.register(r"wallets", WalletViewSet, basename="wallet")

urlpatterns = [
    path("", include(router.urls)),
]
