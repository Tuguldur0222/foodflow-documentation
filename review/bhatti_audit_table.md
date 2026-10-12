# Bhatti audit — сэргээсэн сургалтын fixture

Бодит GPT-4/Claude туршилт болон хүний бие даасан аудит хараахан байхгүй.
Доорх нь зориуд буруу fixture-г кодтой тулгасан Codex-ийн үнэлгээ; 1–5 оноо
нь энэ ажлын rubric болохоос номын албан ёсны оноолт биш.

| Зарчим | Fixture → зассан | Нотолгоо ба засвар |
|---|---|---|
| Explained | 2 → 5 | Owner, in-memory хил, cancellation state, key scope-ийг тайлбарлав. |
| Concise | 3 → 4 | Байхгүй refund амлалтыг хасав; алдаа ба жишээг үлдээв. |
| Clear | 2 → 5 | Pending → Cancelled, MNT, параметрийн нэрийг нэг мөр болгосон. |
| Usable | 1 → 5 | Бүх public callable-д runnable doctest, Args/Returns; constructor-ийн exception байхгүйг prose-р тэмдэглэсэн. |
| Trustworthy | 1 → 4 | Reflection, behavior tests, strict Sphinx-ээр тулгасан; хараат бус хүний аудит хүлээгдэнэ. |

## Use–Verify–Cite

| Use: fixture claim | Verify | Cite | Засвар |
|---|---|---|---|
| OrderService.refund_order / RefundReceipt байдаг | Reflection хоёуланг missing гэж олно | tests/test_ai_hallucinations.py | Байхгүй API/type-г хасав. |
| Ижил key + өөр payload шинэ order үүсгэнэ | test_changed_payload_conflicts → ValueError | OrderService.place_order | Conflict гэж тайлбарлав. |
| Delivered/Confirmed order цуцална | Code зөвхөн Pending-г зөвшөөрнө; repeat cancellation test | OrderService.cancel_order | Pending → Cancelled, refund үгүй. |
| Owner шалгахгүй | 100 foreign-owner lookup + cancellation rejection | tests/test_order_service.py | trusted owner, PermissionError нэмэв. |
| Key 24 цагийн дараа дуусна | Clock/expiry branch байхгүй | OrderService.__init__, place_order | Instance lifetime; TTL хэрэгжээгүй гэж засав. |

Дор хаяж хоёр бодит текстийн засвар хийгдсэн. Гэхдээ handout-ийн
“manual vs. GPT-4/Claude” бүрэн шалгуурийг энэ fixture-ээр хангасан гэж тооцохгүй.
