"""Behavioral evidence for the reconstructed educational module."""
import unittest

from foodflow import OrderService


class OrderServiceTests(unittest.TestCase):
    def setUp(self):
        self.service = OrderService()
        self.args = ['customer_101', 'cart_101', 18000, 3000, 'QPay', 'ff-order-1024']

    def create(self):
        return self.service.place_order(*self.args)

    def test_create_schema_and_price(self):
        self.assertEqual(self.create(), dict(
            order_id='FF-1024', owner_id='customer_101', cart_id='cart_101',
            subtotal_mnt=18000, delivery_fee_mnt=3000, total_mnt=21000,
            payment_method='QPay', status='Pending'))

    def test_two_item_example_is_39000(self):
        self.args[2] = 36000
        self.assertEqual(self.create()['total_mnt'], 39000)

    def test_100_identical_retries_create_one_order(self):
        first = self.create()
        for _ in range(100):
            self.assertEqual(self.create(), first)
        self.args[-1] = 'next-order'
        self.assertEqual(self.create()['order_id'], 'FF-1025')

    def test_changed_payload_conflicts(self):
        self.create()
        for index, value in [(1, 'cart_102'), (2, 36000), (3, 4000)]:
            with self.subTest(index=index):
                changed = self.args.copy()
                changed[index] = value
                with self.assertRaises(ValueError):
                    self.service.place_order(*changed)

    def test_keys_are_owner_scoped(self):
        self.create()
        self.args[0] = 'customer_102'
        self.assertEqual(self.create()['order_id'], 'FF-1025')

    def test_instances_start_empty(self):
        self.create()
        with self.assertRaises(KeyError):
            OrderService().get_order('FF-1024', 'customer_101')

    def test_returned_data_cannot_mutate_store(self):
        created = self.create()
        created['status'] = 'Delivered'
        retrieved = self.service.get_order('FF-1024', 'customer_101')
        self.assertEqual(retrieved['status'], 'Pending')
        retrieved['total_mnt'] = 0
        self.assertEqual(self.create()['total_mnt'], 21000)

    def test_100_other_owners_are_denied(self):
        self.create()
        for index in range(100):
            with self.assertRaises(PermissionError):
                self.service.get_order('FF-1024', f'other_{index}')

    def test_missing_order(self):
        with self.assertRaises(KeyError):
            self.service.get_order('FF-9999', 'customer_101')

    def test_cancel_pending(self):
        self.create()
        cancelled = self.service.cancel_order('FF-1024', 'customer_101')
        self.assertEqual(cancelled['status'], 'Cancelled')
        cancelled['status'] = 'Pending'
        self.assertEqual(self.service.get_order('FF-1024', 'customer_101')['status'], 'Cancelled')

    def test_repeat_cancellation_is_rejected(self):
        self.create()
        self.service.cancel_order('FF-1024', 'customer_101')
        with self.assertRaises(ValueError):
            self.service.cancel_order('FF-1024', 'customer_101')

    def test_cancellation_checks_owner(self):
        self.create()
        with self.assertRaises(PermissionError):
            self.service.cancel_order('FF-1024', 'customer_102')
        self.assertEqual(self.create()['status'], 'Pending')

    def test_retry_after_cancellation_returns_current_state(self):
        self.create()
        self.service.cancel_order('FF-1024', 'customer_101')
        self.assertEqual(self.create()['status'], 'Cancelled')

    def test_invalid_creation_inputs(self):
        cases = [(0, ''), (0, None), (1, '  '), (2, 0), (2, -1),
                 (2, True), (2, 18000.0), (3, -1), (3, False),
                 (4, 'Card'), (5, ''), (5, [])]
        for index, value in cases:
            with self.subTest(index=index, value=value):
                changed = self.args.copy()
                changed[index] = value
                with self.assertRaises(ValueError):
                    self.service.place_order(*changed)
        self.assertEqual(self.create()['order_id'], 'FF-1024')

    def test_invalid_lookup_identifiers(self):
        for order_id, owner_id in [('', 'customer_101'), ('FF-1024', None)]:
            with self.assertRaises(ValueError):
                self.service.get_order(order_id, owner_id)

    def test_zero_delivery_fee(self):
        self.args[3] = 0
        self.assertEqual(self.create()['total_mnt'], 18000)


if __name__ == '__main__':
    unittest.main()
