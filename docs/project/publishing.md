# GitHub дээр нийтлэх ба хөгжүүлэх

Repository: [Tuguldur0222/foodflow-documentation](https://github.com/Tuguldur0222/foodflow-documentation).

```bash
git clone https://github.com/Tuguldur0222/foodflow-documentation.git
cd foodflow-documentation
git switch -c docs/week-07
# Edit the actual assignment, document and evidence.
python tools/verify.py
git add docs templates review tests
git commit -m "7-р семинарын баримтжуулалтыг нэмэв"
git push -u origin docs/week-07
```

Дугаар нь жишээ; W07 агуулгыг handout ирсний дараа бичнэ. Dependency cache, нууц token, түр build output commit хийхгүй.

## Автомат шалгалт

`.github/workflows/quality.yml` нь push/PR бүрт Python тест, doc links, Sphinx doctest/HTML, Redocly lint шалгана. Log/HTML artifact хадгална. Hosted run-ийн URL-ийг [status](status.md)-д бүртгэнэ.

GitHub Pages хүсвэл **Settings → Pages → Source: GitHub Actions** сонгоод optional pages workflow-г гараар ажиллуулна. Deployment амжилттай URL л live documentation-ийн нотолгоо болно. [Official workflow заавар](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages).

W06 нь GitLab CI/Pages шаарддаг тул `.gitlab-ci.yml` тусдаа бий. GitLab project/runner/Pages/Issues бодитоор шалгасны дараа тэр DoD-г биелсэн гэж тэмдэглэнэ.

## Commit-ийн нэр

Нэг commit нэг ойлгомжтой өөрчлөлт агуулна: `1, 2-р семинарын тайланг шинэчлэв`; `Шаардлага ба архитектурын холбоосыг засав`; `API жишээ болон тест нэмэв`; `Баримтжуулалтын автомат шалгалтыг нэмэв`. `update`, `fix all`, `final final` зэрэг тодорхойгүй нэрээс зайлсхий.
