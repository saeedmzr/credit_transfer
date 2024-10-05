from rest_framework import serializers

from apps.base.serializers import BaseModelSerializer
from apps.wallet.models import Wallet, WalletLog, Transfer


class WalletSerializer(BaseModelSerializer):
    class Meta:
        model = Wallet
        fields = '__all__'


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

    # def validate_amount(self, value):

