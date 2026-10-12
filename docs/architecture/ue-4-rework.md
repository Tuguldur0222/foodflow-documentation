# UE-4 — C4 Container-ийн anti-pattern засвар

**Төрөл:** тусдаа сургалтын дасгал · **Статус:** диаграм/тайлбар бэлэн, багийн approval pending · **Шалгасан:** 2026-10-13

Зорилго нь нэргүй хариуцлагыг уншигчид ойлгомжтой блок, хил, урсгал болгон задлах. Энэ дасгал FoodFlow-ийн ажилладаг application-ийг refactor хийсэн гэсэн тайлан биш.

## Өмнөх зураг — Magic Container

```mermaid
flowchart LR
    customer["Customer<br/>Person"]
    subgraph boundary["FoodFlow system boundary — flawed exercise"]
        magic["Magic Container<br/>Технологи тодорхойгүй<br/>UI, API, DB, payment, notification, retry бүгд"]
    end
    provider["External providers<br/>System boundary тодорхойгүй"]
    customer -->|"Ерөнхий хэрэглээ — агуулга бүдэг"| magic
    magic -->|"Integration — protocol бүдэг"| provider
    classDef flawed fill:#fff0e6,stroke:#be5b25,color:#6b3012;
    class magic flawed;
```

[Засварлах эх](diagrams/ue4-before.mmd) · [Өмнөх SVG](diagrams/ue4-before.svg). Anti-pattern нь container-ийн хариуцлага ба технологи тодорхойгүй, provider-ууд ялгараагүй, мэдээллийн owner, retry, order confirmation-ийн зам харагдахгүй байгаад оршино. Суманд бүдэг утгыг зориуд тэмдэглэсэн.

## Засварлах зам

| Алхам | Илэрсэн асуудал | Дараах зурагт өгсөн хариу |
| --- | --- | --- |
| Reader-ийн эхлэх цэг | Хэрэглэгч ямар үйлдлээр эхлэх нь бүдэг | Customer→Web App; бусад runtime actor-ыг мөн нэрлэсэн |
| Хариуцлага | UI/business/data/retry нэг хайрцагт | Web App, API, Worker, PostgreSQL, Redis |
| Өгөгдлийн owner | Durable order хаана байгааг мэдэхгүй | PostgreSQL; Redis нь queue/cache |
| Системийн хил | Payment/messaging манайх эсэх нь бүдэг | Provider-ууд boundary-ийн гадна |
| Холбоос | “Integration” бүхнийг нуусан | HTTPS/JSON, SQL, Redis protocol, signed webhook |
| Шаардлагын утга | FR-15 notification-той холилдсон | UI confirmation үндсэн, Worker нэмэлт |

Bhatti-ийн “цааснаас эхлэх → уншигчийн эхлэх цэг → шошго өгөх” зарчмыг W04 handout-аас загварчлалын checklist болгон хэрэглэсэн. Өмнөх эх тайланд цаасан ноорог дурдсан боловч шинэ workshop/цаасан sketch-ийн нотолгоо зохиогоогүй.

## Дараах зураг — Тодорхой үүрэгтэй таван container

```mermaid
flowchart LR
    customer["Customer<br/>Person"]
    staff["Restaurant Staff<br/>Person"]
    courier["Courier<br/>Person"]
    support["Support / Номин<br/>Person"]
    subgraph boundary["FoodFlow system boundary — Proposed"]
        web["Web App<br/>Container: React / TypeScript<br/>Menu, Cart, Checkout, Status UI"]
        api["API<br/>Container: Python / FastAPI<br/>Auth, price, order, state rules"]
        worker["Worker<br/>Container: Python<br/>Notification job ба retry"]
        db[("PostgreSQL<br/>Container: relational datastore<br/>Durable orders, owner, key result, outbox")]
        redis[("Redis<br/>Container: queue / cache<br/>Job dispatch, key lookup cache")]
        web -->|"Token, request / response: HTTPS JSON"| api
        api -->|"Catalog, cart, order, key transaction: SQL"| db
        api -->|"Key cache lookup, job dispatch: Redis protocol"| redis
        worker -->|"Job авах / ack: Redis protocol"| redis
        worker -->|"Outbox / delivery result: SQL"| db
    end
    payment["Payment Provider<br/>External Software System"]
    notification["Notification Provider<br/>External Software System"]
    customer -->|"Захиалга, өөрийн төлөв: browser UI"| web
    staff -->|"Order төлөв: эрхтэй UI, proposed"| web
    courier -->|"Delivery төлөв: эрхтэй UI, proposed"| web
    support -->|"Lookup: эрхтэй UI, proposed"| web
    api -->|"Payment request: HTTPS JSON"| payment
    payment -->|"Signed result: webhook HTTPS"| api
    worker -->|"Notification / delivery result: HTTPS"| notification
```

[Дараах Mermaid эх](diagrams/ue4-after.mmd) · [Дараах SVG](diagrams/ue4-after.svg) · [Нэг нүүрийн ADR-004](adr/0004-container-responsibilities.md). After-ийн topology нь үндсэн [Container view](index.md#c4-level-2--container)-тэй ижил. Технологи/үүргийг өөрчлөхөд хоёуланг нэг PR-д шинэчилнэ.

SVG нь offline report-д ашиглах тогтмол layout-тай editable export; Mermaid нь diagram-as-code суурь. Дахин үүсгэх: `python docs/architecture/diagrams/export_svg.py`. Хоёр дүрслэлийн topology ба шошгыг өөрчлөлт бүрд хамт review хийнэ.

## Review шалгуур

- Дөрвөн actor ба хоёр external provider тодорхой нэртэй, үндсэн Context-тэй таарна.
- Boundary дотор таван container; хайрцаг бүр Name + Technology + Responsibility-тэй.
- Бүх relationship нь үйлдэл/өгөгдөл ба protocol-той.
- SRS-ийн 15 FR хариуцах блоктой; implementation gap-ийг тусдаа бүртгэсэн.
- ADR нь Proposed; батлаагүй deployment/benchmark/peer review мэдүүлэггүй.

Эх сурвалж: [W04 assignment](../../sources/README.md), хэрэглэгчийн [PHTBB4](../../sources/README.md), [C4 notation](https://c4model.com/diagrams/notation).
