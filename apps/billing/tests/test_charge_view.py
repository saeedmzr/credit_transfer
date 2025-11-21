from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase
from unittest.mock import patch

from apps.base.utils import TestHelper
from apps.billing.models import Wallet, Charge
from apps.billing.enums import TransactionStatuses

User = get_user_model()


class ChargeTests(APITestCase):
    fixtures = [
        "users.json",
        "wallets.json",
        "transactions.json",
        "charges.json",
        "transfers.json"
    ]

    def setUp(self):
        self.charges_url = reverse("api:billing:charge-list")
        self.admin = User.objects.get(username="adminuser")
        self.normal = User.objects.get(username="normaluser")
        self.other = User.objects.get(username="normaluser2")

        self.normal_wallet = Wallet.objects.filter(owner=self.normal).first()
        self.other_wallet = Wallet.objects.filter(owner=self.other).first()


    def auth(self, username: str, password: str = "1234"):
        TestHelper.login_and_authenticate(self.client, username, password)

    def test_list_requires_auth(self):
        resp = self.client.get(self.charges_url)
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

        self.auth("normaluser")
        resp = self.client.get(self.charges_url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_create_charge_only_own_wallet(self):
        payload = {
            "wallet": self.other_wallet.id,
            "amount": 1000,
        }

        resp = self.client.post(self.charges_url, payload, format="json")
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)


        # owner ok
        self.auth("normaluser2")
        resp = self.client.post(self.charges_url, payload, format="json")
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.client.credentials()

    @patch("apps.billing.views.approve_charge_service")
    def test_approve_requires_admin(self, mock_approve):
        charge = Charge.objects.filter(wallet=self.normal_wallet).first()
        url = reverse("api:billing:charge-approve", args=[charge.pk])

        self.auth("normaluser2")
        resp = self.client.post(url)
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)
        self.client.credentials()

        self.auth("adminuser")
        resp = self.client.post(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        mock_approve.assert_called_once_with(charge)

    @patch("apps.billing.views.decline_charge_service")
    def test_decline_owner_or_admin(self, mock_decline):
        charge = Charge.objects.filter(wallet=self.normal_wallet, status=TransactionStatuses.PENDING.value).first()
        url = reverse("api:billing:charge-decline", args=[charge.pk])

        resp = self.client.post(url)
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

        # owner ok
        self.auth("normaluser")
        resp = self.client.post(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        mock_decline.assert_called_once_with(charge)

    def test_user_can_see_own_charges(self):
        self.auth("normaluser")
        resp = self.client.get(self.charges_url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        for charge in resp.data:
            wallet = Wallet.objects.get(id=charge["wallet"])
            self.assertEqual(wallet.owner_id, self.normal.id)

    def test_user_cannot_see_others_charges(self):
        self.auth("normaluser")
        resp = self.client.get(self.charges_url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        for charge in resp.data:
            wallet = Wallet.objects.get(id=charge["wallet"])
            self.assertNotEqual(wallet.owner_id, self.other.id)

    def test_creating_charge_does_not_change_balance_immediately(self):
        self.auth("normaluser2")
        initial_balance = self.other_wallet.balance
        payload = {
            "wallet": self.other_wallet.id,
            "amount": 50,
        }
        resp = self.client.post(self.charges_url, payload, format="json")
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.other_wallet.refresh_from_db()
        self.assertEqual(self.other_wallet.balance, initial_balance)

    def test_creating_charge_changes_balance_if_admin_approves(self):
        self.auth("normaluser")
        charge = Charge.objects.create(
            wallet=self.normal_wallet,
            amount=30,
            status=TransactionStatuses.PENDING.value,
        )
        initial_balance = self.normal_wallet.balance

        self.auth("adminuser")
        approve_url = reverse("api:billing:charge-approve", args=[charge.pk])
        resp = self.client.post(approve_url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        self.normal_wallet.refresh_from_db()
        self.assertEqual(self.normal_wallet.balance, initial_balance + 30)

    def test_creating_charge_does_not_change_balance_if_admin_declines(self):
        self.auth("normaluser")
        charge = Charge.objects.create(
            wallet=self.normal_wallet,
            amount=30,
            status=TransactionStatuses.PENDING.value,
        )
        initial_balance = self.normal_wallet.balance

        self.auth("adminuser")
        decline_url = reverse("api:billing:charge-decline", args=[charge.pk])
        resp = self.client.post(decline_url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        self.normal_wallet.refresh_from_db()
        self.assertEqual(self.normal_wallet.balance, initial_balance)