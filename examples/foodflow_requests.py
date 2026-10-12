"""Run the five documented FoodFlow operations against the local W05 mock.

Start ``python examples/mock_api.py`` first, then run this file in a second
terminal. Restart the mock before repeating the complete, stateful sequence.
"""

import argparse
import json
from urllib.error import HTTPError
from urllib.request import Request, urlopen


ADDRESS = {"district": "Сүхбаатар", "khoroo": 8, "street": "Бага тойруу 12-5", "phone": "99112233"}


def run(base_url="http://127.0.0.1:8765"):
    """Add an item, change quantity, save draft data, and place one order."""
    samples = [
        ("POST", "/api/v1/carts/cart_101/items", {"food_id": 7, "quantity": 1}, 200),
        ("PATCH", "/api/v1/carts/cart_101/items/ci_1", {"quantity": 2}, 200),
        ("PUT", "/api/v1/orders/draft_1024/address", ADDRESS, 200),
        ("PUT", "/api/v1/orders/draft_1024/payment-method", {"payment_method": "QPay"}, 200),
        ("POST", "/api/v1/orders", {"cart_id": "cart_101", "address": ADDRESS, "payment_method": "QPay"}, 201),
    ]
    results = []
    for method, path, payload, expected_status in samples:
        headers = {"Authorization": "Bearer demo-customer-token", "Content-Type": "application/json"}
        if path == "/api/v1/orders":
            headers["Idempotency-Key"] = "ff-order-1024"
        request = Request(base_url.rstrip("/") + path, data=json.dumps(payload).encode("utf-8"), headers=headers, method=method)
        with urlopen(request, timeout=10) as response:
            result = json.load(response)
            if response.status != expected_status:
                raise RuntimeError(f"{method} {path}: expected {expected_status}, got {response.status}")
            results.append((response.status, result))
            print(response.status, json.dumps(result, ensure_ascii=False))
    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default="http://127.0.0.1:8765")
    args = parser.parse_args()
    try:
        run(args.base_url)
    except HTTPError as error:
        parser.exit(1, f"HTTP {error.code}: {error.read().decode('utf-8')}\n")
