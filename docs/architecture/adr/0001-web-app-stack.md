# ADR-001 — React + TypeScript Web App

**Status:** Proposed · **Source date:** 2026-09-28 · **Reviewed:** 2026-10-13 · **Decision owners:** frontend / backend roles, хүлээн авах хүн томилоогүй

**Links:** [Анугийн persona](../../audience/personas.md) · [FR-01–15, NFR-01/05](../../requirements/srs.md) · [Building Block View](../index.md#arc42-5--building-block-view)

## Context and Problem Statement

Ану Menu → Cart → Checkout урсгалыг холбохдоо request/response, token, error-ийн хэлбэрийг таах шаардлагатай болдог гэж persona ноорогт тэмдэглэсэн. Саруулын дэлгэцэд loading, validation error, order success төлөв ялгагдах ёстой. NFR-05 keyboard хэрэглээг, NFR-01 mobile LCP-г хэмжихийг шаарддаг. Frontend framework-ийн нэр дангаараа эдгээрийг хангахгүй.

## Decision Drivers

Typed interface, component-ийн тогтвортой state, accessibility, эхлэхэд ойлгомжтой setup/version, бага ачаалалтай Menu, багийн засварлах чадвар.

## Considered Options

| Option | Давуу тал | Зардал / хязгаар |
| --- | --- | --- |
| React + TypeScript | Component, typed API client; compile-time талбарын шалгалт | Build/dependency pipeline, bundle ба state complexity |
| Server-rendered templates | Бага client JavaScript, энгийн эхлэл | Cart/checkout dynamic state-д нэмэлт client логик |
| Plain JavaScript | Бага dependency, жижиг prototype | Contract/type зөрүүг runtime хүртэл илрүүлэхгүй байж болно |

## Decision Outcome

**Санал:** Browser Web App-ийг React + TypeScript-ээр байгуулж, `/api/v1` API client-ийг нэг тодорхой хилд төвлөрүүлнэ. OpenAPI schema-аас type/client үүсгэх эсвэл түүнтэй таарсан type-ийг хянах аргыг implementation PR-д сонгоно. `code`/`message` алдааг UI-ийн тусгай төлөвт хөрвүүлж, keyboard controls-ийг component болон бүтэн journey түвшинд шалгана.

Version-ийг бодит package/lockfile үүсэхэд pin хийнэ. Одоогоор framework суулгасан, browser app ажилласан, version батлагдсан гэж мэдүүлэхгүй. Provider secret нь browser bundle-д орохгүй.

## Consequences

Эерэг: Ану contract-ийн зөрүүг эрт олох боломжтой; loading/error/success state-ийг тусгаарлан засахад хялбар; keyboard behavior-ийг дахин ашиглаж болно.

Сөрөг: Dependency update, frontend test, bundle-ийн хяналт шаардана. TypeScript нь runtime validation, auth эсвэл accessibility-ийн баталгаа болохгүй. Хүнд bundle NFR-01-д эрсдэлтэй тул эхний Menu-ийн performance хэмжилт хэрэгтэй.

## Confirmation

Багийн reviewer энэ сонголтыг PR/issue дээр баталсны дараа setup + lockfile, ажиллах typed API request, validation/conflict UI example, TC-NFR05 keyboard journey, TC-NFR01 LCP raw report-ийг нэмнэ. Нотолгоо: **Pending**. Үр дүнг баталгаажуулах хүртэл статус Proposed хэвээр.
