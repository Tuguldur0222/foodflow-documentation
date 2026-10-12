# Семинар 05 · OpenAPI 3.0 ба кодын жишээ

| Баримт бичгийн мэдээлэл | Утга |
| --- | --- |
| Төсөл | FoodFlow — хоол захиалгын систем |
| Зохиогч | Ю. Төгөлдөр · 23B1NUM2350 |
| Шинэчилсэн огноо | 2026-10-13 |
| Үндсэн уншигч | API ашиглах хөгжүүлэгч, баримтжуулалт хянах багш |
| Суурь эх | Хавсаргасан W05 handout; `PHTBB5 (1).pdf`, `PHTBB5.yaml`; W03 SRS |
| Хэрэгжүүлэлтийн хүрээ | Таван FoodFlow write endpoint, найман кодын жишээ, локал mock, хоёр HTML харагдац |

## Зорилго ба хамрах хүрээ

Энэхүү семинарын зорилго нь FoodFlow-ийн API гэрээг OpenAPI 3.0.3 стандартаар
машинаар унших хэлбэрт оруулах, хүсэлт ба хариуг ажилладаг жишээгээр тайлбарлах,
кодын жишээний чанарыг Bhatti-ийн таван зарчмаар үнэлэхэд оршино. API гэрээг
Swagger UI болон Redoc гэсэн хоёр харагдацаар уншиж, хөгжүүлэгчийн туршилт ба
лавлах баримтжуулалтын хэрэгцээнд аль нь тохирохыг тодорхойлов.

FoodFlow-ийн таван endpoint нь сагсанд хоол нэмэх, тоо өөрчлөх, хүргэлтийн хаяг
хадгалах, төлбөрийн арга сонгох, захиалга үүсгэх үйлдлийг хамарна. UE-5 заавал
гүйцэтгэх даалгаврын Corg.ly гурван жишээг тусад нь бэлтгэв. Corg.ly-ийн зураг,
дуу, webhook нь FoodFlow бүтээгдэхүүнд нэмсэн боломж биш.

Локал mock нь API гэрээ болон кодын жишээг давтагдах нөхцөлд шалгах сургалтын
хэрэгсэл. Бодит хэрэглэгчийн нэвтрэлт, JWT гарын үсэг, төлбөр, хүргэлт, өгөгдлийн
сангийн найдвартай хадгалалт эсвэл нийтийн API үйлчилгээний баталгаа биш.

## 1. Эх хувилбарыг хянаж хийсэн сайжруулалт

Шинэчилсэн `PHTBB5 (1).pdf` болон хэрэглэгчийн өгсөн YAML-ийг үндсэн эхээр авч,
хуучин `PHTBB5.pdf`-ийг хувилбарын түүх гэж үзэв. Хавсаргасан баримт дахь
сургалтын зааврыг хэрэгжүүлэх шалгуур болгон ашигласан; жишээ production URL,
гүйцэтгэсэн гэж бичсэн шалгалтыг энэ repo-ийн баталгаажсан төлөвтэй адилтгаагүй.

| Хяналтаар илэрсэн зүйл | Шинэчилсэн шийдэл |
| --- | --- |
| API гэрээ, жишээ, серверийн зан төлөвийг хамтад нь дахин шалгах хэрэгцээ | Нэг canonical YAML, ажилладаг mock, response example-тай тулгах автомат тест нэмэв. |
| Idempotency header 24 цаг гэж заасан ч бодит хугацааны нотолгоо шаардана | Хэрэглэгчээр тусгаарласан 24 цагийн кэш; хугацааны зааг болон 100 зэрэгцээ retry-г тестээр шалгана. |
| Schema-д талбарын нэр байсан ч зарим утгын хязгаар тодорхойгүй | Хаягийн урт, хороо, тоо хэмжээ, найман цифртэй утас, үл мэдэгдэх талбарын бодлогыг тодруулав. |
| Demo bearer token-ийг JWT гэж эндүүрэх боломж | JWT хэрэгжүүлээгүйг тодорхой бичиж, ил тод хоёр хэрэглэгчийн fixture-ээр өмчлөл шалгав. |
| Mock хариуг production баталгаа гэж унших боломж | Локал шалгалт, нийтийн HTML, бодит sandbox болон production баталгааг ялгав. |
| Corg.ly зураг, дууны гарал тодорхой байх шаардлага | Шатрын хээтэй JPEG, синус WAV үүсгэж, синтетик гарал ба хязгаарыг файл бүрд тайлбарлав. |
| Хоёр renderer-ийн давхардсан YAML хувилбар зөрөх эрсдэл | Swagger UI, Redoc хоёул `docs/api/openapi.yaml`-ийг уншина. |

## 2. OpenAPI гэрээ ба SRS-ийн холбоо

API-ийн үндсэн эх: [docs/api/openapi.yaml](../api/openapi.yaml).
Шаардлагын дугаар нь хамгийн сүүлд ирүүлсэн `Week_03_FoodFlow.docx`-ийн
суурьтай нийцнэ. Эдгээрийн гүйцэтгэл нь W03-ийн бүх шаардлага хэрэгжсэн гэсэн
утга агуулахгүй.

| Үйлдэл | Параметр, хүсэлтийн бие | Амжилттай хариу | SRS |
| --- | --- | --- | --- |
| `POST /api/v1/carts/{cart_id}/items` | `cart_id`; `food_id`, `quantity` | 200 `CartItem` | FR-04 |
| `PATCH /api/v1/carts/{cart_id}/items/{item_id}` | `cart_id`, `item_id`; `quantity` 1–10 | 200 `CartItem` | FR-05 |
| `PUT /api/v1/orders/{draft_id}/address` | `draft_id`; `district`, `khoroo`, `street`, `phone` | 200 `SavedAddress` | FR-08 |
| `PUT /api/v1/orders/{draft_id}/payment-method` | `draft_id`; `payment_method` | 200 `SavedPayment` | FR-10 |
| `POST /api/v1/orders` | `Idempotency-Key`; `cart_id`, `address`, `payment_method` | 201 шинэ захиалга; 200 ижил key, ижил JSON агуулгын давталт | FR-11, NFR-02 |

Таван үйлдэл бүгд `requestBody`, parameter, authentication, success response,
error response болон schema доторх жишээтэй. Read-only GET хүсэлтэд зохиомол
body нэмээгүй. Шинэ захиалгад 201 хэрэглэх нь FR-11-той нийцнэ; 200 нь өмнө
үүссэн захиалгын idempotent replay-д зориулагдана.

`components` хэсэгт `BearerAuth`, `CartId`, `ItemId`, `DraftId`, `IdempotencyKey`,
request/response schema болон нийтлэг алдаануудыг дахин ашиглав. Бүх endpoint
400, 401, 404, 409, 413, 415, 500 хариутай. `Error` schema нь `code`, `message`
талбарыг шаарддаг; `field` сонголттой. Өмчлөл зөрчигдвөл 404 буцаах бодлого нь
NFR-03-ийн нууцлалын зорилгыг локал хүрээнд дэмжинэ.

## 3. FoodFlow-ийн таван ажилладаг жишээ

[Python скрипт](../../examples/foodflow_requests.py) нь Windows дээр стандарт
сангаар ажиллана. [cURL хувилбар](../../examples/foodflow_requests.sh) нь HTTP
хүсэлт бүрийн method, header, payload-ийг тусад нь харуулна. Хоёр хувилбар ижил
домэйн утга, ижил дараалал хэрэглэнэ.

Эхлээд локал серверийг repo-ийн үндсэн хавтсаас асаана:

```powershell
python examples/mock_api.py
```

Өөр терминалд таван хүсэлтийг дарааллаар явуулна:

```powershell
python examples/foodflow_requests.py
```

| Алхам | Үр дүнгийн гол утга |
| --- | --- |
| Хоол нэмэх | `cart_101`, `ci_1`, `food_id=7`, quantity 1, subtotal 18,000 ₮. |
| Тоо өөрчлөх | Quantity 2, subtotal 36,000 ₮. |
| Хаяг хадгалах | `draft_1024`, дөрвөн талбартай `address`. |
| Төлбөрийн арга | `payment_method=QPay`. |
| Захиалга үүсгэх | `order_id=FF-1024`, `status=Pending`, total 39,000 ₮. |

Нийт үнэ нь 36,000 ₮ хоол + 3,000 ₮ хүргэлт. Таван response example-ийг
mock серверийн бодит HTTP хариутай тэнцүүлж, JSON schema-гаар давхар шалгана.
Ижил хэрэглэгч, key, body-тай хүсэлтийг давтахад 200 болон өмнөх захиалга;
ижил key, өөр body-тай бол 409 буцаахыг тусдаа тестээр батална.

Draft-д хадгалсан хаяг, төлбөрийн аргыг эцсийн POST body-д дахин илгээдэг.
Mock нь нэг хоолны мөртэй сагсыг үзүүлнэ; олон хоол, хөнгөлөлт, хүргэлтийн
цаг сонгох болон захиалгын цаашдын төлөвийн шилжилтийг хэрэгжүүлээгүй.

## 4. UE-5 Corg.ly-ийн гурван Python жишээ

Хавсаргасан handout-ийн UE-5 даалгаврыг орхилгүй, ижил локал сервер дээр
тусдаа `/v1` маршрутаар хэрэгжүүлэв. Жишээ бүрийн өмнө зорилго, оролт,
өгөгдлийн гарал болон mock-ийн хязгаарыг module docstring-д тайлбарлав.

| Endpoint | Python жишээ | Локал хариу ба хязгаар |
| --- | --- | --- |
| `POST /v1/pets/upload-photo` | [Multipart зураг upload](../../examples/corgly_upload_photo.py) | 201, `corgi_98231`, `uploaded`. JPEG нь үүсгэсэн шатрын хээ; сервер fixture зургийн локал URL буцаана. |
| `POST /v1/audio/translate-bark` | [Audio хүсэлт](../../examples/corgly_translate_bark.py) | 200, `language=en`, `translation="I want to play."`. WAV нь синтетик тон; орчуулга тогтмол mock утга. |
| `POST /v1/webhooks/subscribe` | [Webhook бүртгэл](../../examples/corgly_subscribe_webhook.py) | 201, `sub_corgi_1024`, `active`. Callback URL-ийг хариунд тусгана; event илгээхгүй. |

Гурван жишээг mock сервер ассан үед ажиллуулна:

```powershell
python examples/corgly_upload_photo.py
python examples/corgly_translate_bark.py
python examples/corgly_subscribe_webhook.py
```

[Fixture-ийн тайлбар](../../examples/data/README.md)-т JPEG/WAV-ийн формат,
синтетик гарал болон дахин үүсгэх аргыг бичсэн. Бодит амьтны мэдээлэл, дуу
таних AI, гаднын Corg.ly production үйлчилгээ ашигласан гэж мэдэгдээгүй.

## 5. Bhatti-ийн таван зарчмын үнэлгээ

Найман жишээний [бүрэн scorecard](../api/sample-audit.md)-д Explained,
Concise, Clear, Usable, Trustworthy үзүүлэлт тус бүрийн оноо, нотолгоо,
үлдсэн хязгаарыг тэмдэглэв. Нийлбэр нь **184/200 буюу 92%**, таван онооны
дундаж **4.6/5**. Энэ нь локал сургалтын хүрээний өөрийн үнэлгээ юм.

Trustworthy үзүүлэлтэд production баталгаа байхгүй тул бүх жишээнд 4/5
оноо өгсөн. Оролтын домэйн утга тодорхой, fixture repo-д байгаа, standalone
скриптүүд тестээр ажилладаг учраас Usable үзүүлэлтэд 5/5 өгсөн.
Multipart request болон бүтэн address payload шаардлагатай мөрийг Concise
зарчмын нэрээр хасаагүй.

## 6. Swagger UI, Redoc ба сонголтын тайлбар

Хоёр HTML харагдац ижил YAML уншина. Локал сервер дээр
[Swagger UI](http://127.0.0.1:8765/api/swagger.html) нь token, хүсэлт, HTTP хариуг
туршихад; [Redoc](http://127.0.0.1:8765/api/redoc.html) нь навигац, schema,
жишээг хамтатган уншихад зориулагдсан.

[100 үгийн сонголтын тайлбар](../api/renderer-decision.md)-т хайлт, унших
бүтэц, Try it out-ийн хэрэглээг харьцуулав. Зөвхөн үндсэн passage-ийн
хоосон зайгаар салгасан үгсийг тоолох автомат шалгалттай; гарчиг, тайлбар,
эх сурвалж тоонд орохгүй. Хэрэглэгчийн бодит хэмжилт хийгээгүй тул хайлтын
хурдыг хэмжсэн мэт дүгнээгүй.

Static HTML-ийг нийтэлсэн байдал болон API-ийн ажиллах чадвар тусдаа шалгуур.
Одоогийн OpenAPI `servers.url` локал хаягтай тул нийтийн HTTPS хуудсаас
Try it out ажиллахын тулд браузерын бодлого, локал серверийн хүртээмжийг шалгана.
Нийтийн sandbox шаардлагыг бүрэн хаахын өмнө тохирох HTTPS API сервер,
CORS болон браузерын бодит хүсэлтийн нотолгоо хэрэгтэй.

## 7. Баталгаажуулалт ба Definition of Done

Тестүүд schema, response example, server behavior болон кодын жишээг хамтад нь
шалгана. Python helper нь OpenAPI 3.0.3 стандартын бүрэн linter биш; стандартад
нийцэх үндсэн шалгалт нь Redocly CLI хэвээр байна.

```powershell
python -m unittest tests.test_openapi tests.test_mock_api -v
```

| Шалгуур | Нотолгоо, бодит төлөв |
| --- | --- |
| OpenAPI 3.0.3, ≥5 endpoint, auth, reusable components, examples | [YAML](../api/openapi.yaml), [OpenAPI тест](../../tests/test_openapi.py). Таван үйлдэл, local `$ref`, request/response schema example-уудыг шалгана. |
| Redocly CLI, zero errors | Redocly CLI 2.62.1-ийн `recommended` lint амжилттай (exit 0): алдаагүй, `info-license`-ийн нэг warning үлдсэн. Лицензийн эрх олгох шийдвэр хийгээгүй тул зохиомол MIT metadata нэмээгүй. [Ажиллуулалтын бүртгэл](../../review/redocly_log.txt)-тэй тулгана. |
| Найман кодын жишээ, дундаж ≥80% | [Scorecard](../api/sample-audit.md), [HTTP тест](../../tests/test_mock_api.py); локал хүрээний үнэлгээ 92%. |
| Idempotency, ownership, invalid input | Нэг key-тай 100 retry → нэг шинэ order; TTL24h; өөр хэрэглэгчийн нөөц404; token401; 400/409/413/415/500 хариу. |
| Swagger UI ба Redoc | Хоёр static HTML, локал HTTP маршрутууд бэлэн; автомат тест HTML/YAML serving-ийг шалгана. Браузерын харагдах байдал болон нийтийн sandbox-ийг тусад нь нотолно. |
| 100 үгийн шийдвэр | [Шийдвэрийн эх](../api/renderer-decision.md), яг 100 whitespace word байх автомат тест. |
| CI bonus | Бүх sample болон validator-ийг нэг unittest багцаар ажиллуулж болно; GitHub hosted run-ийн дүгнэлтийг бодит run URL-гүйгээр хийхгүй. |

## 8. Эргэцүүлэл ба дараагийн алхам

**Standup-д танилцуулах бодит төлөв.** Таван endpoint-ийн гэрээ, найман
ажилладаг жишээ болон нийтлэг алдааны schema бэлэн. Асуудалтай оролт,
өмчлөл, давтан хүсэлтийг локал тестээр шалгав. Нийтийн sandbox болон production
интеграцын нотолгоог локал mock-ийн үр дүнгээр орлуулаагүй.

**Retrospective.** Bearer header-ийг тайлбарлахдаа transport хэлбэрийг JWT-ийн
бодит хэрэгжүүлэлттэй хольж болохгүйг тодруулав. `foo/bar` нэрийг зохиомол боловч
тодорхой домэйн fixture-ээр сольсон. Уншихад Redoc, хүсэлт туршихад Swagger UI
ашиглах шийдвэрийг хэрэглэгчийн хэмжилтээр дараа нь дахин үнэлнэ.

**Судалсан ойлголтын хэрэглээ.** Handout-д Bhatti Ch. 5, p. 94-ийн Trustworthy
зарчмыг response-оо сервертэй шалгах гэж тайлбарласан. Энэ зарчмыг response
example ба HTTP хариуг автомат тулгалтад оруулснаар хэрэгжүүлэв. Handout-д
заасан Chinchilla Ch. 2, pp. 18–22 болон Ch. 6, p. 79-ийн хүрээнд дараагийн
ажилд нэг эхээс баримт үүсгэх, хэрэглэгчийн хэрэгцээгээр харагдацаа сонгох
зарчмыг үргэлжлүүлэн ашиглана. Номын бүтэн эх хавсаргагдаагүй тул энэ хэсэг
нь handout-ийн тайлбар, унших чиглүүлэгт тулгуурласан; шууд эшлэл биш.

**Гол зөрүү.** Локал зөв ажиллах contract болон нийтэд хүртээмжтэй, бодит
үйлчилгээтэй найдвартай API хоёрын хооронд production authentication,
өгөгдлийн хадгалалт, transaction, payment integration, deployment-ийн ажил
үлдсэн. Дараагийн семинарт эдгээрийг тус тусад нь issue болгон төлөвлөж,
endpoint, SRS холбоос, example, regression test болон өөрчлөлтийн тэмдэглэлийг
хамт шинэчилнэ.

## Эх сурвалж

- Хавсаргасан *Sprint 05 Lab Instructions — OpenAPI 3.0 & Bhatti Code Samples*, US-5.1–US-5.4, UE-5, Definition of Done.
- Хэрэглэгчийн `PHTBB5 (1).pdf`, `PHTBB5.yaml`; `Week_03_FoodFlow.docx`-ийн шаардлагын суурь.
- [OpenAPI 3.0.3 specification](https://spec.openapis.org/oas/v3.0.3) — API гэрээний формат.
- [Swagger UI installation](https://swagger.io/docs/open-source-tools/swagger-ui/usage/installation/), [configuration](https://swagger.io/docs/open-source-tools/swagger-ui/usage/configuration/) — HTML embed ба тохиргоо.
- [Redoc HTML deployment](https://github.com/Redocly/redoc/blob/main/docs/deployment/html.md), [Redocly lint](https://redocly.com/docs/cli/commands/lint) — унших харагдац ба стандарт шалгалт.
