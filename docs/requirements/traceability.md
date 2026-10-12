# Шаардлагын мөрдөх хүснэгт

**Суурь:** шинэ W03 DOCX · **Редакцийн шалгалт:** 2026-10-13 · **Төлөв:** Draft for review

Энэ хүснэгт [SRS](srs.md)-ийн шаардлага бүрийг эх сурвалж, хариуцах үүрэг, шалгах арга, хамааралтай холбоно. `Mapped` нь архитектурын хариуцлага оноосныг, `Not verified` нь бүтээгдэхүүний acceptance test-ийн бодит нотолгоо хараахан байхгүйг илэрхийлнэ. Owner нь санал болгосон **үүрэг**; нэр бүхий багийн гишүүн хүлээн авсан гэсэн мэдэгдэл биш.

## Найман баганатай шаардлагын бүртгэл

| ID | Source | Owner | Verification | Dependency | Risk | Status | Last-Reviewed |
| --- | --- | --- | --- | --- | --- | --- | --- |
| [FR-01](srs.md#fr-01--хоолны-жагсаалт-харах) | W01 Ану; W03 Menu | Product / QA | TC-FR01; Menu fixture: 10 active / 2 inactive | Catalog API | High: буруу каталог | Mapped / Not verified | 2026-10-13 |
| FR-02 | W03 Customer journey | Product / QA | TC-FR02; нэр/ангилал/хоосон үр дүн | FR-01 | High: олдохгүй хоол | Mapped / Not verified | 2026-10-13 |
| FR-03 | W03 food details | Product / QA | TC-FR03; таван талбар | FR-01 | Medium: дутуу мэдээлэл | Mapped / Not verified | 2026-10-13 |
| FR-04 | W01 Ану; W03 cart | Backend / QA | TC-FR04; хоосон сагс → quantity=1 | FR-01 | High: буруу item | Mapped / Not verified | 2026-10-13 |
| FR-05 | W03 cart journey | Backend / QA | TC-FR05; 1/2/10/0/11 boundary | FR-04 | High: quantity/үнэ | Mapped / Not verified | 2026-10-13 |
| FR-06 | Шинэ W03 remove | Backend / QA | TC-FR06; зөвхөн сонгосон item хасагдана | FR-04 | High: өөр item устах | Mapped / Not verified | 2026-10-13 |
| FR-07 | Шинэ W03 price clarity | Backend / QA | TC-FR07; 37,000₮; зөрүү0₮ | FR-04–06 | High: санхүүгийн зөрүү | Mapped / Not verified | 2026-10-13 |
| FR-08 | W03 delivery journey | Product / QA | TC-FR08; 4 invalid + 1 valid хүсэлт | Cart / order draft | High: хүргэлт боломжгүй | Mapped / Not verified | 2026-10-13 |
| FR-09 | Шинэ W03 delivery preference | Product / QA | TC-FR09; available/unavailable | FR-08; slot service | Medium: боломжгүй slot | Mapped / Not verified | 2026-10-13 |
| FR-10 | Шинэ W03 payment | Backend / QA | TC-FR10; гурван аргаас нэг сонголт | Payment contract | High: буруу арга | Mapped / Not verified | 2026-10-13 |
| FR-11 | W01 Билэгт; W03 checkout | Backend / QA | TC-FR11; key retry → нэг order | FR-04/07/08/10; NFR-02 | High: duplicate order | Mapped / sample scope only | 2026-10-13 |
| FR-12 | W01 Номин; W03 status | Backend / QA | TC-FR12; өөрийн төлөв / бусдын order 403 эсвэл 404 | FR-11; NFR-03 | High: мэдээлэл алдах | Mapped / sample scope only | 2026-10-13 |
| FR-13 | Шинэ W03 cancellation | Product / backend | TC-FR13; Pending/Confirmed/Preparing/foreign | FR-12; NFR-03 | High: төлөвийн зөрүү | Mapped / confirmed gap | 2026-10-13 |
| FR-14 | W01 Номин; W03 history | Backend / QA | TC-FR14; А-ийн 3 / B-ийн 2 order; newest-first | FR-11/12; NFR-03 | High: өөр хүний түүх | Mapped / Not verified | 2026-10-13 |
| FR-15 | Шинэ W03 customer confidence | Frontend / QA | TC-FR15; гурван талбар / false success=0 | FR-11; ETA | High: худал success | Mapped / Not verified | 2026-10-13 |
| NFR-01 | W03; web.dev; Chrome Lighthouse | Frontend / QA | TC-NFR01; 30 mobile run, p75 ≤2.5 s | FR-01 | High: удаан Menu | Mapped / Not verified | 2026-10-13 |
| NFR-02 | W03 reliability target | Backend / QA | TC-NFR02; 100 retry, duplicate=0 | FR-11 | High: давхар захиалга | Mapped / production not verified | 2026-10-13 |
| NFR-03 | W03 privacy boundary | Backend / security | TC-NFR03; 100 эрхгүй хүсэлт, leak / change=0 | FR-12–14 | High: IDOR | Mapped / production not verified | 2026-10-13 |
| NFR-04 | W03 service target | Operations / QA | TC-NFR04; 43,200 slot, uptime ≥99.5% | FR-11 | Medium: үйлчилгээ тасрах | Mapped / Not verified | 2026-10-13 |
| NFR-05 | W03 keyboard; W3C SC 2.1.1 | Frontend / QA | TC-NFR05; бүтэн keyboard flow, controls 100% | FR-01/04/08/10/11 | High: checkout хаагдах | Mapped / Not verified | 2026-10-13 |

Test case бүрийн бүрэн өгөгдөл, үйлдэл, Pass/Fail нь [SRS](srs.md)-д байна. Evidence нэмэхдээ commit, environment, command/steps, expected/actual, date, evidence link-ийг хамт хадгална. Нэг жижиг Python модульд unit test амжилттай болсон нь энэ хүснэгтийн 20 бүтээгдэхүүний шаардлагыг батлахгүй.

## Архитектур ба хэрэгжүүлэлтийн холбоо

| ID | Төлөвлөсөн building block | W05 interface / W06 кодын хамрах хүрээ |
| --- | --- | --- |
| FR-01 | Web App, API Catalog, PostgreSQL | Menu API төлөвлөгөө; W06-д байхгүй |
| FR-02 | Web App, API Catalog, PostgreSQL | Search/filter гэрээг өргөтгөх; W06-д байхгүй |
| FR-03 | Web App, API Catalog, PostgreSQL | Detail гэрээг өргөтгөх; W06-д байхгүй |
| FR-04 | Web App, API Cart, PostgreSQL | W05 `POST /cart/items`; W06-д байхгүй |
| FR-05 | Web App, API Cart, PostgreSQL | W05 `PATCH /cart/items/{item_id}`; W06-д байхгүй |
| FR-06 | Web App, API Cart, PostgreSQL | Remove endpoint-ийг гэрээнд баталгаажуулах; W06-д байхгүй |
| FR-07 | API Pricing, Web App | Server total-ийн гэрээ; W06 create-ийн price validation нь бүтэн checkout тооцоолол биш |
| FR-08 | Web App, API Checkout, PostgreSQL | W05 checkout address; W06-д байхгүй |
| FR-09 | Web App, API Delivery slots, PostgreSQL | COULD; W05-д үлдсэн coverage gap |
| FR-10 | Web App, API Checkout, Payment Provider | W05 payment method; W06-д байхгүй |
| FR-11 | Web App, API Orders, PostgreSQL, Redis | W05 `POST /orders`; W06 create function жишээ |
| FR-12 | Web App, API Orders, PostgreSQL | W05 own order read; W06 read function жишээ |
| FR-13 | Web App, API Orders, PostgreSQL | W06 cancel function Pending-only; Confirmed coverage gap |
| FR-14 | Web App, API Orders, PostgreSQL | History list-ийг гэрээнд баталгаажуулах; single-order read нь history биш |
| FR-15 | Web App, API Orders / ETA | Confirmation UI үндсэн; notification Worker зөвхөн дэмжих блок |

**Архитектурын зураглал:** 15/15 FR = 100%, orphan=0. **Runtime coverage:** тогтоогоогүй. NFR-02 нь Redis cache-ээс гадна durable transaction/unique key хамгаалалт шаарддаг; [ADR-002](../architecture/adr/0002-persistence-and-idempotency.md). W05 coverage-ийг endpoint тоогоор бус шаардлагын шалгуур бүрээр [API баримт](../api/README.md)-д дэлгэрүүлнэ.

## Суурь баримтуудын зөрүү

| Сэдэв | Хуучин PHTBB-3 PDF | Шинэ Week_03_FoodFlow DOCX | Энэ repository-ийн шийдэл |
| --- | --- | --- | --- |
| FR-06 / FR-07 | 06 total, 07 remove | 06 remove, 07 total | Шинэ DOCX ID canonical; хуучин ID-г зөвхөн архивын citation-д хэрэглэнэ |
| FR-10 / FR-11 | 10 create order, 11 payment | 10 payment, 11 create order | W04–W06 холбоосуудыг шинэ mapping-аар хөтөлнө |
| FR-03 | Нэр/үнэ/орц/тайлбар | Харшил үүсгэгч нэмэгдсэн | Таван талбарын acceptance хадгалсан |
| FR-09 priority | SHOULD | COULD | Шинэ суурийн COULD; scope дотор хугацаа баталсан гэж үзэхгүй |
| FR-13 | Ерөнхийдөө бэлтгэж эхлээгүй; тест нь Pending | Pending/Confirmed; Preparing409 | Шинэ суурийн дүрэм хадгалсан; W06 Pending-only implementation gap-г ил болгосон |
| FR-15 | Success message + Order ID | order_id + total + estimated delivery time | Шинэ гурван талбар; email/SMS-ээр орлуулахгүй |
| NFR-01 | 1,000request,p95≤2s, response/page гэсэн холимог тайлбар | 30mobileLCP,p75≤2.5s | Хоёр өөр metric; хуучныг хангаж байгаагаар шинэг батлахгүй |
| Peer review | Гурван reviewer comment гэсэн хүснэгт | Self-audit; externalreview pending | Нэр/өдөр/commentlink нотолгоогүй peer review-г биелсэн гэж тооцохгүй |
| GPT-4 comparison | AI quote хүснэгт, runmetadata байхгүй | Сургалтын шинээр үүсгэсэн candidate | Нэр бүхий model benchmark transcript гэж мэдүүлэхгүй |
| W04 FR-15 mapping | Worker/notification-д голлон оноосон | Customer confirmation UI шаардлага | Web App + API Orders / ETA үндсэн; notification дэмжих |
| W04 Redis | Key24h, queue | NFR-02 durable duplicate prevention | PostgreSQL uniqueness, payloadhash, storedresult нэмэх санал; ADR Proposed |

Өөрчлөлт нь архивын эхийг засварлахгүй. Шинэчилсэн бүтээгдэхүүний behavior хэрэгжүүлэхийн өмнө owner нь холбогдох нээлттэй шийдвэрийг баталж, OpenAPI ба тестийг зэрэг шинэчилнэ.

## Редакцийн diff ба баталгаажуулалтын хил

| Өмнөх хэлбэр | Шинэчилсэн хэлбэр | Яагаад хэрэгтэй вэ? |
| --- | --- | --- |
| “Хурдан / амархан / зөв ажиллана” | Оролт, expected result, тоон boundary | Нэг ижил нөхцөлөөр Pass/Fail шийдэх |
| FR-02 зөвхөн Burger хайх тест | Хайлт + ангилал + нийлмэл нөхцөл | Шаардлагын хоёр үйлдлийн нэгийг орхихгүй |
| FR-05 зөвхөн 1→2 | 1,2,10 зөв; 0,11 буруу | Хязгаарын алдааг шалгах |
| FR-08 дутуу хаягтай “draft үүсэхгүй” | Дутуу хаяг хадгалагдахгүй; өмнөх cart/draft-ыг үгүйсгэхгүй | Draft-ийн lifecycle-ийн зөрүүг арилгах |
| “100 security test pass” | Response leak0 ба datastorechange0 | HTTP403/404 body-д мэдээлэл алдах эрсдэлийг хаах |
| Availability denominator тодорхойгүй | 43,200slots; missing≠success; maintenance тусдаа | Uptime хувийг сонгож өсгөхгүй |
| “15/15 implemented” гэх ойлгомжгүй хувь | 15/15 architecture mapped; runtime not verified | Баримт ба ажиллах системийн нотолгоог ялгах |

**W03 trial gate:** 20 requirement-ийн дор хаяж 16 нь бүх acceptance case-ээ бодитоор давсан үед ≥80% гэж тэмдэглэнэ. Partial, Not run, Blocked мөрийг pass-д оруулахгүй. **Одоогийн бүтээгдэхүүний gate:** Not verified; хувь зохиогоогүй. W06-ийн unit/doctest үр дүн тусдаа нотолгоо юм.
