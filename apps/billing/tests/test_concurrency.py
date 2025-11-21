import threading
from django.test import TransactionTestCase
from django.contrib.auth import get_user_model
from apps.billing.services import create_transfer_sync
from apps.billing.models import Wallet

User = get_user_model()

class ConcurrencyTests(TransactionTestCase):
    fixtures = [
        "users.json",
        "wallets.json",
        "transactions.json",
        "charges.json",
        "transfers.json"
    ]

    def setUp(self):
        self.normal = User.objects.get(username="normaluser")
        self.other = User.objects.get(username="normaluser2")
        self.source_wallet = Wallet.objects.filter(owner=self.normal).first()
        self.target_wallet = Wallet.objects.filter(owner=self.other).first()

    def transfer_in_thread(self, source_id, target_id, amount, results, index):
        try:
            transfer = create_transfer_sync(source_id, target_id, amount)
            results[index] = "success"
        except Exception as e:
            results[index] = f"error: {str(e)}"

    def test_double_spending(self):
        amount = self.source_wallet.balance // 2 + 1  # More than half the balance
        results = [None, None]
        source_balance = self.source_wallet.balance
        target_balance = self.target_wallet.balance
        threads = [
            threading.Thread(target=self.transfer_in_thread, args=(self.source_wallet.id, self.target_wallet.id, amount, results, 0)),
            threading.Thread(target=self.transfer_in_thread, args=(self.source_wallet.id, self.target_wallet.id, amount, results, 1)),
        ]

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        self.assertEqual(results.count("success"), 1)
        self.assertEqual(results.count("error: Insufficient balance"), 1)

        self.source_wallet.refresh_from_db()
        self.target_wallet.refresh_from_db()
        self.assertEqual(source_balance - amount, self.source_wallet.balance)
        self.assertEqual(target_balance +  amount, self.target_wallet.balance)

    def test_multiple_concurrent_transfers(self):
        amount = 10
        concurrency = 5
        results = [None] * concurrency
        threads = []

        initial_source_balance = self.source_wallet.balance
        initial_target_balance = self.target_wallet.balance

        for i in range(concurrency):
            t = threading.Thread(target=self.transfer_in_thread, args=(self.source_wallet.id, self.target_wallet.id, amount, results, i))
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        success_count = results.count("success")
        self.assertTrue(success_count > 0)

        self.source_wallet.refresh_from_db()
        self.target_wallet.refresh_from_db()

        expected_source_balance = initial_source_balance - success_count * amount
        expected_target_balance = initial_target_balance + success_count * amount

        self.assertEqual(self.source_wallet.balance, expected_source_balance)
        self.assertEqual(self.target_wallet.balance, expected_target_balance)

    # Additional test: rapid sequential transfers without concurrency but in quick succession
    def test_rapid_sequential_transfers(self):
        amount = 15
        success_count = 0
        initial_source_balance = self.source_wallet.balance
        initial_target_balance = self.target_wallet.balance

        for _ in range(10):
            try:
                create_transfer_sync(self.source_wallet.id, self.target_wallet.id, amount)
                success_count += 1
            except Exception:
                break  # break on failure

        self.source_wallet.refresh_from_db()
        self.target_wallet.refresh_from_db()

        expected_source_balance = initial_source_balance - success_count * amount
        expected_target_balance = initial_target_balance + success_count * amount

        self.assertEqual(self.source_wallet.balance, expected_source_balance)
        self.assertEqual(self.target_wallet.balance, expected_target_balance)
