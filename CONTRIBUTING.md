# Баримтжуулалтыг шинэчлэх журам

Тайлан, source, requirement холбоо, нотолгоог хамт шинэчилнэ. [Нэр томьёо](docs/glossary.md), [эх сурвалжийн зарчим](docs/project/provenance.md)-ыг баримтална.

1. Шинэ handout-ийн acceptance criterion-ийг [загварт](templates/seminar.md) оруулна.
2. `docs/semesters/week-NN.md` нэмнэ; зааврыг хийсэн ажилтай холихгүй.
3. SRS/ADR/OpenAPI/code/test-ийг ижил branch-д засна.
4. README, docs index-ийн toctree, status, CHANGELOG-д холбоос нэмнэ.
5. `python tools/verify.py`; API өөрчилсөн бол Redocly lint ажиллуулна.
6. Энгийн утгатай commit, PR хийнэ; бодит review-ийн дараа Reviewer/Last-Reviewed шинэчилнэ.

Шаардлагын ID-г өөр утгад чимээгүй шилжүүлэхгүй. Шалтгаан/source/affected test/decision-ийг бүртгэнэ; хассан ID retired. ADR-ийг устгахгүй, supersede хийнэ. Proposed→Accepted-д reviewer/огноо шаардлагатай.

Монгол өгүүлбэрийн гол санааг эхэнд нь өгнө. Technical term-д шаардлагатай монгол тайлбар хэрэглэнэ; identifier/enum орчуулахгүй. Implemented/tested/deployed гэсэн claims-д тохирох нотолгоо хавсаргана.

```bash
python -m pip install -r requirements-docs.txt
python tools/verify.py
npx --yes @redocly/cli@2.62.1 lint docs/api/openapi.yaml
```

Шалгалтыг ногоон болгохын тулд warning suppress/test skip/fake output нэмэхгүй. AI ашиглавал [audit загвар](templates/ai-audit.md)-т raw provenance хадгална; хүний зохиол/review-г хийгээгүй бол тэгж нэрлэхгүй.
