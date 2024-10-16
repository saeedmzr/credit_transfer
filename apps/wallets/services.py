from django.db import transaction

from apps.base import helpers
from apps.base.services import BaseService
from apps.crypto.models import Crypto
from apps.users.models import User
from apps.wallets.models import Wallet, WalletLog, WalletLogType
from apps.wallets.repositories import WalletRepository, WalletLogRepository, DepositRepository, TransferRepository
from apps.wallets.serializers import DepositSerializer


class WalletService(BaseService):
    _repository = WalletRepository

    @classmethod
    def create_wallet(cls, data):
        data['hash'] = helpers.generate_random_string()
        super().create(data=data)


class TransferService(BaseService):
    _repository = TransferRepository


class DepositService(BaseService):
    _repository = DepositRepository

    def deposit(self, data):
        deposit = self._repository.create(data)
        return deposit
