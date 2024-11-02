from apps.base.exceptions import ValidationError
from apps.base.repositories import BaseRepository
from apps.wallets.models import Wallet, WalletLog, Deposit, Transfer
from apps.wallets.serializers import WalletSerializer, WalletLogOutputSerializer, DepositSerializer, TransferSerializer


class WalletRepository(BaseRepository):
    _model = Wallet
    _serializer = WalletSerializer

    @classmethod
    def get_wallet_from_hash(cls, hash_value):
        try:
            return Wallet.objects.get(hash=hash_value)
        except Wallet.DoesNotExist:
            raise ValidationError("Wallet with the given hash does not exist.")


class TransferRepository(BaseRepository):
    _model = Transfer
    _serializer = TransferSerializer


class WalletLogRepository(BaseRepository):
    _model = WalletLog
    _serializer = WalletLogOutputSerializer


class DepositRepository(BaseRepository):
    _model = Deposit
    _serializer = DepositSerializer
