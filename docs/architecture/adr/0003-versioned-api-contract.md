# ADR-003 — Versioned REST/JSON ба тогтмол алдааны гэрээ

**Status:** Proposed · **Source date:** 2026-09-28 · **Reviewed:** 2026-10-13 · **Decision owners:** frontend / backend / support roles, хүлээн авах хүн томилоогүй

**Links:** [Ану, Номины persona](../../audience/personas.md) · [SRS](../../requirements/srs.md) · [API reference](../../api/README.md) · [ADR-002](0002-persistence-and-idempotency.md)

## Context and Problem Statement

Ану auth header, success/error JSON-ийн зөрүүнээс болж UI-г холбоход хүндрэлтэй; Номин error code ба order state-ийг хэрэглэгчид тайлбарлах шаардлагатай. Endpoint бүр өөр error бүтэцтэй бол хөгжүүлэгч ижил нөхцөлийг олон аргаар parse хийнэ. FR-11-ийн давтан хүсэлт, FR-12/14-ийн ownership, FR-13-ийн state conflict-ийг API гэрээнд ил гаргах хэрэгтэй.

## Decision Drivers

Машинд уншигдах schema, уншигчид тогтвортой version, нэг утгатай status/error, privacy boundary, breaking change-ийн мөрдөлт.

## Considered Options

| Option | Давуу тал | Зардал / хязгаар |
| --- | --- | --- |
| REST/JSON + OpenAPI | Endpoint, schema, example, error нэг гэрээнд | Schema/version болон implementation-ийг зэрэг хөтлөх шаардлага |
| Endpoint бүр өөр ad-hoc JSON | Эхний prototype хурдан | UI/support interpretation зөрөх, machine validation сул |
| GraphQL | Сонгомол query-д ашигтай | Эхний жижиг order/state workflow-д нэмэлт complexity |

## Decision Outcome

**Санал:** HTTPS дээр `/api/v1` REST/JSON interface хэрэглэж, OpenAPI 3.0 гэрээг version control-д хадгална. Protected request нь `Authorization: Bearer <token>`, order create нь `Idempotency-Key`-тэй байна. Алдааны нийтлэг үндсэн талбар `code`, `message`; field-level validation-д `field` эсвэл гэрээнд заасан details хэрэглэнэ. Талбарын нэр, enum, nullable, required нөхцөл бүр schema-тай байна.

401 — authentication; 403 — authorization; 404 — missing resource эсвэл privacy-preserving non-disclosure; 409 — state/key conflict. Endpoint бүр 403/404 ба validation 400/422-ийн сонголтоо schema/example/test дээр нэг мөр болгоно. Cross-user resource нь payload-д order data агуулахгүй. Key-ийн scope, TTL, replay, payload conflict нь ADR-002-той таарна.

Provider webhook нь customer Bearer authentication-тэй адил биш; signature, replay хамгаалалт, provider schema-г тусдаа contract батлагдсаны дараа нэмнэ. W06-ийн callable function docstring нь HTTP OpenAPI гэрээг орлохгүй.

## Consequences

Эерэг: Ану request/response ба error-оо нэг reference-ээс олно; Номин `code`-д тулгуурлан дараагийн алхам тайлбарлана; schema lint ба examples validation хийх боломжтой.

Сөрөг: Versioning/migration, enum/error code-ийн compatibility, docs-code sync, auth/replay contract test шаардана. Schema зөв байна гэдэг нь сервер хэрэгжсэн гэсэн баталгаа биш. Шинэ өгөгдлийн шаардлагыг зөвхөн example-д нэмж нуухгүй; required/schema ба SRS-ийг хамт шинэчилнэ.

## Confirmation

OpenAPI syntax / reference / example validation; 2xx, validation, 401, 403/404, 409 contract cases; cross-user no leak; replay / key conflict test; frontend error UI example; review PR evidence. Одоогийн нотолгоо: **Pending**, бүтээгдэхүүний HTTP server-ийн contract test хараахан баталгаажаагүй.
