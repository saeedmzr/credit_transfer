from auditlog.registry import auditlog
from django.conf import settings
from django.db import models

from apps.billing.enums import TransactionTypes, TransactionStatuses


class Wallet(models.Model):
    """
    One wallet per seller (or more, if you want).
    No balance field; balance is derived from transactions.
    """
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="wallets",
    )

    phone_number = models.CharField(max_length=50,unique=True)
    name = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return f"Wallet(id={self.id}, owner={self.owner_id})"

    @property
    def balance(self):
        agg = self.transactions.filter(
            status=TransactionStatuses.CONFIRMED.value
        ).aggregate(total=models.Sum("amount"))
        return agg["total"] or 0

class WalletTransaction(models.Model):

    wallet = models.ForeignKey(
        Wallet,
        on_delete=models.CASCADE,
        related_name="transactions",
    )
    type = models.CharField(
        max_length=20,
        choices=TransactionTypes.choices(),
        default=TransactionTypes.CHARGE.value,
    )
    status = models.CharField(
        max_length=20,
        choices=TransactionStatuses.choices(),
        default=TransactionStatuses.PENDING.value,
    )
    amount = models.BigIntegerField()
    balance_after = models.BigIntegerField(null=True, blank=True)
    meta = models.JSONField(blank=True, default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ["id"]
        indexes = [
            models.Index(fields=["wallet", "created_at"]),
        ]

    def __str__(self):
        return f"Txn(id={self.id}, wallet={self.wallet_id}, amount={self.amount})"

class Charge(models.Model):
    wallet = models.ForeignKey(
        Wallet,
        on_delete=models.PROTECT,
        related_name="charges",
    )
    amount = models.BigIntegerField()
    status = models.CharField(
        max_length=20, choices=TransactionStatuses.choices(), default=TransactionStatuses.PENDING.value
    )
    wallet_transaction = models.OneToOneField(
        WalletTransaction,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="charge",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-id"]


class Transfer(models.Model):

    source_wallet = models.ForeignKey(
        Wallet,
        on_delete=models.PROTECT,
        related_name="outgoing_transfers",
    )
    target_wallet = models.ForeignKey(
        Wallet,
        on_delete=models.PROTECT,
        related_name="incoming_transfers",
    )
    amount = models.BigIntegerField()  # positive amount

    status = models.CharField(
        max_length=20, choices=TransactionStatuses.choices(), default=TransactionStatuses.PENDING.value
    )

    debit_transaction = models.OneToOneField(
        WalletTransaction,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="debit_transfer",
    )
    credit_transaction = models.OneToOneField(
        WalletTransaction,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="credit_transfer",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-id"]

auditlog.register(Wallet)
auditlog.register(WalletTransaction)
auditlog.register(Charge)
auditlog.register(Transfer)
