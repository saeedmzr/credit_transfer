from rest_framework import serializers

from apps.base.serializers import BaseModelSerializer
from apps.crypto.models import Crypto


class CryptoSerializer(BaseModelSerializer):
    class Meta:
        model = Crypto
        fields = ['name',"abbreviation","price","fee"]

