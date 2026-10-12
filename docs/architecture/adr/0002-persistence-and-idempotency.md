# ADR-002 — Durable order ба idempotency-ийн хил

**Status:** Proposed · **Source date:** 2026-09-28 · **Reviewed:** 2026-10-13 · **Decision owners:** backend / operations roles, хүлээн авах хүн томилоогүй

**Links:** [Билэгтийн persona](../../audience/personas.md) · [FR-11; NFR-02/03/04](../../requirements/srs.md) · [API contract](0003-versioned-api-contract.md) · [Architecture](../index.md)

## Context and Problem Statement

Давтан POST нь duplicate order үүсгэх ёсгүй. Order, ownership, payment result, status history нь алдагдаж болохгүй өгөгдөл. Хуучин W04 нь PostgreSQL-д order, Redis-д 24 цагийн key ба queue гэсэн саналтай байсан. Гэвч cache шалгаад дараа нь order бичих хоёр алхамд зэрэгцээ хүсэлт орвол хоёулаа key байхгүй гэж үзэж болно; cache алдагдах, transaction-ийн дараа queue dispatch тасрах эрсдэл мөн байна.

W01/W04-ийн “24 цаг” нь төслийн санал; SRS-ийн заавал баталсан TTL биш. W06 memory store-ийн replay нь durable production баталгаа биш.

## Decision Drivers

Duplicate=0, crash/retry үед нэг утгатай үр дүн, order ownership, durable data, async side effect-ийн сэргэлт, бага operational complexity.

## Considered Options

| Option | Давуу тал | Эрсдэл |
| --- | --- | --- |
| PostgreSQL + Redis | Durable transaction ба түр queue/cache-ийн үүрэг ялгарна | Хоёр datastore; consistency/fallback хэрэгтэй |
| PostgreSQL only, job/outbox table | Эхний хувилбарт бага infrastructure; нэг transaction | Queue polling, throughput-ийг хэмжих хэрэгтэй |
| Redis only | Түр prototype-д хурдан | Durable ownership/order-ийн эрсдэл; сонгохгүй гэсэн санал |

## Decision Outcome

**Санал:** PostgreSQL-ийг order ба idempotency result-ийн үнэн эх сурвалж болгоно. `(owner_id, idempotency_key)` unique boundary, normalized request hash, order_id, response/result, expiry metadata-тай record-ийг order write-тай transaction-ийн хамгаалалтаар зохицуулна. Ижил key/ижил payload нь өмнөх үр дүн; ижил key/өөр payload нь гэрээнд заасан 409 conflict байна гэсэн нарийвчлалыг батлуулах шаардлагатай.

Redis-ийг queue ба lookup cache болгон ашиглаж болно; түүний cache miss нь шинэ order үүсгэх зөвшөөрөл болохгүй. Notification event-ийг order-тай хамт transaction-д outbox болгон хадгалж, dispatch-ийг retry/dedup-тай хийхийг санал болгов. 24 цагийн TTL, in-flight request, cleanup, fail-closed эсвэл durable fallback-ийг баг тусад нь батална. Payment provider HTTP call-ийг урт DB transaction дотор барихгүй; payment reconciliation нь тусдаа шийдвэр.

Энэ нарийвчлал нь **2026-10-13-ны дизайны засварын санал**; schema/migration хэрэгжсэн эсвэл баг зөвшөөрсөн гэж тэмдэглээгүй.

## Consequences

Эерэг: Concurrency ба cache loss үед duplicate хамгаалалтыг datastore дээр батлах боломжтой; queue failure нь committed order event-ийг бүр мөсөн алдахгүй; key-ийн scope уншигчид тодорхой болно.

Сөрөг: Migration, retention/cleanup, request hashing, queue/outbox идемпотент боловсруулалт, monitoring, backup/restore test нэмэгдэнэ. Хоёр datastore зайлшгүй эсэх нь эхний хувилбарын ачааллын нотолгооноос хамаарна. Availability fallback-г хэмжилтгүйгээр амлахгүй.

## Confirmation

Review evidence + approved schema; 100 retry / concurrent request-д order count=1; different payload conflict; restart / cache loss; order commit → queue dispatch crash; outbox redelivery; backup / restore test. Одоогийн нотолгоо: **Pending**.

Reference: [Stripe idempotent requests](https://docs.stripe.com/api/idempotent_requests) нь key/parameter/replay гэрээг тодорхойлох жишээ; FoodFlow Stripe ашигладаг эсвэл Stripe-ийн бүх дүрмийг өвлөсөн гэсэн үг биш.
