from django.db import models

from apps.base.models import BaseModel


# Create your models here.

class Crypto(BaseModel):
    name = models.CharField(max_length=255)
    abbreviation = models.CharField(max_length=255, unique=True)
    description = models.TextField()
    price = models.FloatField()
    fee = models.FloatField(default=0.0)

    def __str__(self):
        return self.abbreviation


class CryptoPriceHistory(BaseModel):
    crypto = models.ForeignKey(Crypto, on_delete=models.CASCADE)
    price = models.FloatField()
