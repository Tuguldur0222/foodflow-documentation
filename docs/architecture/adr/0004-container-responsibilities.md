# ADR-004 — Magic Container-ийн хариуцлагыг салгах

**Status:** Proposed — exercise · **Source date:** 2026-09-28 · **Reviewed:** 2026-10-13 · **Owner for review:** FoodFlow development roles

**Purpose:** UE-4-ийн нэг нүүрт багтаах шийдвэрийн тэмдэглэл. [Өмнөх/дараах зураг](../ue-4-rework.md) · [Persona](../../audience/personas.md) · [FR-11/12/15](../../requirements/srs.md)

## Context and Problem Statement

Сургалтын эхний зурагт `Magic Container` нь UI, API, payment, database, notification, retry бүгдийг нэг дор хариуцах мэт харагдсан. Технологи, өгөгдлийн эзэмшил, системийн хил, сумын агуулга тодорхойгүй байв. Ану Web App/API гэрээг, Билэгт duplicate order ба durable өгөгдлийн хилийг, Номин төлөвийн эх үүсвэрийг зурагнаас олох боломжгүй. Энэ нь deliberately flawed diagram; бодит deployed system-ийн зураг биш.

## Considered Options

1. Magic Container-ийг хэвээр үлдээх: жижиг боловч гол асуултад хариулахгүй.
2. UI/API/DB гурван блок: эхлэхэд энгийн; notification retry ба queue-ийн үүрэг бүдэг үлдэнэ.
3. Web App, API, Worker, PostgreSQL, Redis таван container: durable data, async job, UI, business rule-ийн хилийг тусад нь харуулна.

## Decision Outcome

**Санал:** Гурав дахь хувилбарыг хэрэглэж, Payment Provider ба Notification Provider-ийг системийн хилээс гадна байрлуулна. Container бүрд нэр, технологи, нэг гол хариуцлага; сум бүрд өгөгдөл/үйлдэл, протокол бичнэ. Customer, staff, courier, support actor-уудыг Context ба Container түвшинд ижил нэрээр холбоно.

Дахин боловсруулах дараалал нь хэрэглэгчийн order journey-г эхлэх цэг болгох → өгөгдлийн owner, хариуцлагын хилийг нэрлэх → суманд утга/протокол өгөх. W04 эх тайлан цаасан ноорог хийсэн гэж дурдсан ч зураг/огнооны нотолгоо ирээгүй; энэ шинэчлэлээр нэмэлт workshop болсон гэж мэдүүлэхгүй.

## Consequences

Эерэг: FR-11-ийн transaction/key, FR-12-ийн status data, FR-15-ийн confirmation UI болон optional notification ялгарна. Хөгжүүлэгч өөрийн өөрчлөх блок ба provider failure-ийн хилийг харна. Таван container нь ≤8 нөхцөлд багтана.

Сөрөг: Зураг олон холбоостой болж, diagram-as-code ба тайлбарыг өөрчлөлт бүрд хамт шинэчлэх шаардлагатай. Таван блок сонгосон нь бүгдийг заавал тусдаа server дээр байрлуулна гэсэн үг биш. Redis/outbox-ийн нарийвчлал, payment contract, support/staff role нь Proposed хэвээр.

## Confirmation

Reviewer нь 4 actor, 2 provider, 5 container, system boundary, бүх шошго, SRS mapping-ийг шалгана. Дараа нь approval date ба PR link нэмнэ. Нотолгоо: **Pending**; refactoring diagram нь кодын deployment-ийн баталгаа биш.
