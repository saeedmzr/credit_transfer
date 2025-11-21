from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from apps.base.utils import TestHelper
from apps.billing.models import Wallet

User = get_user_model()


class TransferViewSetTest(APITestCase):
    fixtures = [
        "users.json",
        "wallets.json",
        "transactions.json",
        "charges.json",
        "transfers.json"
    ]

    def setUp(self):
        self.create_async_url = reverse("api:billing:transfer-create-async")
        self.create_sync_url = reverse("api:billing:transfer-create-sync")
        self.admin = User.objects.get(username="adminuser")
        self.normal = User.objects.get(username="normaluser")
        self.source_wallet = Wallet.objects.filter(owner=self.normal).first()
        self.target_wallet = Wallet.objects.exclude(owner=self.normal).first()

    def auth(self, username: str, password: str = "1234"):
        TestHelper.login_and_authenticate(self.client, username, password)

    def test_create_async_requires_auth(self):
        payload = {
            "source_wallet_id": self.source_wallet.id,
            "target_phone": self.target_wallet.phone_number,
            "amount": 100,
        }
        resp = self.client.post(self.create_async_url, payload, format="json")
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_async_ok_for_owner(self):
        self.auth("normaluser")
        payload = {
            "source_wallet_id": self.source_wallet.id,
            "target_phone": self.target_wallet.phone_number,
            "amount": 100,
        }

        resp = self.client.post(self.create_async_url, payload, format="json")
        self.assertEqual(resp.status_code, status.HTTP_202_ACCEPTED)
        self.assertIn("task_id", resp.data)

    def test_create_sync_ok_for_owner(self):
        self.auth("normaluser")
        payload = {
            "source_wallet_id": self.source_wallet.id,
            "target_phone": self.target_wallet.phone_number,
            "amount": 100,
        }
        resp = self.client.post(self.create_sync_url, payload, format="json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn("id", resp.data)
        self.assertEqual(resp.data["amount"], 100)
        self.assertEqual(resp.data["source_wallet"], self.source_wallet.id)
        self.assertEqual(resp.data["target_wallet"], self.target_wallet.id)
