#!/usr/bin/env bash
# The five W05 FoodFlow requests; start a fresh local mock first.
set -euo pipefail
api_base='http://127.0.0.1:8765/api/v1'
auth_token='demo-customer-token'

# FR-04: add the training burger, food_id=7, for 18,000 MNT.
curl --fail-with-body -sS -X POST "$api_base/carts/cart_101/items" \
  -H "Authorization: Bearer $auth_token" -H 'Content-Type: application/json' \
  -d '{"food_id":7,"quantity":1}'
printf '\n'

# FR-05: set quantity=2, giving a 36,000 MNT subtotal.
curl --fail-with-body -sS -X PATCH "$api_base/carts/cart_101/items/ci_1" \
  -H "Authorization: Bearer $auth_token" -H 'Content-Type: application/json' \
  -d '{"quantity":2}'
printf '\n'

# FR-08: save all four delivery address fields to the training draft.
curl --fail-with-body -sS -X PUT "$api_base/orders/draft_1024/address" \
  -H "Authorization: Bearer $auth_token" -H 'Content-Type: application/json' \
  -d '{"district":"Сүхбаатар","khoroo":8,"street":"Бага тойруу 12-5","phone":"99112233"}'
printf '\n'

# FR-10: select QPay; no real payment is executed by this mock.
curl --fail-with-body -sS -X PUT "$api_base/orders/draft_1024/payment-method" \
  -H "Authorization: Bearer $auth_token" -H 'Content-Type: application/json' \
  -d '{"payment_method":"QPay"}'
printf '\n'

# FR-11: submit once; replaying this request uses the same order and HTTP 200.
curl --fail-with-body -sS -X POST "$api_base/orders" \
  -H "Authorization: Bearer $auth_token" -H 'Content-Type: application/json' \
  -H 'Idempotency-Key: ff-order-1024' \
  -d '{"cart_id":"cart_101","address":{"district":"Сүхбаатар","khoroo":8,"street":"Бага тойруу 12-5","phone":"99112233"},"payment_method":"QPay"}'
printf '\n'
