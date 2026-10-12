# FoodFlow — Word ба PDF хувилбар

Markdown нь үндсэн эх. Доорх Word файлын текст, хүснэгт, код, холбоосыг засварлаж болно. PDF-д фонтыг нь суулгасан тул Монгол Unicode текстийг сонгож, хайж, хуулж болно.

| Баримт | Word | PDF | PDF хуудас | Засварлах эх |
| --- | --- | --- | ---: | --- |
| Week 01 FoodFlow | [DOCX](Week_01_FoodFlow.docx) | [PDF](Week_01_FoodFlow.pdf) | 6 | [Markdown](../docs/semesters/week-01.md) |
| Week 02 FoodFlow | [DOCX](Week_02_FoodFlow.docx) | [PDF](Week_02_FoodFlow.pdf) | 10 | [Markdown](../docs/semesters/week-02.md) |
| Week 03 FoodFlow | [DOCX](Week_03_FoodFlow.docx) | [PDF](Week_03_FoodFlow.pdf) | 5 | [Markdown](../docs/semesters/week-03.md) |
| Week 04 FoodFlow | [DOCX](Week_04_FoodFlow.docx) | [PDF](Week_04_FoodFlow.pdf) | 3 | [Markdown](../docs/semesters/week-04.md) |
| Week 05 FoodFlow | [DOCX](Week_05_FoodFlow.docx) | [PDF](Week_05_FoodFlow.pdf) | 5 | [Markdown](../docs/semesters/week-05.md) |
| Week 06 FoodFlow | [DOCX](Week_06_FoodFlow.docx) | [PDF](Week_06_FoodFlow.pdf) | 3 | [Markdown](../docs/semesters/week-06.md) |
| UE-2 Scope Charter | [DOCX](Scope_Charter.docx) | [PDF](Scope_Charter.pdf) | 1 | [Markdown](../docs/requirements/scope.md) |
| UE-1 Corg.ly | [DOCX](UE_01_Corgly.docx) | [PDF](UE_01_Corgly.pdf) | 2 | [Markdown](../docs/audience/corg-ly-exercise.md) |
| Нэгдсэн төслийн баримт | [DOCX](FoodFlow_Documentation.docx) | [PDF](FoodFlow_Documentation.pdf) | 100 | [Markdown](../docs/index.md) |

Нэгдсэн баримт нь зургаан семинарын бүрэн эх, нэр томьёо, persona, хамрах хүрээ, SRS, traceability, mock UI, архитектур, дөрвөн ADR, UE-4, API лавлах ба аудит, техникийн өр, төлөв, эх сурвалж, roadmap-ийг агуулна. Сонгосон хэсгүүдийн текстийг товчлоогүй. Mermaid source кодыг хэвээр хадгалж, түүнд харгалзах SVG дүрслэлийг зураг болгон нэмж оруулсан.

Өргөн traceability хүснэгт болон архитектурын зураг PDF/DOCX-ийн landscape хэсэгт байрлана. DOCX-ийн агуулгын хүснэгтийг Word дээр Update Field → Update entire table гэж шинэчилнэ. Word-ийн бодит хуудасны тоо тухайн төхөөрөмжийн фонт, хувилбараас хамаардаг; хүснэгтэд PDF-ийн бодит тоог үзүүлэв.

Хуудасны тоо, source/output SHA-256, Unicode болон ZIP/XML шалгалт: [manifest.json](manifest.json). Эхээс уншсан бүтцийн өгөгдөл: [block_data.json](block_data.json). Зураг ба эхийн mapping: [diagram_manifest.json](assets/diagram_manifest.json).

Дахин үүсгэхэд ReportLab, markdown-it-py, pypdf, Pillow болон Windows-ийн Arial/Consolas фонт хэрэгтэй. Туршсан dependency хувилбар: [requirements.txt](requirements.txt), SVG/PDF preview хэрэгсэл: [requirements-renderer.txt](requirements-renderer.txt). SVG-г шинэчилсэн бол эхлээд PySide6-тэй offscreen asset renderer ажиллуулна:

    python reports/assets/render_diagrams.py
    python tools/export_project.py

Нэгдсэн PDF-ийн дүрслэл ба DOCX зургийн бүтэц, эх/гаралтын hash-ийг дахин шалгах:

    python reports/assets/inspect_pdf.py reports/FoodFlow_Documentation.pdf --pages 1 2
    python reports/assets/audit_exports.py

Энэ аудит нь хуудасны хил, ZIP/XML, эхийн бүрэн байдлыг шалгана. Зургийн шошго, хүснэгтийн уншигдах байдлыг [preview](assets/previews/FoodFlow_Documentation/page-001.png) ашиглан нүдээр хянана.

PDF/DOCX-ийг өөрчилснөөр Markdown автоматаар шинэчлэгдэхгүй. Дараагийн семинарын өөрчлөлтийг эхлээд canonical Markdown-д хийж, дараа нь экспорт ба manifest-ийг хамт шинэчилнэ.
