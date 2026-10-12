# FoodFlow API · Week 05

Энэ лавлах нь API ашиглах хөгжүүлэгчид зориулсан. Сагсанд хоол нэмэхээс захиалга
үүсгэх хүртэлх таван HTTP үйлдлийг [OpenAPI 3.0.3 гэрээнд](openapi.yaml) тодорхойлж,
хүсэлт, хариу, алдааны нөхцөлийг ажилладаг локал mock-той тулган шалгана.

| Ашиглах зүйл | Эх файл |
| --- | --- |
| Машинаар унших API гэрээ | [openapi.yaml](openapi.yaml) |
| Хүсэлт турших Swagger UI | [swagger.html](swagger.html) |
| Уншихад зориулсан Redoc | [redoc.html](redoc.html) |
| Таван FoodFlow үйлдэл | [Python](../../examples/foodflow_requests.py), [cURL](../../examples/foodflow_requests.sh) |
| Кодын жишээний үнэлгээ | [Bhatti scorecard](sample-audit.md) |
| Хоёр харагдацын сонголт | [100 үгийн тайлбар](renderer-decision.md) |
| Семинарын тайлан | [Week 05](../semesters/week-05.md) |

## 1. Локал ажиллуулах

Repo-ийн үндсэн хавтсаас серверийг асаана. Python 3.11+ стандарт сан хангалттай;
сервер нь зөвхөн энэ компьютерт хандах `127.0.0.1` хаягт сонсоно.

```powershell
python examples/mock_api.py
```

Өөр терминалд дараах командыг ажиллуулна. Таван хүсэлт дарааллаар явж, JSON
хариуг хэвлэнэ. Windows дээр Python хувилбар нь нэмэлт Bash шаардахгүй.

```powershell
python examples/foodflow_requests.py
```

Bash болон cURL ≥7.76 байгаа орчинд ижил таван үйлдлийг хүсэлт бүрээр нь уншиж,
ажиллуулах хувилбар:

```bash
bash examples/foodflow_requests.sh
```

Бүрэн дарааллыг дахин туршихдаа `Ctrl+C`-ээр серверийг зогсоогоод дахин асаана.
Бүх өгөгдөл санах ойд хадгалагддаг тул дахин асаахад fixture болон idempotency
кэш анхны төлөвт орно. Өөр порт хэрэгтэй бол серверийн `--port`, Python
жишээнүүдийн `--base-url` аргументыг ижил тохируулна.

Хоёр харагдацыг **сервер ажиллаж байх үед** браузераар нээнэ:

- [Локал Swagger UI](http://127.0.0.1:8765/api/swagger.html)
- [Локал Redoc](http://127.0.0.1:8765/api/redoc.html)

HTML-ийг `file://`-ээр шууд нээхэд YAML татах хүсэлтийг браузер хязгаарлаж болно.
CDN-ээс JavaScript/CSS татдаг учраас HTML харагдац интернет холболт шаарддаг.
Локал mock болон Python жишээнүүд интернетгүйгээр ажиллана.

## 2. Таних мэдээлэл ба өмчлөл

| Ил тод demo token | Хэрэглэгч | Өөрийн нөөц |
| --- | --- | --- |
| `demo-customer-token` | `customer_1` | `cart_101`, `draft_1024` |
| `demo-other-token` | `customer_2` | `cart_202`, `draft_2024` |
| `demo-corgly-token` | UE-5 Corg.ly жишээ | `corgi_98231` fixture |

HTTP хүсэлтэд `Authorization: Bearer demo-customer-token` header илгээнэ.
Swagger UI-ийн **Authorize** талбарт зөвхөн token утгыг оруулна. Token байхгүй
эсвэл буруу бол **401**, өөр хэрэглэгчийн сагс эсвэл draft-д хандвал **404**
буцаана. Ингэснээр нөөц байгаа эсэхийг гаднын хэрэглэгчид ялгаж харуулахгүй.

HTTP authentication-ийн scheme нэр том жижиг үсгээс хамаарахгүй: `Bearer`
болон `bearer` ижил. Харин token утгын үсгийг яг хэвээр нь хэрэглэнэ.
Энэ нь [RFC 9110 §11.1](https://www.rfc-editor.org/rfc/rfc9110.html#section-11.1)
болон [RFC 6750 §2.1](https://www.rfc-editor.org/rfc/rfc6750.html#section-2.1)-ийн
header syntax-т нийцүүлсэн parsing; OAuth үйлчилгээ хэрэгжүүлсэн гэсэн утга биш.

Эдгээр token нь баримтжуулалтад зориуд ил тавьсан тогтмол утга. JWT үүсгэх,
гарын үсэг шалгах, token сунгах, хэрэглэгч нэвтрүүлэх үйлчилгээг хэрэгжүүлээгүй.

## 3. Таван HTTP үйлдэл

| Дараалал | Үйлдэл | Оролтын гол талбар | Амжилттай хариу | W03 шаардлага |
| --- | --- | --- | --- | --- |
| 1 | `POST /api/v1/carts/{cart_id}/items` | `food_id`, `quantity` | 200 `CartItem` | FR-04 |
| 2 | `PATCH /api/v1/carts/{cart_id}/items/{item_id}` | `quantity` | 200 `CartItem` | FR-05 |
| 3 | `PUT /api/v1/orders/{draft_id}/address` | `district`, `khoroo`, `street`, `phone` | 200 `SavedAddress` | FR-08 |
| 4 | `PUT /api/v1/orders/{draft_id}/payment-method` | `payment_method` | 200 `SavedPayment` | FR-10 |
| 5 | `POST /api/v1/orders` | `cart_id`, `address`, `payment_method`; `Idempotency-Key` header | 201 шинэ захиалга; 200 давтан хүсэлт | FR-11, NFR-02 |

Read-only GET үйлдэлд зохиомол request body нэмэхийн оронд handout-ийн таван
үйлдэлд `requestBody` шаардах шалгуурыг дээрх таван write үйлдлээр хангав.

Сургалтын `food_id=7` хоолны нэгж үнэ **18,000 ₮**. Quantity нь **1–10 бүхэл тоо**;
`true`, `1.5`, `"2"` утгууд буруу оролт болно. Ижил хоолыг сагсанд дахин POST
хийхэд 409; тоог өөрчлөхдөө PATCH хэрэглэнэ. Локал mock зөвхөн нэг хоолны
нэг мөртэй сагсыг үзүүлдэг.

Хаягийн дөрвөн талбар заавал байна: `district`, `street` хоосон биш, 200 хүртэл
тэмдэгт; `khoroo` нь 1–100 бүхэл тоо; `phone` нь яг найман ASCII цифртэй string.
Энэ нь байршлын бодит шалгалт биш. Төлбөрийн нэршил том жижиг үсгээс хамаарна:
`QPay`, `BankCard`, `CashOnDelivery`.

Draft-ийн хоёр PUT нь өгөгдөл хадгалах үйлдлийг тусад нь үзүүлнэ. Эцсийн POST
хүсэлт address, payment_method-оо body-д илгээдэг; тухайн body захиалгын
эцсийн утга болно. Draft-ийн PUT-уудыг заавал өмнө нь дуудах шаардлагагүй.
Submit хийсэн сагс болон түүнд хамаарах draft-ийг дахин засахад 409 буцаана.

Quantity 2 үед `subtotal_mnt=36000`; хүргэлтийн **3,000 ₮** хураамж нэмж
`total_mnt=39000` болно. Эхний захиалгын шалгагдсан хариу:

```json
{"order_id":"FF-1024","status":"Pending","total_mnt":39000}
```

Бодит төлбөр төлөгдсөн, ресторан баталгаажуулсан, хүргэлт эхэлсэн гэсэн утга
агуулахгүй. Status-ийн цаашдын шилжилт Week 05 mock-ийн хамрах хүрээнд ороогүй.

## 4. Idempotency ба алдаа

`Idempotency-Key` нь 1–128 тэмдэгттэй, ASCII үсэг, цифр, `_ . : -` тэмдэгтээс
бүрдэнэ. Кэш нь **хэрэглэгч + key**-ээр ялгагдаж, 24 цаг хадгалагдана.

| Нөхцөл | HTTP үр дүн |
| --- | --- |
| Шинэ key, өөрийн хоосон биш сагс | 201, захиалга шинээр үүснэ. |
| Ижил хэрэглэгч, key, JSON агуулга; 24 цаг дуусаагүй | 200, өмнөх `order_id` болон хариу; JSON түлхүүрийн дараалал нөлөөлөхгүй. |
| Ижил хэрэглэгч, key, өөр JSON агуулга | 409, шинэ захиалга үүсэхгүй. |
| Өөр хэрэглэгч ижил key хэрэглэсэн | Өөрийн сагсанд тусдаа хүсэлт гэж үзнэ. |
| 24 цаг дууссан | Кэшийн entry арилна; submit хийсэн сагс түгжээтэй тул 409. |
| Сервер дахин ассан | Санах ойн кэш болон захиалгын төлөв арилна. |

Зэрэгцээ хүсэлтүүдийг локал серверийн lock дотор атомик боловсруулна. Нэг
сагсанд ижил key-тай **100 зэрэгцээ retry** явуулах тест нэг 201, 99 ширхэг
200, нэг `order_id` үүссэнийг шалгана. Энэ нотолгоо нь нэг процессын локал
mock-д хамаарна; олон сервер, өгөгдлийн сангийн transaction-ийг батлахгүй.

Бүх алдаа `Error` schema-тай: `code`, `message` шаардлагатай; `field` нь
сонголттой. Mock-ийн одоогийн хариунд field оруулдаггүй.

| Код | Утга |
| --- | --- |
| 400 | JSON, оролтын төрөл, талбар эсвэл idempotency key буруу. |
| 401 | Token байхгүй эсвэл танигдахгүй; `WWW-Authenticate: Bearer` header байна. |
| 404 | Нөөц олдоогүй эсвэл тухайн хэрэглэгчийн өмч биш. |
| 409 | Хоосон/submit хийсэн сагс, item давхардал эсвэл key-ийн агуулгын зөрчил. |
| 413 | Request body 1 MiB-ээс их. |
| 415 | `Content-Type` тохироогүй. |
| 500 | Хүлээгдээгүй серверийн алдаа; дотоод exception-ийн мэдээлэл буцаахгүй. |

Body-г бүрэн уншихаас өмнө 413 эсвэл 401 буцаах үед JSON хариуг TCP reset-ээр
алдахаас сэргийлж, хариуг flush хийсний дараа холболтын write талыг хааж,
үлдсэн upload-аас хамгийн ихдээ 2 MiB-ийг нэг секундийн дотор хаяна.
Энэ нь [RFC 9112 §9.6](https://www.rfc-editor.org/rfc/rfc9112.html#section-9.6)-ийн
холболтыг үе шаттай хаах зарчмыг хэрэглэсэн локал mock-ийн зан төлөв юм.
1 MiB request limit хэвээр; rejected body-г application өгөгдөл болгон хадгалахгүй.

## 5. UE-5: Corg.ly-ийн гурван Python жишээ

Corg.ly нь W05 handout-д өгсөн зохиомол дадлагын систем. Эдгээр жишээ нь
FoodFlow-ийн домэйн эсвэл public API-д нэмсэн бүтээгдэхүүний боломж биш.

| Скрипт | Зорилго, оролт | Шалгагдсан локал үр дүн |
| --- | --- | --- |
| [corgly_upload_photo.py](../../examples/corgly_upload_photo.py) | `pet_id=corgi_98231`, синтетик JPEG-ийг multipart-ээр `POST /v1/pets/upload-photo` руу илгээнэ. | 201, `status=uploaded`, локал fixture зургийн URL. |
| [corgly_translate_bark.py](../../examples/corgly_translate_bark.py) | Синтетик WAV, `X-Pet-Id`, `X-Target-Language=en` header-тай `POST /v1/audio/translate-bark`. | 200, тогтмол `translation="I want to play."`; дуу таних AI биш. |
| [corgly_subscribe_webhook.py](../../examples/corgly_subscribe_webhook.py) | Локал receiver URL, `events=["pet.activity"]`-г `POST /v1/webhooks/subscribe` руу илгээнэ. | 201, `subscription_id=sub_corgi_1024`; callback илгээхгүй. |

Локал сервер ассан үед дараах гурван командыг тус тус ажиллуулна:

```powershell
python examples/corgly_upload_photo.py
python examples/corgly_translate_bark.py
python examples/corgly_subscribe_webhook.py
```

Upload mock нь JPEG/WAV-ийн header/signature-ийг л шалгана; медиа файлыг бүрэн
тайлж унших, хорлонтой файл илрүүлэх, зураг хадгалах, жинхэнэ орчуулга хийхгүй.
Webhook хүсэлтийн бүтэц, URL-ийн схемийг шалгаж хариу өгнө; receiver байгаа
эсэх, event хүргэлт, retry, гарын үсэг шалгахгүй. [Fixture-ийн гарал](../../examples/data/README.md)
болон [чанарын үнэлгээ](sample-audit.md)-г хамт уншина.

## 6. Шалгалт ба нийтийн харагдацын хязгаар

Эхлээд dev dependency-уудыг суулгаад OpenAPI бүтэц, JSON example, HTTP зан
төлөв, найман жишээг локал сервертэй шалгана:

```powershell
python -m pip install -r requirements-docs.txt
python -m unittest tests.test_openapi tests.test_mock_api -v
```

OpenAPI стандартын үндсэн lint-ийг repo-ийн тогтоосон Redocly CLI хувилбараар
ажиллуулна. Python helper нь local `$ref`, JSON Schema-д нийцсэн example-уудыг
шалгадаг; Redocly-г орлох OpenAPI стандартын бүрэн validator биш.

Static HTML болон YAML-ийг хамтад нь нийтлэх боломжтой. Одоогийн `servers.url`
нь `http://127.0.0.1:8765` тул нийтийн HTTPS хуудсаас **Try it out** ажиллах
эсэх нь локал сервер, браузерын mixed-content болон local-network бодлогоос
хамаарна. Нийтийн sandbox-ийг ажилласан гэж үзэхийн өмнө тусдаа хүртээмжтэй
API сервер, CORS, HTTPS болон браузерын бодит хүсэлтийг шалгана. Нийтэд
унших static баримтжуулалт байршсан нь production API ажилласны баталгаа биш.

## 7. Эх сурвалж ба дараагийн шинэчлэл

Гэрээний суурь нь хэрэглэгчийн өгсөн `PHTBB5.yaml` болон шинэчилсэн
`PHTBB5 (1).pdf`; шаардлагын дугаарын суурь нь `Week_03_FoodFlow.docx`.
Өмнөх `PHTBB5.pdf` хувилбарын тайлбарыг эх хувилбарын түүх гэж үзэв.
Хавсаргасан W05 handout нь даалгаврын шалгуурыг тогтооно; түүн дэх жишээ
production URL болон JWT-ийг энэ төслийн бодит холболт гэж үзээгүй.

OpenAPI-ийн шинэ endpoint нэмэхдээ schema, request/response example, SRS-ийн
холбоос, mock-ийн дэмжлэг, HTTP зан төлөвийн тестийг хамт шинэчилнэ. API талбар
эсвэл утга өөрчлөгдвөл хувилбарын дугаар, өөрчлөлтийн тэмдэглэл болон хэрэглэгчид
нөлөөлөх өөрчлөлтийг бүртгэнэ. Хоёр HTML нь нэг YAML унших зарчмыг хадгална.

Хэрэгжүүлэлтийн албан эх сурвалж:
[OpenAPI 3.0.3](https://spec.openapis.org/oas/v3.0.3),
[Swagger UI installation](https://swagger.io/docs/open-source-tools/swagger-ui/usage/installation/),
[Swagger UI configuration](https://swagger.io/docs/open-source-tools/swagger-ui/usage/configuration/),
[Redoc HTML](https://github.com/Redocly/redoc/blob/main/docs/deployment/html.md),
[Redocly lint](https://redocly.com/docs/cli/commands/lint).
