from rest_framework import serializers

from apps.base.serializers import BaseModelSerializer
from apps.crypto.models import Crypto
from apps.wallets.models import Wallet


class CryptoSerializer(BaseModelSerializer):
    class Meta:
        model = Crypto
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')
