from apps.base.repositories import BaseRepository
from apps.crypto.models import Crypto
from apps.crypto.serializers import CryptoSerializer


class CryptoRepository(BaseRepository):
    _model = Crypto
    _serializer = CryptoSerializer

