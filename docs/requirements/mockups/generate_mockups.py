"""Rebuild editable SVG acceptance mockups; these are designs, not screenshots."""
from pathlib import Path
from html import escape

OUT = Path(__file__).resolve().parent


def text(x, y, value, size=18, weight="400", color="#293241"):
    return (f'<text x="{x}" y="{y}" font-size="{size}" '
            f'font-weight="{weight}" fill="{color}">{escape(value)}</text>')


def box(x, y, w, h, fill="#ffffff", stroke="#b8c1cc", radius=8):
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{radius}" '
            f'fill="{fill}" stroke="{stroke}"/>')


def button(x, y, label, w=170):
    return box(x, y, w, 42, "#293241", "#293241") + text(x+16, y+27, label, 16, "600", "#ffffff")


def base(title, fr, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="760" height="570" viewBox="0 0 760 570" '
            f'role="img" aria-labelledby="title desc">'
            f'<title id="title">FoodFlow — {escape(title)}</title>'
            f'<desc id="desc">{escape(fr)} acceptance mock UI. Редакцийн wireframe; ажилладаг системийн screenshot биш.</desc>'
            '<g font-family="Arial, sans-serif">'
            + box(1, 1, 758, 568, "#f6f7f9", "#b8c1cc", 12)
            + box(1, 1, 758, 65, "#ffffff", "#d8dee6", 12)
            + text(30, 42, "FoodFlow", 24, "700")
            + text(520, 40, "ACCEPTANCE WIREFRAME", 13, "600", "#697586")
            + text(30, 108, title, 25, "700")
            + text(30, 138, fr + " · жишээ өгөгдөл", 15, "400", "#697586")
            + body
            + text(30, 543, "Загвар зураг · ажилладаг UI-ийн screenshot биш · 2026-10-13", 13, "400", "#697586")
            + '</g></svg>')


def save(name, title, fr, body):
    (OUT / f"{name}.svg").write_text(base(title, fr, body), encoding="utf-8")


def build():
    body = box(30, 160, 700, 44) + text(48, 188, "Хоолны нэрээр хайх…", 17, color="#697586")
    for x, name, price, detail in [(30, "Burger", "18,000 ₮", "Үхрийн мах, ногоо"),
                                  (390, "Pizza", "25,000 ₮", "Бяслаг, улаан лооль")]:
        body += box(x, 222, 340, 274) + box(x+16, 238, 308, 90, "#e5e9ee")
        body += text(x+110, 288, "ЗУРГИЙН ОРОНД", 13, color="#697586")
        body += text(x+18, 360, name, 22, "700") + text(x+18, 390, price, 18, "600")
        body += text(x+18, 420, detail, 15) + button(x+18, 438, "Сагсанд нэмэх", 190)
    save("menu", "Хоолны жагсаалт", "FR-01", body)

    body = box(30, 170, 700, 112) + text(48, 205, "Burger · ID 7", 21, "700")
    body += text(48, 236, "Нэгж үнэ: 18,000 ₮", 17)
    body += box(398, 190, 115, 48) + text(418, 221, "−   1   +", 21)
    body += text(555, 221, "18,000 ₮", 19, "600")
    body += text(48, 263, "[ Хасах ]", 15)
    body += text(30, 337, "Сагс: 1 item · quantity = 1 · badge = 1", 18)
    body += text(30, 376, "Нийт: 18,000 ₮", 23, "700") + button(30, 420, "Checkout", 190)
    save("cart", "Сагс", "FR-04 · FR-05 · FR-06", body)

    body = ""
    for y, label, value in [(170, "Дүүрэг *", "Сүхбаатар"), (244, "Хороо *", "8"),
                            (318, "Гудамж / байр *", "Жишээ гудамж, 12-р байр"),
                            (392, "Утас *", "Жишээ утасны дугаар")]:
        body += text(30, y, label, 15, "600") + box(30, y+10, 700, 42)
        body += text(46, y+38, value, 17)
    body += button(30, 468, "Хадгалах", 190)
    save("address", "Хүргэлтийн хаяг", "FR-08", body)

    body = text(30, 176, "Зөвхөн нэг аргыг сонгоно", 17)
    for y, label, selected in [(202, "QPay", True), (282, "Bank card", False), (362, "Cash on delivery", False)]:
        body += box(30, y, 700, 62, "#edf1f5" if selected else "#ffffff")
        body += f'<circle cx="60" cy="{y+31}" r="11" fill="white" stroke="#293241"/>'
        if selected:
            body += f'<circle cx="60" cy="{y+31}" r="5" fill="#293241"/>'
        body += text(86, y+38, label, 20, "600")
    body += button(30, 458, "Үргэлжлүүлэх", 190)
    save("payment", "Төлбөрийн арга", "FR-10", body)

    body = box(30, 170, 330, 330) + text(48, 204, "Захиалгын хураангуй", 20, "700")
    for y, value in [(244, "Burger × 2: 36,000 ₮"), (280, "Delivery fee: 3,000 ₮"),
                     (316, "Discount: 2,000 ₮"), (365, "Total: 37,000 ₮")]:
        body += text(48, y, value, 17, "600" if y==365 else "400")
    body += button(48, 416, "Place Order", 210)
    body += box(384, 170, 346, 330, "#edf1f5") + text(404, 204, "Амжилтын баталгаа", 20, "700")
    for y, value in [(248, "Order ID: FF-1024"), (291, "Total: 37,000 ₮"),
                     (334, "Estimated delivery: 30–45 min")]:
        body += text(404, y, value, 16)
    body += text(404, 392, "Зөвхөн order үүссэний дараа", 15)
    body += text(404, 418, "ETA нь тооцоолсон хугацаа.", 15)
    save("summary", "Checkout → Confirmation", "FR-07 · FR-11 · FR-15", body)

    body = box(30, 170, 700, 300) + text(48, 207, "Order FF-1024 · өөрийн захиалга", 21, "700")
    for y, value, active in [(251, "Pending", False), (290, "Confirmed", False),
                             (329, "Preparing — одоогийн төлөв", True),
                             (368, "Out for delivery", False), (407, "Delivered", False)]:
        body += f'<circle cx="60" cy="{y-6}" r="7" fill="{"#293241" if active else "#ffffff"}" stroke="#293241"/>'
        body += text(82, y, value, 18, "700" if active else "400")
    body += text(30, 505, "Өөр хэрэглэгчийн order → 403 / 404; мэдээлэл харагдахгүй", 16)
    save("status", "Захиалгын төлөв", "FR-12", body)

    body = text(30, 178, "Өөрийн захиалгууд · хамгийн сүүлийнх эхэнд", 17)
    for y, order, date, price, status in [(204, "FF-1024", "2026-10-12", "37,000 ₮", "Preparing"),
                                        (296, "FF-1019", "2026-10-10", "32,000 ₮", "Delivered"),
                                        (388, "FF-1007", "2026-10-08", "25,000 ₮", "Cancelled")]:
        body += box(30, y, 700, 78) + text(48, y+30, order, 20, "700")
        body += text(48, y+58, date, 16, color="#697586")
        body += text(300, y+44, price, 18, "600") + text(540, y+44, status, 17)
    save("history", "Захиалгын түүх", "FR-14", body)


if __name__ == "__main__":
    build()
    print("Generated 7 editable SVG mockups.")
