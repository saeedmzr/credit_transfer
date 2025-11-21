# Transfer async task with retry and atomicity
from celery import shared_task
from celery.exceptions import Retry
from django.db import transaction

from apps.billing.services import create_transfer_sync


@shared_task(bind=True, max_retries=3, default_retry_delay=10)
def create_transfer_async_task(self, source_id, target_id, amount):
    try:
        with transaction.atomic():
            transfer = create_transfer_sync(source_id, target_id, amount)
            return transfer.id
    except Exception as exc:
        try:
            raise self.retry(exc=exc)
        except Retry:
            # log failure here, manual intervention possibly needed
            raise
