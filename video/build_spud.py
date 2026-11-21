import sys, numpy as np
from multiprocessing import Pool
import variants as v
which = sys.argv[1]
if which == "deep":
    SC = [(0.0, "Hey there... I'm Spud.", "hi"), (3.36, "I'm a loaded potato bowl, cooked fresh today.", "fresh"), (6.96, "Packed with protein — up to 75 grams.", "protein"),
          (10.9, "Keep me in the fridge, or freeze for later. Reheat when you're ready.", "store"), (16.47, "Whole ingredients. Clean eating. High protein, zero prep.", "clean"),
          (22.76, "Pick a bowl, get 5 — a whole week of lunches.", "five"), (26.76, "Pick your day & time... I'll come right to your door.", "door"), (30.10, "Order at colossalpotato.com", "cta")]
    DUR = 35.65
else:
    SC = [(0.0, "Hiii! I'm Spud!", "hi"), (2.87, "I'm a loaded potato bowl, cooked fresh today!", "fresh"), (6.12, "Packed with protein — up to 75 grams!", "protein"),
          (9.9, "Keep me in the fridge, or freeze for later. Warm me up when you're ready!", "store"), (14.76, "Whole ingredients. Clean eating. Great for gym days & bodybuilders!", "clean"),
          (20.18, "Pick a bowl, get 5 — a whole week of lunches!", "five"), (23.94, "Pick your day & time... I come right to your door!", "door"), (26.97, "Order at colossalpotato.com", "cta")]
    DUR = 31.3
v.SC = SC; v.MOUTH = np.load(f"mouth_full_{which}2.npy" if which=="deep" else f"mouth_full_{which}.npy")
import os; os.makedirs(f"fr_{which}", exist_ok=True)
N = int(DUR * v.FPS)
def w(idx):
    for i in idx: v.v2(i).save(f"fr_{which}/f{i:05d}.jpg", quality=88)
if __name__ == "__main__":
    if len(sys.argv) > 2:
        for tt in sys.argv[2:]: v.v2(int(float(tt) * 30)).save(f"/tmp/sp_{which}_{tt}.jpg")
        sys.exit()
    with Pool(2) as p: p.map(w, [list(range(N))[k::2] for k in range(2)])
    print(which, N)
