from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from apps.base.utils import TestHelper
from apps.billing.models import Wallet

User = get_user_model()


class WalletViewSetTest(APITestCase):
    fixtures = [
        "users.json",
        "wallets.json",
        "transactions.json",
        "charges.json",
        "transfers.json"
    ]

    def setUp(self):
        self.list_url = reverse("api:billing:wallet-list")
        self.admin = User.objects.get(username="adminuser")
        self.normal = User.objects.get(username="normaluser")
        self.other = User.objects.get(username="normaluser2")

    def auth(self, username: str, password: str = "1234"):
        TestHelper.login_and_authenticate(self.client, username, password)

    def test_list_requires_auth(self):
        resp = self.client.get(self.list_url)
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

        self.auth("normaluser")
        resp = self.client.get(self.list_url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_retrieve_owner_or_admin(self):
        wallet = Wallet.objects.filter(owner=self.normal).first()
        detail_url = reverse("api:billing:wallet-detail", args=[wallet.id])

        # unauth
        resp = self.client.get(detail_url)
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

        # owner ok
        self.auth("normaluser")
        resp = self.client.get(detail_url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.client.credentials()

        # other normal user forbidden
        self.auth("normaluser2")
        resp = self.client.get(detail_url)
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
        self.client.credentials()


        # admin ok
        self.auth("adminuser")
        resp = self.client.get(detail_url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
