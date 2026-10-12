# Захиалга ба idempotency өгөгдлийг найдвартай хадгалах

**Төлөв:** нээлттэй [GitHub issue #1](https://github.com/Tuguldur0222/foodflow-documentation/issues/1). **Холбоо:** FR-11, NFR-02, [ADR-002](../../architecture/adr/0002-persistence-and-idempotency.md).

W06-ийн `OrderService` захиалга болон idempotency түлхүүрийг санах ойд хадгалдаг. Процесс дахин эхлэхэд өгөгдөл алдагдана; 24 цагийн TTL болон зэрэгцээ хүсэлтийн баталгаа хэрэгжээгүй. W05 mock-ийн TTL/lock нь production хадгалалтын нотолгоо биш.

ADR-002-ын саналын дагуу PostgreSQL transaction, `(owner_id, idempotency_key)` unique constraint, request hash болон хадгалсан хариуг хэрэгжүүлнэ. Ижил түлхүүр, ижил payload-д өмнөх хариуг өгч, өөр payload-д 409 буцаана. Түлхүүрийн 24 цагийн хугацаа, төлбөрийн event-ийн consistency-г хамт шалгана.

Хүлээн авах шалгуур:

- Restart-ийн дараа захиалга болон хугацаа дуусаагүй түлхүүр хадгалагдана.
- Нэг хэрэглэгчийн ижил түлхүүртэй 100 зэрэгцээ хүсэлт яг нэг захиалга үүсгэнэ.
- Өөр хэрэглэгчийн түлхүүр тусгаарлагдана; өөр payload-тай давтан хүсэлт 409 болно.
- Migration, rollback болон integration test-ийн нотолгоог хавсаргана.

Шийдвэрийг батлахаас өмнө ADR Proposed хэвээр байна. Ахиц, review болон шалгалтын нотолгоог issue-д бүртгэнэ.
