from drf_spectacular.utils import extend_schema
from rest_framework import viewsets, status, serializers
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import WalletTransaction, Charge, Transfer, Wallet
from .serializers import WalletTransactionSerializer, ChargeSerializer, TransferSerializer, WalletSerializer, \
    TransferCreateSerializer
from .services import (
    approve_charge_service,
    decline_charge_service, create_transfer_sync
)
from .tasks import create_transfer_async_task
from ..base.permissions import IsAdminOrOwner, IsAdminPermission


@extend_schema(tags=["Wallet"])
class WalletViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminOrOwner]
    serializer_class = WalletSerializer
    def get_queryset(self):
        user = self.request.user
        if user.is_staff or user.is_superuser:
            return Wallet.objects.all().order_by("-created_at")
        return Wallet.objects.filter(
            owner=user
        ).order_by("-created_at")

@extend_schema(tags=["Transactions"])
class WalletTransactionViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAdminOrOwner]
    serializer_class = WalletTransactionSerializer
    def get_queryset(self):
        user = self.request.user
        if user.is_staff or user.is_superuser:
            return WalletTransaction.objects.all().order_by("-created_at")
        return WalletTransaction.objects.filter(
            wallet__owner=user
        ).order_by("-created_at")


@extend_schema(tags=["Charges"])
class ChargeViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminOrOwner]
    serializer_class = ChargeSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_staff or user.is_superuser:
            return Charge.objects.all().order_by("-created_at")
        return Charge.objects.filter(
            wallet__owner=user
        ).order_by("-created_at")

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
    serializer_class = TransferSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_staff or user.is_superuser:
            return Charge.objects.all().order_by("-created_at")
        return Transfer.objects.filter(
            source_wallet__owner=user
        ).order_by("-created_at")

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
            task = create_transfer_async_task.delay(source_wallet.id, target_wallet.id, amount)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"task_id": task.id}, status=status.HTTP_202_ACCEPTED)

    @extend_schema(
        request=TransferCreateSerializer,
        responses={200: TransferSerializer, 400: serializers.Serializer},
    )
    @action(detail=False, methods=["post"], url_path="create-sync")
    def create_sync(self, request):
        serializer = TransferCreateSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        source_wallet = serializer.validated_data["source_wallet"]
        target_wallet = serializer.validated_data["target_wallet"]
        amount = serializer.validated_data["amount"]

        try:
            transfer = create_transfer_sync(source_wallet.id, target_wallet.id, amount)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(TransferSerializer(transfer).data, status=status.HTTP_200_OK)