from email.policy import default

from django.db import models
from rest_framework.fields import empty

from apps.base.models import BaseModel
from apps.crypto.models import Crypto
from apps.users.models import User


# Create your models here.

class Wallet(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    hash = models.CharField(max_length=32, unique=True, primary_key=True)
    crypto = models.ForeignKey(Crypto, on_delete=models.CASCADE)
    balance = models.FloatField(default=0)

    def __str__(self):
        return self.hash

    class Meta:
        indexes = [
            models.Index(fields=['hash', "crypto"]),
        ]


class WalletLogType(models.TextChoices):
    DEPOSIT = "deposit"
    TRANSFER = "transfer"
    WITHDRAW = "withdraw"
    DEFAULT = DEPOSIT


class TransferStatus(models.TextChoices):
    DONE = "done"
    FAILED = "failed"
    PENDING = "pending"
    DEFAULT = PENDING


class WalletLog(BaseModel):
    wallet = models.ForeignKey(Wallet, on_delete=models.DO_NOTHING)
    amount = models.FloatField(default=0)
    balance = models.FloatField(default=0)
    type = models.Choices(WalletLogType.choices)
    payload = models.JSONField(null=True, max_length=1500)


class Transfer(BaseModel):
    sender = models.ForeignKey(Wallet, on_delete=models.CASCADE)
    receiver = models.ForeignKey(Wallet, on_delete=models.CASCADE)
    amount = models.FloatField()
    status = models.Choices(TransferStatus.choices)
