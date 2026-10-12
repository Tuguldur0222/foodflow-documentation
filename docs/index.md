# FoodFlow баримтжуулалтын гарын авлага

FoodFlow нь хоол сонгох, сагс бүрдүүлэх, хүргэлт ба төлбөрийн арга сонгох, захиалга үүсгэх, явцыг хянах онлайн системийн сургалтын төсөл юм. Энэхүү баримтжуулалт эхний зургаан семинарын ажлыг нэгтгэж, дараагийн семинар бүрээр үргэлжлүүлэн хөгжүүлэх үндэс болно.

## Ямар мэдээлэл хайж байна вэ?

| Уншигчийн зорилго | Эхлэх баримт | Дараагийн алхам |
|---|---|---|
| Хэрэглэгчийн хэрэгцээг мэдэх | [Persona](audience/personas.md) | [Хамрах хүрээ](requirements/scope.md) |
| Шаардлагыг шалгах | [SRS](requirements/srs.md) | [Traceability](requirements/traceability.md) |
| Архитектурыг ойлгох | [Архитектур](architecture/index.md) | ADR-ийн Context, Decision, Consequences |
| HTTP хүсэлт турших | [API гарын авлага](api/README.md) | OpenAPI ба локал mock |
| Python классыг ашиглах | [W06](semesters/week-06.md) | [Autodoc API](source/api.rst) |
| Үр дүнг үнэлэх | [Төлөв](project/status.md) | [Гарал ба нотолгоо](project/provenance.md) |
| Дараагийн семинар нэмэх | [Журам](../CONTRIBUTING.md) | [Roadmap](project/roadmap.md) |

## Семинарын дараалал

1. [W01 — Уншигч ба баримтжуулалтын суурь](semesters/week-01.md)
2. [W02 — SRS бүтэц ба хамрах хүрээ](semesters/week-02.md)
3. [W03 — Шалгаж болох шаардлага](semesters/week-03.md)
4. [W04 — Архитектур ба шийдвэр](semesters/week-04.md)
5. [W05 — OpenAPI ба кодын жишээ](semesters/week-05.md)
6. [W06 — Кодын баримтжуулалт ба AI аудит](semesters/week-06.md)

## Баримтыг зөв унших нь

SRS нь шаардагдах эцсийн зан үйлийг, ADR нь санал болгосон архитектурын шийдвэрийг, mock нь локал туршилтын хязгаарлагдмал ажиллагааг илэрхийлнэ. Шаардлагын дугаарыг хэрэглэгчийн `Week_03_FoodFlow.docx` хувилбараар жигдэлсэн; хуучин PDF-ийн өөр дугаарыг [өөрчлөлтийн бүртгэлд](../CHANGELOG.md) тайлбарласан.

Англи нэр томьёог [тайлбар толь](glossary.md)-д нэг утгаар тогтоосон. Бүтэн номын эх ирээгүй үед handout-аар дамжуулсан тайлбарыг номын үгчилсэн эшлэл гэж үзэхгүй.

## Нэмэлт баримт

- [UE-1: Corg.ly](audience/corg-ly-exercise.md)
- [Техникийн өр](../review/technical_debt.md)
- [AI аудит](../review/bhatti_audit_table.md)
- [Нийтлэх заавар](project/publishing.md)
- [Word ба PDF тайлан](../reports/README.md)

```{toctree}
:hidden:
:maxdepth: 2

semesters/week-01
semesters/week-02
semesters/week-03
semesters/week-04
semesters/week-05
semesters/week-06
audience/personas
audience/corg-ly-exercise
requirements/scope
requirements/srs
requirements/traceability
architecture/index
api/README
source/api
glossary
project/status
project/provenance
project/roadmap
project/publishing
```
