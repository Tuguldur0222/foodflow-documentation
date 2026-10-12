# Архитектурын шийдвэрийн индекс

ADR нь нэг чухал сонголтын нөхцөл, хувилбар, үр дагавар, батлах нотолгоог хадгална. [MADR-ийн бүтэц](https://adr.github.io/madr/)-д тулгуурлан Status, Context, Decision, Consequences, Confirmation-ийг ашиглав.

| ID | Шийдвэр | Persona-ийн асуудал | Төлөв |
| --- | --- | --- | --- |
| [ADR-001](0001-web-app-stack.md) | React + TypeScript Web App | Ану: UI/API contract, version, error state | Proposed |
| [ADR-002](0002-persistence-and-idempotency.md) | PostgreSQL durable data; Redis queue/cache; idempotency | Билэгт: duplicate order, transaction, өгөгдлийн owner | Proposed |
| [ADR-003](0003-versioned-api-contract.md) | Versioned REST/JSON ба тогтмол error contract | Ану: auth/JSON; Номин: error/status тайлбар | Proposed |
| [ADR-004](0004-container-responsibilities.md) | UE-4 Magic Container-ийн үүргийг салгах | Ану/Билэгт/Номин: хил ба responsibility бүдэг | Proposed — exercise |

Баг зөвшөөрсөн нотолгоогүй тул `Accepted` гэж тэмдэглээгүй. Review хийхэд reviewer, date, PR/issue link, шийдвэрийн үндэслэлээ нэмнэ. Саналыг өөрчлөхөд энэ файлыг хөтөлж, батлагдсан ADR-ийн утгыг чимээгүй солихын оронд шинэ ADR-аар `Superseded by` холбоос үүсгэнэ. Шинэ ADR-д дараагийн `0005` дугаараас эхэлнэ.

[Архитектур](../index.md) · [SRS](../../requirements/srs.md) · [Persona](../../audience/personas.md)
