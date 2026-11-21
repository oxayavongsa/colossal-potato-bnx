import sys, os, math
from multiprocessing import Pool
from PIL import Image, ImageDraw
import render as R
from render import W, H, FPS, INK, GREEN, ORANGE, CREAM, WHITE, T, pill, paste, appear, back, ease, rrect, EM, PH, TH, LOGO, SPUD, BG, emoji

DARK = (32, 58, 38)
def bg_green():
    im = Image.new("RGBA", (W, H), DARK + (255,)); d = ImageDraw.Draw(im)
    for y in range(0, H, 6):
        a = int(18 * math.sin(y / 90)); d.line((0, y, W, y), fill=(DARK[0] + a // 3, DARK[1] + a // 2, DARK[2] + a // 3, 255), width=6)
    return im
GBG = bg_green()
BIG = {k: R.photo(k, 1080, 1100, 0) for k in ["chicken", "steak", "bbq", "pork", "country", "supreme", "classic", "sweet"]}
NAMES = {"chicken": ("Chicken Bacon Ranch", "75g protein"), "steak": ("Steakhouse Loaded", "70g protein"), "bbq": ("BBQ Chicken Stack", "69g protein"),
         "pork": ("Pulled Pork & Crispy Onion", "62g protein"), "country": ("Country Breakfast", "43g protein"), "supreme": ("Breakfast Supreme", "58g protein"),
         "classic": ("Classic Loaded", "$50 / 5-pack"), "sweet": ("Garden Sweet Potato", "Vegetarian")}
import numpy as _np
from PIL import ImageFilter as _IF
DEEP = os.environ.get("DEEP") == "1"
MOUTH = _np.load("mouth_deep.npy" if DEEP else "mouth.npy") if os.path.exists("mouth.npy") else None
_SK = SPUD.copy()
def spud_face(o, blink):
    im = _SK.copy(); d = ImageDraw.Draw(im)
    if o > 0.08:
        patch = _SK.crop((250, 530, 392, 600)); m = Image.new("L", patch.size, 0); ImageDraw.Draw(m).rounded_rectangle((0, 0) + patch.size, 26, fill=255)
        m = m.filter(_IF.GaussianBlur(4)); im.paste(patch, (250, 448), m)
        w = 44 + 46 * o; h = 14 + 46 * o; cx, cy = 321, 480 + 6 * o
        d.ellipse((cx - w, cy - h * 0.55, cx + w, cy + h), fill=(74, 36, 18), outline=(58, 39, 22), width=6)
        if o > 0.3: d.ellipse((cx - w * 0.55, cy + h * 0.25, cx + w * 0.55, cy + h * 0.95), fill=(226, 119, 123))
    if blink > 0:
        for ex in (200, 441):
            lid = _SK.crop((ex - 66, 413 - 62 - 186, ex + 66, 413 + 62 - 186))
            hh = int(124 * blink); m = Image.new("L", (132, 124), 0); ImageDraw.Draw(m).ellipse((2, 2, 130, 122), fill=255)
            m2 = Image.new("L", (132, 124), 0); m2.paste(m.crop((0, 0, 132, hh)), (0, 0))
            im.paste(lid, (ex - 66, 413 - 62), m2)
            if blink > 0.9: d.arc((ex - 60, 413 - 40, ex + 60, 413 + 60), 20, 160, fill=(58, 39, 22), width=9)
    return im
BIG5 = R.photo("chicken", 320, 240, 28)
EM2 = {c: emoji(c, 120) for c in ["❓", "💪", "🚗", "🏠", "💖", "📅", "🥔", "⚡"]}

def spud(base, t, cx, cy, h, mode="bob", rot0=0, face=None):
    sc = h / SPUD.height; dy = 0; rot = rot0; sy = 1
    src = face if face is not None else SPUD
    if mode == "bob": dy = -abs(math.sin(t * 3.2)) * 26; sy = 1 + 0.03 * math.sin(t * 6.4)
    if mode == "talk": dy = -abs(math.sin(t * 4.5)) * 5; rot = 1.8 * math.sin(t * 1.6); sy = 1 + 0.012 * math.sin(t * 9)
    if mode == "calm": dy = -abs(math.sin(t * 1.6)) * 10; rot = 2.5 * math.sin(t * 1.2); sy = 1 + 0.015 * math.sin(t * 3.2)
    if mode == "jump": p = (t % 1.2) / 1.2; dy = -math.sin(p * math.pi) * 140
    im = src.resize((int(SPUD.width * sc), int(SPUD.height * sc * sy)), Image.LANCZOS)
    paste(base, im, cx, cy + dy, 1, 1, rot)

def bubble(txt, size=54, w=820):
    t = T(txt, size, INK, "Bold", w - 80)
    bw, bh = t.width + 90, t.height + 70
    im = Image.new("RGBA", (bw + 60, bh + 110), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((30, 30, 30 + bw, 30 + bh), 46, fill=WHITE)
    cx = 30 + bw // 2; d.polygon([(cx - 40, 30 + bh - 2), (cx + 40, 30 + bh - 2), (cx, 30 + bh + 60)], fill=WHITE)
    im.alpha_composite(t, (30 + 45, 30 + 35)); return im

# ---------------- V1: punchy 15s ----------------
V1_DUR = 15.5
def v1(i):
    t = i / FPS
    im = BG.copy().convert("RGBA")
    if t < 1.6:
        a = back(t / 0.4)
        paste(im, T("HUNGRY?", 190, INK), W / 2, 700, max(0.01, min(a, 1.2)), min(1, t / 0.15))
        spud(im, t, W / 2, 1300, 520, "bob"); paste(im, EM2["❓"], W / 2 + 230, 1000, 0.8, appear(t, 0.5))
    elif t < 6.4:
        keys = ["chicken", "steak", "bbq", "pork", "country", "supreme", "classic", "sweet"]
        k = keys[min(7, int((t - 1.6) / 0.6))]; tl = (t - 1.6) % 0.6
        paste(im, BIG[k], W / 2, 760, 1 + 0.06 * (tl / 0.6), 1)
        nm, sub = NAMES[k]
        paste(im, pill(nm, 60, GREEN), W / 2, 1420, 1, 1)
        paste(im, pill(sub, 52, ORANGE), W / 2, 1580, 1, 1)
        paste(im, T("8 LOADED BOWLS", 64, INK), W / 2, 180, 1, 1)
    elif t < 9.6:
        t0 = 6.4
        for k, (w_, col) in enumerate([("FRESH", GREEN), ("SAME DAY", ORANGE), ("NEVER FROZEN", INK)]):
            a = back((t - t0 - k * 0.45) / 0.35)
            paste(im, T(w_, 150 if k < 2 else 118, col), W / 2, 620 + k * 260, max(0.01, min(a, 1.25)), min(1, max(0, (t - t0 - k * 0.45) / 0.12)))
        paste(im, T("Cooked today. At your door today.", 46, INK, "Medium"), W / 2, 1480, 1, appear(t, t0 + 1.6))
    elif t < 12.6:
        t0 = 9.6
        paste(im, T("5-PACKS", 170, INK), W / 2, 520, 1, appear(t, t0))
        paste(im, T("a full week of lunches", 58, INK, "Medium"), W / 2, 680, 1, appear(t, t0 + 0.3))
        for k in range(5):
            at = t0 + 0.4 + k * 0.18
            paste(im, TH["steak"], W / 2 + (k - 2) * 190, 1000 + (k % 2) * 70, back((t - at) / 0.35) if t < at + 0.35 else 1, min(1, max(0, (t - at) / 0.1)))
        a = back((t - t0 - 1.5) / 0.4)
        paste(im, pill("FROM $50", 90, ORANGE, padx=50, pady=26), W / 2, 1420, max(0.01, min(a, 1.2)), min(1, max(0, (t - t0 - 1.5) / 0.12)))
    else:
        t0 = 12.6
        paste(im, LOGO, W / 2, 470, 0.42, appear(t, t0))
        paste(im, T("ORDER NOW", 120, INK), W / 2, 820, 1, appear(t, t0 + 0.1))
        paste(im, pill("colossalpotato.com", 70, GREEN, padx=44, pady=24), W / 2, 990, 1, appear(t, t0 + 0.3))
        paste(im, T("Same-day delivery • Sacramento", 42, INK, "Medium"), W / 2, 1110, 1, appear(t, t0 + 0.5))
        spud(im, t, W / 2, 1520, 440, "jump")
    return im.convert("RGB")
V1_SFX = [("hey", 0.05, 1.0), ("wow", 1.7, .8), ("ooh", 4.2, .7), ("yay", 6.45, .9), ("tada", 9.7, .9), ("yummy", 13.0, 1.0), ("hehe", 14.5, .8)]

# ---------------- V2: Spud tells it, 24s ----------------
V2 = [(0.0, "Hiii! I'm Spud!", "hey"), (2.87, "I'm a loaded potato bowl, cooked fresh today!", "hehe"), (6.12, "Packed with protein — up to 75 grams!", "wow"),
      (9.79, "Pick a bowl, get 5 — a whole week of lunches!", "yay"), (13.55, "Pick your day & time... I come right to your door!", "whee"),
      (16.58, "Order at colossalpotato.com", "loveyou")]
V2_DUR = 21.6
if DEEP:
    V2 = [(0.0, "Hey there... I'm Spud.", "hey"), (3.36, "I'm a loaded potato bowl, cooked fresh today.", "hehe"), (6.96, "Packed with protein — up to 75 grams.", "wow"),
          (10.83, "Pick a bowl, get 5 — a whole week of lunches.", "yay"), (14.83, "Pick your day & time... I'll come right to your door.", "whee"),
          (18.17, "Order at colossalpotato.com", "loveyou")]
    V2_DUR = 23.8
EM3 = {c: emoji(c, 120) for c in ["❄️", "🔥", "🥦", "🥩", "🏋️", "🥚", "✅"]}
SC = None  # list of (start, text, scene)
def v2(i):
    t = i / FPS
    im = GBG.copy()
    sc = SC
    idx = max(k for k in range(len(sc)) if t >= sc[k][0]); t0, txt, name = sc[idx]
    if name == "fresh": paste(im, R.photo("chicken", 860, 560, 40), W / 2, 520, 1, appear(t, t0))
    if name == "protein":
        paste(im, R.photo("steak", 860, 560, 40), W / 2, 520, 1, appear(t, t0))
        paste(im, EM2["💪"], W / 2 + 330, 760, 1, appear(t, t0 + 0.4))
    if name == "store":
        cards = [("❄️", "FRIDGE", "up to 4 days", GREEN), ("❄️", "FREEZER", "up to 2 months", (60, 110, 150)), ("🔥", "REHEAT", "2–3 minutes", ORANGE)]
        for k, (e, h1, h2, col) in enumerate(cards):
            at = t0 + 0.2 + k * 0.9; a = appear(t, at)
            card = rrect((300, 400), CREAM, 36); paste(im, card, W / 2 + (k - 1) * 340, 560 + (1 - a) * 60, 1, a)
            paste(im, EM3[e], W / 2 + (k - 1) * 340, 470 + (1 - a) * 60, 0.9, a)
            paste(im, T(h1, 46, col), W / 2 + (k - 1) * 340, 600 + (1 - a) * 60, 1, a)
            paste(im, T(h2, 32, INK, "Medium"), W / 2 + (k - 1) * 340, 665 + (1 - a) * 60, 1, a)
    if name == "clean":
        for k, (e, x, y) in enumerate([("🥔", -400, 250), ("🥩", 400, 250), ("🥦", -400, 690), ("🥚", 400, 690)]):
            paste(im, EM3.get(e, EM2.get(e)), W / 2 + x, y, 1.0, appear(t, t0 + 0.2 + k * 0.25))
        for k, (w_, col) in enumerate([("Whole ingredients", GREEN), ("Clean eating", ORANGE), ("High protein · zero prep", INK)]):
            paste(im, pill(w_, 46, col), W / 2, 330 + k * 130, 1, appear(t, t0 + 0.3 + k * 0.7))
        paste(im, EM2["⚡"], W / 2, 740, 0.9, appear(t, t0 + 2.2))
    if name == "five":
        pos = [(W / 2 - 345, 330), (W / 2, 330), (W / 2 + 345, 330), (W / 2 - 172, 600), (W / 2 + 172, 600)]
        for k, (x, y) in enumerate(pos):
            at = t0 + 0.3 + k * 0.28
            paste(im, BIG5, x, y, back((t - at) / .4) if t < at + .4 else 1, min(1, max(0, (t - at) / .12)))
            nb = T(str(k + 1), 44, WHITE); c = Image.new("RGBA", (70, 70), (0, 0, 0, 0)); ImageDraw.Draw(c).ellipse((0, 0, 69, 69), fill=ORANGE); c.alpha_composite(nb, ((70 - nb.width) // 2, (70 - nb.height) // 2 - 4))
            paste(im, c, x + 125, y - 95, 1, min(1, max(0, (t - at - .2) / .15)))
    if name == "door":
        p = max(0, min(1, (t - t0 - 0.4) / 3.0))
        d = ImageDraw.Draw(im); d.line((160, 560, 920, 560), fill=(90, 130, 95), width=14)
        paste(im, EM2["🏠"], 920, 520, 1, 1); paste(im, EM2["🚗"], 160 + 700 * p, 520, 1, 1)
        paste(im, EM2["📅"], 220, 340, 0.8, appear(t, t0 + 0.2))
    if name == "cta":
        paste(im, LOGO, W / 2, 470, 0.42, appear(t, t0))
        paste(im, EM2["💖"], W / 2 - 300, 420, 0.7, appear(t, t0 + 0.5)); paste(im, EM2["💖"], W / 2 + 300, 420, 0.7, appear(t, t0 + 0.7))
    if name == "hi":
        paste(im, T("COLOSSAL", 130, CREAM), W / 2, 430, 1, appear(t, 0.2)); paste(im, T("POTATO", 130, (255, 190, 120)), W / 2, 570, 1, appear(t, 0.4))
    b = bubble(txt, 70 if name == "hi" else 56)
    a = ease((t - t0) / 0.5)
    paste(im, b, W / 2, 1000 + (1 - a) * 30, 0.96 + 0.04 * a, a)
    fi = int(t * FPS); o = float(MOUTH[fi]) if MOUTH is not None and fi < len(MOUTH) else 0.0
    bt = (t % 3.7); blink = max(0.0, 1 - abs(bt - 0.09) / 0.09) if bt < 0.18 else 0.0
    spud(im, t, W / 2, 1520, 560, "talk", face=spud_face(o, blink))
    paste(im, T("colossalpotato.com", 44, CREAM, "Medium"), W / 2, 1850, 1, 1)
    return im.convert("RGB")
V2_SFX = [(s, t0 + 0.1, 1.0) for t0, _, s in V2] + [("hihi", 21.8, .9)]

# ---------------- V3: original + captions ----------------
CAP = [(0, 4.25, None), (4.61, 8.71, "Every bowl is cooked fresh and delivered the same day. Never frozen."),
       (9.06, 14.92, "Big, high-protein bowls — up to 75g of protein — on a real baked potato."),
       (15.29, 19.31, "Pick from 8 bowls, including breakfast, with a low-carb swap."),
       (19.78, 23.77, "Ordering is easy. Go to colossalpotato.com and pick your bowl."),
       (24.11, 28.41, "Order in 5-packs — 5 of the same bowl, a full week of lunches."),
       (28.72, 32.65, "Choose your day and delivery time. Preorder up to 3 months ahead."),
       (33.04, 37.43, "Pay online, get a text at every step, and watch your driver live."),
       (37.80, 42.76, None)]
def v3(i):
    t = i / FPS; im = R.frame(i).convert("RGBA"); v = t - R.OFF
    for a_, b_, txt in CAP:
        if txt and a_ <= v < b_ + 0.15:
            c = T(txt, 44, WHITE, "Bold", 920)
            box = Image.new("RGBA", (c.width + 60, c.height + 36), (20, 14, 8, 190))
            m = Image.new("L", box.size, 0); ImageDraw.Draw(m).rounded_rectangle((0, 0) + box.size, 24, fill=190); box.putalpha(m)
            box.alpha_composite(c, (30, 18)); paste(im, box, W / 2, 1830 - box.height / 2 + 40, 1, 1)
    return im.convert("RGB")

JOBS = {"v1": (v1, V1_DUR), "v2": (v2, V2_DUR), "v3": (v3, R.DUR)}
def work(args):
    name, idxs = args; fn = JOBS[name][0]
    for i in idxs: fn(i).save(f"fr_{name}/f{i:05d}.jpg", quality=88)

if __name__ == "__main__":
    name = sys.argv[1]
    if len(sys.argv) > 2:
        for tt in sys.argv[2:]: JOBS[name][0](int(float(tt) * FPS)).save(f"/tmp/{name}_{tt}.jpg", quality=85)
        sys.exit()
    os.makedirs(f"fr_{name}", exist_ok=True); n = int(JOBS[name][1] * FPS)
    with Pool(2) as p: p.map(work, [(name, list(range(n))[k::2]) for k in range(2)])
    print(name, n)
