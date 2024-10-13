from apps.base.repositories import BaseRepository
from apps.wallets.models import Wallet, WalletLog, Deposit, Transfer
from apps.wallets.serializers import WalletSerializer, WalletLogSerializer, DepositSerializer, TransferSerializer


class WalletRepository(BaseRepository):
    _model = Wallet
    _serializer = WalletSerializer


class TransferRepository(BaseRepository):
    _model = Transfer
    _serializer = TransferSerializer


class WalletLogRepository(BaseRepository):
    _model = WalletLog
    _serializer = WalletLogSerializer


class DepositRepository(BaseRepository):
    _model = Deposit
    _serializer = DepositSerializer
