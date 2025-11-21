from datetime import timezone

from django.db import transaction
from django.utils.timezone import now

from .enums import TransactionStatuses, TransactionTypes
from .models import WalletTransaction, Charge, Transfer, Wallet


def approve_charge_service(charge: Charge):
    with transaction.atomic():
        if charge.status != TransactionStatuses.PENDING.value:
            raise ValueError("Charge already processed")

        wallet = charge.wallet

        txn = WalletTransaction.objects.create(
            wallet=wallet,
            type=TransactionTypes.CHARGE.value,
            status=TransactionStatuses.CONFIRMED.value,
            amount=charge.amount,
            meta={"charge_id": charge.id},
        )

        charge.wallet_transaction = txn
        charge.status = TransactionStatuses.CONFIRMED.value
        charge.processed_at = now()
        charge.save()

def decline_charge_service(charge: Charge):
    with transaction.atomic():
        if charge.status != TransactionStatuses.PENDING.value:
            raise ValueError("Charge already processed")
        charge.status = TransactionStatuses.FAILED.value
        charge.processed_at = now()
        charge.save()

@transaction.atomic
def create_transfer_sync(source_id, target_id, amount):
    source_wallet = Wallet.objects.select_for_update().get(id=source_id)
    target_wallet = Wallet.objects.select_for_update().get(id=target_id)

    amount = int(amount)

    if source_wallet.balance < amount:
        raise ValueError("Insufficient balance")

    debit_txn = WalletTransaction.objects.create(
        wallet=source_wallet,
        type=TransactionTypes.TRANSFER_OUT.value,
        status=TransactionStatuses.CONFIRMED.value,
        amount=-amount,
    )

    credit_txn = WalletTransaction.objects.create(
        wallet=target_wallet,
        type=TransactionTypes.TRANSFER_IN.value,
        status=TransactionStatuses.CONFIRMED.value,
        amount=amount,
    )

    transfer = Transfer.objects.create(
        source_wallet=source_wallet,
        target_wallet=target_wallet,
        amount=amount,
        status=TransactionStatuses.CONFIRMED.value,
        debit_transaction=debit_txn,
        credit_transaction=credit_txn,
        processed_at=now(),
    )
    return transfer
