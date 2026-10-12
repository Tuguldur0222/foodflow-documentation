<p align="center"><img src="docs/assets/foodflow-banner.svg" alt="FoodFlow — Software Project Documentation" width="900"></p>

# FoodFlow · Програм хангамжийн төслийн баримтжуулалт

**Онлайн хоол захиалгын системийн шаардлага, архитектур, API, кодын баримтжуулалтыг нэг эх сурвалжаас унших төсөл.**

Ю. Төгөлдөр · 23B1NUM2350 · МУИС · Семинар 01–06 · Шинэчилсэн: **2026-10-13**

[Эхлэх](docs/index.md) · [Шаардлага](docs/requirements/srs.md) · [Архитектур](docs/architecture/index.md) · [HTTP API](docs/api/README.md) · [Word/PDF](reports/README.md) · [Нэр томьёо](docs/glossary.md) · [Дараагийн семинар нэмэх](CONTRIBUTING.md)

Баримт бичиг нь хэрэглэгчийн хэрэгцээнээс шаардлага, архитектурын шийдвэр, API contract, шалгалтын нотолгоо руу дараалан шилжинэ. Семинарын тайлан бүр зорилго, хийсэн ажил, шалгах баримт, үлдсэн ажлыг агуулна. Сургалтын жишээ код нь сонгосон зан үйлийг шалгахад зориулагдсан; production системийг бүрэн хэрэгжүүлсэн гэж үзэхгүй.

## Зургаан семинар

| Семинар | Гол агуулга | Тайлан | Дагалдах баримт |
|---|---|---|---|
| 01 | Уншигч, баримтжуулалтын төрөл, ойлгомжтой бичих | [W01](docs/semesters/week-01.md) | [Persona](docs/audience/personas.md) |
| 02 | SRS бүтэц, хамрах хүрээ, traceability | [W02](docs/semesters/week-02.md) | [Scope charter](docs/requirements/scope.md) |
| 03 | 15 FR, 5 NFR, acceptance ба verification | [W03](docs/semesters/week-03.md) | [SRS](docs/requirements/srs.md), [мөрдөх хүснэгт](docs/requirements/traceability.md) |
| 04 | arc42, C4, архитектурын шийдвэр | [W04](docs/semesters/week-04.md) | [Архитектур ба ADR](docs/architecture/index.md) |
| 05 | OpenAPI 3.0.3, ажиллах кодын жишээ | [W05](docs/semesters/week-05.md) | [API reference](docs/api/README.md), [OpenAPI](docs/api/openapi.yaml) |
| 06 | Google-style docstring, Sphinx, AI аудит | [W06](docs/semesters/week-06.md) | [Python API](docs/source/api.rst), [аудит](review/bhatti_audit_table.md) |

[Нэгдсэн шалгуур ба нотолгоо](docs/project/status.md) · [Хийсэн засвар](CHANGELOG.md) · [Эх сурвалж, гарал](docs/project/provenance.md)

Засварлаж болох [нэгдсэн Word тайлан](reports/FoodFlow_Documentation.docx), хэвлэхэд зориулсан [PDF тайлан](reports/FoodFlow_Documentation.pdf), [семинар бүрийн тусдаа хувилбар](reports/README.md) бэлэн.

## Локал ажиллуулах

Python **3.11 эсвэл шинэ** хувилбар ашиглана. Төслийн үндсэн хавтсаас:

```bash
python -m pip install -r requirements-docs.txt
python -m unittest discover -s tests -v
python -m doctest foodflow/order_service.py
python tools/check_repository.py
python tools/prepare_docs.py
python -m sphinx -c docs -n -W --keep-going -b html . public
```

Үүссэн `public/index.html`-ийг browser-оор нээнэ. [HTTP сургалтын сервер](docs/api/README.md)-ийн заавар API баримтад бий. Тест нь mock серверийг өөрөө асааж унтраадаг; гараар асаасан сервер шаардлагагүй.

Бүх локал шалгалтыг ажиллуулж log хадгалах:

```bash
python tools/verify.py
```

W05-ийн OpenAPI linter-ийг Node.js **24** орчинд ажиллуулна:

```bash
npx --yes @redocly/cli@2.62.1 lint docs/api/openapi.yaml
```

## Төслийн бүтэц

```text
docs/
  audience/       Уншигчийн persona, UE-1
  requirements/   Scope, SRS, traceability
  architecture/   arc42, C4, MADR шийдвэрүүд
  api/            OpenAPI, Swagger UI, Redoc
  semesters/      01–06 тайлан; дараа нь 07–15
  project/        Төлөв, эх сурвалж, шалгах нотолгоо
  source/         Python API-ийн Sphinx autodoc
examples/         FoodFlow/Corg.ly сургалтын HTTP жишээ
foodflow/         W06 Python OrderService
tests/            Зан үйл, API contract, AI аудитын шалгалт
review/           Аудит, diff, build/test log
reports/          Засварлах Word, хэвлэх PDF ба экспортын бүртгэл
sources/          Оюутны анхны ажил, эх сурвалжийн бүртгэл
templates/        Дараагийн семинарын загвар
.github/          CI, issue болон pull request загвар
.gitlab-ci.yml    W06 handout-ийн GitLab хувилбар
```

## Үргэлжлүүлэн хөгжүүлэх

Шинэ семинар бүрт `docs/semesters/week-NN.md` нэмээд навигац, шаардлагын холбоо, нотолгоог хамт шинэчилнэ. [CONTRIBUTING](CONTRIBUTING.md) нь branch, commit, PR, review, шалгалтын дарааллыг тайлбарлана. Хийгдээгүй даалгаварт дууссан мэт хоосон тайлан үүсгэхгүй; [roadmap](docs/project/roadmap.md)-д хүлээгдэж буйгаар бүртгэнэ.

Ярилцлага, хүний peer review, quiz, өмнөх hosted CI-ийн үр дүнг шинэ кодын тестээр орлуулахгүй. GitLab Pages нь W06-ийн тусдаа шаардлага; GitHub repository түүнийг автоматаар биелүүлэхгүй.
