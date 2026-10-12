# Acceptance mock UI

Эдгээр нь SRS-ийн харагдах үр дүнг тайлбарлах **редакцийн wireframe**. Хэрэглэгчийн шинэ W03 материал дахь mock UI-ийн шаардлагад нийцүүлэн дахин байгуулсан; эх DOCX-ийн зургийг шууд хуулсан эсвэл ажилладаг системийн screenshot гэж мэдүүлээгүй. SVG файл бүр текст/shape-аар засварлагдана.

| Mock | Requirement | Шалгах зүйл |
| --- | --- | --- |
| Menu | FR-01 | Нэр, үнэ, зураг, товч тайлбар |
| Cart | FR-04 / FR-05 / FR-06 | Item ID, quantity, badge, subtotal, remove |
| Address | FR-08 | Дөрвөн required талбар |
| Payment | FR-10 | Дэмжих гурван аргаас нэг сонголт |
| Summary / Confirmation | FR-07 / FR-11 / FR-15 | Үнэ; Place Order; order_id, total, ETA |
| Status | FR-12 | Өөрийн order-ийн одоогийн төлөв |
| History | FR-14 | Зөвхөн өөрийн order; newest-first |

## Menu — FR-01

![Menu: нэр, үнэ, зураг, тайлбар бүхий хоёр хоолны wireframe](menu.svg)

## Cart — FR-04 / FR-05 / FR-06

![Cart: ID7 Burger quantity1, badge1, subtotal18000 төгрөг](cart.svg)

## Address — FR-08

![Address: дүүрэг, хороо, гудамж/байр, утас гэсэн дөрвөн required талбар](address.svg)

## Payment — FR-10

![Payment: QPay, Bank card, Cash on delivery сонголт](payment.svg)

## Summary ба Confirmation — FR-07 / FR-11 / FR-15

![Checkout summary total37000 төгрөг ба амжилтын order_id, total, estimated delivery мэдээлэл](summary.svg)

## Status — FR-12

![Өөрийн захиалга Preparing төлөвтэй; өөр хүний захиалгын мэдээлэл харуулахгүй](status.svg)

## History — FR-14

![Өөрийн гурван захиалга хамгийн сүүлийн огнооноос эхэлсэн дараалалтай](history.svg)

Дахин үүсгэх: `python docs/requirements/mockups/generate_mockups.py`. Жишээ үнэ, order ID, хугацаа нь fixture; бодит хэрэглэгчийн өгөгдөл биш. Mock-ийн гоо зүй нь acceptance test-ийн орлуулга биш; шалгах алхам, Pass/Fail нь [SRS](../srs.md)-д байна.
