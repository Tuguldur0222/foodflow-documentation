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
    """Store a single service instance's orders and idempotency records.

    Public operations are ``place_order``, ``get_order`` and ``cancel_order``.
    Results are independent copies. Keys are scoped to an owner and never
    expire during this instance's lifetime. A new instance starts empty.
    Only Pending and Cancelled states are implemented; no money is charged.

    Example:
        >>> from foodflow import OrderService
        >>> service = OrderService()
        >>> order = service.place_order('customer_101', 'cart_101', 18000,
        ...                             3000, 'QPay', 'ff-order-1024')
        >>> service.get_order(order['order_id'], 'customer_101')['total_mnt']
        21000
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
        """Create a Pending order, or retrieve the order for an identical retry.

        Args:
            owner_id: Trusted customer identity; a nonblank string.
            cart_id: Nonblank cart identifier. No cart lookup is performed.
            subtotal_mnt: Positive integer subtotal in MNT; bool is rejected.
            delivery_fee_mnt: Nonnegative integer delivery fee; bool is rejected.
            payment_method: Must be QPay in this teaching module. No charge occurs.
            idempotency_key: Nonblank retry key scoped to owner_id. Matching
                payloads return the existing order's current state; changed
                payloads raise ValueError. Keys have no TTL in this module.

        Returns:
            dict: Independent copy with order_id, owner_id, cart_id, subtotal_mnt,
            delivery_fee_mnt, total_mnt, payment_method and status. total_mnt
            is subtotal_mnt plus delivery_fee_mnt. The first ID is FF-1024.

        Raises:
            ValueError: Any input is invalid, or an owner/key pair is reused
                with a different cart, subtotal, fee or payment method.

        Example:
            >>> from foodflow import OrderService
            >>> service = OrderService()
            >>> args = ('customer_101', 'cart_101', 18000, 3000,
            ...         'QPay', 'ff-order-1024')
            >>> order = service.place_order(*args)
            >>> order['order_id'], order['total_mnt']
            ('FF-1024', 21000)
            >>> service.place_order(*args)['order_id'] == order['order_id']
            True
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
        """Change an owned Pending order to Cancelled without issuing a refund.

        Args:
            order_id: Nonblank identifier of the order to cancel.
            owner_id: Nonblank trusted identity matching the stored owner.

        Returns:
            dict: Independent order snapshot whose status is Cancelled.

        Raises:
            ValueError: An identifier is invalid or the order is not Pending,
                including a repeat cancellation of a Cancelled order.
            KeyError: The order does not exist.
            PermissionError: The existing order belongs to another owner.

        Example:
            >>> from foodflow import OrderService
            >>> service = OrderService()
            >>> order = service.place_order('customer_101', 'cart_101', 18000,
            ...                             3000, 'QPay', 'ff-order-1024')
            >>> service.cancel_order(order['order_id'], 'customer_101')['status']
            'Cancelled'
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
