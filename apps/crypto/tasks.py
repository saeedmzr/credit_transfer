from datetime import timedelta

from celery import shared_task
from django.db import transaction
from django.utils import timezone

from .crypto_price_fetcher import CryptoFetcher
from .models import Crypto
from .repositories import CryptoRepository
from .serializers import CryptoSerializer


@shared_task
def fetch_crypto_list():
    crypto_fetcher = CryptoFetcher(type="fcs")
    crypto_list = crypto_fetcher.fetcher.get_crypto_list()

    for crypto in crypto_list:
        CryptoRepository.create_or_update(
            insert_data={
                "abbreviation": crypto.get("symbol")
            },
            update_data={
                "name": crypto.get("name")
            }
        )
    return crypto_list


@shared_task
def fetch_crypto_list():
    crypto_fetcher = CryptoFetcher(type="fcs")
    crypto_list = crypto_fetcher.fetcher.get_crypto_list()

    for crypto in crypto_list:
        CryptoRepository.create_or_update(
            insert_data={
                "abbreviation": crypto.get("symbol")
            },
            update_data={
                "name": crypto.get("name")
            }
        )
    return crypto_list
