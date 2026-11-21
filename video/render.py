import math, sys, os
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from multiprocessing import Pool

W, H, FPS = 1080, 1920, 30
OFF = 1.0  # voiceover starts at 1.0s
DUR = 42.76 + OFF + 1.6
N = int(DUR * FPS)
IMG = "/home/claude/menu/img/"
FD = "/usr/share/fonts/truetype/google-fonts/"
INK = (58, 39, 22); GREEN = (47, 93, 58); ORANGE = (217, 107, 43); CREAM = (247, 240, 227); WHITE = (255, 255, 255)

def F(sz, w="Bold"): return ImageFont.truetype(FD + f"Poppins-{w}.ttf", sz)
EMO = ImageFont.truetype("/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf", 109)

def emoji(ch, size):
    im = Image.new("RGBA", (140, 140), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((6, 6), ch, font=EMO, embedded_color=True)
    bb = im.getbbox(); im = im.crop(bb) if bb else im
    return im.resize((size, int(size * im.height / im.width)), Image.LANCZOS)

# assets
BG = Image.open(IMG + "kraft.jpg").convert("RGB")
s = max(W / BG.width, H / BG.height); BG = BG.resize((int(BG.width * s) + 1, int(BG.height * s) + 1)).crop((0, 0, W, H))
SPUD = Image.open(IMG + "spud_cut.png").convert("RGBA")
LOGO = Image.open(IMG + "logo_round.png").convert("RGBA")
def photo(k, w, h, r=36):
    im = Image.open(IMG + f"{k}.png").convert("RGB")
    sc = max(w / im.width, h / im.height); im = im.resize((int(im.width * sc) + 1, int(im.height * sc) + 1), Image.LANCZOS)
    x = (im.width - w) // 2; y = (im.height - h) // 2; im = im.crop((x, y, x + w, y + h)).convert("RGBA")
    m = Image.new("L", (w, h), 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, w, h), r, fill=255); im.putalpha(m); return im
PH = {k: photo(k, 900, 600) for k in ["chicken", "steak", "bbq", "country"]}
TH = {k: photo(k, 300, 220, 24) for k in ["chicken", "steak", "bbq", "pork", "sweet", "classic", "country", "supreme"]}
EM = {c: emoji(c, 120) for c in ["🥔", "🔥", "💪", "📱", "📅", "💳", "📲", "🚗", "🏠", "✅", "❄️", "⭐"]}

def ease(t): t = max(0, min(1, t)); return 1 - (1 - t) ** 3
def back(t):
    t = max(0, min(1, t)); c = 1.70158; return 1 + (c + 1) * (t - 1) ** 3 + c * (t - 1) ** 2
def appear(t, t0, d=0.45): return ease((t - t0) / d)

def paste(base, im, cx, cy, scale=1.0, alpha=1.0, rot=0):
    if alpha <= 0.01 or scale <= 0.01: return
    if scale != 1: im = im.resize((max(1, int(im.width * scale)), max(1, int(im.height * scale))), Image.LANCZOS)
    if rot: im = im.rotate(rot, resample=Image.BICUBIC, expand=True)
    if alpha < 1:
        a = im.getchannel("A").point(lambda v: int(v * alpha)); im = im.copy(); im.putalpha(a)
    base.alpha_composite(im, (int(cx - im.width / 2), int(cy - im.height / 2)))

def text_img(txt, font, fill, maxw=None, spacing=10, align="center"):
    d = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
    lines = []
    for para in txt.split("\n"):
        words = para.split(" "); cur = ""
        for w_ in words:
            tst = (cur + " " + w_).strip()
            if maxw and d.textlength(tst, font=font) > maxw and cur: lines.append(cur); cur = w_
            else: cur = tst
        lines.append(cur)
    asc, desc = font.getmetrics(); lh = asc + desc
    wmax = int(max(d.textlength(l, font=font) for l in lines)) + 8
    im = Image.new("RGBA", (wmax, lh * len(lines) + spacing * (len(lines) - 1) + 8), (0, 0, 0, 0)); dd = ImageDraw.Draw(im)
    for i, l in enumerate(lines):
        lw = dd.textlength(l, font=font); x = (wmax - lw) / 2 if align == "center" else 0
        dd.text((x, i * (lh + spacing)), l, font=font, fill=fill)
    return im
TCACHE = {}
def T(txt, size, fill=INK, w="Bold", maxw=960):
    k = (txt, size, fill, w, maxw)
    if k not in TCACHE: TCACHE[k] = text_img(txt, F(size, w), fill, maxw)
    return TCACHE[k]

def rrect(size, fill, r=40, shadow=True):
    w, h = size; pad = 30
    im = Image.new("RGBA", (w + pad * 2, h + pad * 2), (0, 0, 0, 0))
    if shadow:
        sh = Image.new("RGBA", im.size, (0, 0, 0, 0)); ImageDraw.Draw(sh).rounded_rectangle((pad, pad + 12, pad + w, pad + h + 12), r, fill=(40, 25, 10, 90))
        im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(12)))
    ImageDraw.Draw(im).rounded_rectangle((pad, pad, pad + w, pad + h), r, fill=fill)
    return im
def pill(txt, size, fill, tc=WHITE, padx=36, pady=18):
    t = T(txt, size, tc); im = rrect((t.width + padx * 2, t.height + pady * 2), fill, r=(t.height + pady * 2) // 2)
    im.alpha_composite(t, (30 + padx, 30 + pady)); return im

def spud_at(base, t, cx, cy, h, mode="bob"):
    sc = h / SPUD.height
    dy = 0; sx = sy = 1; rot = 0
    if mode == "bob": dy = -abs(math.sin(t * 3.2)) * 28; sy = 1 + 0.03 * math.sin(t * 6.4)
    if mode == "jump":
        p = (t % 1.4) / 1.4; dy = -math.sin(min(p, .5) * 2 * math.pi / 1) * 0 - (math.sin(p * math.pi) * 160 if p < 1 else 0); rot = 8 * math.sin(t * 5)
    if mode == "wave": rot = 9 * math.sin(t * 5); dy = -abs(math.sin(t * 2.5)) * 18
    im = SPUD.resize((int(SPUD.width * sc * sx), int(SPUD.height * sc * sy)), Image.LANCZOS)
    paste(base, im, cx, cy + dy, 1, 1, rot)

def section_title(base, t, t0, txt, y=230, col=GREEN):
    a = appear(t, t0); im = pill(txt, 52, col)
    paste(base, im, W / 2, y + (1 - a) * -60, 1, a)

def step_badge(base, t, t0, n, y=420):
    a = back((t - t0) / 0.5)
    c = Image.new("RGBA", (190, 190), (0, 0, 0, 0)); d = ImageDraw.Draw(c); d.ellipse((5, 5, 185, 185), fill=ORANGE)
    tn = T(str(n), 110, WHITE); c.alpha_composite(tn, ((190 - tn.width) // 2, (190 - tn.height) // 2 - 8))
    paste(base, c, W / 2, y, max(0.01, a), min(1, max(0, (t - t0) / 0.2)))

def frame(i):
    t = i / FPS
    im = BG.copy().convert("RGBA")
    # global header strip
    v = t - OFF
    # ---------- S1 intro ----------
    if t < 5.4:
        a = appear(t, 0.0, 0.6)
        paste(im, LOGO, W / 2, 560, 0.55 * back(t / 0.7) if t < 0.7 else 0.55, a)
        spud_at(im, t, W / 2, 1420, 420, "jump" if t < 1.2 else "bob")
        paste(im, T("Meet", 64, INK, "Medium"), W / 2, 930, 1, appear(t, 0.9))
        paste(im, T("COLOSSAL", 130, INK), W / 2, 1030, 1, appear(t, 1.1))
        paste(im, T("POTATO", 130, GREEN), W / 2, 1160, 1, appear(t, 1.3))
        paste(im, T("Sacramento's loaded potato meal prep", 44, INK, "Medium"), W / 2, 1720, 1, appear(t, 2.4))
    # ---------- S2 fresh ----------
    elif v < 9.0:
        t0 = 4.4 + OFF
        paste(im, PH["chicken"], W / 2, 640 + (1 - appear(t, t0)) * 80, 1, appear(t, t0))
        for k, (txt, col, at) in enumerate([("Cooked fresh", GREEN, 0.2), ("Delivered same day", ORANGE, 1.4), ("Never frozen", INK, 3.1)]):
            card = pill(txt, 66, col)
            paste(im, card, W / 2 + (1 - appear(t, t0 + at)) * 400, 1130 + k * 190, 1, appear(t, t0 + at))
        if t > t0 + 3.1:
            ice = EM["❄️"]; a = appear(t, t0 + 3.3)
            paste(im, ice, W / 2 + 360, 1510, 0.8, a)
            d = ImageDraw.Draw(im)
            if a > 0.5: d.line((W / 2 + 310, 1460, W / 2 + 410, 1560), fill=(200, 40, 40), width=14)
    # ---------- S3 protein ----------
    elif v < 15.1:
        t0 = 9.0 + OFF
        section_title(im, t, t0, "HIGH PROTEIN", 230, ORANGE)
        k = "steak" if (t - t0) < 3 else "chicken"
        paste(im, PH[k], W / 2, 630, 1, 1)
        a = back((t - t0 - 0.6) / 0.6)
        circ = Image.new("RGBA", (420, 420), (0, 0, 0, 0)); dd = ImageDraw.Draw(circ); dd.ellipse((10, 10, 410, 410), fill=GREEN)
        n = T("75g", 130, WHITE); circ.alpha_composite(n, ((420 - n.width) // 2, 95)); p = T("protein", 50, CREAM, "Medium"); circ.alpha_composite(p, ((420 - p.width) // 2, 255))
        paste(im, circ, W / 2, 1250, max(0.01, a) * 1.0, min(1, max(0, (t - t0 - 0.6) / 0.2)))
        paste(im, T("up to", 46, INK, "Medium"), W / 2, 1010, 1, appear(t, t0 + 0.8))
        paste(im, T("Built on a real baked potato", 54, INK), W / 2, 1580, 1, appear(t, t0 + 3.6))
        paste(im, EM["💪"], W / 2 - 300, 1250, 0.9, appear(t, t0 + 1.2))
        paste(im, EM["🔥"], W / 2 + 300, 1250, 0.9, appear(t, t0 + 1.4))
    # ---------- S4 menu ----------
    elif v < 19.5:
        t0 = 15.1 + OFF
        section_title(im, t, t0, "8 BOWLS", 210, GREEN)
        keys = ["chicken", "steak", "bbq", "pork", "sweet", "classic", "country", "supreme"]
        for j, k in enumerate(keys):
            r, c = divmod(j, 2); x = W / 2 + (c - 0.5) * 340; y = 470 + r * 255
            paste(im, TH[k], x, y, back((t - t0 - 0.15 * j) / 0.4) if t < t0 + 0.15 * j + 0.4 else 1, min(1, max(0, (t - t0 - 0.15 * j) / 0.2)))
        paste(im, pill("Breakfast bowls too", 48, ORANGE), W / 2, 1520, 1, appear(t, t0 + 1.6))
        paste(im, pill("Low-carb swap available", 48, GREEN), W / 2, 1670, 1, appear(t, t0 + 2.4))
    # ---------- S5-S8 how to order ----------
    elif v < 37.6:
        steps = [(19.5, 1, "Pick your bowl", "at colossalpotato.com", "📱"), (23.9, 2, "Order in 5-packs", "5 of the same bowl — a full week of lunches", "🥔"),
                 (28.6, 3, "Choose day & time", "Preorder up to 3 months ahead", "📅"), (32.8, 4, "Pay & track", "Text updates + watch your driver live", "🚗")]
        cur = max(s for s in steps if v >= s[0])
        st0, n, title, sub, em = cur; t0 = st0 + OFF
        section_title(im, t, 19.5 + OFF, "HOW TO ORDER", 200, ORANGE) if n == 1 else paste(im, pill("HOW TO ORDER", 52, ORANGE), W / 2, 200)
        # progress dots
        d = ImageDraw.Draw(im)
        for k in range(4):
            cx = W / 2 + (k - 1.5) * 70; f = ORANGE if k < n else (220, 200, 170)
            d.ellipse((cx - 16, 300 - 16, cx + 16, 300 + 16), fill=f)
        step_badge(im, t, t0, n, 470)
        paste(im, T(title, 80, INK), W / 2, 660, 1, appear(t, t0 + 0.2))
        paste(im, T(sub, 46, INK, "Medium", 900), W / 2, 770, 1, appear(t, t0 + 0.4))
        a = appear(t, t0 + 0.6)
        card = rrect((900, 700), CREAM, 50)
        paste(im, card, W / 2, 1300 + (1 - a) * 100, 1, a)
        if n == 1:
            paste(im, TH["chicken"], W / 2 - 190, 1170, 1, a); paste(im, TH["steak"], W / 2 + 190, 1170, 1, a)
            paste(im, TH["country"], W / 2 - 190, 1420, 1, a); paste(im, TH["classic"], W / 2 + 190, 1420, 1, a)
            pk = 0.5 + 0.5 * math.sin((t - t0) * 6)
            if t > t0 + 1.5:
                d = ImageDraw.Draw(im); d.rounded_rectangle((W / 2 - 340, 1060, W / 2 - 40, 1280), 24, outline=ORANGE, width=int(8 + 4 * pk))
                paste(im, EM["✅"], W / 2 - 70, 1080, 0.6, appear(t, t0 + 1.5))
        elif n == 2:
            for k in range(5):
                at = t0 + 0.8 + k * 0.35
                paste(im, TH["chicken"].resize((220, 160)), W / 2 + (k - 2) * 160, 1240 + (k % 2) * 60, back((t - at) / 0.4) if t < at + 0.4 else 1, min(1, max(0, (t - at) / 0.15)))
            paste(im, T("x5", 120, ORANGE), W / 2, 1500, 1, appear(t, t0 + 2.6))
        elif n == 3:
            # calendar
            d = ImageDraw.Draw(im); x0, y0 = W / 2 - 360, 1010
            d.rounded_rectangle((x0, y0, x0 + 720, y0 + 90), 20, fill=GREEN)
            mt = T("PICK A DAY", 44, WHITE); im.alpha_composite(mt, (int(W / 2 - mt.width / 2), y0 + 18))
            for k in range(14):
                r, c = divmod(k, 7); cx = x0 + 52 + c * 102; cy = y0 + 150 + r * 100
                sel = (k == 9 and t > t0 + 1.2)
                d.ellipse((cx - 40, cy - 40, cx + 40, cy + 40), fill=ORANGE if sel else (235, 222, 200))
                nm = T(str(k + 15), 36, WHITE if sel else INK); im.alpha_composite(nm, (int(cx - nm.width / 2), int(cy - nm.height / 2 - 4)))
            for k, w_ in enumerate(["9–11 AM", "2–4 PM", "7–9 PM"]):
                sel = (k == 1 and t > t0 + 2.0)
                pp = pill(w_, 38, ORANGE if sel else GREEN, padx=26, pady=14)
                paste(im, pp, W / 2 + (k - 1) * 275, 1500, 1, appear(t, t0 + 1.4 + k * 0.15))
        elif n == 4:
            # map with route and car
            d = ImageDraw.Draw(im); x0, y0, x1, y1 = W / 2 - 400, 1000, W / 2 + 400, 1600
            d.rounded_rectangle((x0, y0, x1, y1), 30, fill=(232, 236, 226))
            for gx in range(int(x0) + 60, int(x1), 120): d.line((gx, y0 + 10, gx, y1 - 10), fill=WHITE, width=16)
            for gy in range(y0 + 60, y1, 120): d.line((x0 + 10, gy, x1 - 10, gy), fill=WHITE, width=16)
            pts = [(x0 + 60, y1 - 60), (x0 + 60, y0 + 300), (x0 + 420, y0 + 300), (x0 + 420, y0 + 60), (x1 - 100, y0 + 60)]
            d.line(pts, fill=ORANGE, width=12, joint="curve")
            # car position along route
            p = max(0, min(1, (t - t0 - 0.8) / 3.0))
            segs = [(pts[k], pts[k + 1]) for k in range(len(pts) - 1)]; L = [math.dist(a_, b_) for a_, b_ in segs]; tot = sum(L); dist = p * tot
            for (a_, b_), l in zip(segs, L):
                if dist <= l: cx = a_[0] + (b_[0] - a_[0]) * dist / l; cy = a_[1] + (b_[1] - a_[1]) * dist / l; break
                dist -= l
            else: cx, cy = pts[-1]
            paste(im, EM["🏠"], x1 - 100, y0 + 60, 0.7)
            paste(im, EM["🚗"], cx, cy, 0.7)
            # text bubbles
            for k, (msg, at) in enumerate([("✓ Order confirmed", 0.6), ("🔥 Cooking now", 1.6), ("🚗 On the way!", 2.6)]):
                b = pill(msg.replace("✓ ", "").replace("🔥 ", "").replace("🚗 ", ""), 34, GREEN if k < 2 else ORANGE, padx=24, pady=12)
                paste(im, b, W / 2 + 200, 1680 + k * 0, 1, appear(t, t0 + at) * (1 if k == 2 or t < t0 + [1.6, 2.6, 9][k] else 0))
            paste(im, EM["📲"], W / 2 - 260, 1690, 0.6, appear(t, t0 + 0.6))
    # ---------- S9 CTA ----------
    else:
        t0 = 37.6 + OFF
        paste(im, LOGO, W / 2, 470, 0.45, appear(t, t0))
        paste(im, T("Fresh meals,", 92, INK), W / 2, 820, 1, appear(t, t0 + 0.2))
        paste(im, T("right to your door.", 92, GREEN), W / 2, 940, 1, appear(t, t0 + 0.4))
        a = back((t - t0 - 1.0) / 0.5)
        paste(im, pill("ORDER AT COLOSSALPOTATO.COM", 50, ORANGE, padx=40, pady=24), W / 2, 1120, max(0.01, min(a, 1.15)), min(1, max(0, (t - t0 - 1.0) / 0.2)))
        paste(im, T("Same-day delivery • Sacramento", 40, INK, "Medium"), W / 2, 1240, 1, appear(t, t0 + 1.6))
        spud_at(im, t, W / 2, 1580, 380, "jump" if t > DUR - 2.2 else "wave")
    return im.convert("RGB")

def render(rng):
    for i in rng:
        frame(i).save(f"frames/f{i:05d}.jpg", quality=88)

if __name__ == "__main__":
    os.makedirs("frames", exist_ok=True)
    if len(sys.argv) > 1:
        for tt in sys.argv[1:]:
            frame(int(float(tt) * FPS)).save(f"/tmp/test_{tt}.jpg", quality=85)
        sys.exit()
    idx = list(range(N)); chunks = [idx[k::2] for k in range(2)]
    with Pool(2) as p: p.map(render, chunks)
    print("frames", N)
