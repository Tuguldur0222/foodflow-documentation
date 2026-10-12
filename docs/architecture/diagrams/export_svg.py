"""Rebuild editable C4 overview vectors from the documented target topology.

Mermaid sources remain the canonical diagram-as-code. This small dependency-free
export uses a fixed, reviewable SVG layout for offline Word/PDF use.
"""
from html import escape
from pathlib import Path

OUT = Path(__file__).resolve().parent


def label(x, y, lines, size=17, color="#25334a", anchor="middle", weight="400"):
    return ''.join(f'<text x="{x}" y="{y+i*(size+6)}" text-anchor="{anchor}" '
                   f'font-size="{size}" font-weight="{weight}" fill="{color}">{escape(line)}</text>'
                   for i, line in enumerate(lines))


def node(x, y, w, h, lines, kind="internal"):
    colors = {"internal": ("#e7f3ee", "#39836a"),
              "person": ("#e8eef7", "#607898"),
              "external": ("#f1f2f4", "#7b8796"),
              "flawed": ("#fff0e7", "#c76b36")}
    fill, stroke = colors[kind]
    parts = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="14" '
             f'fill="{fill}" stroke="{stroke}" stroke-width="2"/>']
    for i, line in enumerate(lines):
        parts.append(label(x+w/2, y+34+i*29, [line], 20 if i==0 else 16,
                           weight="700" if i==0 else "400"))
    return ''.join(parts)


def boundary(x, y, w, h):
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="20" '
            f'fill="#fbfdfc" stroke="#39836a" stroke-width="2" stroke-dasharray="9 6"/>'
            + label(x+24, y+32, ["FoodFlow system boundary · Proposed"], 18,
                    anchor="start", weight="700"))


def edge(points, x, y, lines, anchor="middle", dashed=False):
    coords=' '.join(f'{px},{py}' for px,py in points)
    dash='stroke-dasharray="6 5"' if dashed else ''
    return (f'<polyline points="{coords}" fill="none" stroke="#526983" '
            f'stroke-width="2" marker-end="url(#arrow)" {dash}/>'
            + label(x, y, lines, 15, "#3d5069", anchor))


def svg(name, title, width, height, body):
    doc=(f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
         f'viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">'
         f'<title id="title">{escape(title)}</title>'
         '<desc id="desc">FoodFlow proposed target architecture. Editable vector; deployed system-ийн нотолгоо биш.</desc>'
         '<defs><marker id="arrow" markerWidth="9" markerHeight="7" refX="8" refY="3.5" orient="auto">'
         '<path d="M0,0 L9,3.5 L0,7 Z" fill="#526983"/></marker></defs>'
         f'<rect width="{width}" height="{height}" fill="white"/>'
         '<g font-family="Arial, sans-serif">'
         + label(40, 45, [title], 28, anchor="start", weight="700")
         + label(40, 75, ["Proposed · 2026-10-13 · Person / Container / External System · labelled data flows"],
                 16, "#697586", "start")
         + body
         + label(40, height-32, ["Ногоон: FoodFlow · Цэнхэр: Person · Саарал: External System · Mermaid эхтэй хамт шинэчилнэ"],
                 16, "#697586", "start")
         + '</g></svg>')
    (OUT/name).write_text(doc, encoding="utf-8")


def context():
    body=boundary(560, 280, 480, 370)
    body+=node(610, 385, 380, 170, ["FoodFlow", "Software System", "Хоол захиалга ба өөрийн төлөв"])
    actors=[(130, "Саруул / Customer", "Хоол захиалагч", "Хоол / checkout / өөрийн төлөв"),
            (330, "Restaurant Staff", "Захиалга боловсруулагч", "Захиалга / төлөв шинэчлэх"),
            (530, "Courier", "Хүргэлтийн ажилтан", "Хүргэлтийн явц шинэчлэх"),
            (730, "Номин / Support", "Тусламжийн ажилтан", "Эрхийн хүрээтэй lookup")]
    for i,(y,title,role,flow) in enumerate(actors):
        body+=node(35,y,300,122,[title,"Person",role],"person")
        target=405+i*40
        body+=edge([(335,y+61),(475,y+61),(475,target),(610,target)],460,y+39,[flow,"HTTPS"],"middle")
    body+=node(1240,250,330,135,["Payment Provider","External Software System","Төлбөр боловсруулна"],"external")
    body+=node(1240,650,330,135,["Notification Provider","External Software System","Мэдэгдэл хүргэнэ"],"external")
    body+=edge([(990,415),(1130,415),(1130,285),(1240,285)],1120,220,["Payment request / reference","HTTPS JSON"])
    body+=edge([(1240,350),(1185,350),(1185,460),(990,460)],1130,485,["Баталгаажсан result","Webhook HTTPS"])
    body+=edge([(990,510),(1100,510),(1100,680),(1240,680)],1110,600,["Event / destination","HTTPS"])
    body+=edge([(1240,750),(1160,750),(1160,545),(990,545)],1170,815,["Delivery result","HTTPS"])
    svg("context.svg","FoodFlow · C4 System Context",1620,960,body)


def container(name="container.svg",title="FoodFlow · C4 Container — 5 containers"):
    body=boundary(360,110,1080,1010)
    body+=node(430,205,320,165,["Web App","Container · React / TypeScript","Menu / Cart / Checkout","Status / History UI"])
    body+=node(955,205,380,165,["API","Container · Python / FastAPI","Auth / price / orders","State rules"])
    body+=node(955,520,380,165,["Worker","Container · Python","Notification job / retry","Outbox dispatch"])
    body+=node(430,865,350,170,["PostgreSQL","Container · relational datastore","Durable order / owner","Key result / outbox"])
    body+=node(955,865,380,170,["Redis","Container · queue / cache","Job dispatch / key lookup","Order source of truth биш"])
    actors=[(160,"Customer","Захиалга / өөрийн төлөв"),(390,"Restaurant Staff","Эрхтэй order UI · proposed"),
            (620,"Courier","Delivery UI · proposed"),(850,"Support / Номин","Lookup UI · proposed")]
    for i,(y,actor_title,role) in enumerate(actors):
        body+=node(25,y,260,120,[actor_title,"Person",role],"person")
        end_y=225+i*38
        body+=edge([(285,y+60),(330,y+60),(330,end_y),(430,end_y)],310,y+42,["Browser UI"],"middle")
    body+=edge([(750,285),(955,285)],850,245,["Token / request / response","HTTPS JSON"])
    body+=edge([(1040,370),(1040,435),(600,435),(600,865)],755,465,["Catalog / cart / order","Key transaction · SQL"])
    body+=edge([(1305,370),(1385,370),(1385,935),(1335,935)],1375,775,["Key lookup cache","Job dispatch","Redis protocol"],"end")
    body+=edge([(1145,685),(1145,865)],1145,765,["Job авах / ack","Redis protocol"])
    body+=edge([(955,602),(825,602),(825,950),(780,950)],820,715,["Outbox / result","SQL"],"end")
    body+=node(1520,205,350,165,["Payment Provider","External Software System","Төлбөр боловсруулна"],"external")
    body+=node(1520,520,350,165,["Notification Provider","External Software System","Мэдэгдэл хүргэнэ"],"external")
    body+=edge([(1335,255),(1520,255)],1435,210,["Payment request","HTTPS JSON"])
    body+=edge([(1520,325),(1335,325)],1430,355,["Signed result","Webhook HTTPS"])
    body+=edge([(1335,602),(1520,602)],1430,555,["Notification / result","HTTPS"])
    svg(name,title,1920,1200,body)


def before():
    body=boundary(410,170,610,420)
    body+=node(35,300,300,130,["Customer","Person","Хоол захиалагч"],"person")
    body+=node(460,290,510,190,["Magic Container","Технологи тодорхойгүй","UI / API / DB / payment","Notification / retry бүгд"],"flawed")
    body+=node(1120,300,340,130,["External providers","System boundary бүдэг","Payment / notification"],"external")
    body+=edge([(335,365),(460,365)],390,280,["Ерөнхий хэрэглээ","Агуулга бүдэг"])
    body+=edge([(970,365),(1120,365)],1045,280,["Integration","Protocol бүдэг"])
    svg("ue4-before.svg","UE-4 · BEFORE — Magic Container anti-pattern",1520,720,body)


if __name__ == "__main__":
    context()
    container()
    before()
    container("ue4-after.svg","UE-4 · AFTER — Clear container responsibilities")
    print("Generated 4 editable architecture SVG exports.")
