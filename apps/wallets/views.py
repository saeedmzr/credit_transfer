from lib2to3.fixes.fix_input import context

from django.shortcuts import render
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.serializers import ModelSerializer

from apps.base.responses import Response
from apps.base.views import BaseViewSet
from apps.wallets.models import Deposit
from apps.wallets.serializers import DepositSerializer, WalletSerializer, TransferSerializer
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


class TransferView(BaseViewSet):
    _service = TransferService
    serializer_class = TransferSerializer
