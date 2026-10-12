# Техникийн өрийн бүртгэл

`python tools/check_docs.py` scans Python files under foodflow/ and tests/
for inline TODO/FIXME comments and verifies public-callable doc structure.
No historical source was supplied, so this result covers only reconstructed code.

Тэргүүлэх хоёр ажил:

| Ажил | Одоогийн зөрүү | Бэлэн даалгавар |
|---|---|---|
| Найдвартай хадгалалт, idempotency | W06 нь санах ойд хадгалдаг; restart, TTL, зэрэгцээ хүсэлтийн баталгаа байхгүй | [Хадгалалтын даалгавар](../docs/project/issues/durable-orders.md) |
| Confirmed захиалгыг цуцлах | Шинэ Week_03_FoodFlow.docx шаарддаг; W06 зөвхөн Pending дэмждэг | [Цуцлалтын даалгавар](../docs/project/issues/confirmed-cancellation.md) |

2026-10-13-нд эхний GitHub integration оролдлого `403` хариу өгсөн. Хэрэглэгч GitHub CLI нэвтрэлтийг баталгаажуулсны дараа [issue #1](https://github.com/Tuguldur0222/foodflow-documentation/issues/1), [issue #2](https://github.com/Tuguldur0222/foodflow-documentation/issues/2)-ыг бодитоор үүсгэв. GitLab дээр issue үүсгээгүй. HTTP/JWT холболт, сагснаас сервер талд үнэ тооцох, хүргэлтийн хаяг шалгах, төлбөрийн үйлчилгээтэй холбох ажил дараагийн хэрэгжилтэд үлдэнэ.

Once a real issue is created, any necessary inline marker must use its real
ID, for example `# TODO(#<real-ID>): ...`. No fictional numeric ID is used.
