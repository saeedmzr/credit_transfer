from threading import local

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import transaction

from .models import Wallet, WalletLog, Deposit, WalletLogType
from ..users.models import User

_signal_processing = local()


@receiver(post_save, sender=Deposit)
def change_wallet_after_deposit(sender, instance, created, **kwargs):
    if getattr(_signal_processing, 'in_signal', False):
        return

    with transaction.atomic():
        _signal_processing.in_signal = True

        Wallet.objects.filter(pk=instance.wallet).update({
            "balance": instance.wallet.balance + instance.amount,
        })
        WalletLog.objects.create({
            "wallets": instance,
            "amount": instance.amount,
            "balance": instance.wallet.balance + instance.amount,
            "type": WalletLogType.DEPOSIT,
            "payload": {
                "wallets": instance.wallet,
                "amount": instance.amount,
            }
        })

        instance.save(update_fields=['status'])

        _signal_processing.in_signal = False

