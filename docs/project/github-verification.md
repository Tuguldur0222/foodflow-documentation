# GitHub нийтлэлийн шалгах баримт

**Repository:** [Tuguldur0222/foodflow-documentation](https://github.com/Tuguldur0222/foodflow-documentation).

**Баталгаажуулсан:** 2026-10-13, Asia/Ulaanbaatar. `main` салбарт баримт бичиг, код, эх материалын бүртгэл, Word/PDF тайлан нийтлэгдсэн.

Шалгасан commit: [`c1271d3`](https://github.com/Tuguldur0222/foodflow-documentation/commit/c1271d3cb354b01da214badf81d99f411598233f). [GitHub Actions run](https://github.com/Tuguldur0222/foodflow-documentation/actions/runs/38286161079) бүх job амжилттай дууссан.

| Шалгалт | Үр дүн | Бодит нотолгоо |
|---|---|---|
| Python 3.11 + Sphinx 9.0.4 | 49 unit test, 25 doctest; Sphinx doctest/HTML амжилттай | [Job](https://github.com/Tuguldur0222/foodflow-documentation/actions/runs/38286161079/job/114934936208) |
| Python 3.14 + Sphinx 9.1.0 | 49 unit test, 25 doctest; Sphinx doctest/HTML амжилттай | [Job](https://github.com/Tuguldur0222/foodflow-documentation/actions/runs/38286161079/job/114934936520) |
| Redocly 2.62.1, Node 24 | Алдаа 0; лицензийн metadata-ийн нэг анхааруулга | [Job](https://github.com/Tuguldur0222/foodflow-documentation/actions/runs/38286161079/job/114934936527) |

Python-ийн хоёр job дээр ижил 25 жишээг Python doctest болон Sphinx doctest builder-ээр давхар ажиллуулсан; 50 өөр жишээ гэж тооцоогүй. Лицензийг хэрэглэгчийн өмнөөс сонгоогүй. [Машинаар унших бүртгэл](../../review/github_ci.json)-д job ID, URL, log-ийн батлах мөрүүд бий. Run-ийн **Artifacts** хэсэгт Python орчин бүрийн log болон үүссэн HTML хадгалагдана.

Эхний [run](https://github.com/Tuguldur0222/foodflow-documentation/actions/runs/38285825434)-ийн Python 3.11 job нь Sphinx 9.1-ийн Python ≥3.12 шаардлагаас болж dependency суулгах үед зогссон. `requirements-docs.txt`-д Python хувилбараас хамаарсан pin хийж зассаны дараах run амжилттай болсон. Алдааны түүхийг нууж, эхний run-ийг амжилттай гэж тэмдэглээгүй.

Commit-ийн тайлбарыг семинар, API, автомат шалгалт, тайлангийн файл, нийцлийн засвар гэсэн агуулгаар энгийн монголоор бичсэн. PHTBB ажлын хавтас нь Git repository бөгөөд `origin/main`-тай холбогдсон; дараагийн семинарыг [CONTRIBUTING](../../CONTRIBUTING.md)-ийн дарааллаар нэмнэ.

[Локал шалгалт](../../review/verification.json) · [Техникийн өр](../../review/technical_debt.md) · [Word/PDF](../../reports/README.md).

Энэ хуудас нь нийтлэлийн дараах нотолгоог шинэчлэх бүртгэл. Экспортын тайлан эхийн hash, үүсгэсэн огноогоороо тухайн үеийн хувилбарыг хадгална. Дараагийн commit-ийн одоогийн төлөвийг [Actions](https://github.com/Tuguldur0222/foodflow-documentation/actions/workflows/quality.yml)-оос шалгана.

GitHub Pages-ийн workflow бэлтгэсэн боловч deployment ажиллуулаагүй. GitLab CI/Pages, хүний бие даасан review болон нэрлэсэн model-ийн эх хариу шаардах семинарын нотолгоо тусдаа хүлээгдэж байна.
