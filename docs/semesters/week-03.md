# Семинар 03 — SRS ба шаардлагын баталгаажуулалт

**Төсөл:** FoodFlow · **Deliverable:** SRS 1.1 editorial revision · **Шалгасан:** 2026-10-13

Энэ семинарын зорилго нь FoodFlow-ийн хийх ёстой ажиллагааг хэрэглэгчид харагдах үр дүнгээр тодорхойлж, шаардлага бүрийг шалгаж болох нөхцөлтэй болгох юм. 15 functional requirement (FR), таван measurable non-functional requirement (NFR)-ийг нэг суурь ID-гаар хөтөлж, AI-ийн бүдэг тайлбар, эх баримтын зөрүү, гаднын баталгаажуулалт дутуу хэсгийг ялгав.

**Гол материал:** [SRS](../requirements/srs.md) · [Traceability](../requirements/traceability.md) · [Acceptance mock UI](../requirements/mockups/index.md) · [Архитектур](../architecture/index.md)

## Даалгавар ба шинэчилсэн үр дүн

| Handout story | Шаардлага | Шинэчилсэн материал / төлөв |
| --- | --- | --- |
| US-3.1 | 15 FR, тус бүр test procedure, priority; ≥5 mock UI | SRS 15/15 FR; TC-FR01–15; 7 editable SVG mockup |
| US-3.2 | 5 measurable NFR, ≥3 category, boundary + method | 5 NFR / 5 category; raw evidence, denominator, Pass/Fail тодорхой |
| US-3.3 | GPT-4 candidate-тай ≥3 ялгаа, quote + correction, wiki artifact | Гурван сургалтын AI comparison бэлэн; шаардсан GPT-4 run metadata / transcript pending |
| US-3.4 | Peer review; ≥3 comment; v0.9 → v1.0 diff | Self-audit-ийн 3 мөр ба archive diff бэлэн; бодит peer review pending |
| UE-3 | Corg.ly 5 FR, AI 3 error, нэг нүүрийн reflection | Энэ тайлангийн тусдаа UE-3 хэсэг |

ID-ийн суурь нь шинэ `Week_03_FoodFlow.docx`. Хуучин `PHTBB-3.pdf`-ийн FR-06/07, FR-10/11 солигдсон; NFR-01 metric өөрчлөгдсөн. Зөрүүг [canonical mapping](../requirements/traceability.md#суурь-баримтуудын-зөрүү)-д хадгалсан. Архивын эхийг өөрчлөөгүй.

## Шаардлагын чанарт хийсэн засвар

Шаардлага бүр “систем юу хийх вэ?” гэсэн гол үр дүнгээр эхэлнэ. Test procedure нь өгөгдөл → үйлдэл → expected result → Pass/Fail гэсэн дараалалтай. “Хурдан”, “амархан”, “зөв” гэх хэмжүүргүй үнэлгээг дангаар acceptance болгон ашиглаагүй.

| Олдсон цоорхой | Засвар | Нөлөө |
| --- | --- | --- |
| FR-02 нь хайлт, ангилал гэсэн хоёр үйлдэлтэй ч тест зөвхөн хайлттай | Хайлт/шүүлт/хамтарсан нөхцөл/үр дүнгүй case | Шаардлагын нэг хэсгийг шалгалтаас алдахгүй |
| FR-05 quantity 1–10 боловч тест зөвхөн 1→2 | 1 / 2 / 10 valid; 0 / 11 invalid | Boundary ил тод |
| FR-08 нь cart draft ба хаяг хадгалалтыг хольсон | Дутуу хаяг хадгалагдахгүй, өмнөх draft-ыг үгүйсгэхгүй | Checkout lifecycle логик зөрөхгүй |
| FR-13 шинэ суурь нь Confirmed зөвшөөрөх, W06 нь Pending-only | SRS хадгалж, implementation gap бүртгэсэн | Кодыг хараад business rule-г чимээгүй өөрчлөхгүй |
| NFR-01 API response p95 ба UI LCP p75 холилдсон | Mobile 30 run, p75 LCP ≤2.5 s-г тодорхойлсон | Өөр metric-ийн pass-аар нотлохгүй |
| NFR-04 uptime denominator тодорхойгүй | 43,200 scheduled slots; missing ≠ success; maintenance тусдаа | Хэмжилт нөхөн сэргээж шалгаж болно |

NFR-01-ийн 2.5 секундийг [web.dev](https://web.dev/articles/lcp), [Chrome Lighthouse](https://developer.chrome.com/docs/lighthouse/performance/lighthouse-largest-contentful-paint) гэсэн хоёр албан баримтаар тайлбарласан. Энэ нь нэг Google/Chrome эх үүсвэрийн хоёр материал; бие даасан хоёр судалгаа гэж нэрлээгүй. 30 run-ийн lab p75 нь бодит хэрэглэгчдийн field p75 гэсэн үг биш. Akamai-ийн ерөнхий хурдны судалгааг 2.5 секунд тогтоосон эх сурвалж болгон ашиглаагүй.

## Use → Verify → Cite — AI-ийн гурван алдаа

Доорх candidate нь эх шинэ W03 материалд сургалтын зориулалтаар AI-аар үүсгэсэн жишээ гэж тэмдэглэгдсэн. Тусдаа GPT-4/Claude session-ийн transcript, model version, timestamp ирээгүй тул нэр бүхий model benchmark гэж мэдүүлээгүй.

| AI candidate | Verify — ямар асуудалтай вэ? | Зассан шаардлага | Cite — шалгах суурь |
| --- | --- | --- | --- |
| “Menu хурдан нээгдэнэ.” | Metric, device, percentile, boundary алга | NFR-01: mobile 30 run, p75 LCP ≤2.5 s | SRS; web.dev LCP; Lighthouse mobile threshold |
| “Хэрэглэгч амархан захиална.” | Оролт / үр дүн ба duplicate нөхцөл алга | FR-11: valid checkout, ижил key → нэг order_id | W02 Scope Charter; W01 Билэгт; TC-FR11 |
| “Хүн бүх захиалгаа харна.” | Ownership-ийн хил бүдэг | FR-12/14, NFR-03: өөрийн order; 100 foreign request → leak / change=0 | W01 Номин; W03 privacy boundary; TC-NFR03 |

**Use:** Candidate-ийг бүтэц/ноорог гаргахад хэрэглэнэ. **Verify:** Үг бүрийг scope, SRS, schema, код, тесттэй тулгана; хэмжих арга ба нээлттэй шийдвэрийг тодруулна. **Cite:** Зөвхөн тухайн мэдэгдлийг дэмждэг эх сурвалж, version, evidence-ийг холбоно. AI-ийн итгэлтэй өгүүлбэр нь баталгаажуулалтын орлуулга биш.

## v0.9 → v1.0-ийн редакцийн diff ба peer review

| Self-audit comment | Өмнөх ноорог | Засварласан үр дүн | Evidence |
| --- | --- | --- | --- |
| Нийт үнэ тодорхойгүй | FR-07 “зөв үнэ” | Subtotal + fee − discount; зөрүү 0₮ | TC-FR07 |
| Давтан хүсэлтийн үр дүн тодорхойгүй | FR-11 “order үүсгэнэ” | Ижил key + payload → нэг order; DB count=1 | TC-FR11; NFR-02 |
| Өөр хэрэглэгчийн хил алга | FR-12 “төлөв харах” | Өөрийн order; foreign 403/404; data=0 | TC-FR12; NFR-03 |

Энэ нь өөрийн редакцийн шалгалт. Хуучин PDF-д “reviewer comment” гэсэн хүснэгт байсан ч reviewer нэр, өдөр, comment link нотлогдоогүй. Шинэ DOCX үүнийг self-audit гэж зөв ялгасан тул бодит peer team-ийн ≥3 comment биелсэн гэж тооцоогүй.

Бодит review хийхэд доорх мөрийг санал бүрээр бөглөнө. Саналыг rejected болгох нь боломжтой; яагаад гэдгийг заавал тайлбарлана.

| Review ID | Reviewer / date | Confluence эсвэл PR comment | Requirement | Decision / rationale | Commit / verification |
| --- | --- | --- | --- | --- | --- |
| PR-W03-01 | Pending | Pending | Pending | Pending | Pending |
| PR-W03-02 | Pending | Pending | Pending | Pending | Pending |
| PR-W03-03 | Pending | Pending | Pending | Pending | Pending |

GitHub review нь энэ repository-ийн ирээдүйн ажлын үндсэн урсгал; handout Confluence comment шаардсан бол course workspace-д тэр холбоосыг тусад нь бүртгэнэ. GitHub дээр баримт байгаа нь LMS/course milestone автоматаар биелсэн гэсэн үг биш.

## UE-3 — Corg.ly Pet Translation API

Corg.ly бол handout-ийн тусдаа зохиомол нөхцөл. Доорх endpoint, language policy, error code, retry нь **Charlotte-ийн launch-д зориулсан proposal**; бодит үйлчилгээний батлагдсан гэрээ биш. FoodFlow SRS-ийн 20 шаардлагад нэмэхгүй.

### Таван FR — хамгийн чухал мэдээлэл эхэнд

| ID | Үр дүнгээр эхэлсэн шаардлага | Test procedure / Pass-Fail |
| --- | --- | --- |
| C-FR-01 | Developer хүчинтэй API key-ээр translate үйлдэл ашиглаж чадна | Ижил valid body-той POST `/v1/translate`: зөв Bearer key →200, key-гүй →401; бусад үр дүн Fail |
| C-FR-02 | Valid text, sourceLanguage, targetLanguage-ийн хариунд орчуулсан текст харагдана | 3 required field-тэй JSON →200 + nonempty `translation`; empty text →400; invalid body-д success=0 |
| C-FR-03 | Дэмжигдээгүй хэлд developer ойлгомжтой error code авна | Approved language fixture-д байхгүй `xx` →422 + `unsupported_language`; translation=0; өөр үр дүн Fail |
| C-FR-04 | Түр алдааны дараа хүсэлтийг хязгаартай retry хийж болно | Stub 503→200; policy-ийн дээд 3 attempt; 401 / validation 4xx-д retry=0; хязгаар давбал Fail |
| C-FR-05 | Rate limit хүрсэн үед developer дахин оролдох хугацааг мэднэ | Stub 429 → valid numeric `Retry-After`; client заасан хугацаанаас өмнө retry хийхгүй; field-гүй / эрт retry бол Fail |

Key авах арга, дэмжих хэлний жагсаалт, error status, timeout, retry attempt-ийн утгыг API эзэн батлах ёстой. “Нийт 3 attempt” ба “эхнийхээс хойш 3 retry” нь өөр утгатай тул гэрээнд нэгийг сонгоно.

### AI хувилбарын гурван алдаа ба засвар

| AI candidate — сургалтын жишээ | Concise / Usable зөрчил | Засвар |
| --- | --- | --- |
| “The service provides a seamless and highly reliable authentication experience.” | Үр дүн ба failure behavior алга; хэмжүүргүй магтаал | C-FR-01: valid key →200, key-гүй →401 |
| “The API translates any pet message into every language.” | “Any/every” нь батлагдаагүй хүрээ; хэт амлалт | C-FR-03: approved language; unsupported →422 |
| “Retry all errors until it works.” | Auth / validation алдааг дэмий давтана; хязгааргүй хүлээлт | C-FR-04: transient 503; max 3 attempt; 4xx retry=0 |

Эдгээр нь эх материалын сургалтын AI өгүүлбэрүүд. Тусдаа GPT-4/Claude run-ийн date/model/prompt/output metadata pending хэвээр; handout-ийн model-specific evidence-ийг нөхөөгүй.

### Нэг нүүрт багтаах эргэцүүлэл

Charlotte-ийн хамгийн эхний ажил нь API-г “найдвартай, хэрэглэхэд амар” гэж тодорхойлох биш, хөгжүүлэгч эхний хүсэлтээ явуулж үр дүн харахад хэрэгтэй мэдээллийг эрэмбэлэх юм. Key хаанаас авах, ямар header хэрэглэх, JSON-ийн required талбарууд юу болох, success/error response ямар хэлбэртэйг нэг дарааллаар өгвөл уншигч өөрийн апптай холбох алхмаа ойлгоно. Bhatti-ийн гол мэдээллээ эхэнд бичих зарчим (Ch. 3, p. 58; handout-ийн заалт) нь requirement-ийг урт шалгалтын тайлбараар эхлүүлэхийн оронд харагдах үр дүнгээр эхлүүлэхэд тусална.

Гэвч тодорхой өгүүлбэр болгон үнэн байдаггүй. “Бүх хэл рүү орчуулна” гэсэн candidate нь уншихад амар ч бүтээгдэхүүний хүрээг хэтрүүлсэн байж болно. “503 үед ихдээ гурван удаа оролдоно” гэдэг нь шалгаж болохуйц болсон боловч API баг батлаагүй бол proposal хэвээр. Иймээс concise зарчмыг зөвхөн үгийн тоо цөөлөхөөр ойлгож болохгүй. Auth, unsupported language, rate limit, transient error зэрэг уншигчийн дараагийн үйлдэлд нөлөөлөх нөхцөлийг хасвал богино текст ашиггүй болно. Usable баримт нь тухайн алдаанд яг юу хийхийг хэлэх ёстой.

Use–Verify–Cite урсгал энэ ялгааг ил болгодог. AI-г ноорог боловсруулахад ашиглаж, дараа нь амлалт бүрийг API schema, эзний тайлбар, ажиллуулах боломжтой тесттэй тулгана. Эх сурвалж нь өөр зүйл дэмждэг бол тухайн өгүүлбэрийн citation болгож ашиглахгүй. Ялангуяа retry-ийн policy, дэмжих хэл, 429-ийн header-ийг үйлчилгээний батлагдсан гэрээнээс авах шаардлагатай. Metadata-гүй харьцуулалтыг GPT-4-ийн бодит benchmark гэж нэрлэхгүй байх нь энэ шалгалтын нэг хэсэг.

Charlotte нь engineering-ийн тайлбарыг зөвхөн дахин найруулах үүрэгтэй хүн биш. Product-ийн амлалт, support-ийн түгээмэл асуулт, DevRel-ийн эхний ажиллах жишээ, хөгжүүлэгчийн бодит алдааг нэг гэрээнд холбоно. Баримт дутуу үед мэддэг мэт бичихээс илүү шийдвэр хүлээгдэж буй асуулт, хариуцах үүрэг, батлах нотолгоог жагсаах нь launch-д хэрэгтэй. Дараагийн төсөлд ч requirement, interface, test, evidence-ийг холбоотой хөтөлж, уншигчийн эхний амжилтаар баримтын хэрэгцээг үнэлэх нь зохистой.

## Definition of Done — баримт ба нотолгоо

| Шалгуур | Төлөв | Үлдсэн ажил |
| --- | --- | --- |
| SRS 15 FR + 5 NFR, priority / test, ≥5 mock UI | Баримт бэлэн | Бүтээгдэхүүний owner review |
| 5 NFR ≥3 category, measurable boundary | Баримт бэлэн | Raw runtime measurement |
| GPT-4 candidate-тай ≥3 ялгаа | Named-model evidence pending | US-3.3-т шаардсан GPT-4 run metadata / transcript, prompt, output, correction |
| Peer team ≥3 comment | Pending | Reviewer, date, comment link, resolution |
| Trial test ≥80% | Not verified | 20 requirement-ээс ≥16 нь бүх case-ээ Passed болсны evidence |
| M3 milestone / course workspace | External verification | LMS / instructor-ийн бодит үнэлгээ |

Unit test эсвэл docstring-ийн doctest нь бүтээгдэхүүний бүх SRS acceptance-ийн pass хувь биш. Үлдсэн ажлыг биелсэн мэт тэмдэглээгүй.

## Эргэцүүллийн гурван асуултад өгөх хариу

1. **Bhatti-ийн сорьсон ойлголт:** Ch.3p.58-ын гол мэдээллээ эхэнд бичих зарчим. “Шалгахдаа...” гэж эхлэхийн оронд “Хэрэглэгч зөвхөн өөрийн захиалгыг харна” гэж үр дүнг эхэлж хэлэх нь contract-ийг ойлгомжтой болгоно.
2. **Chinchilla-аас цааш хэрэглэх зүйл:** Ch.9pp.119–131-ийн generative documentation-ийг хүний шалгалттай хэрэглэх зарчим. Page заалт handout-аас; AI draft-ийн эх үүсвэр, өөрчлөлт, нотолгоог хадгална.
3. **Ном ба практикийн гол зөрүү:** Бодит peer review ба trial measurement нь хүн, хугацаа, ажиллах environment шаарддаг. Баримтын completeness-ээр энэ нотолгоог орлуулахгүй; pending gate-ийг ил үлдээнэ.

Эх материал: [Week 03 handout](../../sources/README.md), [шинэ W03](../../sources/README.md), [хуучин PHTBB-3](../../sources/README.md). Номын хуудасны заалтыг эдгээр материалаас авсан.
