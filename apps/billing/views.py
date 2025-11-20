from drf_spectacular.utils import extend_schema
from rest_framework import viewsets, status, serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction

from .models import WalletTransaction, Charge, Transfer, Wallet
from .serializers import WalletTransactionSerializer, ChargeSerializer, TransferSerializer, WalletSerializer, \
    TransferCreateSerializer
from .services import (
    approve_charge_service,
    decline_charge_service,
    create_transfer_sync
)
from .tasks import create_transfer_async_task
from ..base.permissions import IsAdminOrOwner, IsAdminPermission


@extend_schema(tags=["Wallet"])
class WalletViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminOrOwner]
    queryset = Wallet.objects.all().order_by("-created_at")
    serializer_class = WalletSerializer
    # Read-only, no create/update/delete
@extend_schema(tags=["Transactions"])

class WalletTransactionViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAdminOrOwner]
    queryset = WalletTransaction.objects.all().order_by("-created_at")
    serializer_class = WalletTransactionSerializer
    # Read-only, no create/update/delete

@extend_schema(tags=["Charges"])
class ChargeViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminOrOwner]
    queryset = Charge.objects.all().order_by("-created_at")
    serializer_class = ChargeSerializer

    # Approve charge endpoint for admins
    @action(detail=True, methods=["post"])
    def approve(self, request, pk=None):
        self.permission_classes = [IsAdminPermission]
        self.check_permissions(request)
        charge = self.get_object()

        try:
            approve_charge_service(charge)
            return Response({"detail": "Charge approved"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST
            )

    # Decline charge endpoint
    @action(detail=True, methods=["post"])
    def decline(self, request, pk=None):
        charge = self.get_object()
        self.permission_classes = [IsAdminOrOwner]
        self.check_permissions(request)
        self.check_object_permissions(request, charge)


        try:
            decline_charge_service(charge)
            return Response({"detail": "Charge declined"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST
            )

@extend_schema(tags=["Transfers"])
class TransferViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminOrOwner]
    queryset = Transfer.objects.all().order_by("-created_at")
    serializer_class = TransferSerializer

    @extend_schema(
        request=TransferCreateSerializer,
        responses=TransferSerializer,
    )
    @action(detail=False, methods=["post"])
    def create_async(self, request):
        serializer = TransferCreateSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)

        source_wallet = serializer.validated_data["source_wallet"]
        target_wallet = serializer.validated_data["target_wallet"]
        amount = serializer.validated_data["amount"]

        try:
            async_result = create_transfer_async_task.delay(source_wallet.id, target_wallet.id, amount)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"task_id": async_result.id}, status=status.HTTP_202_ACCEPTED)
    @extend_schema(
        request=TransferCreateSerializer,
        responses={"202": serializers.Serializer},
    )
    @action(detail=False, methods=["post"])
    def create_async(self, request):
        serializer = TransferCreateSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)

        source_wallet = serializer.validated_data["source_wallet"]
        target_wallet = serializer.validated_data["target_wallet"]
        amount = serializer.validated_data["amount"]

        try:
            task_id = create_transfer_async_task.delay(source_wallet.id, target_wallet.id, amount)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"task_id": task_id}, status=status.HTTP_202_ACCEPTED)