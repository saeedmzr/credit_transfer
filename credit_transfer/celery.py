import os

from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'credit_transfer.settings.local')

app = Celery('credit_transfer')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
