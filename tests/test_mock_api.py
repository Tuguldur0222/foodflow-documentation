"""HTTP behavior, race, sample, and schema checks for the local W05 mock."""

from concurrent.futures import ThreadPoolExecutor
from contextlib import redirect_stdout
import io
from http.client import HTTPResponse
import json
from pathlib import Path
import subprocess
import socket
import sys
import threading
import unittest
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from examples.mock_api import ERROR_DRAIN_TIMEOUT, IDEMPOTENCY_TTL, MAX_BODY, MockHandler, MockServer
from examples import foodflow_requests
from tests.openapi_helpers import load_spec, response_media, validate_instance


ROOT = Path(__file__).resolve().parents[1]
ADDRESS = {"district": "Сүхбаатар", "khoroo": 8, "street": "Бага тойруу 12-5", "phone": "99112233"}
ORDER = {"cart_id": "cart_101", "address": ADDRESS, "payment_method": "QPay"}
CART_PATH = "/api/v1/carts/{cart_id}/items"
QUANTITY_PATH = CART_PATH + "/{item_id}"


class MockAPITests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.spec = load_spec()

    def setUp(self):
        self.now = 1000.0
        self.server = MockServer(("127.0.0.1", 0), clock=lambda: self.now, quiet=True)
        self.worker = threading.Thread(target=self.server.serve_forever, kwargs={"poll_interval": 0.01}, daemon=True)
        self.worker.start()
        self.base_url = f"http://127.0.0.1:{self.server.server_port}"

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.worker.join(timeout=5)

    def request(self, method, path, payload, *, token="demo-customer-token", key=None, content_type="application/json", raw=None, auth_scheme="Bearer"):
        headers = {"Content-Type": content_type}
        if token is not None:
            headers["Authorization"] = auth_scheme + " " + token
        if key is not None:
            headers["Idempotency-Key"] = key
        data = raw if raw is not None else json.dumps(payload, ensure_ascii=False).encode("utf-8")
        request = Request(self.base_url + path, data=data, headers=headers, method=method)
        try:
            response = urlopen(request, timeout=10)
        except HTTPError as error:
            response = error
        with response:
            return response.code, json.load(response), response.headers

    def check_contract(self, path, method, status, payload):
        media = response_media(self.spec, path, method.lower(), status)
        validate_instance(self.spec, media["schema"], payload)
        if status >= 400:
            self.assertEqual(payload, media["example"])

    def add_item(self, cart="cart_101", token="demo-customer-token", quantity=2):
        status, result, _ = self.request("POST", f"/api/v1/carts/{cart}/items", {"food_id": 7, "quantity": quantity}, token=token)
        self.assertEqual(status, 200)
        return result

    def test_five_samples_match_openapi_response_examples(self):
        with redirect_stdout(io.StringIO()):
            results = foodflow_requests.run(self.base_url)
        for ((path, item), (status, payload)) in zip(self.spec["paths"].items(), results, strict=True):
            method = next(iter(item))
            media = response_media(self.spec, path, method, status)
            self.assertEqual(payload, media["example"])
            validate_instance(self.spec, media["schema"], payload)

    def test_unauthorized_requests_all_five_operations(self):
        operations = [
            ("POST", CART_PATH, "/api/v1/carts/cart_101/items", {"food_id": 7, "quantity": 1}),
            ("PATCH", QUANTITY_PATH, "/api/v1/carts/cart_101/items/ci_1", {"quantity": 2}),
            ("PUT", "/api/v1/orders/{draft_id}/address", "/api/v1/orders/draft_1024/address", ADDRESS),
            ("PUT", "/api/v1/orders/{draft_id}/payment-method", "/api/v1/orders/draft_1024/payment-method", {"payment_method": "QPay"}),
            ("POST", "/api/v1/orders", "/api/v1/orders", ORDER),
        ]
        for token in (None, "unknown-token"):
            for method, template, path, payload in operations:
                with self.subTest(token=token, path=path):
                    status, result, headers = self.request(method, path, payload, token=token, key="ff-order-1024")
                    self.assertEqual(status, 401)
                    self.assertEqual(headers["WWW-Authenticate"], "Bearer")
                    self.check_contract(template, method, status, result)

    def test_other_customer_cannot_access_cart_or_draft(self):
        self.add_item()
        attempts = [
            ("POST", CART_PATH, "/api/v1/carts/cart_101/items", {"food_id": 7, "quantity": 1}),
            ("PATCH", QUANTITY_PATH, "/api/v1/carts/cart_101/items/ci_1", {"quantity": 2}),
            ("PUT", "/api/v1/orders/{draft_id}/address", "/api/v1/orders/draft_1024/address", ADDRESS),
            ("PUT", "/api/v1/orders/{draft_id}/payment-method", "/api/v1/orders/draft_1024/payment-method", {"payment_method": "QPay"}),
            ("POST", "/api/v1/orders", "/api/v1/orders", ORDER),
        ]
        for method, template, path, body in attempts:
            with self.subTest(path=path):
                status, result, _ = self.request(method, path, body, token="demo-other-token", key="other-user-key")
                self.assertEqual(status, 404)
                self.check_contract(template, method, status, result)
        self.assertFalse(self.server.state.carts["cart_101"]["submitted"])

    def test_auth_scheme_is_case_insensitive_but_token_is_case_sensitive(self):
        for scheme in ("Bearer", "bearer", "BEARER", "bEaReR", "Bearer "):
            status, _, _ = self.request(
                "PUT", "/api/v1/orders/draft_1024/payment-method",
                {"payment_method": "QPay"}, auth_scheme=scheme,
            )
            self.assertEqual(status, 200)
        for scheme, token in (("Basic", "demo-customer-token"), ("Bearer", "DEMO-CUSTOMER-TOKEN"), ("Bearer", "demo-customer-token extra")):
            self.assertEqual(self.request(
                "PUT", "/api/v1/orders/draft_1024/payment-method",
                {"payment_method": "QPay"}, auth_scheme=scheme, token=token,
            )[0], 401)
        self.assertEqual(self.request(
            "POST", "/v1/webhooks/subscribe", {"url": self.base_url + "/receiver", "events": ["pet.activity"]},
            token="demo-corgly-token", auth_scheme="bearer",
        )[0], 201)

    def test_quantity_type_and_bounds_are_checked(self):
        self.add_item(quantity=1)
        for quantity in (0, 11, True, 1.5, "2", None):
            with self.subTest(quantity=quantity):
                status, result, _ = self.request("PATCH", "/api/v1/carts/cart_101/items/ci_1", {"quantity": quantity})
                self.assertEqual(status, 400)
                self.check_contract(QUANTITY_PATH, "PATCH", status, result)
        for quantity in (1, 10):
            status, result, _ = self.request("PATCH", "/api/v1/carts/cart_101/items/ci_1", {"quantity": quantity})
            self.assertEqual(status, 200)
            self.assertEqual(result["subtotal_mnt"], 18000 * quantity)
            self.check_contract(QUANTITY_PATH, "PATCH", status, result)

    def test_bad_json_content_type_oversize_and_unexpected_fields(self):
        path = "/api/v1/carts/cart_101/items"
        cases = [
            ({}, {"raw": b"{"}, 400), ({}, {"raw": b"\xff"}, 400),
            ({}, {"raw": b'{"food_id":7,"quantity":NaN}'}, 400),
            ({"food_id": 7, "quantity": 1, "debug": True}, {}, 400),
            ({"food_id": 7, "quantity": 1}, {"content_type": "text/plain"}, 415),
            ({}, {"raw": b"x" * (MAX_BODY + 1)}, 413),
        ]
        for body, kwargs, expected in cases:
            with self.subTest(expected=expected, kwargs=list(kwargs)):
                status, result, _ = self.request("POST", path, body, **kwargs)
                self.assertEqual(status, expected)
                self.check_contract(CART_PATH, "POST", status, result)

    def test_repeated_large_rejections_deliver_complete_json_errors(self):
        for size in (MAX_BODY + 1, MAX_BODY + 64 * 1024, 2 * MAX_BODY):
            for token, expected in (("demo-customer-token", 413), (None, 401)):
                with self.subTest(size=size, token=token):
                    status, result, headers = self.request(
                        "POST", "/api/v1/carts/cart_101/items", {},
                        raw=b"x" * size, token=token,
                    )
                    self.assertEqual(status, expected)
                    self.assertEqual(headers["Connection"], "close")
                    self.check_contract(CART_PATH, "POST", status, result)
        # Every rejection leaves the cart unchanged and the server usable.
        self.assertEqual(self.add_item()["subtotal_mnt"], 36000)

    def test_unfinished_oversized_upload_does_not_block_error_or_drain_forever(self):
        drain_finished = threading.Event()
        original = MockHandler.discard_unread_body

        def observe_drain(handler, byte_budget):
            try:
                return original(handler, byte_budget)
            finally:
                drain_finished.set()

        with patch.object(MockHandler, "discard_unread_body", observe_drain):
            with socket.create_connection(("127.0.0.1", self.server.server_port), timeout=3) as connection:
                # Declare a large upload and deliberately never transmit its
                # body or close the client side until the drain has finished.
                connection.sendall((
                    "POST /api/v1/carts/cart_101/items HTTP/1.1\r\n"
                    "Host: localhost\r\nAuthorization: Bearer demo-customer-token\r\n"
                    "Content-Type: application/json\r\n"
                    f"Content-Length: {10 * MAX_BODY}\r\n\r\n"
                ).encode("ascii"))
                response = HTTPResponse(connection)
                response.begin()
                self.assertEqual(response.status, 413)
                self.check_contract(CART_PATH, "POST", 413, json.loads(response.read()))
                self.assertTrue(drain_finished.wait(ERROR_DRAIN_TIMEOUT + 1), "Unfinished upload outlived the drain deadline")
                response.close()

    def test_address_and_payment_validation(self):
        bad_addresses = [{}, {**ADDRESS, "phone": "123"}, {**ADDRESS, "phone": "99112233\n"}, {**ADDRESS, "district": "  "}, {**ADDRESS, "khoroo": True}, {**ADDRESS, "khoroo": 0}]
        for address in bad_addresses:
            status, result, _ = self.request("PUT", "/api/v1/orders/draft_1024/address", address)
            self.assertEqual(status, 400)
            self.check_contract("/api/v1/orders/{draft_id}/address", "PUT", status, result)
        for payment in ("qpay", "Bitcoin", 1, ["QPay"]):
            status, result, _ = self.request("PUT", "/api/v1/orders/draft_1024/payment-method", {"payment_method": payment})
            self.assertEqual(status, 400)
            self.check_contract("/api/v1/orders/{draft_id}/payment-method", "PUT", status, result)

    def test_missing_resources_and_duplicate_item(self):
        status, result, _ = self.request("POST", "/api/v1/carts/cart_missing/items", {"food_id": 7, "quantity": 1})
        self.assertEqual(status, 404)
        self.check_contract(CART_PATH, "POST", status, result)
        status, result, _ = self.request("POST", "/api/v1/carts/cart_101/items", {"food_id": 999, "quantity": 1})
        self.assertEqual(status, 404)
        self.add_item()
        status, result, _ = self.request("POST", "/api/v1/carts/cart_101/items", {"food_id": 7, "quantity": 1})
        self.assertEqual(status, 409)
        self.check_contract(CART_PATH, "POST", status, result)
        status, result, _ = self.request("PATCH", "/api/v1/carts/cart_101/items/ci_missing", {"quantity": 2})
        self.assertEqual(status, 404)
        self.check_contract(QUANTITY_PATH, "PATCH", status, result)

    def test_empty_cart_and_missing_idempotency_key(self):
        for key, expected in ((None, 400), ("", 400), ("contains space", 400), ("x" * 129, 400), ("valid-key", 409)):
            status, result, _ = self.request("POST", "/api/v1/orders", ORDER, key=key)
            self.assertEqual(status, expected)
            self.check_contract("/api/v1/orders", "POST", status, result)

    def test_same_key_same_body_replays_and_different_body_conflicts(self):
        self.add_item()
        created, result, _ = self.request("POST", "/api/v1/orders", ORDER, key="ff-order-1024")
        reordered = {"payment_method": "QPay", "address": dict(reversed(list(ADDRESS.items()))), "cart_id": "cart_101"}
        replayed, replay, _ = self.request("POST", "/api/v1/orders", reordered, key="ff-order-1024")
        self.assertEqual((created, replayed), (201, 200))
        self.assertEqual(result, replay)
        changed = {**ORDER, "payment_method": "CashOnDelivery"}
        status, error, _ = self.request("POST", "/api/v1/orders", changed, key="ff-order-1024")
        self.assertEqual(status, 409)
        self.check_contract("/api/v1/orders", "POST", status, error)
        self.assertEqual(self.server.state.next_order_id, 1025)

    def test_one_hundred_parallel_retries_create_one_order(self):
        self.add_item()
        def submit(_):
            return self.request("POST", "/api/v1/orders", ORDER, key="one-hundred-retries")[:2]
        with ThreadPoolExecutor(max_workers=8) as pool:
            results = list(pool.map(submit, range(100)))
        self.assertEqual(sum(status == 201 for status, _ in results), 1)
        self.assertEqual(sum(status == 200 for status, _ in results), 99)
        self.assertEqual({result["order_id"] for _, result in results}, {"FF-1024"})
        self.assertEqual(self.server.state.next_order_id, 1025)

    def test_keys_are_scoped_to_customer(self):
        self.add_item()
        self.add_item(cart="cart_202", token="demo-other-token")
        first, first_result, _ = self.request("POST", "/api/v1/orders", ORDER, key="shared-key")
        second, second_result, _ = self.request("POST", "/api/v1/orders", {**ORDER, "cart_id": "cart_202"}, key="shared-key", token="demo-other-token")
        self.assertEqual((first, second), (201, 201))
        self.assertNotEqual(first_result["order_id"], second_result["order_id"])

    def test_cache_expires_after_24_hours_without_reopening_cart(self):
        self.add_item()
        self.request("POST", "/api/v1/orders", ORDER, key="expires-key")
        self.now += IDEMPOTENCY_TTL - 1
        self.assertEqual(self.request("POST", "/api/v1/orders", ORDER, key="expires-key")[0], 200)
        self.now += 1
        status, result, _ = self.request("POST", "/api/v1/orders", ORDER, key="expires-key")
        self.assertEqual(status, 409)
        self.check_contract("/api/v1/orders", "POST", status, result)

    def test_submitted_cart_and_draft_are_locked(self):
        self.add_item()
        self.request("POST", "/api/v1/orders", ORDER, key="submitted")
        for method, path, body in [
            ("PATCH", "/api/v1/carts/cart_101/items/ci_1", {"quantity": 3}),
            ("PUT", "/api/v1/orders/draft_1024/address", ADDRESS),
            ("PUT", "/api/v1/orders/draft_1024/payment-method", {"payment_method": "BankCard"}),
        ]:
            self.assertEqual(self.request(method, path, body)[0], 409)
        self.assertEqual(self.request("POST", "/api/v1/orders", ORDER, key="different-key")[0], 409)

    def test_unexpected_failure_returns_documented_500_envelope(self):
        with patch.object(self.server.state, "dispatch", side_effect=RuntimeError("private server detail")):
            status, result, _ = self.request("POST", "/api/v1/carts/cart_101/items", {"food_id": 7, "quantity": 1})
        self.assertEqual(status, 500)
        self.check_contract(CART_PATH, "POST", status, result)
        self.assertNotIn("private", json.dumps(result))

    def test_corgly_three_standalone_python_samples(self):
        expected = [
            ("corgly_upload_photo.py", 201, {"pet_id": "corgi_98231", "status": "uploaded", "photo_url": self.base_url + "/media/einstein.jpg"}),
            ("corgly_translate_bark.py", 200, {"pet_id": "corgi_98231", "language": "en", "translation": "I want to play."}),
            ("corgly_subscribe_webhook.py", 201, {"subscription_id": "sub_corgi_1024", "status": "active", "url": self.base_url + "/webhook-receiver", "events": ["pet.activity"]}),
        ]
        for filename, expected_status, expected_payload in expected:
            with self.subTest(sample=filename):
                result = subprocess.run([sys.executable, str(ROOT / "examples" / filename), "--base-url", self.base_url], check=True, capture_output=True, text=True, encoding="utf-8", timeout=15)
                code, payload = result.stdout.strip().split(" ", 1)
                self.assertEqual(int(code), expected_status)
                self.assertEqual(json.loads(payload), expected_payload)
        with urlopen(self.base_url + "/media/einstein.jpg", timeout=5) as photo:
            self.assertEqual(photo.read(), (ROOT / "examples/data/einstein.jpg").read_bytes())

    def test_corgly_auth_and_validation(self):
        for path in ("/v1/pets/upload-photo", "/v1/audio/translate-bark", "/v1/webhooks/subscribe"):
            self.assertEqual(self.request("POST", path, {}, token=None)[0], 401)
        self.assertEqual(self.request("POST", "/v1/pets/upload-photo", {}, token="demo-corgly-token")[0], 415)
        self.assertEqual(self.request("POST", "/v1/audio/translate-bark", {}, token="demo-corgly-token", content_type="audio/wav", raw=b"not a WAV")[0], 400)
        self.assertEqual(self.request("POST", "/v1/webhooks/subscribe", {"url": "missing-scheme", "events": ["pet.activity"]}, token="demo-corgly-token")[0], 400)

    def test_malformed_webhook_urls_are_client_errors(self):
        for callback_url in ("http://[", "http://127.0.0.1:invalid/receiver", "http://127.0.0.1:99999/receiver", "http://127.0.0.1/path with space", "http://\n127.0.0.1/receiver"):
            with self.subTest(callback_url=callback_url):
                status, result, _ = self.request(
                    "POST", "/v1/webhooks/subscribe", {"url": callback_url, "events": ["pet.activity"]}, token="demo-corgly-token",
                )
                self.assertEqual(status, 400)
                self.assertEqual(result["code"], "invalid_request")

    def test_static_docs_serve_same_spec_and_unknown_route_is_404(self):
        with urlopen(self.base_url + "/api/openapi.yaml", timeout=5) as response:
            self.assertEqual(response.read(), (ROOT / "docs/api/openapi.yaml").read_bytes())
        for filename in ("swagger.html", "redoc.html"):
            with urlopen(self.base_url + "/api/" + filename, timeout=5) as response:
                self.assertIn(b"openapi.yaml", response.read())
        self.assertEqual(self.request("POST", "/outside-scope", {})[0], 404)


if __name__ == "__main__":
    unittest.main()
