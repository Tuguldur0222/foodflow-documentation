# W06 — Кодын баримтжуулалт ба AI аудит

**Төсөл:** FoodFlow · **Оюутан:** Ю. Төгөлдөр, 23B1NUM2350 · **Шинэчилсэн:** 2026-10-13

## Зорилго ба хамрах хүрээ

Энэхүү семинарын ажлын зорилго нь FoodFlow-ийн public API-г Google-style docstring ашиглан баримтжуулах, Sphinx-ээр алдаа, анхааруулгагүй HTML баримтжуулалт үүсгэх, AI-ийн боловсруулсан тайлбарыг кодын бодит ажиллагаатай тулган үнэлэх, техникийн өрийг бүртгэхэд оршино. Баримтжуулалт нь API ашиглах хөгжүүлэгчдэд зориулагдсан бөгөөд захиалга үүсгэх, өөрийн захиалгын мэдээллийг авах, `Pending` төлөвтэй захиалгыг цуцлах үйлдэл бүхий Python модулийг хамарна.

Кодыг анх PDF-ийн тайлбараас сургалтын зориулалтаар сэргээн байгуулсан. Одоо хэрэглэгчийн нэмсэн Word баримттай уялдуулсан. Энэ модуль нь W05 HTTP mock-оос тусдаа; database, JWT, бодит QPay төлбөр, key TTL, concurrency баталгаа агуулахгүй.

## US-6.1 — Public API ба docstring

[`order_service.py`](../../foodflow/order_service.py)-д module, class, constructor, гурван public method буюу 6 хэсгийг тайлбарласан. `foodflow.__all__` зөвхөн `OrderService`-ийг export хийнэ. Public callable constructor-тайгаа 4. Private state/helper-ийг хассан шалтгаан comment-той.

| Callable | Гэрээ | Алдаа |
|---|---|---|
| `OrderService()` | Шинэ хоосон instance; эхний ID FF-1024 | Application-level exception байхгүй |
| `place_order(...)` | Pending; ижил owner/key + payload → одоогийн snapshot | ValueError: input/key conflict |
| `get_order(id, owner)` | Өөрийн order-ийн independent copy | ValueError, KeyError, PermissionError |
| `cancel_order(id, owner)` | Pending → Cancelled; refund үгүй | Lookup errors; Pending биш үед ValueError |

Жишээ бүр import болон шинэ instance-оос эхэлнэ. Домэйн утга customer_101, cart_101, FF-1024, QPay; integer MNT үнэ хэрэглэнэ.

```python
from foodflow import OrderService

service = OrderService()
order = service.place_order(
    'customer_101', 'cart_101', 18000, 3000,
    'QPay', 'ff-order-1024',
)
assert order['total_mnt'] == 21000
assert service.cancel_order(order['order_id'], 'customer_101')['status'] == 'Cancelled'
```

Нэг хоол: 18,000 + 3,000 = 21,000₮. W05 хоёр хоол: 36,000 + 3,000 = 39,000₮. W06 subtotal-ийг оролтоор авдаг тул сагсны серверийн үнийн тооцоог шалгасан гэж үзэхгүй.

Chinchilla чанарын практик checklist: уншигчид чиглэх; оролт/гаралт/алдааг бүрэн тайлбарлах; ижил domain schema; runnable example; API навигац; кодтой хамт шинэчлэгдэх build. Бүтэн ном ирээгүй тул үүнийг номын зургаан зарчмын үгчилсэн нэр гэж эшлээгүй.

## Одоогийн SRS-тэй холбоо

| Шаардлага | W06-д хамрах хэсэг | Хязгаар |
|---|---|---|
| FR-11, NFR-02 | Order үүсгэх, single-instance retry | Database/24hTTL/concurrency үгүй |
| FR-10 | QPay аргыг хадгалах | Provider холболтгүй |
| FR-12, NFR-03 | Trusted owner-ийн order | JWT/role authentication тест биш |
| FR-13 | Pending цуцлах | SRS-ийн Confirmed цуцлалтыг хэрэгжүүлээгүй |
| FR-15 | Order ID, нийт дүн | UI success message/ETA үгүй |

W03-ийн одоогийн Word эх FR-11=order, FR-10=payment, FR-13=Pending/Confirmed гэж заасан. Хуучин PDF-ийг дагасан 2026-10-12 тайлангийн холбоосыг шинэчилж, түүхийг [CHANGELOG](../../CHANGELOG.md)-д хадгалав.

## US-6.2 — Sphinx ба CI/CD

Autodoc Python docstring-ийг, Napoleon Google-style бүтцийг, MyST бусад семинарын Markdown-ийг нэг баримтжуулалтад оруулна. Mermaid диаграм GitHub/HTML дээр харагдана.

```bash
python tools/prepare_docs.py
python -m sphinx -c docs -n -W --keep-going -b doctest . build/doctest
python -m sphinx -c docs -n -W --keep-going -b html . public
```

`-n` unresolved reference шалгана; `-W` warning-ийг build failure болгоно. [GitHub CI](../../.github/workflows/quality.yml), [GitLab тохируулга](../../.gitlab-ci.yml)-г тусад нь хадгалсан. GitHub repository, GitHub Pages, GitLab Pages-ийг нэг нотолгоо гэж үзэхгүй. Локал үр дүн [verification.json](../../review/verification.json), hosted үр дүн [status](../project/status.md)-д байна.

## US-6.3, UE-6 — Manual vs. AI аудит

| Үе шат | Artifact | Нотолгооны хүрээ |
|---|---|---|
| (a) Baseline | [manual_docstring.py](../../review/manual_docstring.py) | Codex corrected snapshot; independent human authoring батлаагүй |
| (b) Candidate/audit | [candidate](../../review/ai_candidate_docstring.py), [diff](../../review/manual_vs_ai.diff), [Bhatti matrix](../../review/bhatti_audit_table.md) | Seeded negative fixture; GPT-4/Claude raw output биш |
| (c) Integration | [Autodoc](../source/api.rst), [build log](../../review/sphinx_html_log.txt) | Нийтлэгдэх docstring-ийг code-оос үүсгэнэ |
| (d) Reflection | [Тест](../../tests/test_ai_hallucinations.py) | Байхгүй method/type; ижил executable AST |

Use–Verify–Cite: байхгүй refund_order/RefundReceipt; өөр payload-тай key replay; Delivered цуцлалт; owner шалгахгүй; хэрэгжээгүй TTL гэсэн мэдэгдлүүдийг code/test-тэй тулгасан. Хоёроос олон засвар нь бодит exception, Pending хил, trusted identity, instance lifetime-ийг сэргээсэн.

Explained, Concise, Clear, Usable, Trustworthy гэсэн таван зарчмыг [audit matrix](../../review/bhatti_audit_table.md)-д хэрэглэв. Зориудын алдааг model hallucination гэж тайлагнахгүй. Нэрлэсэн GPT-4/Claude prompt/output, human review үлдсэн; [provenance](../../review/provenance.md)-д дараалал бий.

## US-6.4 — Техникийн өр

[`check_docs.py`](../../tools/check_docs.py) public section/parameter, inline TODO/FIXME-ийг шалгана. Durable order/idempotency, state policy-ийн ажил [debt register](../../review/technical_debt.md)-д байна. GitHub issue-г GitLab issue гэж тооцохгүй; хуурамч ID үүсгэхгүй.

## DoD ба эргэцүүлэл

Docstring, runnable example, reflection, strict build-ийг локал нотолгоогоор шалгана. Hosted pipeline, public GitLab Pages, нэрлэсэн model audit, human review нь тусдаа нотолгоо шаардана. [Нэгдсэн DoD](../project/status.md)-д ялгасан.

**Standup:** Public class 1, callable 4; build exit code log-д бий; fixture-ийн ghost method/type, зан үйлийн зөрүүг шалгасан.

**Retrospective:** Google-style бүтэц оролт/буцаалт/алдааг тогтвортой уншуулахад тустай. Python болон Sphinx doctest-ийг хоёуланг ажиллуулах нь import context-ийн далд нөхцөлийг ил гаргадаг. Дараагийн семинарт model provenance, requirement version, human review-г эхнээс нь бүртгэнэ.

**Reflection:** Trustworthy шалгалтад өнгө аяс бус code/test/source чухал. Ижил domain example, docs-as-code gate-ийг цааш хэрэглэнэ. Ideal workflow, локал prototype, hosted deployment-ийн ялгааг нуухгүй. Эргэцүүллийг оюутан эцэслэн хянана.

**Эх сурвалж:** Sprint 06 handout, агуулгатай х.1–2; Week_06_FoodFlow тайлан; [Sphinx autodoc](https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html), [build options](https://www.sphinx-doc.org/en/master/man/sphinx-build.html), [GitLab Pages](https://docs.gitlab.com/user/project/pages/introduction/).
