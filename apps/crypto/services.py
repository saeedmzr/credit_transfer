from django.db import transaction

from apps.base import helpers
from apps.base.services import BaseService
from apps.crypto.models import Crypto
from apps.crypto.repositories import CryptoRepository
from apps.users.models import User
from apps.wallets.models import Wallet, WalletLog, WalletLogType
from apps.wallets.repositories import WalletRepository, WalletLogRepository, DepositRepository, TransferRepository
from apps.wallets.serializers import DepositSerializer


class CryptoService(BaseService):
    _repository = CryptoRepository
