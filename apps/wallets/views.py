from lib2to3.fixes.fix_input import context

from django.shortcuts import render
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.serializers import ModelSerializer

from apps.base.responses import Response
from apps.base.serializers import DynamicFilteringSerializer
from apps.base.views import BaseViewSet
from apps.wallets.models import Deposit, Wallet
from apps.wallets.serializers import DepositSerializer, WalletSerializer, TransferSerializer, WalletOutputSerializer
from apps.wallets.services import DepositService, WalletService, TransferService


# Create your views here.


class DepositView(BaseViewSet):
    _service = DepositService
    serializer_class = DepositSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context

    @extend_schema(
        request=DepositSerializer,
        summary="Create a deposit",
        description="This endpoint creates a deposit.",
        responses=DepositSerializer,
    )
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        deposit = self.get_service().create(serializer.validated_data)
        return Response(
            data={
                "deposit": self.get_serializer(deposit).data
            },
            message="Deposit created successfully.",
            status=status.HTTP_201_CREATED
        )


class WalletView(BaseViewSet):
    _service = WalletService
    serializer_class = WalletSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context

    @extend_schema(
        summary="Get list of wallets",
        description="This endpoint gets user's wallets.",
        responses=WalletOutputSerializer,
    )
    def list(self, request, *args, **kwargs):
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', self.pagination_class.page_size))

        wallets, meta = self._service.pagination(queryset=self._service.get_owned(request.user.id), page=page, page_size=page_size)
        return Response(
            data={
                "wallets": WalletOutputSerializer(wallets, many=True).data
            }, message="List of wallets.", meta=meta
        )

    @extend_schema(
        request=WalletSerializer,
        summary="Create a wallet",
        description="This endpoint creates a wallet.",
        responses=WalletSerializer,
    )
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        data["user"] = request.user

        wallet = self.get_service().create_wallet(data)
        return Response(
            data={
                "wallet": self.get_serializer(wallet).data
            },
            message="Wallet created successfully.",
            status=status.HTTP_201_CREATED
        )


class TransferView(BaseViewSet):
    _service = TransferService
    serializer_class = TransferSerializer
