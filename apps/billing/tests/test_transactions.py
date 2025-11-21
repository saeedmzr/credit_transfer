from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from apps.billing.models import Wallet, WalletTransaction, Transfer
from apps.billing.enums import TransactionStatuses

User = get_user_model()


class TransactionsTest(APITestCase):
    fixtures = [
        "users.json",
        "wallets.json",
        "transactions.json",
        "charges.json",
        "transfers.json"
    ]

    def setUp(self):
        self.wallets_url = reverse("api:billing:wallet-list")
        self.transactions_url = reverse("api:billing:transaction-list")
        self.transfers_sync_url = reverse("api:billing:transfer-create-sync")
        self.admin = User.objects.get(username="adminuser")
        self.normal = User.objects.get(username="normaluser")
        self.other = User.objects.get(username="normaluser2")

        self.normal_wallet = Wallet.objects.filter(owner=self.normal).first()
        self.other_wallet = Wallet.objects.filter(owner=self.other).first()

    def auth(self, user):
        self.client.force_authenticate(user=user)

    def test_user_can_see_own_wallets_with_balance(self):
        self.auth(self.normal)
        resp = self.client.get(self.wallets_url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        for wallet in resp.data:
            self.assertEqual(wallet["owner"], self.normal.id)
            self.assertIn("balance", wallet)

    def test_user_can_see_own_transactions(self):
        self.auth(self.normal)
        resp = self.client.get(self.transactions_url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        for txn in resp.data:
            wallet_id = txn["wallet"]
            wallet = Wallet.objects.get(id=wallet_id)
            self.assertEqual(wallet.owner_id, self.normal.id)

    def test_user_cannot_see_others_transactions(self):
        self.auth(self.normal)
        resp = self.client.get(self.transactions_url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        txn_wallet_ids = [txn["wallet"] for txn in resp.data]
        other_wallet_txns = WalletTransaction.objects.filter(wallet__owner=self.other).values_list("id", flat=True)
        for txn in resp.data:
            wallet = Wallet.objects.get(id=txn["wallet"])
            self.assertNotEqual(wallet.owner_id, self.other.id)

    def test_creating_transfer_does_change_balance_immediately(self):
        self.auth(self.normal)
        initial_balance = self.normal_wallet.balance
        amount = 10
        payload = {
            "source_wallet_id": self.normal_wallet.id,
            "target_phone": self.other_wallet.phone_number,
            "amount": amount,
        }
        resp = self.client.post(self.transfers_sync_url, payload, format="json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.normal_wallet.refresh_from_db()
        self.assertEqual(self.normal_wallet.balance, initial_balance - amount)