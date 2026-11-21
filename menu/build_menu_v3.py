from PIL import Image
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor, white
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import ImageReader
import os

F = "/usr/share/fonts/truetype/google-fonts/"
pdfmetrics.registerFont(TTFont("P", F + "Poppins-Regular.ttf"))
pdfmetrics.registerFont(TTFont("PM", F + "Poppins-Medium.ttf"))
pdfmetrics.registerFont(TTFont("PB", F + "Poppins-Bold.ttf"))
pdfmetrics.registerFont(TTFont("PI", F + "Poppins-Italic.ttf"))

CREAM = HexColor("#FBF6EC")
GREEN = HexColor("#1F4D36")
LEAF = HexColor("#5FA04E")
ORANGE = HexColor("#E8772E")
INK = HexColor("#2A2A2A")
GREY = HexColor("#6B6B6B")
LINE = HexColor("#E6DDCB")

W, H = letter
M = 36


def crop(src, ratio, out):
    im = Image.open(src).convert("RGB")
    w, h = im.size
    if w / h > ratio:
        nw = int(h * ratio)
        im = im.crop(((w - nw) // 2, 0, (w - nw) // 2 + nw, h))
    else:
        nh = int(w / ratio)
        im = im.crop((0, (h - nh) // 2, w, (h - nh) // 2 + nh))
    im.save(out, "JPEG", quality=88)
    return out


def rrect_img(c, path, x, y, w, h, r=10):
    c.saveState()
    p = c.beginPath()
    p.roundRect(x, y, w, h, r)
    c.clipPath(p, stroke=0, fill=0)
    c.drawImage(ImageReader(path), x, y, w, h)
    c.restoreState()


def pill(c, x, y, text, bg, fg=white, size=7.5, font="PB", pad=6, h=15):
    tw = pdfmetrics.stringWidth(text, font, size)
    c.setFillColor(bg)
    c.roundRect(x, y, tw + pad * 2, h, h / 2, stroke=0, fill=1)
    c.setFillColor(fg)
    c.setFont(font, size)
    c.drawString(x + pad, y + (h - size) / 2 + 1.2, text)
    return tw + pad * 2


def wrap(text, font, size, width):
    words, lines, cur = text.split(), [], ""
    for wd in words:
        t = (cur + " " + wd).strip()
        if pdfmetrics.stringWidth(t, font, size) <= width:
            cur = t
        else:
            lines.append(cur)
            cur = wd
    if cur:
        lines.append(cur)
    return lines


def background(c):
    c.setFillColor(CREAM)
    c.rect(0, 0, W, H, stroke=0, fill=1)


def footer(c, page):
    c.setFillColor(GREEN)
    c.rect(0, 0, W, 30, stroke=0, fill=1)
    c.setFillColor(white)
    c.setFont("PM", 8.5)
    c.drawCentredString(W / 2, 11, "Cooked fresh today  •  Never frozen  •  Delivered today  •  Sacramento local")
    c.setFont("P", 7)
    c.drawRightString(W - M, 11, f"{page}/2")


os.makedirs("img/c", exist_ok=True)
bowls = [
    ("chicken", "Chicken Bacon Ranch", "$70",
     "Baked potato, grilled chicken (6 oz), broccoli, cheddar, crispy bacon, butter, ranch drizzle, green onion.",
     "955 cal • 75g protein", "#1 BEST SELLER"),
    ("steak", "Steakhouse Loaded", "$90",
     "Baked potato, seared steak (6 oz), mushrooms, garlic, bacon, cheddar, butter, sour cream drizzle, chives.",
     "900 cal • 72g protein", "FAN FAVORITE"),
    ("bbq", "BBQ Chicken Stack", "$65",
     "Baked potato, pulled chicken (6 oz), smoky BBQ sauce, cheddar, butter, sour cream, pickled red onion, green onion.",
     "915 cal • 57g protein", None),
    ("pork", "Pulled Pork & Crispy Onion", "$65",
     "Baked potato, pulled pork (6 oz), BBQ sauce, cheddar, butter, ranch drizzle, crispy fried onions, green onion.",
     "1,075 cal • 59g protein", None),
    ("sweet", "Garden Sweet Potato", "$55",
     "Roasted sweet potato, black beans, spinach, onions, mushrooms, cheese, butter, sour cream drizzle.",
     "685 cal • 24g protein", "VEGETARIAN"),
]
breakfast = [
    ("country", "Country Breakfast", "$65",
     "Baked potato, breakfast sausage, peppery sausage gravy, 2 boiled eggs, bacon, butter, green onion.",
     "1,090 cal • 47g protein", "BREAKFAST"),
    ("supreme", "Breakfast Supreme", "$65",
     "Baked potato, Mexican chorizo, black beans, 2 boiled eggs, cheese, butter, sour cream & hot sauce drizzle.",
     "1,140 cal • 54g protein", "BREAKFAST"),
    ("classic", "Classic Loaded", "$50",
     "Baked potato, butter, cheddar, crispy bacon, sour cream drizzle, chives.",
     "630 cal • 21g protein", None),
]

def draw_cards(c, items, y, card_h=104, gap=8):
    imw, imh = 168, card_h - 16
    for key, name, price, desc, prot, tag in items:
        top = y; bot = top - card_h
        c.setFillColor(white); c.setStrokeColor(LINE)
        c.roundRect(M, bot, W - 2 * M, card_h, 12, stroke=1, fill=1)
        p = crop(f"img/{key}.png", imw / imh, f"img/c/{key}.jpg")
        rrect_img(c, p, M + 8, bot + 8, imw, imh, 9)
        tx = M + 8 + imw + 16; tw = W - M - 16 - tx
        if tag:
            col = ORANGE if "BEST" in tag else (LEAF if tag == "VEGETARIAN" else (HexColor("#8a5a2b") if tag == "BREAKFAST" else GREEN))
            pill(c, tx, top - 26, tag, col); ny = top - 45
        else:
            ny = top - 30
        c.setFillColor(INK); c.setFont("PB", 15); c.drawString(tx, ny, name)
        c.setFillColor(ORANGE); c.setFont("PB", 17); c.drawRightString(W - M - 16, ny, price)
        c.setFillColor(GREY); c.setFont("P", 8.8); ly = ny - 15
        for ln in wrap(desc, "P", 8.8, tw):
            c.drawString(tx, ly, ln); ly -= 12
        pill(c, tx, bot + 10, prot, HexColor("#E7F1E2"), GREEN, 7.5, "PB")
        y = bot - gap
    return y

c = canvas.Canvas("Colossal_Potato_Menu.pdf", pagesize=letter)
c.setTitle("Colossal Potato - Menu")

# ---------------- PAGE 1 ----------------
background(c)
# header band
c.setFillColor(GREEN)
c.rect(0, H - 118, W, 118, stroke=0, fill=1)
c.drawImage("img/logo_round.png", M, H - 106, 88, 88, mask="auto")
LX = M + 100
c.setFillColor(white)
c.setFont("PB", 27)
c.drawString(LX, H - 58, "COLOSSAL")
fw = pdfmetrics.stringWidth("COLOSSAL ", "PB", 27)
c.setFillColor(ORANGE)
c.drawString(LX + fw, H - 58, "POTATO")
c.setFillColor(white)
c.setFont("PM", 10.5)
c.drawString(LX, H - 78, "High-protein loaded potato meal prep  •  5-packs")
c.setFont("PI", 9)
c.setFillColor(HexColor("#CFE3C9"))
c.drawString(LX, H - 94, "Fresh, never frozen  •  colossalpotato.com")
# right badge
bx, by = W - M - 110, H - 96
c.setFillColor(ORANGE)
c.roundRect(bx, by, 110, 58, 10, stroke=0, fill=1)
c.setFillColor(white)
c.setFont("PB", 13)
c.drawCentredString(bx + 55, by + 36, "SAME-DAY")
c.drawCentredString(bx + 55, by + 20, "DELIVERY")
c.setFont("P", 7.5)
c.drawCentredString(bx + 55, by + 7, "One fee per order")

# section title
y = H - 146
c.setFillColor(GREEN)
c.setFont("PB", 15)
c.drawString(M, y, "SIGNATURE BOWLS")
c.setFillColor(GREY)
c.setFont("P", 8.5)
c.drawRightString(W - M, y + 1, "Prices per 5-pack (5 of the same bowl)")
c.setStrokeColor(LINE)
c.setLineWidth(1)
c.line(M, y - 8, W - M, y - 8)

y = draw_cards(c, bowls, y - 18)

# double protein strip
c.setFillColor(GREEN)
c.setFont("PB", 9.5)
c.drawCentredString(W / 2, 44, "Extra 4 oz meat: chicken +$20 / steak +$30 per 5-pack   •   Sauce drizzled or on the side — free")
footer(c, 1)
c.showPage()

# ---------------- PAGE 2 ----------------
background(c)
c.setFillColor(GREEN)
c.rect(0, H - 70, W, 70, stroke=0, fill=1)
c.setFillColor(white)
c.setFont("PB", 22)
c.drawString(M, H - 44, "BREAKFAST & CLASSIC")
c.setFillColor(HexColor("#CFE3C9"))
c.setFont("P", 9)
c.drawRightString(W - M, H - 44, "Prices per 5-pack")
yb2 = draw_cards(c, breakfast, H - 90)
sy = yb2 + 8
box_h = 0
# add-ons row
ay = sy - 22
c.setFillColor(GREEN)
c.setFont("PB", 10)
c.drawString(M, ay, "ADD-ONS / PACK")
xx = M + 100
for t in ["+4 oz Chicken $20", "+4 oz Steak $30", "Bacon $10", "Cheese $5", "Sour cream $5", "Crispy onions $5", "Mushrooms $5", "LOW-CARB cauliflower base $5"]:
    w_ = pdfmetrics.stringWidth(t, "PM", 7.6) + 12
    if xx + w_ > W - M: xx = M + 100; ay -= 20
    xx += pill(c, xx, ay - 4, t, HexColor("#FCE6D6"), HexColor("#A14E14"), 7.6, "PM") + 6

# mix & match + fit packs
py = ay - 22
c.setStrokeColor(LINE)
c.line(M, py, W - M, py)
py -= 22
c.setFillColor(GREEN)
c.setFont("PB", 15)
c.drawString(M, py, "ORDER IN 5-PACKS — 5 OF THE SAME BOWL")
packs = [("5 BOWLS", "1 pack", "Mon–Fri lunches"), ("10 BOWLS", "2 packs", "Mix 2 bowl types"), ("15 BOWLS", "3 packs", "Mix 3 bowl types")]
pw = (W - 2 * M - 20) / 3
for i, (t, pr, sub) in enumerate(packs):
    x = M + i * (pw + 10)
    yb = py - 92
    c.setFillColor(ORANGE if i >= 1 else GREEN)
    c.roundRect(x, yb, pw, 80, 12, stroke=0, fill=1)
    c.setFillColor(white)
    c.setFont("PB", 20)
    c.drawCentredString(x + pw / 2, yb + 48, t)
    c.setFont("PM", 9)
    c.drawCentredString(x + pw / 2, yb + 30, pr)
    c.setFont("P", 7.8)
    c.drawCentredString(x + pw / 2, yb + 13, sub)

# fresh photo strip
sy2 = py - 92
strip_h = 0
sw = (W - 2 * M - 20) / 3
for i, key in enumerate([]):
    pth = crop(f"img/{key}.png", sw / strip_h, f"img/c/{key}_s.jpg")
    rrect_img(c, pth, M + i * (sw + 10), sy2 - strip_h, sw, strip_h, 10)

# delivery + how to order
dy = sy2 - strip_h - 22
half = (W - 2 * M - 14) / 2
# delivery box
c.setFillColor(white)
c.setStrokeColor(LINE)
c.roundRect(M, dy - 150, half, 150, 12, stroke=1, fill=1)
c.setFillColor(GREEN)
c.setFont("PB", 13)
c.drawString(M + 14, dy - 24, "SAME-DAY DELIVERY")
rows = [("Up to 10 driving miles", "$7"), ("10–20 driving miles", "$14"), ("One fee per order", "Any size")]
ry = dy - 50
for lbl, fee in rows:
    c.setFillColor(INK)
    c.setFont("PM", 10.5)
    c.drawString(M + 14, ry, lbl)
    c.setFillColor(ORANGE if fee == "FREE" else INK)
    c.setFont("PB", 12)
    c.drawRightString(M + half - 14, ry, fee)
    c.setStrokeColor(LINE)
    c.line(M + 14, ry - 8, M + half - 14, ry - 8)
    ry -= 26
c.setFillColor(GREY)
c.setFont("P", 7.6)
c.drawString(M + 14, dy - 140, "Live map tracking + text updates on every order.")

# how to order box
ox = M + half + 14
c.setFillColor(GREEN)
c.roundRect(ox, dy - 150, half, 150, 12, stroke=0, fill=1)
c.setFillColor(white)
c.setFont("PB", 13)
c.drawString(ox + 14, dy - 24, "ORDER PLACED BY  •  DELIVERED")
how = [("7 PM the night before", "9 – 11 AM"), ("11 AM same day", "2 – 4 PM"), ("3 PM same day", "7 – 9 PM")]
hy = dy - 50
for a, b in how:
    c.setFillColor(white)
    c.setFont("PM", 9.2)
    c.drawString(ox + 14, hy, a)
    c.setFillColor(ORANGE)
    c.setFont("PB", 10.5)
    c.drawRightString(ox + half - 14, hy, b)
    c.setStrokeColor(HexColor("#3E6B53"))
    c.line(ox + 14, hy - 8, ox + half - 14, hy - 8)
    hy -= 24
c.setFillColor(white)
c.setFont("PM", 8.5)
c.drawString(ox + 14, hy - 2, "Order & pay at colossalpotato.com")
c.setFillColor(HexColor("#CFE3C9"))
c.setFont("PI", 7.4)
c.drawString(ox + 14, dy - 140, "Protein amounts are estimates. Ask about allergens.")

footer(c, 2)
c.save()
print("done")
