from crypt import crypt

from django.core.serializers.python import Serializer
from django.core.validators import MinValueValidator
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from apps.base.exceptions import NotFoundError
from apps.base.serializers import BaseModelSerializer
from apps.users.models import User
from apps.crypto.models import Crypto
from apps.users.managers import UserManager
from apps.wallets.models import Wallet, WalletLog, Transfer, Deposit


class WalletSerializer(BaseModelSerializer):
    class Meta:
        model = Wallet
        fields = '__all__'
        read_only_fields = ['user', 'balance', "hash", "deleted_at"]

    crypto = serializers.PrimaryKeyRelatedField(queryset=Crypto.objects.all())


class WalletLogSerializer(BaseModelSerializer):
    class Meta:
        model = WalletLog
        fields = '__all__'


class TransferSerializer(BaseModelSerializer):
    class Meta:
        model = Transfer
        fields = '__all__'
        read_only_fields = ['status', 'sender']

    receiver = serializers.PrimaryKeyRelatedField(queryset=Wallet.objects.all())
    sender = serializers.PrimaryKeyRelatedField(queryset=Wallet.objects.all())
    amount = serializers.FloatField()

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError('Amount must be positive')
        return value

    def validate(self, attrs):
        user = self.context['request'].user
        sender_wallet = Wallet.objects.owner(user=user).filter(pk=attrs['sender'])
        if sender_wallet is None:
            raise NotFoundError()
        receiver_wallet = Wallet.objects.filter(pk=attrs['receiver'], crypto=sender_wallet.crypto)
        if receiver_wallet is None:
            raise NotFoundError()

        if attrs['amount'] + sender_wallet.crypto.fee > sender_wallet.balance:
            raise serializers.ValidationError("You do not have enough credit.")
        return attrs


class DepositSerializer(serializers.Serializer):
    class Meta:
        model = Deposit
        fields = '__all__'
        read_only_fields = ['status']

    amount = serializers.FloatField()
    wallet = serializers.PrimaryKeyRelatedField(queryset=Wallet.objects.all())

    def validate_wallet(self, value):
        user = self.context['request'].user
        wallet = Wallet.objects.owner(user=user).filter(pk=value)
        if wallet is None:
            raise NotFoundError()
        return value

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError('Amount must be positive')
        return value
