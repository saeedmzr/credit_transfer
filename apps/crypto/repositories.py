from apps.base.repositories import BaseRepository
from apps.crypto.models import Crypto
from apps.crypto.serializers import CryptoSerializer


class CryptoRepository(BaseRepository):
    _model = Crypto
    _serializer = CryptoSerializer

    @classmethod
    def get_items_for_updating_price(cls):
        items = cls._model.objects.all().order_by("updated_at")[:10]
        return items
