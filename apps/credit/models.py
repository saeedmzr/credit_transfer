from django.db import models

from apps.base.models import BaseModel
from apps.users.models import User
from apps.wallet.models import Wallet


# Create your models here.

class Transfer(BaseModel):
    sender = models.ForeignKey(Wallet, on_delete=models.CASCADE)
    receiver = models.ForeignKey(Wallet, on_delete=models.CASCADE)
    amount = models.FloatField()
    status = models.BooleanField(default=False)


