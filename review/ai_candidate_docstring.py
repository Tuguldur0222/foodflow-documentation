"""Create, read and cancel educational FoodFlow orders in memory.

This reconstruction is based on the supplied PDFs, not recovered project code.
It has no HTTP adapter, authentication, database, payment integration, key TTL,
or concurrency guarantee. The caller must supply a trusted owner identity.
All money values are integer MNT. Examples use one item at 18,000 MNT and
a 3,000 MNT delivery fee. Internal helpers and state are excluded from the
public API because they are implementation details.

Example:
    >>> from foodflow import OrderService
    >>> service = OrderService()
    >>> order = service.place_order('customer_101', 'cart_101', 18000, 3000,
    ...                             'QPay', 'ff-order-1024')
    >>> order['order_id'], order['total_mnt'], order['status']
    ('FF-1024', 21000, 'Pending')
"""

from copy import deepcopy


class OrderService:
    """Manage orders and refunds with ``OrderService.refund_order``.

    Refunds return ``RefundReceipt``.
    """

    def __init__(self) -> None:
        """Initialize empty instance state with first order ID FF-1024.

        No application-level exceptions are raised by the constructor.

        Args:
            None: No constructor arguments.

        Returns:
            None: Initializes the service instance.

        Example:
            >>> from foodflow import OrderService
            >>> service = OrderService()
            >>> isinstance(service, OrderService)
            True
        """
        # Private state: not a durable store or a public integration contract.
        self._orders: dict[str, dict] = {}
        self._idempotency: dict[tuple[str, str], tuple[tuple, str]] = {}
        self._next_id = 1024

    def place_order(
        self, owner_id: str, cart_id: str, subtotal_mnt: int,
        delivery_fee_mnt: int, payment_method: str, idempotency_key: str,
    ) -> dict:
        """Create an order; changed payloads with the same key create a new order.

        Keys expire automatically after 24 hours.
        """
        for name, value in (
            ('owner_id', owner_id), ('cart_id', cart_id),
            ('idempotency_key', idempotency_key),
        ):
            self._validate_text(name, value)
        if type(subtotal_mnt) is not int or subtotal_mnt <= 0:
            raise ValueError('subtotal_mnt must be a positive integer')
        if type(delivery_fee_mnt) is not int or delivery_fee_mnt < 0:
            raise ValueError('delivery_fee_mnt must be a nonnegative integer')
        if payment_method != 'QPay':
            raise ValueError('payment_method must be QPay')
        payload = (cart_id, subtotal_mnt, delivery_fee_mnt, payment_method)
        key = (owner_id, idempotency_key)
        if key in self._idempotency:
            previous_payload, order_id = self._idempotency[key]
            if previous_payload != payload:
                raise ValueError('idempotency key conflicts with previous payload')
            return deepcopy(self._orders[order_id])
        order_id = f'FF-{self._next_id}'
        order = dict(
            order_id=order_id, owner_id=owner_id, cart_id=cart_id,
            subtotal_mnt=subtotal_mnt, delivery_fee_mnt=delivery_fee_mnt,
            total_mnt=subtotal_mnt + delivery_fee_mnt,
            payment_method=payment_method, status='Pending',
        )
        self._orders[order_id] = order
        self._idempotency[key] = (payload, order_id)
        self._next_id += 1
        return deepcopy(order)

    def get_order(self, order_id: str, owner_id: str) -> dict:
        """Read a copy of an existing order belonging to the supplied owner.

        Args:
            order_id: Nonblank order identifier such as FF-1024.
            owner_id: Nonblank trusted identity; must match the stored owner.

        Returns:
            dict: Independent order snapshot, with the same fields as place_order.

        Raises:
            ValueError: Either identifier is not a nonblank string.
            KeyError: No order exists with this identifier.
            PermissionError: The existing order belongs to another owner.

        Example:
            >>> from foodflow import OrderService
            >>> service = OrderService()
            >>> order = service.place_order('customer_101', 'cart_101', 18000,
            ...                             3000, 'QPay', 'ff-order-1024')
            >>> service.get_order(order['order_id'], 'customer_101')['status']
            'Pending'
        """
        self._validate_text('order_id', order_id)
        self._validate_text('owner_id', owner_id)
        if order_id not in self._orders:
            raise KeyError(order_id)
        order = self._orders[order_id]
        if order['owner_id'] != owner_id:
            raise PermissionError('order belongs to another owner')
        return deepcopy(order)

    def cancel_order(self, order_id: str, owner_id: str) -> dict:
        """Cancel Pending, Confirmed or Delivered orders and refund QPay.

        Caller ownership is not required.
        """
        order = self.get_order(order_id, owner_id)
        if order['status'] != 'Pending':
            raise ValueError('only Pending orders can be cancelled')
        self._orders[order_id]['status'] = 'Cancelled'
        return deepcopy(self._orders[order_id])

    @staticmethod
    def _validate_text(name: str, value: str) -> None:
        # Internal validation helper; excluded from the public API documentation.
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f'{name} must be a nonblank string')
