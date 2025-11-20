# apps/users/tests/test_user_view.py
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.reverse import reverse

from django.contrib.auth import get_user_model

from apps.base.utils import TestHelper
from apps.users.enums import UserRoleEnum

User = get_user_model()


class UserViewSetTest(APITestCase):
    fixtures = ["users.json"]

    def setUp(self):
        self.login_url = reverse(TestHelper.LOGIN_URL_NAME)
        self.list_url = reverse("api:users:user-list")

        self.admin = User.objects.get(username="adminuser")
        self.normal = User.objects.get(username="normaluser")
        self.normal2 = User.objects.get(username="normaluser2")

    def auth(self, username: str, password: str = "1234"):
        TestHelper.login_and_authenticate(self.client, username, password)

    def test_list(self):
        resp = self.client.get(self.list_url)
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

        self.auth("normaluser")
        resp = self.client.get(self.list_url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn("users", resp.data["data"])
        self.client.credentials()

        self.auth("adminuser")
        resp = self.client.get(self.list_url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_retrieve(self):
        target = self.normal2
        detail_url = reverse("api:users:user-detail", args=[target.id])

        self.auth("adminuser")
        resp = self.client.get(detail_url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn("user", resp.data["data"])
        self.client.credentials()


    def test_get_me_returns_current_user(self):
        me_url = reverse("api:users:user-get-me")

        resp = self.client.get(me_url)
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

        self.auth("normaluser")
        resp = self.client.get(me_url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn("user", resp.data["data"])
        self.assertEqual(resp.data["data"]["user"]["id"], self.normal.id)

    def test_create_requires_admin(self):
        payload = {
            "username": "newuser",
            "email": "newuser@example.com",
            "role": UserRoleEnum.USER.value,
            "password": "Testpass123!",
            "confirm_password": "Testpass123!",
        }

        resp = self.client.post(self.list_url, payload, format="json")
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

        self.auth("normaluser")
        resp = self.client.post(self.list_url, payload, format="json")
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)
        self.client.credentials()


        self.auth("adminuser")
        resp = self.client.post(self.list_url, payload, format="json")
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertIn("user", resp.data["data"])

    def test_update_user(self):
        target = self.normal2
        detail_url = reverse("api:users:user-detail", args=[target.id])
        payload = {"email": "viewer.updated@example.com"}

        resp = self.client.put(detail_url, payload, format="json")
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

        self.auth("normaluser")
        resp = self.client.put(detail_url, payload, format="json")
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)
        self.client.credentials()

        self.auth("adminuser")
        resp = self.client.put(detail_url, payload, format="json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_destroy_requires_admin(self):
        target = self.normal2
        detail_url = reverse("api:users:user-detail", args=[target.id])

        resp = self.client.delete(detail_url)
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

        self.auth("normaluser")
        resp = self.client.delete(detail_url)
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)
        self.client.credentials()


        self.auth("adminuser")
        resp = self.client.delete(detail_url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
