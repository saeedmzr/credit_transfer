from django.db import transaction

from apps.base import helpers
from apps.base.services import BaseService
from apps.wallets.models import WalletLogType, TransferStatus
from apps.wallets.repositories import WalletRepository, WalletLogRepository, DepositRepository, TransferRepository


class WalletService(BaseService):
    _repository = WalletRepository

    @classmethod
    def create_wallet(cls, data):
        data['hash'] = helpers.generate_random_string()
        return super().create(data=data)


class WalletLogService(BaseService):
    _repository = WalletLogRepository


class TransferService(BaseService):
    _repository = TransferRepository
    _wallet_service = WalletService()
    _wallet_log_service = WalletLogService()

    @classmethod
    def create(cls, data: dict):
        data["sender"] = WalletRepository.get_wallet_from_hash(data["sender"])
        data["receiver"] = WalletRepository.get_wallet_from_hash(data["receiver"])
        transfer = super().create(data=data)

        with transaction.atomic():
            sender_wallet = cls._wallet_service.get_and_lock_for_update(transfer.sender.pk)
            receiver_wallet = cls._wallet_service.get_and_lock_for_update(transfer.receiver.pk)
            cls._wallet_service.update(sender_wallet.pk, {
                'balance': sender_wallet.balance - transfer.amount
            })
            cls._wallet_service.update(receiver_wallet.pk, {
                'balance': receiver_wallet.balance + transfer.amount
            })

            cls._wallet_log_service.create(data={
                'wallet': sender_wallet,
                'amount': transfer.amount,
                'balance': sender_wallet.balance - transfer.amount,
                'type': WalletLogType.TRANSFER
            })
            cls._wallet_log_service.create(data={
                'wallet': receiver_wallet,
                'amount': transfer.amount,
                'balance': receiver_wallet.balance + transfer.amount,
                'type': WalletLogType.TRANSFER
            })
            return cls.update(transfer.id, {'status': TransferStatus.DONE})


class DepositService(BaseService):
    _repository = DepositRepository
    _wallet_service = WalletService()
    _wallet_log_service = WalletLogService()

    @classmethod
    def create(cls, data: dict):
        deposit = super().create(data=data)

        with transaction.atomic():
            wallet = cls._wallet_service.get_and_lock_for_update(deposit.wallet.hash)
            cls._wallet_service.update(wallet.hash, {
                'balance': wallet.balance + deposit.amount
            })

            cls._wallet_log_service.create(data={
                'wallet': wallet,
                'amount': deposit.amount,
                'balance': wallet.balance + deposit.amount,
                'type': WalletLogType.DEPOSIT
            })
            cls.update(deposit.id, {'status': TransferStatus.DONE})
