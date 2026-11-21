from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor, white, Color
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.utils import ImageReader
import math

src = open("build_menu.py").read().split("os.makedirs")[0]
ns = {}
exec(src, ns)
crop, rrect_img, pill = ns["crop"], ns["rrect_img"], ns["pill"]

INK = HexColor("#3A2716")
GREEN = HexColor("#2E5A37")
LEAF = HexColor("#5E9A47")
ORANGE = HexColor("#D2642A")
CREAM = HexColor("#FBF4E4")
TAN = HexColor("#E9D6B4")

W, H = 1080, 1350
M = 40
c = canvas.Canvas("BnX_Kitchens_IG_FarmToFork.pdf", pagesize=(W, H))
c.drawImage(ImageReader("img/kraft.jpg"), 0, 0, W, H)


def wheat(cx, cy, scale=1.0, ang=0, col=INK):
    c.saveState()
    c.translate(cx, cy)
    c.rotate(ang)
    c.scale(scale, scale)
    c.setStrokeColor(col)
    c.setFillColor(col)
    c.setLineWidth(2.2)
    c.line(0, 0, 0, 70)
    for i in range(5):
        y = 22 + i * 10
        for s in (-1, 1):
            c.saveState()
            c.translate(0, y)
            c.rotate(s * 35)
            c.ellipse(-3.2, 0, 3.2, 13, stroke=0, fill=1)
            c.restoreState()
    c.ellipse(-3, 70, 3, 84, stroke=0, fill=1)
    c.restoreState()


def leaf_icon(cx, cy, r):
    c.setFillColor(white)
    p = c.beginPath()
    p.moveTo(cx - r * 0.45, cy - r * 0.45)
    p.curveTo(cx - r * 0.5, cy + r * 0.4, cx + r * 0.2, cy + r * 0.55, cx + r * 0.5, cy + r * 0.5)
    p.curveTo(cx + r * 0.55, cy + r * 0.1, cx + r * 0.3, cy - r * 0.5, cx - r * 0.45, cy - r * 0.45)
    c.drawPath(p, stroke=0, fill=1)
    c.setStrokeColor(GREEN)
    c.setLineWidth(2)
    c.line(cx - r * 0.42, cy - r * 0.42, cx + r * 0.3, cy + r * 0.3)


def basket_icon(cx, cy, r):
    c.setFillColor(white)
    c.setStrokeColor(white)
    c.setLineWidth(3)
    p = c.beginPath()
    p.moveTo(cx - r * 0.55, cy + r * 0.05)
    p.lineTo(cx + r * 0.55, cy + r * 0.05)
    p.lineTo(cx + r * 0.4, cy - r * 0.45)
    p.lineTo(cx - r * 0.4, cy - r * 0.45)
    p.close()
    c.drawPath(p, stroke=0, fill=1)
    c.arc(cx - r * 0.32, cy - r * 0.2, cx + r * 0.32, cy + r * 0.5, 0, 180)


def clock_icon(cx, cy, r):
    c.setStrokeColor(white)
    c.setLineWidth(3)
    c.circle(cx, cy, r * 0.48, stroke=1, fill=0)
    c.line(cx, cy, cx, cy + r * 0.32)
    c.line(cx, cy, cx + r * 0.25, cy)


def house_icon(cx, cy, r):
    c.setFillColor(white)
    p = c.beginPath()
    p.moveTo(cx - r * 0.5, cy - 0.02 * r)
    p.lineTo(cx, cy + r * 0.48)
    p.lineTo(cx + r * 0.5, cy - 0.02 * r)
    p.close()
    c.drawPath(p, stroke=0, fill=1)
    c.rect(cx - r * 0.35, cy - r * 0.45, r * 0.7, r * 0.45, stroke=0, fill=1)
    c.setFillColor(ORANGE)
    c.rect(cx - r * 0.09, cy - r * 0.45, r * 0.18, r * 0.27, stroke=0, fill=1)


def paper_card(x, y, w, h, r=14, fill=CREAM):
    c.setFillColor(Color(0.2, 0.12, 0.05, alpha=0.22))
    c.roundRect(x + 4, y - 5, w, h, r, stroke=0, fill=1)
    c.setFillColor(fill)
    c.roundRect(x, y, w, h, r, stroke=0, fill=1)


# ---------- header ----------
# farm to fork stamp line
c.drawImage("img/logo_round.png", M, H - 176, 128, 128, mask="auto")
LX = M + 142
c.setFillColor(INK)
c.setFont("PB", 54)
c.drawString(LX, H - 112, "COLOSSAL")
bw = pdfmetrics.stringWidth("COLOSSAL ", "PB", 54)
c.setFillColor(GREEN)
c.drawString(LX + bw, H - 112, "POTATO")
c.setFillColor(INK)
c.setFont("PM", 20)
c.drawString(LX + 2, H - 146, "Fresh, healthy whole meals — right to your doorstep.")

# round stamp badge
sx, sy, sr = W - M - 92, H - 92, 84
c.setFillColor(ORANGE)
c.circle(sx, sy, sr, stroke=0, fill=1)
c.setStrokeColor(CREAM)
c.setLineWidth(2)
c.setDash(4, 4)
c.circle(sx, sy, sr - 9, stroke=1, fill=0)
c.setDash()
c.setFillColor(white)
c.setFont("PB", 18)
c.drawCentredString(sx, sy + 26, "SOLD IN")
c.setFont("PB", 29)
c.drawCentredString(sx, sy - 4, "5-PACKS")
c.setFont("PM", 13)
c.drawCentredString(sx, sy - 30, "same bowl x5")

# ---------- benefits row ----------
by = H - 268
bens = [(basket_icon, "Skip the", "shopping"), (clock_icon, "Skip the", "cooking"),
        (leaf_icon, "Fresh, never", "frozen"), (house_icon, "Delivered to", "your door")]
bwid = (W - 2 * M - 3 * 14) / 4
for i, (fn, a, b) in enumerate(bens):
    x = M + i * (bwid + 14)
    paper_card(x, by, bwid, 76, 38, TAN)
    c.setFillColor(GREEN)
    c.circle(x + 40, by + 38, 28, stroke=0, fill=1)
    fn(x + 40, by + 38, 36)
    c.setFillColor(INK)
    c.setFont("PM", 15)
    c.drawString(x + 78, by + 44, a)
    c.setFont("PB", 19)
    c.drawString(x + 78, by + 20, b)

# ---------- bowl grid ----------
bowls = [
    ("chicken", "Chicken Bacon Ranch", "$70", "955 cal • 75g P • 72g C • 41g F",
     ["Baked potato", "Grilled chicken 6 oz", "Broccoli", "Cheddar", "Bacon", "Butter", "Ranch drizzle", "Green onion"]),
    ("steak", "Steakhouse Loaded", "$90", "900 cal • 72g P • 71g C • 36g F",
     ["Baked potato", "Seared steak 6 oz", "Mushrooms", "Garlic", "Bacon", "Cheddar", "Sour cream", "Chives"]),
    ("country", "Country Breakfast", "$65", "1,090 cal • 47g P • 77g C • 66g F",
     ["Baked potato", "Breakfast sausage", "Sausage gravy", "2 boiled eggs", "Bacon", "Butter", "Green onion"]),
    ("supreme", "Breakfast Supreme", "$65", "1,140 cal • 54g P • 89g C • 64g F",
     ["Baked potato", "Mexican chorizo", "Black beans", "2 boiled eggs", "Cheese", "Butter", "Sour cream", "Hot sauce"]),
    ("bbq", "BBQ Chicken Stack", "$65", "915 cal • 57g P • 82g C • 40g F",
     ["Baked potato", "Pulled chicken 6 oz", "BBQ sauce", "Cheddar", "Butter", "Sour cream", "Pickled red onion", "Green onion"]),
    ("pork", "Pulled Pork & Crispy Onion", "$65", "1,075 cal • 59g P • 83g C • 57g F",
     ["Baked potato", "Pulled pork 6 oz", "BBQ sauce", "Cheddar", "Butter", "Ranch drizzle", "Crispy onions", "Green onion"]),
    ("sweet", "Garden Sweet Potato", "$55", "685 cal • 24g P • 93g C • 26g F",
     ["Sweet potato", "Black beans", "Spinach", "Onions", "Mushrooms", "Cheese", "Butter", "Sour cream"]),
    ("classic", "Classic Loaded", "$50", "630 cal • 21g P • 66g C • 32g F",
     ["Baked potato", "Butter", "Cheddar", "Bacon", "Sour cream", "Chives"]),
]
gap = 18
rg = 12
tw = (W - 2 * M - gap) / 2
th = 150
imh = 98
top = by - 22
for i in range(9):
    col, row = i % 2, i // 2
    x = M + col * (tw + gap)
    yb = top - (row + 1) * th - row * rg
    if i < len(bowls):
        key, name, price, mac, ings = bowls[i]
        paper_card(x, yb, tw, th, 14)
        iw = 236
        p = crop(f"img/{key}.png", iw / imh, f"img/c/{key}_k2.jpg")
        rrect_img(c, p, x + 10, yb + th - 10 - imh, iw, imh, 10)
        if i == 0:
            pill(c, x + 16, yb + th - 34, "#1 BEST SELLER", ORANGE, white, 11, "PB", 8, 20)
        if key == "sweet":
            pill(c, x + 16, yb + th - 34, "VEGETARIAN", LEAF, white, 11, "PB", 8, 20)
        if key in ("country", "supreme"):
            pill(c, x + 16, yb + th - 34, "BREAKFAST", HexColor("#8a5a2b"), white, 11, "PB", 8, 20)
        ix = x + 10 + iw + 14
        iy = yb + th - 18
        c.setFillColor(GREEN)
        c.setFont("PB", 10)
        c.drawString(ix, iy, "WHAT'S INSIDE")
        iy -= 15
        for ing in ings:
            c.setFillColor(LEAF)
            c.circle(ix + 3, iy + 3.8, 2.6, stroke=0, fill=1)
            c.setFillColor(INK)
            c.setFont("PM", 11.2)
            c.drawString(ix + 10, iy, ing)
            iy -= 13.6
        c.setFillColor(INK)
        c.setFont("PB", 16.5 if len(name) > 22 else 18)
        c.drawString(x + 14, yb + 26, name)
        c.setFillColor(HexColor("#6B5440"))
        c.setFont("PM", 10.5)
        c.drawString(x + 14, yb + 10, mac)
        c.setFillColor(ORANGE)
        c.setFont("PB", 24)
        c.drawRightString(x + tw - 14, yb + 24, price)
        c.setFillColor(HexColor("#7A6450"))
        c.setFont("P", 9)
        c.drawRightString(x + tw - 14, yb + 11, "per 5-pack")
    else:
        ww = W - 2 * M
        c.setFillColor(Color(0.2, 0.12, 0.05, alpha=0.22))
        c.roundRect(x + 4, yb - 5, ww, th, 14, stroke=0, fill=1)
        c.setFillColor(GREEN)
        c.roundRect(x, yb, ww, th, 14, stroke=0, fill=1)
        lx = x + 22
        c.setFillColor(white)
        c.setFont("PB", 16)
        c.drawString(lx, yb + th - 28, "HOW TO ORDER")
        c.setFont("PM", 11.5)
        c.drawString(lx, yb + th - 48, "Pick 1 bowl, get 5 of the same.")
        c.drawString(lx, yb + th - 66, "Packs of:")
        cx = lx
        for n in ["5", "10", "15"]:
            hi = n in ("10", "15")
            c.setFillColor(ORANGE if hi else CREAM)
            c.circle(cx + 20, yb + 52, 20, stroke=0, fill=1)
            c.setFillColor(white if hi else GREEN)
            c.setFont("PB", 16)
            c.drawCentredString(cx + 20, yb + 46.5, n)
            cx += 48
        c.setFillColor(HexColor("#FFD3B3"))
        c.setFont("PB", 12)
        c.drawString(lx + 150, yb + 56, "Mix bowls:")
        c.drawString(lx + 150, yb + 40, "1 type per pack")
        dx = x + 300
        c.setStrokeColor(HexColor("#4E7A57"))
        c.setLineWidth(1.5)
        c.line(dx, yb + 16, dx, yb + th - 16)
        rx = dx + 20
        c.setFillColor(white)
        c.setFont("PB", 16)
        c.drawString(rx, yb + th - 28, "ADD-ONS")
        c.setFillColor(HexColor("#CFE3C9"))
        c.setFont("PM", 10)
        c.drawString(rx + 88, yb + th - 28, "per bowl")
        adds = [("+ Chicken 4 oz", "$4"), ("+ Steak 4 oz", "$6"), ("Bacon", "$2"), ("Extra cheese", "$1"),
                ("Sour cream", "$1"), ("Crispy onions", "$1"), ("Mushrooms", "$1"), ("LOW-CARB: cauliflower base", "$1")]
        colw2 = (x + ww - 22 - rx - 30) / 2
        for k, (nm, pr) in enumerate(adds):
            if k < 4:
                ax, ay = rx, yb + th - 52 - k * 22
            else:
                ax, ay = rx + colw2 + 30, yb + th - 52 - (k - 4) * 22
            lc = k == 7
            c.setFillColor(HexColor("#FFD3B3") if lc else white)
            c.setFont("PB" if lc else "PM", 10.5 if lc else 11.5)
            c.drawString(ax, ay, nm)
            c.setFillColor(HexColor("#FFB98A"))
            c.setFont("PB", 12)
            c.drawRightString(ax + colw2, ay, pr)

# ---------- delivery windows ----------
sy = top - 5 * th - 4 * rg - 26
c.setFillColor(INK)
c.setFont("PB", 24)
c.drawString(M, sy - 6, "DELIVERY TIMES")
wheat(W - M - 10, sy - 30, 0.55, 15, GREEN)
rows = [("ORDER PLACED BY", "7 PM the night before", "9 – 11 AM"),
        ("ORDER PLACED BY", "11 AM same day", "2 – 4 PM"),
        ("ORDER PLACED BY", "3 PM same day", "7 – 9 PM")]
cw = (W - 2 * M - 2 * gap) / 3
ch = 104
cy = sy - 26 - ch
for i, (a, b, d) in enumerate(rows):
    x = M + i * (cw + gap)
    paper_card(x, cy, cw, ch, 14)
    c.setFillColor(HexColor("#7A6450"))
    c.setFont("PB", 10.5)
    c.drawCentredString(x + cw / 2, cy + ch - 20, a)
    c.setFillColor(INK)
    c.setFont("PB", 16)
    c.drawCentredString(x + cw / 2, cy + ch - 39, b)
    c.setFillColor(HexColor("#7A6450"))
    c.setFont("PB", 10.5)
    c.drawCentredString(x + cw / 2, cy + ch - 60, "DELIVERED")
    c.setFillColor(ORANGE)
    c.setFont("PB", 26)
    c.drawCentredString(x + cw / 2, cy + 14, d)

# order line
c.setFillColor(INK)
c.setFont("PB", 20)
c.drawCentredString(W / 2, 74, "Order at colossalpotato.com  •  Preorder up to 3 months ahead")

# footer band
c.setFillColor(INK)
c.rect(0, 0, W, 56, stroke=0, fill=1)
c.setFillColor(CREAM)
c.setFont("PB", 19)
c.drawCentredString(W / 2, 20, "Delivery: $7 up to 10 mi  •  $14 up to 20 mi  •  one fee per order")
c.save()
print("ok", cy)
