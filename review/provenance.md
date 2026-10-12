# Зохиогч ба нотолгооны гарал

- Анхны W06 сэргээн байгуулалт: 2026-10-12. Нэгдсэн шинэчлэл: 2026-10-13, Asia/Ulaanbaatar.
- Орчин: Codex; тусдаа GPT-4/Claude session ажиллуулаагүй. Нарийн model version-ийг баттай мэдээлээгүй тул нэр зохиогоогүй.
- Анхны W06 оролт: хэрэглэгчийн өгсөн 9 PDF. Нэгдсэн шинэчлэлд W01–W03 Word, W04–W05 PDF, W05 YAML болон handout-ийн нэмэлт хувилбаруудыг ашигласан; [бүртгэл](../sources/manifest.json)-д нэр, hash бий. Анхны эх код, GitLab repository ирээгүй.
- `foodflow/order_service.py`: PDF-ийн тайлбарт тулгуурлан энэ удаа шинээр байгуулсан сургалтын хэрэгжилт.
- `manual_docstring.py`: зассан baseline snapshot. Файлын нэр нь handout-ийн deliverable нэрийг дагана; хүний гараар бие даан зохиосон эх гэсэн баталгаа биш.
- `ai_candidate_docstring.py`: хуучин W06 тайланд өгүүлсэн алдаануудыг зориуд сэргээсэн **seeded negative fixture**. Бодит model-ийн түүхий output биш.
- `manual_vs_ai.diff`: дээрх ижил executable code-ийн docstring зөрүү. AST тест implementation ижил эсэхийг шалгана.
- Нийтлэгдэх docstring болон тайланг Codex бэлтгэсэн. Бие даасан хүний peer review хийгдсэн гэж мэдүүлээгүй.

## Нэрлэсэн model audit-ийг гүйцээх prompt

“Attached is `foodflow/order_service.py`. Change only its module, class and public
callable docstrings to Google style. Document every actual parameter, return
field, raised exception and runnable example. Use customer_101, cart_101,
FF-1024 and integer MNT. Infer behavior only from the attached code; do not
add methods, types, persistence, authentication, refunds or key expiry.
Return the complete module and identify uncertainties.”

GPT-4 эсвэл Claude дээр үүнийг ажиллуулаад exact model ID, огноо, prompt,
оролтын SHA-256, засварлаагүй output, шинэ diff, хүний review-г хадгална.
Бодит output-д ghost API байхгүй бол “олдоогүй” гэж бичнэ; fixture-ийн
зориудын алдааг model-ийн санамсаргүй hallucination гэж тайлагнахгүй.
