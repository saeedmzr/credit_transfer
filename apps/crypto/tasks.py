from datetime import timedelta

from celery import shared_task
from django.db import transaction
from django.utils import timezone

from .crypto_price_fetcher import CryptoFetcher
from .models import Crypto
from .repositories import CryptoRepository
from .serializers import CryptoSerializer


@shared_task
def fetch_crypto_prices():
    crypto_fetcher = CryptoFetcher(type="fcs")
    items = CryptoRepository.get_items_for_updating_price()
    for crypto in items:
        result = crypto_fetcher.fetcher.get_crypto_price(crypto.abbreviation)
        if result.get("code", 0) == 200:
            price_item = result.get("response")[0]
            crypto.price = price_item.get("c") or price_item.get("o")
            crypto.save()


@shared_task
def fetch_crypto_list():
    crypto_fetcher = CryptoFetcher(type="fcs")
    result = crypto_fetcher.fetcher.get_crypto_list()
    if result.get("code", 0) == 200:
        crypto_list = result.get("response")
        for crypto in crypto_list:
            CryptoRepository.create_or_update(
                insert_data={
                    "abbreviation": crypto.get("symbol")
                },
                update_data={
                    "name": crypto.get("name")
                }
            )
