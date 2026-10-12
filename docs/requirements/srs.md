# FoodFlow — Системийн шаардлагын тодорхойлолт

**Баримтын хувилбар:** 1.1, редакцийн шинэчлэл · **Шалгасан:** 2026-10-13 · **Төлөв:** Draft for review

FoodFlow нь хэрэглэгчид хоол сонгох, сагс бүрдүүлэх, хүргэлтийн мэдээлэл оруулах, төлбөрийн арга сонгох, захиалга үүсгэх, өөрийн захиалгын явцыг харах боломж олгоно. Энэ баримт нь системийн **хийх ёстой ажиллагаа ба хүлээн авах шалгуур** юм. Шаардлага бичигдсэн, архитектурт зураглагдсан, жишээ кодод шалгагдсан гурван төлөвийг тусад нь хөтөлнө.

Үндсэн уншигч нь API ашиглах хөгжүүлэгч, хэрэгжүүлэгч баг, QA. Уншигчдын хэрэгцээг [persona](../audience/personas.md), бүтээгдэхүүний хил ба хойшлуулсан боломжийг [Scope Charter](scope.md), архитектурын үүргийг [arc42 баримт](../architecture/index.md)-аас харна.

## Суурь хувилбар ба өөрчлөлтийн дүрэм

ID ба үндсэн утгыг хэрэглэгчийн шинэчилсэн **Week_03_FoodFlow.docx**-ийн [текст хуулбар](../../sources/README.md)-аас авсан. Хуучин [PHTBB-3.pdf-ийн текст](../../sources/README.md) нь архивын хувилбар; түүний ID-г шинэ баримтад шууд хэрэглэхгүй. Зөрүүг [мөрдөх хүснэгтийн өөрчлөлтийн бүртгэл](traceability.md#суурь-баримтуудын-зөрүү) харуулна. `1.1` нь энэ repository дахь редакцийн хувилбар бөгөөд багийн баталсан шинэ бүтээгдэхүүний release гэсэн утгагүй.

- **MUST:** эхний хувилбарын зайлшгүй хүрээ.
- **SHOULD:** чухал боловч нөөц хүрэлцэхгүй үед хойшлуулж болох боломж.
- **COULD:** дараагийн хувилбарт шилжүүлж болох боломж.

Доорх acceptance criterion нь эх баримтын утгыг тодруулсан шалгах нөхцөл. Шинэ business rule шаардсан зүйлсийг **шийдвэр хүлээгдэж буй** гэж ялгасан. Жишээ өгөгдөл нь бүтээгдэхүүний бодит каталог, үнийн санал биш. Тестүүд нь төлөвлөгөө; ажиллуулсан нотолгоогүй мөрийг `Passed` гэж тэмдэглэхгүй.

## Функциональ шаардлага — 15 FR

### FR-01 — Хоолны жагсаалт харах

**Үр дүн:** Menu нь идэвхтэй хоол бүрийн нэр, үнэ, зураг, товч тайлбарыг харуулна. **Priority:** MUST.

**Acceptance:** `active=true` хоол бүгд харагдана; идэвхгүй хоол харагдахгүй; дөрвөн мэдээлэл эх өгөгдөлтэй тохирно. Зураг харах боломжгүй үед утгатай текстэн орлуулга өгөхийг accessibility хэрэгжүүлэлтэд шалгана.

**TC-FR01 — UI inspection / integration test:** 10 active, 2 inactive хоолтой fixture бэлтгэнэ. Menu-г нээгээд API-ийн хоолны ID-г UI-тай тулгана. **Pass:** active 10/10, inactive 0/2; нэр, үнэ, зураг, тайлбарын зөрүү 0. Аль нэг шалгуур зөрчигдвөл **Fail**.

**Source:** W01 Анугийн Menu-ээс эхлэх хэрэгцээ, W03 шинэ суурь. **Dependency:** Catalog API. **Mock:** [Menu](mockups/menu.svg).

### FR-02 — Хоол хайх, ангиллаар шүүх

**Үр дүн:** Хэрэглэгч хоолны нэрийн хэсгээр хайж, ангиллаар шүүн тохирох хоолоо олно. **Priority:** MUST.

**Acceptance:** Нэрийн хайлт ба ангиллын шүүлт тус тус ажиллана; хамт хэрэглэвэл хоёр нөхцөлд нийцсэн хоол л гарна. Үр дүнгүй үед хоосон төлөвийг ойлгомжтой харуулна. Том/жижиг үсэг, кирилл тэмдэгтийн normalization-ийн дүрмийг API гэрээнд шийдвэрлэнэ.

**TC-FR02 — UI / API test:** `Burger` орсон нэртэй 2, өөр нэртэй 3 active хоол бэлтгэж, хоёр Burger-ийг өөр ангилалд байрлуулна. `Burger` гэж хайхад 2/2 тохирох, 0/3 бусад үр дүн гарна. Дараа нь нэг ангиллыг сонгоход зөвхөн тэр ангиллын Burger үлдэнэ; тохирохгүй нэрээр хайхад 0 үр дүн гарна. **Pass:** бүх case-ийн хүлээгдсэн ID багцтай яг таарна; бусад тохиолдол **Fail**.

**Source:** Customer journey, W03. **Dependency:** FR-01.

### FR-03 — Хоолны дэлгэрэнгүй мэдээлэл харах

**Үр дүн:** Сонгосон хоолны нэр, үнэ, орц, харшил үүсгэгч, тайлбарыг хэрэглэгч харна. **Priority:** SHOULD.

**Acceptance:** Таван талбар харагдаж, сонгосон хоолтой тохирно. Харшлын мэдээлэл байхгүйг “харшил үүсгэгчгүй” гэж автоматаар тайлбарлахгүй; мэдээллийн чанарын дүрэм тусдаа шийдвэр шаарддаг.

**TC-FR03 — inspection:** Таван талбарыг нь бүрэн бөглөсөн fixture-ийн дэлгэрэнгүйг нээнэ. **Pass:** 5/5 талбарын утга fixture-тэй яг таарна; өөр хоолны өгөгдөл, буруу үнэ, орхигдсон талбар байвал **Fail**.

**Source:** Customer journey, шинэ W03-ийн allergen нэмэлт. **Dependency:** FR-01.

### FR-04 — Сагсанд хоол нэмэх

**Үр дүн:** Хэрэглэгчийн сонгосон хоол хоосон сагсанд `quantity=1`-ээр нэмэгдэнэ. **Priority:** MUST.

**Acceptance:** Хоолны ID, тоо ширхэг, UI-ийн сагсны badge нэг нэмэх үйлдэлтэй тохирно. Өмнө нь байгаа хоолыг дахин нэмэхэд item нэгтгэх эсэхийг API гэрээнд тусад нь батална.

**TC-FR04 — integration test:** Хоосон сагс, ID=7 хоол бэлтгэн `Add to Cart`-ыг нэг удаа дарна. Сагсыг дахин уншина. **Pass:** яг нэг item, ID=7, quantity=1, badge=1; бусад үр дүн **Fail**.

**Source:** W01 Анугийн UI/API холбоо. **Dependency:** FR-01. **Mock:** [Cart](mockups/cart.svg).

### FR-05 — Сагсны тоо ширхэг өөрчлөх

**Үр дүн:** Хэрэглэгч item-ийн тоо ширхэгийг 1–10 хооронд өөрчлөхөд subtotal шинэчлэгдэнэ. **Priority:** MUST.

**Acceptance:** Хүчинтэй бүхэл тоо 1–10; 0, 11, сөрөг болон бутархай утга хадгалагдахгүй. Subtotal нь серверийн үнэ × quantity-тай таарна; item устгах үйлдлийг FR-06 зохицуулна.

**TC-FR05 — boundary / integration test:** 18,000₮ үнэтэй item-ийн quantity-г 1→2→10→1 болгоно. Дараа 0 ба 11 утга илгээнэ. **Pass:** зөвшөөрсөн тоонууд хадгалагдаж, 2 үед subtotal=36,000₮; хориглосон утгад алдаа гарч сүүлчийн хүчинтэй утга хэвээр үлдэнэ. Аль нэг зөрүү **Fail**.

**Source:** Customer cart journey, W03. **Dependency:** FR-04.

### FR-06 — Сагснаас хоол хасах

**Үр дүн:** Хэрэглэгчийн сонгосон item сагснаас хасагдана. **Priority:** MUST.

**Acceptance:** Зөвхөн сонгосон item хасагдаж, бусад item болон тэдгээрийн quantity өөрчлөгдөхгүй.

**TC-FR06 — integration test:** ID=7, ID=8 бүхий сагснаас ID=7-г `Remove` хийнэ; сагсыг дахин уншина. **Pass:** ID=7 нь 0 удаа, ID=8 нь 1 удаа зөв quantity-тай байна; бусад үр дүн **Fail**.

**Source:** Customer cart journey, шинэ W03 ID. **Dependency:** FR-04.

### FR-07 — Нийт үнэ тооцох

**Үр дүн:** Систем `total = subtotal + delivery_fee − discount` томьёогоор нийт үнийг төгрөгөөр тооцно. **Priority:** MUST.

**Acceptance:** Subtotal нь item-уудын нийлбэртэй, total нь дээрх томьёотой таарна. Discount-ийг хэн, хэрхэн олгох нь энэ FR-ийн хүрээнд шийдэгдээгүй; coupon engine батлагдсан гэсэн үг биш. Үнэ, хүргэлтийн төлбөрийг клиентээс ирсэн утгаар сохроор батлахгүй.

**TC-FR07 — arithmetic / integration test:** Subtotal=36,000₮, delivery_fee=3,000₮, discount=2,000₮ өгөгдөлтэй Checkout Summary нээнэ. Item-ийн quantity-г өөрчилж дахин тооцоолно. **Pass:** эхний total=37,000₮; дараагийн total нь шинэ subtotal-тай зөв; зөрүү 0₮. Аль нэг дүн зөрвөл **Fail**.

**Source:** Customer price clarity, шинэ W03. **Dependency:** FR-04–06.

### FR-08 — Хүргэлтийн хаяг хадгалах

**Үр дүн:** Хэрэглэгч дүүрэг, хороо, гудамж/байр, утас гэсэн дөрвөн заавал бөглөх мэдээллээ order draft-д хадгална. **Priority:** MUST.

**Acceptance:** Хоосон эсвэл зөвхөн зай агуулсан заавал бөглөх талбарыг хүлээн авахгүй; бүрэн мэдээлэл дараагийн алхамд хэвээр байна. Утасны улсын код, regex, хүргэлтийн бүсийг эх баримт тогтоогоогүй тул business rule болгон дур мэдэн нэмэхгүй.

**TC-FR08 — validation / integration test:** Дөрвөн талбарыг ээлжлэн хоосолж, нийт 4 хүчингүй хүсэлт илгээнэ. Дараа бүрэн fixture хадгална. **Pass:** 4/4 хүчингүй хүсэлтэд validation алдаа гарч, дутуу хаяг хадгалагдахгүй; бүрэн хүсэлтэд 4/4 утга яг хадгалагдана. Бусад үр дүн **Fail**.

**Source:** Customer delivery journey. **Dependency:** Cart / order draft; FR-11-ийн урьдчилсан нөхцөл. **Mock:** [Address](mockups/address.svg).

### FR-09 — Хүргэлтийн цагийн цонх сонгох

**Үр дүн:** Хэрэглэгч API-аас ирсэн боломжтой хүргэлтийн цагийн цонхоос нэгийг сонгож хадгална. **Priority:** COULD.

**Acceptance:** Боломжгүй цагийг сонгох, хадгалах боломжгүй. Энэ сонголт нь хүргэлтийн хугацааны баталгаа биш; FR-15-ийн estimated time-тэй ялгаатай.

**TC-FR09 — UI / API test:** 09:00–10:00 `available`, 10:00–11:00 `unavailable` slot бэлтгэнэ. Боломжгүй slot-ыг UI болон API-аар сонгохыг оролдоод, боломжтой slot-ыг хадгална. **Pass:** боломжгүй ID хадгалагдахгүй; сүүлд зөвхөн available ID хадгалагдана. Бусад үр дүн **Fail**.

**Source:** Customer delivery preference, шинэ W03. **Dependency:** FR-08; slot service.

### FR-10 — Төлбөрийн арга сонгох

**Үр дүн:** Хэрэглэгч QPay, bank card, cash on delivery гэсэн сонголтоос яг нэг аргыг order draft-д хадгална. **Priority:** MUST.

**Acceptance:** Дэмжих сонголтоос нэг утга хадгалагдана; хоосон, үл мэдэгдэх эсвэл олон утга хүлээн авахгүй. Энэ нь төлбөрийн provider бодитоор холбогдсон, мөнгө шилжсэн гэсэн баталгаа биш.

**TC-FR10 — validation / integration test:** Арга бүрийг ээлжлэн сонгож draft-аа уншина; дараа хоосон болон үл мэдэгдэх утга илгээнэ. **Pass:** зөв 3/3 утга нэг нэгээр хадгалагдаж, хүчингүй хүсэлтэд сүүлчийн зөв сонголт өөрчлөгдөхгүй; QPay сонгоход API-ийн гэрээнд заасан QPay enum буцна. Бусад үр дүн **Fail**.

**Source:** Customer checkout journey. **Dependency:** Payment integration-ийн гэрээ. **Mock:** [Payment](mockups/payment.svg).

### FR-11 — Захиалга үүсгэх

**Үр дүн:** Зөв сагс, хаяг, төлбөрийн аргатай `Place Order` үйлдэл яг нэг захиалга үүсгэж, `order_id` буцаана. **Priority:** MUST.

**Acceptance:** Ижил хэрэглэгч, ижил checkout, ижил `Idempotency-Key`-тэй давтан хүсэлт нэг order_id руу заана. Хүчингүй checkout захиалга үүсгэхгүй. Replay-ийн status/body, key-ийн хугацаа болон өөр payload-тай key-ийн зөрчлийг [ADR-002](../architecture/adr/0002-persistence-and-idempotency.md), OpenAPI гэрээнд нэг мөр шийдвэрлэнэ.

**TC-FR11 — API / persistence test:** Хүчинтэй checkout бэлтгэж, ижил key ба payload-тай хүсэлтийг дараалан хоёр удаа, дараа зэрэгцүүлэн илгээнэ. Response-ийн order_id ба datastore дахь тухайн хэрэглэгч/key-ийн count-ыг шалгана. **Pass:** эхний хүсэлт 201; давтан хүсэлтүүд ижил order_id; шинэ order-ийн тоо яг 1. Хүчингүй checkout-д count=0. Өөр тохиолдол **Fail**.

**Source:** Checkout story, W01 Билэгтийн duplicate order-ийн асуудал. **Dependency:** FR-04, FR-07, FR-08, FR-10, NFR-02. **Mock:** [Order summary](mockups/summary.svg).

### FR-12 — Өөрийн захиалгын төлөв харах

**Үр дүн:** Нэвтэрсэн хэрэглэгч өөрийн захиалгын одоогийн төлөвийг харна. **Priority:** MUST.

**Acceptance:** Төлөв нь Pending, Confirmed, Preparing, Out for delivery, Delivered, Cancelled гэсэн бүтээгдэхүүний төлөвүүдийн нэг байна. API-ийн enum нь OpenAPI-д тусдаа машинд уншигдах нэртэй байж болно. Өөр хүний захиалгын ID-аар мэдээлэл авах боломжгүй.

**TC-FR12 — ownership / integration test:** А-ийн захиалга Preparing, B-ийн захиалга Confirmed байхаар бэлтгэнэ. А хэрэглэгч өөрийн болон B-ийн ID-г уншина. **Pass:** өөрийн response нь хадгалсан Preparing төлөвтэй; B-ийн хүсэлт 403 эсвэл 404, захиалгын өгөгдөл 0. Хоёрын аль нэг зөрвөл **Fail**.

**Source:** Customer status journey, W01 Номины тайлбарлах хэрэгцээ. **Dependency:** FR-11, NFR-03. **Mock:** [Order status](mockups/status.svg).

### FR-13 — Захиалга цуцлах

**Үр дүн:** Хэрэглэгч зөвхөн өөрийн Pending эсвэл Confirmed төлөвтэй захиалгыг цуцалж, Cancelled болгоно. **Priority:** SHOULD.

**Acceptance:** Preparing болон түүнээс хойших төлөвтэй захиалгыг цуцлахад 409 буцаж, төлөв өөрчлөгдөхгүй. Өөр хүний захиалгыг цуцлах боломжгүй. Төлбөр буцаах процесс энэ FR-д батлагдаагүй.

**TC-FR13 — state / ownership test:** Өөрийн Pending, Confirmed, Preparing захиалга болон B-ийн Pending захиалга бэлтгэн цуцлах хүсэлт илгээнэ. **Pass:** эхний 2 нь Cancelled; Preparing нь 409 ба хэвээр; B-ийнх 403/404 ба хэвээр. Бусад үр дүн **Fail**.

**Source:** Шинэ W03-ийн тодорхой Pending/Confirmed дүрэм. **Dependency:** FR-12, NFR-03. **Зөрүү:** W06 жишээ модуль Pending-only. Иймээс жишээ тестийн амжилтыг FR-13 бүрэн хэрэгжсэн гэж тооцохгүй. Confirmed цуцлалтын хэрэгжүүлэлт ба төлбөрийн нөлөөг бүтээгдэхүүний эзэн батлах шаардлагатай.

### FR-14 — Өөрийн захиалгын түүх харах

**Үр дүн:** Хэрэглэгч зөвхөн өөрийн захиалгуудыг хамгийн сүүлийн огнооноос эхлэн харна. **Priority:** SHOULD.

**Acceptance:** Өөр хүний захиалга жагсаалтад орохгүй; мөр бүр огноо, нийт үнэ, одоогийн төлөвтэй байна. Хуудаслалт, ижил огнооны tie-break дүрэм нь API гэрээний нээлттэй шийдвэр.

**TC-FR14 — API / UI test:** А-д өөр өөр огноотой 3, B-д 2 order бэлтгэнэ. А `My Orders`-ыг нээнэ. **Pass:** А-ийн 3/3 order newest-first, B-ийн 0/2; огноо/total/status нь fixture-тэй таарна. Бусад үр дүн **Fail**.

**Source:** Customer history journey, W01 Номины order query хэрэгцээ. **Dependency:** FR-11, FR-12, NFR-03. **Mock:** [Order history](mockups/history.svg).

### FR-15 — Амжилттай захиалгын баталгаа харах

**Үр дүн:** Захиалга амжилттай үүсэхэд хэрэглэгч `order_id`, нийт үнэ, хүргэлтийн тооцоолсон хугацааг харна. **Priority:** MUST.

**Acceptance:** Амжилтын дэлгэц бодит үүссэн захиалгатай тохирно; алдаатай хүсэлтэд амжилтын дэлгэц харуулахгүй. ETA нь тооцоолол бөгөөд баталгаат хүргэлтийн амлалт биш. Email/SMS notification нь энэ FR-ийн орлуулга биш.

**TC-FR15 — integration / UI test:** Хүчинтэй болон хүчингүй checkout-оор тус бүр хүсэлт илгээнэ. **Pass:** амжилтад 3/3 талбар захиалгатай тохирч харагдана; алдаанд success screen=0, ойлгомжтой алдаа гарна. Бусад үр дүн **Fail**.

**Source:** Customer confidence, шинэ W03. **Dependency:** FR-11; ETA эх үүсвэрийг хэрэгжүүлэлтэд шийдвэрлэнэ. **Mock:** [Order summary / confirmation](mockups/summary.svg).

## Чанарын шаардлага — 5 NFR

Эндэх 100 туршилт, 30 run, 99.5% нь шалгалтын хэмжээ эсвэл төслийн зорилт. Гадаад стандарт бүх тоог тогтоосон гэж тайлбарлахгүй. Таван NFR нь Performance, Reliability, Security, Availability, Accessibility гэсэн таван ангилалд хамаарна.

### NFR-01 — Performance

**Шаардлага:** Menu-ийн mobile lab LCP нь ижил нөхцөлтэй 30 run-ийн p75 дээр ≤2.5 секунд байна. **Priority:** MUST. **Холбоо:** FR-01.

**TC-NFR01:** Browser, Lighthouse version, төхөөрөмжийн profile, viewport, CPU/network throttling, URL, commit, fixture, cache-ийн горимыг хадгална. Ижил profile, cold-cache-тай 30 амжилттай navigation ажиллуулж raw LCP-ийг JSON/CSV-д бүртгэнэ. Өсөх дарааллаар эрэмбэлсэн 30 утгын nearest-rank p75 нь `ceil(0.75×30)=23` дахь утга. **Pass:** 30/30 хүчинтэй run ба 23 дахь LCP ≤2,500 ms. Crash/missing run-ийг хасаж амжилт мэт тооцохгүй; дахин ажиллуулах шалтгааныг бүртгэнэ. Нөхцөл, raw data дутуу бол **Not verified**.

**Үндэслэл:** 2.5 s ба p75 зорилгыг [web.dev-ийн LCP тайлбар](https://web.dev/articles/lcp) дэмждэг; [Chrome Lighthouse-ийн mobile босго](https://developer.chrome.com/docs/lighthouse/performance/lighthouse-largest-contentful-paint) мөн 0–2.5 s-ийг сайн ангилалд оруулдаг. Эдгээр нь хоёр албан баримт боловч нэг Google/Chrome эх үүсвэрийн хүрээнд байна. 30 удаагийн lab aggregation нь FoodFlow-ийн шалгалтын сонголт; бодит хэрэглэгчдийн field p75-г хэмжсэн нотолгоо биш. Хуучин PDF-ийн API response p95≤2 s хэмжүүртэй сольж хольж болохгүй.

### NFR-02 — Reliability

**Шаардлага:** Ижил checkout, хэрэглэгч, `Idempotency-Key`-тэй 100 давтан хүсэлтэд duplicate order=0 байна. **Priority:** MUST. **Холбоо:** FR-11.

**TC-NFR02:** Тусгаарласан datastore-д нэг хүчинтэй checkout ба key бэлтгэнэ. Дараалсан retry, зэрэгцээ хүсэлт, response тасарсны дараах retry гэсэн нөхцөлүүдийг хамруулан нийт 100 хүсэлт илгээнэ. Хүсэлт бүрийн timestamp, key, response/order_id, datastore count-ыг бүртгэнэ. **Pass:** хүсэлтүүд нэг order_id-д холбогдож, durable order count=1; давхар үүсэлт 0. Timeout-д order_id ирээгүй бол серверийн үр дүнг datastore-аар шалгана. Restart болон cache loss-ийн баталгааг нэмэлт resilience test-гүйгээр дүгнэхгүй.

**Үндэслэл:** Давхар захиалгаас сэргийлэх нь FoodFlow-ийн өөрийн зорилт. [Stripe-ийн idempotent request тайлбар](https://docs.stripe.com/api/idempotent_requests) нь key, параметр, давтан үр дүнгийн гэрээг тодорхой бичих сайн жишээ; FoodFlow Stripe ашигладаг гэсэн үг биш. 100 хүсэлт ба 24 цагийн санал нь бүх API-д мөрдөх стандарт биш.

### NFR-03 — Security

**Шаардлага:** А хэрэглэгч B-ийн захиалгыг унших, өөрчлөх оролдлогын 100 хүсэлтэд мэдээлэл алдах, зөвшөөрөлгүй өөрчлөх тохиолдол 0 байна. **Priority:** MUST. **Холбоо:** FR-12–14.

**TC-NFR03:** Хоёр хэрэглэгчийн ялгаатай order үүсгэж, А-ийн identity-гаар B-ийн ID-г ашигласан унших, жагсаалтаас хайх, цуцлах хүсэлтүүдийг нийлүүлэн 100 удаа илгээнэ. Response ба datastore before/after snapshot-ыг шалгана. **Pass:** бүгд 403/404 эсвэл жагсаалтаас бүрэн хасагдсан; B-ийн order-ийн утга response-д 0, өөрчлөлт 0. Auth token, утас, хаягийг evidence log-д бүтнээр нь нийтлэхгүй. HTTP код зөв байсан ч body-д өгөгдөл алдвал **Fail**.

**Үндэслэл:** W03-ийн хэрэглэгчийн нууцлалын хил. Нэвтрэлт байгаа нь object-level authorization зөв гэсэн баталгаа биш. Жишээ модульд `user_id` параметрээр ownership шалгах нь production Bearer auth-ийг батлахгүй.

### NFR-04 — Availability

**Шаардлага:** Core ordering API-ийн 30 хоногийн хэмжсэн uptime ≥99.5% байна. **Priority:** SHOULD. **Холбоо:** FR-11.

**TC-NFR04:** Тусгаарласан synthetic tenant-тай core ordering dependency-г хамарсан probe-ийг минут тутам ажиллуулна; зөвхөн process амьд байгааг шалгасан `/health` нь захиалга үүсэх боломжийн нотолгоо болохгүй. Probe-ийн URL/үйлдэл, timeout, зөв хариуны шалгуурыг эхлэхээс өмнө review хийнэ. 30 хоногт төлөвлөсөн 43,200 slot байна. `uptime = successful_slots / scheduled_slots × 100`. Missing probe-ийг амжилт гэж тооцохгүй. Maintenance-ийг нийт дүнд оруулж, тусдаа задалж тайлагнана. **Pass:** ≥99.5%; нэг минутын slot-ийн загварт амжилтгүй ≤216 slot буюу 3 цаг 36 минут. Хэмжилтийн 30 хоногийн нотолгоогүй бол **Not verified**.

**Үндэслэл:** FoodFlow-ийн үйлчилгээний зорилт; provider contract эсвэл ISO-ийн заавал мөрдөх хувь биш. Нэгж тестээр сарын uptime-ийг батлахгүй.

### NFR-05 — Accessibility

**Шаардлага:** Menu → Cart → Checkout → Payment → Place Order урсгалын зайлшгүй controls-ийн 100%-ийг keyboard-аар focus хийж, ажиллуулж болно. **Priority:** MUST. **Холбоо:** FR-01, FR-04, FR-08, FR-10, FR-11.

**TC-NFR05:** Mouse ашиглахгүйгээр Tab/Shift+Tab, Enter/Space, шаардлагатай arrow key-ээр хоол сонгож, сагсанд нэмж, quantity өөрчилж, хаяг бөглөж, төлбөрийн арга сонгон, захиалга үүсгэнэ. Controls-ийн checklist ба focus дарааллыг хадгалж, validation алдаанаас буцаж засахыг хамруулна. **Pass:** чухал controls 100% ажиллана; focus харагдана, keyboard trap=0; амжилтын баталгаа хүртэл mouse шаардлагагүй. Automated checker-ийн pass нь manual урсгалыг орлохгүй.

**Үндэслэл:** [W3C WCAG 2.2-ийн Keyboard (SC 2.1.1) тайлбар](https://www.w3.org/WAI/WCAG22/Understanding/keyboard.html) нь keyboard equivalent-ийн зарчмыг тайлбарлана. Энэ ганц NFR-ийн шалгалт нь бүтэн WCAG conformance audit биш.

## Гадаад интерфейс ба өгөгдлийн хил

UI нь Menu, Cart, Address, Payment, Order Summary, Status, History дэлгэцтэй. Бүтээгдэхүүний API нь HTTPS/JSON, `/api/v1` versioned зам, хамгаалалттай хүсэлтэд Bearer token ашиглахаар төлөвлөсөн. OpenAPI гэрээг [API баримт](../api/README.md)-аас харна. W06 Python-ийн **public API** гэдэг нь импортлон дуудах функцийн интерфейс; энэ нь **public HTTP API** ажиллаж байна гэсэн утгагүй.

Алдааны үндсэн JSON нь `code`, `message`, шаардлагатай үед `field` агуулна. 401 нь нэвтрэлт, 403 нь хандах эрх, 404 нь байхгүй эсвэл нууцлах resource, 409 нь төлөв/гэрээний зөрчлийг ялгана. 403/404-ийн privacy сонголт ба validation 400/422-ийн дүрмийг endpoint бүрд OpenAPI-д нэг мөр тогтооно.

FoodFlow нь raw card number хадгалахгүй. Payment/Notification Provider-ийн бодит URL, credentials, webhook schema, retry ба timeout, refund нь батлагдаагүй. Restaurant staff/courier нь төлөвийн эх үүсвэр боловч тэдгээрийн бүрэн portal энэ Customer SRS-ийн батлагдсан 15 FR-д нэмэгдээгүй.

## Шийдвэр хүлээгдэж буй асуудлууд

| ID | Асуудал | Яагаад шийдвэр хэрэгтэй вэ? | Хариуцах үүрэг |
| --- | --- | --- | --- |
| REQ-OPEN-01 | FR-13 Confirmed цуцлалт ба Pending-only жишээ | Business rule, API, кодын хамрах хүрээ зөрж байна | Product / backend |
| REQ-OPEN-02 | Idempotency key-ийн TTL, scope, payload conflict, replay | NFR-02-г найдвартай батлахын өмнөх гэрээ | Backend / QA |
| REQ-OPEN-03 | Хаяг/утасны validation, delivery zones | Бүрэн талбар нь бодит хүргэлт боломжтой гэсэн үг биш | Product / operations |
| REQ-OPEN-04 | ETA эх үүсвэр ба payment success холбоо | FR-15 амжилтын мэдээллийг зөв гаргах | Product / backend |
| REQ-OPEN-05 | Provider webhook, signature, timeout, refund | Баталгаажаагүй төлбөрийг success болгохгүй | Backend / security |

Санал хүлээн авахад эхлээд шаардлагын ID ба version-ийг тэмдэглэж, өөрчлөлтийн нөлөөг Scope → SRS → Architecture/ADR → OpenAPI → код/тест → баримт дарааллаар шалгана. Хуучин ID-г дахин өөр утгаар ашиглахгүй; retired шаардлагыг шинэ ID-ийн холбоостой хадгална.

## Эх сурвалж

Хэрэглэгчийн шинэ W03 DOCX, хуучин PHTBB-3 PDF, [Week 03 handout](../../sources/README.md), [Week 01 persona](../../sources/README.md), [Week 02 Scope Charter](../../sources/README.md). Номын chapter/page заалтыг handout болон хэрэглэгчийн материалаас авсан; номын бүтэн эхийг уншиж баталсан гэж мэдүүлээгүй. Гадаад албан эх сурвалжуудыг 2026-10-13-нд шалгасан.
