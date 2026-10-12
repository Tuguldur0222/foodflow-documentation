# Шалгуур ба нотолгооны бүртгэл

**Шинэчилсэн:** 2026-10-13 · **Хамрах хүрээ:** W01–W06 баримтжуулалт, W05/W06 сургалтын код.

**Бэлэн** гэж агуулга, бүтэц нь боловсруулсан баримтыг; **локал шалгасан** гэж командын үр дүн, log-оор баталсан ажлыг тэмдэглэв. Хүний бие даасан хяналт, ярилцлага, quiz, цахим орчны гүйцэтгэл, CI/Pages-ийн нийтлэгдсэн үр дүн, model-ийн эх хариу шаардагдах ажлыг тусад нь хүлээгдэж буйгаар бүртгэсэн.

| Семинар | Бэлтгэсэн зүйл | Шалгалтын хүрээ | Үлдсэн нотолгоо |
|---|---|---|---|
| W01 | 3×4 doc matrix; persona; diff; UE-1; reflection | Markdown/navigation | Interview, non-engineer review, quiz, workspace |
| W02 | SRS structure; 5 requirement; scope; traceability | Бүтэц/холбоос | Owner/source approval; peer review/workspace |
| W03 | 15FR+5NFR; acceptance/test; UI mock; UE-3 | ID/traceability | Production acceptance; human review |
| W04 | arc42; Context/Container; ADR1–4; UE-4 | Source diagrams/build | Proposed ADR approval; runtime/workspace |
| W05 | OpenAPI; 5+3 жишээ; audit; comparison | Schema/contract/mock; Redocly log | Production payload; public Swagger/Redoc/Try-it-out |
| W06 | Docstring; Sphinx; fixture; reflection/debt | Unit/doctest/strict build | GPT-4/Claude; human baseline/review; GitLab Pages |

## Бодит шалгалт

[verification.json](../../review/verification.json) нь огноо, орчин, command exit code, log path-ыг хадгална. [Unit log](../../review/unit_tests_log.txt), [HTML log](../../review/sphinx_html_log.txt), [doctest log](../../review/sphinx_doctest_log.txt)-оос дэлгэрэнгүй үр дүнг уншина. Тест нэмэгдэхэд гараар бичсэн тоо хуучрахгүйн тулд одоогийн үр дүнг JSON/log-оор заана.

OpenAPI-г Redocly 2.62.1-ээр шалгахад алдаа гараагүй, лицензийн мэдээлэл дутуу гэсэн нэг `info-license` анхааруулга гарсан. Хэрэглэгчийн өмнөөс лиценз сонгоогүй. [Бодит log](../../review/redocly_log.txt)-т үр дүнг хадгалсан. Sphinx-ийн HTML үүсгэлтийг `-n -W --keep-going` нөхцөлөөр шалгана.

Засварлах Word, хэвлэх PDF болон экспортын эх/үр дүнгийн hash-ийг [тайлангийн бүртгэлээс](../../reports/README.md) үзнэ.

## GitHub ба GitLab-ийн нотолгоо

| Үйлчилгээ | Баталгааны утга |
|---|---|
| GitHub repository | [Source](https://github.com/Tuguldur0222/foodflow-documentation); commit-оор шалгана |
| GitHub Actions | Workflow бэлтгэсэн; run URL ба commit SHA-аар баталгаажуулна |
| GitHub Pages | Optional workflow; URL батлагдах хүртэл live гэж тооцохгүй |
| GitLab CI/Pages | Тохируулга бий; GitLab project/run/URL ирээгүй |
| Issues | GitHub CLI-гаар [#1](https://github.com/Tuguldur0222/foodflow-documentation/issues/1), [#2](https://github.com/Tuguldur0222/foodflow-documentation/issues/2) үүсгэсэн; [техникийн өрийн бүртгэл](../../review/technical_debt.md) |

Эх код нийтлэгдсэнээр ADR автоматаар Accepted болохгүй. Локал mock-ийн тест нь сарын availability, хэрэглэгчийн бодит орчны LCP, production authentication болон өгөгдлийн сангийн найдвартай ажиллагааг батлахгүй.
