from lib2to3.fixes.fix_input import context

from django.shortcuts import render
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.serializers import ModelSerializer

from apps.base.responses import Response
from apps.base.views import BaseViewSet
from apps.crypto.serializers import CryptoSerializer
from apps.crypto.services import CryptoService
from apps.crypto.tasks import fetch_crypto_list, fetch_crypto_prices
from apps.wallets.models import Deposit
from apps.wallets.serializers import DepositSerializer, WalletSerializer, TransferSerializer
from apps.wallets.services import DepositService, WalletService, TransferService


# Create your views here.


class CryptoView(BaseViewSet):
    _service = CryptoService
    serializer_class = CryptoSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context

    @extend_schema(
        summary="Get list of crypto currencies",
        description="This endpoint gets all crypto currencies.",
        responses=CryptoSerializer,
    )
    def list(self, request, *args, **kwargs):
        list = fetch_crypto_list()
        owned = self._service.get_owned(request.user)
        wallets, meta = self._service.get_by_pagination(
            queryset=self._service.get_list(owned),
            page=self.request.query_params.get("page", 1),
            size=self.request.query_params.get("size", 10),

        )
        return Response(
            data={
                "wallets": self.get_serializer(wallets, many=True).data
            }, message="List of wallets.", meta=meta
        )

    @extend_schema(
        summary="Get a product",
        description="This endpoint gets a product.",
        responses=WalletSerializer,
    )
    def retrieve(self, request, *args, **kwargs):
        wallet = kwargs.get('wallet')
        product = self._service.get_by_pk(pk=wallet)
        return Response(
            data={
                "wallet": self.get_serializer(product).data
            }, message="The product.", meta={}
        )
