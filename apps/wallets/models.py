from email.policy import default

from django.db import models
from rest_framework.fields import empty

from apps.base.models import BaseModel
from apps.crypto.models import Crypto
from apps.users.models import User


# Create your models here.

class Wallet(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    hash = models.CharField(max_length=64, unique=True)
    crypto = models.ForeignKey(Crypto, on_delete=models.CASCADE)
    balance = models.FloatField(default=0)

    def __str__(self):
        return self.hash

    class Meta:
        indexes = [
            models.Index(fields=['hash', "crypto"]),
        ]


class TransferStatus(models.TextChoices):
    DONE = "done"
    FAILED = "failed"
    PENDING = "pending"


class WalletLogType(models.TextChoices):
    DEPOSIT = "deposit"
    TRANSFER = "transfer"
    WITHDRAW = "withdraw"


class WalletLog(BaseModel):
    wallet = models.ForeignKey(Wallet, on_delete=models.DO_NOTHING)
    amount = models.FloatField(default=0)
    balance = models.FloatField(default=0)
    type = models.CharField(max_length=20, choices=WalletLogType.choices, default=WalletLogType.DEPOSIT)


class Deposit(BaseModel):
    wallet = models.ForeignKey(Wallet, on_delete=models.DO_NOTHING)
    amount = models.FloatField(default=0)
    status = models.CharField(max_length=20, choices=TransferStatus.choices, default=TransferStatus.PENDING)


class Transfer(BaseModel):
    sender = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name="sender")
    receiver = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name="receiver")
    amount = models.FloatField()
    status = models.CharField(max_length=20, choices=TransferStatus.choices, default=TransferStatus.PENDING)
