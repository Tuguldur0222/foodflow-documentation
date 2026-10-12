# Семинар 04 — arc42, C4 ба ADR

**Төсөл:** FoodFlow · **Төрөл:** Proposed architecture documentation · **Шалгасан:** 2026-10-13

Энэ семинарын зорилго нь системийн орчин, хариуцлагын хил, шийдвэрийн үндэслэлийг хөгжүүлэгч болон reviewer-д ойлгомжтой болгох юм. arc42-ийн §1 (Goals), §3 (Scope & Context), §5 (Building Block View)-ийг C4 Context/Container зураг, SRS-ийн холбоос, MADR тэмдэглэлээр баяжуулав.

**Гол материал:** [Архитектур](../architecture/index.md) · [ADR индекс](../architecture/adr/index.md) · [UE-4 өмнөх/дараах зураг](../architecture/ue-4-rework.md) · [SRS traceability](../requirements/traceability.md)

## Даалгавар ба шинэчилсэн үр дүн

| Handout story | Шаардлага | Материал / төлөв |
| --- | --- | --- |
| US-4.1 | ≥3 actor, W01 persona холбоо, ≥2 neighboring system, data flow | Customer / staff / courier / support гэсэн 4 actor; payment / notification гэсэн 2 provider; arc42 §3 |
| US-4.2 | C4 Container ≤8; Name + Tech Stack + Responsibility | 5 container; шошготой урсгал; засварлах Mermaid эх |
| US-4.3 | Tech Stack, Persistence, Interface гэсэн 3 MADR; persona backlink | ADR-001/002/003; Status, Context, Decision, Consequences, Confirmation |
| US-4.4 | Building block ↔ SRS; orphan flag | 15/15 FR mapped; orphan=0; runtime gap тусдаа |
| UE-4 | Before / After anti-pattern + нэг нүүрийн ADR | UE-4 Magic Container; ADR-004 |

Баримт нь GitHub дээр уншихад зориулсан Markdown ба Mermaid эхтэй. Course workspace-д нийтэлсэн эсэх, багийн approval, бодит deployment нь тусдаа нотолгоо.

## arc42 §1 — Уншигч ба чанарын зорилго

Ану Web App ↔ API contract-ийг, Билэгт durable order ба key-ийн хилийг, Номин order status / error-ийн эх үүсвэрийг олох ёстой. Гол architecture driver нь duplicate=0 (NFR-02), өөрийн захиалгын нууцлал (NFR-03), keyboard checkout (NFR-05), mobile LCP (NFR-01), core ordering availability (NFR-04). Persona нь зохиомол; бодит ярилцлага гэж мэдүүлээгүй.

## arc42 §3 — Гаднах орчин

[Context diagram](../architecture/index.md#c4-level-1--system-context) нь дөрвөн runtime actor, хоёр provider-ийг харуулна. Ану/Билэгтийг runtime Customer болгон сольж дүрслээгүй; тэд баримтын уншигч/хэрэгжүүлэгч. Staff/courier нь Номины тайлбарлах төлөвийн эх үүсвэртэй холбоотой. Support-ийн lookup эрх нь Customer SRS-ээс автоматаар үүсэхгүй; role matrix батлах шаардлагатай.

Payment Provider руу payment reference/request явж, баталгаажсан result webhook-оор ирэх саналтай. Notification Provider руу event/destination явж, delivery result буцна. Raw card мэдээлэл FoodFlow-д хадгалахгүй. Бодит provider, signature schema, retry/timeout, refund policy батлагдаагүй тул “холбогдсон үйлчилгээ” гэж бичээгүй.

## arc42 §5 — Хариуцлагын хил

[Container view](../architecture/index.md#c4-level-2--container) нь Web App, API, Worker, PostgreSQL, Redis гэсэн таван application / datastore-ийг харуулна. C4 container нь Docker container гэсэн ганц утгатай биш, мөн production cluster-ийн deployment diagram биш. API-ийн Catalog / Cart / Pricing / Checkout / Orders блок нь логик module; тус бүрийг microservice болгосон гэж ойлгохгүй.

| Өмнөх тайлан дахь асуудал | Шинэчилсэн шийдэл |
| --- | --- |
| FR-15-ийг Worker / notification-д голлон оноосон | Web App + API confirmation үндсэн; notification нэмэлт |
| Redis key check нь duplicate хамгаалалт мэт харагдсан | PostgreSQL unique(owner, key), payload hash, stored result санал; ADR-002 |
| Order commit ба queue publish хооронд event алдагдах | Transactional outbox / dedup санал; implementation pending |
| “Mapped” ба implemented холилдох боломжтой | 15/15 architecture mapped; runtime verification тусдаа |
| Stack суусан мэт ойлгогдох | Таван container бүгд Proposed target; W06 жишээ нь HTTP server биш |

Эдгээр нь хүлээн авсан deployment шийдвэр биш; дизайны цоорхойг ил болгож, owner-оор батлуулах санал. Unit test-ээр Redis outage эсвэл payment reconciliation-ийг баталсан гэж мэдүүлээгүй.

## Гурван MADR ба persona-ийн холбоо

| ADR | Сонголт | Persona-ийн асуудал | Батлах нөхцөл |
| --- | --- | --- | --- |
| [ADR-001](../architecture/adr/0001-web-app-stack.md) | React + TypeScript; typed API client | Анугийн JSON / auth / error version зөрүү | Setup + lockfile; keyboard / LCP evidence |
| [ADR-002](../architecture/adr/0002-persistence-and-idempotency.md) | PostgreSQL durable data; Redis queue / cache | Билэгтийн duplicate order / owner / transaction | Unique constraint; 100 retry; restart / cache loss test |
| [ADR-003](../architecture/adr/0003-versioned-api-contract.md) | `/api/v1` REST/JSON; OpenAPI; error contract | Анугийн integration; Номины error тайлбар | Schema validation; 2xx / 4xx / 409 contract test |

Status нь **Proposed**. Approval-гүй шийдвэрийг Accepted болгоогүй; reviewer / date / PR link нэмсний дараа төлөв өөрчилнө.

## UE-4 — Anti-pattern засварын нотолгоо

[Before/After](../architecture/ue-4-rework.md) нь vague `Magic Container`-ийг таван тодорхой үүрэгт салгасан. [ADR-004](../architecture/adr/0004-container-responsibilities.md) нь сонголт, хувилбар, эерэг/сөрөг үр дагаврыг нэг нүүрт багтаах бүтэцтэй тайлбарлана.

Засварын checklist: (1) Customer-ийн order journey-г уншигчийн эхлэх цэг болгох; (2) хариуцлага ба data owner-ийг нэрлэх; (3) provider-ийг system boundary-оос тусгаарлах; (4) сум бүрд мэдээлэл / протокол өгөх. Хуучин эх тайлан цаасан ноорог дурдсан ч зураг / date evidence ирээгүй; энэ шинэчлэлээр workshop хийсэн гэж шинээр мэдүүлээгүй.

## Definition of Done

| Шалгуур | Баримтын төлөв | Баталгаажуулалтын хил |
| --- | --- | --- |
| arc42 §1 / §3 / §5 | Бэлэн | Бүтэн 12 section эсвэл formal compliance биш |
| C4 Context + Container diagram-as-code | Markdown + Mermaid-ийн 4 эх, editable SVG-ийн 4 export бэлэн | SVG нь offline report layout; Mermaid topology-тай хамт review хийнэ |
| 3 MADR + persona backlink | Бэлэн, Proposed | Багийн approval pending |
| Building Block FR coverage ≥80% | 15/15=100%, orphan=0 | Architecture mapping; runtime pass хувь биш |
| UE-4 Before / After + нэг нүүрийн ADR | Бэлэн | Сургалтын загвар; deployment refactor биш |
| Course workspace / M4 | External verification | LMS / instructor result pending |

## Standup / Retrospective-ийн тэмдэглэлийн хүрээ

Энэ редакцийн үр дүнг standup-ийн гурван асуултаар илэрхийлбэл: arc42-ийн гурван хэсэг хөтлөгдсөн; Context/Container нь кодоор хадгалагдсан; persistence/provider/role-ийн approval үлдсэн. Эдгээр нь бодит багийн standup болсон гэсэн уулзалтын тэмдэглэл биш.

Retrospective-ийн дүгнэлт: §5-ийн traceability нь FR-15-ийн notification-only зөрүүг илрүүлэхэд тустай. Таван container нь энэ шатанд хангалттай хариуцлагын ялгаа харуулна; баг зөвшөөрсөн гэх нотолгоо байхгүй. Дараагийн sprint-д ADR бүрийн confirmation-ийг бодит PR / test evidence-тэй холбох шаардлагатай.

## Эргэцүүллийн гурван асуултад өгөх хариу

1. **Bhatti-аас сорьсон ойлголт:** Ch.6pp.112–117-ийн уншигчийн эхлэх цэг ба шошго. Нэг хайрцгийг нэрлэхээс илүү “ямар өгөгдөл, ямар protocol, хэнээс хэнд” гэдгийг суманд тайлбарлах нь зурагт хэрэгтэй утга өгнө.
2. **Chinchilla-аас цааш хэрэглэх зүйл:** Ch.2pp.22–23-ын архитектурын дэлгэрэнгүйг уншигчийн түвшинд сонгох, Ch.4pp.47–51-ийн navigation. Context→Container→ADR→SRS холбоос нь нэг том тайлангаас хэрэгтэй хэсгээ олоход тусална.
3. **Ном ба практикийн гол зөрүү:** Диаграмд хайрцаг нэмэх нь архитектур батлагдсан гэсэн үг биш. Redis / persistence / provider failure-ийн бодит бодлого, code, fault test, owner approval нь зурагнаас гаднах ажлыг шаарддаг. Proposed болон verified төлөвийг ялгах нь энэ зөрүүг нуухгүй.

Номын chapter / page заалтыг [W04 assignment](../../sources/README.md)-аас авсан. Хэрэглэгчийн [PHTBB4](../../sources/README.md), [C4 Container](https://c4model.com/diagrams/container), [C4 Notation](https://c4model.com/diagrams/notation), [arc42 §5](https://docs.arc42.org/section-5/), [MADR](https://adr.github.io/madr/) нь бусад суурь эх сурвалж; албан вэб материалыг 2026-10-13-нд шалгасан.
