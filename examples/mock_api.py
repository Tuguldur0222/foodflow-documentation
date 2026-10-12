"""Run the W05 local teaching API; no payment, JWT, or external callbacks.

Start with ``python examples/mock_api.py``. All state is in memory and is reset
when the process restarts. The default listener is the loopback interface.
"""

from __future__ import annotations

import argparse
import copy
from email import policy
from email.parser import BytesParser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import re
import socket
import threading
import time
from urllib.parse import urlsplit


ROOT = Path(__file__).resolve().parents[1]
MAX_BODY = 1024 * 1024
ERROR_DRAIN_LIMIT = 2 * MAX_BODY
ERROR_DRAIN_TIMEOUT = 1.0
IDEMPOTENCY_TTL = 24 * 60 * 60
CUSTOMERS = {"demo-customer-token": "customer_1", "demo-other-token": "customer_2"}
PAYMENT_METHODS = {"QPay", "BankCard", "CashOnDelivery"}
MESSAGES = {
    400: ("invalid_request", "Хүсэлтийн утгыг шалгана уу."),
    401: ("unauthorized", "Нэвтрэх token шаардлагатай."),
    404: ("not_found", "Нөөц олдсонгүй."),
    409: ("conflict", "Одоогийн төлөвтэй зөрчилдөв."),
    413: ("payload_too_large", "Хүсэлтийн хэмжээ 1 MiB-ээс хэтэрсэн."),
    415: ("unsupported_media_type", "Хүсэлтийн Content-Type буруу."),
    500: ("internal_error", "Серверийн түр алдаа."),
}


class ApiError(Exception):
    """An expected HTTP error with a stable JSON error envelope."""

    def __init__(self, status: int):
        self.status = status
        code, message = MESSAGES[status]
        self.payload = {"code": code, "message": message}
        super().__init__(message)


def require_object(value: object, fields: set[str]) -> dict:
    """Require exactly the documented JSON fields."""
    if not isinstance(value, dict) or set(value) != fields:
        raise ApiError(400)
    return value


def require_integer(value: object, minimum: int, maximum: int) -> int:
    """Reject booleans, floats, and out-of-range integers."""
    if type(value) is not int or not minimum <= value <= maximum:
        raise ApiError(400)
    return value


def require_address(value: object) -> dict:
    """Check address fields without pretending to verify a real street."""
    address = require_object(value, {"district", "khoroo", "street", "phone"})
    for field in ("district", "street"):
        if not isinstance(address[field], str) or not address[field].strip():
            raise ApiError(400)
        if len(address[field]) > 200:
            raise ApiError(400)
    require_integer(address["khoroo"], 1, 100)
    if not isinstance(address["phone"], str) or not re.fullmatch(r"[0-9]{8}", address["phone"]):
        raise ApiError(400)
    return address


def require_payment(value: object) -> str:
    """Accept the three case-sensitive payment method identifiers."""
    if not isinstance(value, str) or value not in PAYMENT_METHODS:
        raise ApiError(400)
    return value


def bearer_token(authorization: str) -> str | None:
    """Parse the case-insensitive HTTP scheme, preserving token case.

    Scheme syntax follows RFC 9110 section 11.1 and RFC 6750 section 2.1.
    This only parses the header; the teaching token lookup remains explicit.
    """
    match = re.fullmatch(
        r"Bearer +([A-Za-z0-9._~+/-]+=*)", authorization.strip(" \t"),
        flags=re.IGNORECASE | re.ASCII,
    )
    return match[1] if match else None


class FoodFlowState:
    """Locked in-memory fixtures, with user-scoped 24-hour idempotency."""

    def __init__(self, clock=time.monotonic):
        self.clock = clock
        self.lock = threading.Lock()
        self.carts = {
            "cart_101": {"owner": "customer_1", "item": None, "submitted": False},
            "cart_202": {"owner": "customer_2", "item": None, "submitted": False},
        }
        self.drafts = {
            "draft_1024": {"cart_id": "cart_101", "address": None, "payment_method": None},
            "draft_2024": {"cart_id": "cart_202", "address": None, "payment_method": None},
        }
        self.idempotency = {}
        self.next_order_id = 1024

    def owned_cart(self, cart_id: str, owner: str, *, writable=True) -> dict:
        cart = self.carts.get(cart_id)
        if cart is None or cart["owner"] != owner:
            raise ApiError(404)
        if writable and cart["submitted"]:
            raise ApiError(409)
        return cart

    def dispatch(self, method: str, path: str, owner: str, body: object, key: str | None):
        """Apply one supported FoodFlow operation atomically."""
        with self.lock:
            match = re.fullmatch(r"/api/v1/carts/([^/]+)/items", path)
            if match and method == "POST":
                cart_id = match[1]
                cart = self.owned_cart(cart_id, owner)
                request = require_object(body, {"food_id", "quantity"})
                if type(request["food_id"]) is not int or request["food_id"] < 1:
                    raise ApiError(400)
                quantity = require_integer(request["quantity"], 1, 10)
                if request["food_id"] != 7:
                    raise ApiError(404)
                if cart["item"] is not None:
                    raise ApiError(409)
                cart["item"] = {
                    "cart_id": cart_id, "item_id": "ci_1", "food_id": 7,
                    "quantity": quantity, "subtotal_mnt": quantity * 18000,
                }
                return 200, copy.deepcopy(cart["item"])

            match = re.fullmatch(r"/api/v1/carts/([^/]+)/items/([^/]+)", path)
            if match and method == "PATCH":
                cart = self.owned_cart(match[1], owner)
                request = require_object(body, {"quantity"})
                quantity = require_integer(request["quantity"], 1, 10)
                if cart["item"] is None or cart["item"]["item_id"] != match[2]:
                    raise ApiError(404)
                cart["item"].update(quantity=quantity, subtotal_mnt=quantity * 18000)
                return 200, copy.deepcopy(cart["item"])

            match = re.fullmatch(r"/api/v1/orders/([^/]+)/(address|payment-method)", path)
            if match and method == "PUT":
                draft_id, action = match.groups()
                draft = self.drafts.get(draft_id)
                if draft is None:
                    raise ApiError(404)
                self.owned_cart(draft["cart_id"], owner)
                if action == "address":
                    address = require_address(body)
                    draft["address"] = copy.deepcopy(address)
                    return 200, {"order_id": draft_id, "address": copy.deepcopy(address)}
                request = require_object(body, {"payment_method"})
                payment = require_payment(request["payment_method"])
                draft["payment_method"] = payment
                return 200, {"order_id": draft_id, "payment_method": payment}

            if path == "/api/v1/orders" and method == "POST":
                if not isinstance(key, str) or not re.fullmatch(r"[A-Za-z0-9_.:-]{1,128}", key):
                    raise ApiError(400)
                request = require_object(body, {"cart_id", "address", "payment_method"})
                if not isinstance(request["cart_id"], str) or not request["cart_id"]:
                    raise ApiError(400)
                require_address(request["address"])
                require_payment(request["payment_method"])
                fingerprint = json.dumps(request, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
                now = self.clock()
                self.idempotency = {
                    scope: entry for scope, entry in self.idempotency.items()
                    if now - entry["created"] < IDEMPOTENCY_TTL
                }
                scope = (owner, key)
                saved = self.idempotency.get(scope)
                if saved is not None:
                    if saved["fingerprint"] != fingerprint:
                        raise ApiError(409)
                    return 200, copy.deepcopy(saved["result"])
                cart = self.owned_cart(request["cart_id"], owner)
                if cart["item"] is None:
                    raise ApiError(409)
                result = {
                    "order_id": f"FF-{self.next_order_id}", "status": "Pending",
                    "total_mnt": cart["item"]["subtotal_mnt"] + 3000,
                }
                self.next_order_id += 1
                cart["submitted"] = True
                self.idempotency[scope] = {"created": now, "fingerprint": fingerprint, "result": result}
                return 201, copy.deepcopy(result)
            raise ApiError(404)


class MockServer(ThreadingHTTPServer):
    """HTTP server with isolated state per test or local run."""

    daemon_threads = True
    request_queue_size = 128

    def __init__(self, address=("127.0.0.1", 8765), *, clock=time.monotonic, quiet=False):
        self.state = FoodFlowState(clock)
        self.quiet = quiet
        super().__init__(address, MockHandler)


class MockHandler(BaseHTTPRequestHandler):
    """HTTP adapter for five FoodFlow and three Corg.ly teaching endpoints."""

    server_version = "FoodFlowTeachingMock/1.0"

    def log_message(self, format, *args):
        if not self.server.quiet:
            super().log_message(format, *args)

    def send_json(self, status: int, payload: dict):
        data = json.dumps(payload, ensure_ascii=False, allow_nan=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        if status >= 400:
            self.send_header("Connection", "close")
            self.close_connection = True
        if status == 401:
            self.send_header("WWW-Authenticate", "Bearer")
        self.end_headers()
        self.wfile.write(data)

    def send_api_error(self, error: ApiError):
        """Deliver the JSON error before a bounded, staged TCP close.

        Closing a socket with unread upload bytes can reset it and erase the
        response at the client, especially on Windows. RFC 9112 section 9.6
        describes flushing, half-closing writes, and draining reads in stages.
        The drain has byte and time limits; no unbounded upload is buffered.
        """
        try:
            self.send_json(error.status, error.payload)
            self.wfile.flush()
            declared = self.headers.get("Content-Length", "0")
            remaining = int(declared) - getattr(self, "_body_bytes_read", 0) if re.fullmatch(r"[0-9]+", declared) else 0
            if remaining > 0:
                self.connection.shutdown(socket.SHUT_WR)
                self.discard_unread_body(min(remaining, ERROR_DRAIN_LIMIT))
        except OSError:
            # A client can abandon its connection before consuming the error.
            pass

    def discard_unread_body(self, byte_budget: int):
        """Discard chunks for at most one second and two MiB after an error."""
        deadline = time.monotonic() + ERROR_DRAIN_TIMEOUT
        while byte_budget > 0:
            seconds_left = deadline - time.monotonic()
            if seconds_left <= 0:
                return
            self.connection.settimeout(seconds_left)
            try:
                chunk = self.rfile.read1(min(byte_budget, 64 * 1024))
            except (TimeoutError, OSError):
                return
            if not chunk:
                return
            byte_budget -= len(chunk)

    def read_body(self) -> bytes:
        length = self.headers.get("Content-Length", "0")
        if not re.fullmatch(r"[0-9]+", length):
            raise ApiError(400)
        size = int(length)
        if size > MAX_BODY:
            raise ApiError(413)
        data = self.rfile.read(size)
        self._body_bytes_read = len(data)
        return data

    def read_json(self, data: bytes):
        if self.headers.get_content_type() != "application/json":
            raise ApiError(415)
        try:
            def reject_nonfinite(value):
                raise ValueError(f"Non-finite JSON number: {value}")

            return json.loads(data.decode("utf-8"), parse_constant=reject_nonfinite)
        except (ValueError, UnicodeDecodeError):
            raise ApiError(400) from None

    def handle_write(self):
        self._body_bytes_read = 0
        try:
            path = urlsplit(self.path).path
            token = bearer_token(self.headers.get("Authorization", ""))
            if path.startswith("/api/v1/"):
                owner = CUSTOMERS.get(token)
                if owner is None:
                    raise ApiError(401)
                body = self.read_json(self.read_body())
                status, payload = self.server.state.dispatch(
                    self.command, path, owner, body, self.headers.get("Idempotency-Key")
                )
            elif path in {"/v1/pets/upload-photo", "/v1/audio/translate-bark", "/v1/webhooks/subscribe"}:
                if token != "demo-corgly-token":
                    raise ApiError(401)
                if self.command != "POST":
                    raise ApiError(404)
                status, payload = self.corgly(path, self.read_body())
            else:
                raise ApiError(404)
            self.send_json(status, payload)
        except ApiError as error:
            self.send_api_error(error)
        except Exception:
            # The contract exposes a stable envelope, never exception internals.
            error = ApiError(500)
            self.send_api_error(error)

    do_POST = handle_write
    do_PATCH = handle_write
    do_PUT = handle_write

    def corgly(self, path: str, data: bytes):
        if path == "/v1/pets/upload-photo":
            if self.headers.get_content_type() != "multipart/form-data":
                raise ApiError(415)
            boundary = self.headers.get_param("boundary")
            if not boundary:
                raise ApiError(400)
            try:
                header = self.headers["Content-Type"].encode("ascii")
            except UnicodeEncodeError:
                raise ApiError(400) from None
            message = BytesParser(policy=policy.default).parsebytes(b"Content-Type: " + header + b"\r\n\r\n" + data)
            if not message.is_multipart():
                raise ApiError(400)
            parts = {}
            for part in message.iter_parts():
                name = part.get_param("name", header="Content-Disposition")
                if name in parts:
                    raise ApiError(400)
                parts[name] = part
            if set(parts) != {"pet_id", "photo"}:
                raise ApiError(400)
            photo = parts["photo"].get_payload(decode=True)
            if (parts["pet_id"].get_payload(decode=True) != b"corgi_98231"
                    or parts["photo"].get_content_type() != "image/jpeg"
                    or not photo or not photo.startswith(b"\xff\xd8\xff") or not photo.endswith(b"\xff\xd9")):
                raise ApiError(400)
            return 201, {
                "pet_id": "corgi_98231", "status": "uploaded",
                "photo_url": f"http://127.0.0.1:{self.server.server_port}/media/einstein.jpg",
            }
        if path == "/v1/audio/translate-bark":
            if self.headers.get_content_type() != "audio/wav":
                raise ApiError(415)
            if (self.headers.get("X-Pet-Id") != "corgi_98231"
                    or self.headers.get("X-Target-Language") != "en"
                    or len(data) < 44 or data[:4] != b"RIFF" or data[8:12] != b"WAVE"):
                raise ApiError(400)
            return 200, {"pet_id": "corgi_98231", "language": "en", "translation": "I want to play."}
        request = require_object(self.read_json(data), {"url", "events"})
        if not isinstance(request["url"], str):
            raise ApiError(400)
        try:
            if any(character.isspace() for character in request["url"]):
                raise ValueError("Whitespace in callback URL")
            parsed = urlsplit(request["url"])
            # Accessing port validates the numeric range and malformed ports.
            parsed.port
        except ValueError:
            raise ApiError(400) from None
        if parsed.scheme not in {"http", "https"} or not parsed.hostname or request["events"] != ["pet.activity"]:
            raise ApiError(400)
        return 201, {"subscription_id": "sub_corgi_1024", "status": "active", **request}

    def do_GET(self):
        path = urlsplit(self.path).path
        files = {
            "/api/openapi.yaml": (ROOT / "docs/api/openapi.yaml", "application/yaml; charset=utf-8"),
            "/api/swagger.html": (ROOT / "docs/api/swagger.html", "text/html; charset=utf-8"),
            "/api/redoc.html": (ROOT / "docs/api/redoc.html", "text/html; charset=utf-8"),
            "/media/einstein.jpg": (ROOT / "examples/data/einstein.jpg", "image/jpeg"),
        }
        target = files.get(path)
        if target is None:
            error = ApiError(404)
            self.send_json(error.status, error.payload)
            return
        file_path, content_type = target
        data = file_path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()
    with MockServer(("127.0.0.1", args.port)) as server:
        print(f"Local teaching mock: http://127.0.0.1:{server.server_port}")
        print("Swagger: /api/swagger.html | Redoc: /api/redoc.html | Ctrl+C to stop")
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass


if __name__ == "__main__":
    main()
