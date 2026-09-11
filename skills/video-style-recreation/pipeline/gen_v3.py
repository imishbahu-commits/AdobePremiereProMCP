#!/usr/bin/env python3
"""gen_v3 — plates + per-block graphs for v3_depth_magic (27s, 1080x1920@30).
Techniques: shared camera q(t), per-plane depth coefficients, rack-focus
blur pairs, whip-pan smear + light leak, impact shake accents, overshoot pop."""
import math
import re
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps

W, H = 1080, 1920
OUT = Path("plates_v3"); OUT.mkdir(exist_ok=True)
FT = lambda p: ImageFont.truetype(f"/usr/share/fonts/truetype/dejavu/{p}", 96)
B, BL, SM = FT("DejaVuSans-Bold.ttf"), FT("DejaVuSans-Bold.ttf"), FT("DejaVuSans.ttf")

def rgba_from(img):  return img.convert("RGBA")

def keyed(im, floor=30, sat=70):
    """luminance-key an AI black-bg asset into RGBA cutout (bbox from hard mask)."""
    im = im.convert("RGB"); px = im.load()
    alpha = Image.new("L", im.size, 0); ap = alpha.load()
    mask = Image.new("L", im.size, 0); mp = mask.load()
    for y in range(im.height):
        for x in range(im.width):
            r, g, b = px[x, y]
            lum = max(r, g, b)
            ap[x, y] = 255 if lum >= sat else (int((lum - floor) * 8) if lum > floor else 0)
            mp[x, y] = 255 if lum >= sat else 0
    bbox = mask.getbbox()
    pad = 22
    bx = (max(0, bbox[0]-pad), max(0, bbox[1]-pad), min(im.width, bbox[2]+pad), min(im.height, bbox[3]+pad))
    out = im.convert("RGBA"); out.putalpha(alpha)
    return out.crop(bx)

def save(im, n):
    im.save(OUT / f"{n}.png")

# ---------------- 1. AI asset prep: screens cluster → depth planes -----------
src = Image.open("assets/v3_screens.png").convert("RGB")
k = 1200 / src.width
src = src.resize((1200, int(src.height * k)), Image.LANCZOS)
fullkey = keyed(src)
save(fullkey, "cluster")
# sub-crops by original-art coordinates (on resized 1200-wide canvas)
crops = {"cl_left": (0, 330, 480, 1150), "cl_right": (760, 260, 1200, 1150),
         "cl_bottom": (180, 1000, 980, 1376)}
for n, (x0, y0, x1, y1) in crops.items():
    save(keyed(src.crop((x0, y0, x1, y1))), n)
# rack-focus blurred variants
for n in ("cluster", "cl_left", "cl_right", "cl_bottom"):
    im = Image.open(OUT / f"{n}.png")
    im.filter(ImageFilter.GaussianBlur(9)).save(OUT / f"{n}_b.png")

wall = Image.open("plates_v2/wall_full.png").convert("RGB")
save(rgba_from(wall), "wall")
save(rgba_from(wall.resize((int(W*0.78), int(H*0.78)), Image.LANCZOS)), "wall_sm")
save(rgba_from(wall.resize((int(W*1.06), int(H*1.06)), Image.LANCZOS)), "wall_lg")
wallb = wall.filter(ImageFilter.GaussianBlur(6))
save(rgba_from(wallb), "wall_b")

card = keyed(src.crop((300, 460, 740, 1090)))
save(card, "card")
# perspective tilts for orbit (PIL perspective on a canvas)
def tilt(im, dx):
    canv = Image.new("RGBA", (im.width, im.height + 120), (0,0,0,0))
    canv.paste(im, (0, 60))
    w, h = canv.size
    p = [dx, 0, w - dx, 40, w + dx if dx>0 else w - dx, h, dx if dx>0 else -dx, h-40]
    # simple quad warp via perspective coefficients from source rect to target
    def find_coeffs(target, source):
        import numpy as np
        A = []
        for (x, y), (u, v) in zip(source, target):
            A.append([x, y, 1, 0, 0, 0, -u*x, -u*y]); A.append([0,0,0,x,y,1,-v*x,-v*y])
        A = np.array(A); B = np.array([v for (u, v) in target]).reshape(16, 1)
        r = np.linalg.solve(A, B)
        return r.flatten().tolist()
    try:
        import numpy as np
        src_rect = [(0,0),(w,0),(w,h),(0,h)]
        tgt = [(dx,30),(w-dx,0),(w+dx,h-30),(-dx,h)]
        coeffs = find_coeffs(tgt + [ (0,0),(w,0),(w,h),(0,h) ][:0], src_rect + tgt) if False else None
        c = find_coeffs(src_rect, tgt)
        return canv.transform(canv.size, Image.PERSPECTIVE, c, Image.BICUBIC).crop(
            (max(0, -dx-10), 0, min(w, w+dx+10), h))
    except Exception:
        return canv
save(tilt(card, -70), "card_l")
save(tilt(card, 70), "card_r")

# ---------------- 2. PIL plates ---------------------------------------------
def lin_grad(size, stops, horiz=False):
    w, h = size
    base = Image.new("RGB", (1 if horiz else w, h if horiz else 1))
    n = h if horiz else w
    grad = Image.new("RGB", (1, n))
    for i in range(n):
        t = i / max(1, n - 1)
        for j in range(len(stops) - 1):
            t0, c0 = stops[j]; t1, c1 = stops[j + 1]
            if t0 <= t <= t1:
                f = (t - t0) / max(1e-6, t1 - t0)
                grad.putpixel((0, i), tuple(int(c0[k] + (c1[k] - c0[k]) * f) for k in range(3)))
                break
    grad = grad.resize((w, h))
    return grad

def text_plate(name, text, font, fill, tracking=0, blur=0):
    d = ImageDraw.Draw(tmp := Image.new("RGBA", (10, 10)))
    widths = [d.textlength(ch, font=font) for ch in text]
    w = int(sum(widths) + tracking * (len(text) - 1)) + 20
    im = Image.new("RGBA", (w, font.size + 30), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    x = 10
    for ch, cw in zip(text, widths):
        d.text((x, 15), ch, font=font, fill=fill)
        x += cw + tracking
    if blur: im = im.filter(ImageFilter.GaussianBlur(blur))
    save(im, name)

# hero titles / labels
titleA = "DEPTH / LIVE"
big = FT("DejaVuSans-Bold.ttf"); big.size = 118
text_plate("hero", titleA, big, (244, 244, 248, 255), tracking=6)
text_plate("hero_b", titleA, big, (244, 244, 248, 255), tracking=6, blur=14)
sm = FT("DejaVuSans.ttf"); sm.size = 30
text_plate("lab_corridor", "VIRTUAL CAMERA — PARALLAX CORRIDOR", sm, (168, 172, 184, 235), tracking=10)
text_plate("lab_orbit", "ORBIT IN 2.5D — PERSPECTIVE CARD", sm, (168, 172, 184, 235), tracking=10)
text_plate("lab_mosaic", "LIVING MOSAIC — IMPACT SHAKE", sm, (168, 172, 184, 235), tracking=10)
text_plate("lab_end", "NO DEAD FRAMES", sm, (200, 204, 214, 240), tracking=12)

# CTA card (fresh word)
cta = Image.new("RGBA", (780, 340), (0, 0, 0, 0)); d = ImageDraw.Draw(cta)
d.rounded_rectangle([4, 4, 776, 336], 40, fill=(246, 244, 238, 255))
fb = FT("DejaVuSans-Bold.ttf"); fb.size = 74
d.text((58, 52), "LOOKS ALIVE.", font=fb, fill=(18, 18, 20, 255))
sm2 = FT("DejaVuSans.ttf"); sm2.size = 32
d.text((60, 158), "motion you can feel", font=sm2, fill=(90, 92, 99, 255))
d.rounded_rectangle([60, 218, 318, 288], 34, fill=(16, 16, 18, 255))
fsm = FT("DejaVuSans.ttf"); fsm.size = 30
d.text((92, 231), "made by agents", font=fsm, fill=(244, 244, 246, 255))
save(cta, "cta")
save(cta.resize((int(780*0.92), int(340*0.92)), Image.LANCZOS), "cta_sm")

# bokeh orbs (foreground depth plane)
bk = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(bk)
for cx, cy, r, a in ((140, 320, 130, 90), (960, 700, 170, 70), (200, 1450, 150, 80),
                     (900, 1700, 120, 66), (560, 260, 90, 55)):
    d.ellipse([cx-r, cy-r, cx+r, cy+r], fill=(150, 180, 255, a))
bk = bk.filter(ImageFilter.GaussianBlur(24))
save(bk, "bokeh")

# whip smear plate (horizontal light streaks) + light leak
smear = Image.new("RGBA", (W+400, 320), (0, 0, 0, 0)); d = ImageDraw.Draw(smear)
import random
random.seed(4)
for i in range(16):
    y = random.randint(10, 300); hh = random.randint(3, 14)
    x0 = random.randint(0, 300)
    ww = random.randint(500, 1200)
    alpha = random.randint(50, 130)
    d.rounded_rectangle([x0, y, x0+ww, y+hh], hh//2+2, fill=(190, 210, 255, alpha))
smear = smear.filter(ImageFilter.GaussianBlur(10))
save(smear, "smear")

leak = lin_grad((W, H), [(0.0, (255, 236, 210)), (0.25, (255, 220, 190)), (0.6, (60, 40, 60)), (1.0, (10, 8, 14))], horiz=True)
leak = leak.point(lambda v: v)
save(leak.convert("RGBA"), "leak")

# beam for orbit scene
beam = lin_grad((W, H), [(0.0, (30, 40, 90)), (0.5, (12, 14, 30)), (1.0, (5, 5, 8))])
save(beam.convert("RGBA"), "beam")
save(ray := lin_grad((700, 1400), [(0.0, (70, 90, 170)), (1.0, (8, 8, 16))]).convert("RGBA"), "shaftc")

# dust reuse v2
import shutil
for n in ("shaft", "dustA", "dustB"):
    shutil.copy(f"plates_v2/{n}.png", OUT / f"{n}.png")
print("v3 plates:", len(list(OUT.glob('*.png'))))

# ================= 3. Block graphs ==========================================
DRIFT = lambda amp, p, ph: f"+{amp}*sin(2*PI*t/{p}+{ph})"

class Blk:
    def __init__(self, name, t0, dur):
        self.name, self.t0, self.dur = name, t0, dur
        self.lines, self.ch, self.uses = [], "0:v", {}
    def use(self, p):
        self.uses[p] = self.uses.get(p, 0) + 1
        return self.uses[p] - 1
    def layer(self, p, x, y, enable=None, fades=(), extra=""):
        k = self.use(p)
        fx = [f"fade=t={t}:st={max(0.0, st - self.t0)}:d={dd}:alpha=1" for t, st, dd in fades]
        if extra: fx.insert(0, extra)
        fx = fx or ["null"]
        self.lines.append(f"[w_{p}_{k}]" + ",".join(fx) + f"[e_{p}_{k}]")
        def rb(m):
            dv = float(m.group(1)) - self.t0
            return f"(t+{-dv:.4f})" if dv < 0 else f"(t-{dv:.4f})"
        x = re.sub(r"\(t-([0-9]+(?:\.[0-9]+)?)\)", rb, x)
        y = re.sub(r"\(t-([0-9]+(?:\.[0-9]+)?)\)", rb, y)
        en = f":enable='between(t,{max(0.0, enable[0]-self.t0):.3f},{min(self.dur, enable[1]-self.t0):.3f})'" if enable else ""
        self.lines.append(f"[{self.ch}][e_{p}_{k}]overlay='{x}':'{y}'{en}[{self.ch}_n]")
        self.ch += "_n"
    def dip(self, st_in, st_out, dd=0.22):
        self.layer("BLACKdip", "0", "0", enable=(st_in - 0.05, st_out + 0.4),
                   fades=[("in", st_in, dd), ("out", st_out, dd)])
    def emit(self):
        dips = self.uses.get("BLACKdip", 0)
        head = ["[0:v]format=rgba,split=%d[cv0]%s" % (dips + 1, "".join(f"[w_BLACKdip_{k}]" for k in range(dips)))]
        order = [p for p in self.uses if p != "BLACKdip"]
        idx = {p: i + 1 for i, p in enumerate(order)}
        for i, p in enumerate(order):
            n = self.uses[p]
            body = f"[{i+1}:v]format=rgba" + (f",split={n}" if n > 1 else "") + "".join(f"[w_{p}_{k}]" for k in range(n))
            head.append(body)
        out = []
        for l in self.lines:
            l = re.sub(r"\[0:v(?:_n)*\]", lambda m: "[cv0" + "_n" * m.group(0).count("_n") + "]", l)
            out.append(l)
        out[-1] = re.sub(r"\[[\w:]+\]\s*$", "[vpre]", out[-1])
        out += ["[vpre]split[v_src][v_bm]", "[v_bm]gblur=sigma=24[v_bmg]",
                "[v_src][v_bmg]blend=all_mode='screen':all_opacity=0.18[v_bb]",
                "[v_bb]eq=contrast=1.06:saturation=0.98,vignette=angle=PI/4.8,format=yuv420p[vf]"]
        Path(f"graph3_{self.name}.txt").write_text(";\n".join(head + out) + "\n")
        return idx

# ---- B1 0-6.6 parallax corridor --------------------------------------------
b = Blk("c1", 0.0, 6.6)
Q = "clip((t-0.15)/6.1,0,1)"; Q3 = f"(Q:=0)".replace(":=", "=") if False else Q
cub = f"(p{p0:=0})" if False else Q
# camera push term: cubic-smoothed
q = f"(qc:=0)" if False else Q
push = f"P*({Q}*{Q}*(3-2*{Q}))"
P_ = lambda fi, fe=1.0: f"({fe}+{fi-1}*({Q}*{Q}*(3-2*{Q})))"
# global factor as string used below instead
s_ = f"({Q}*{Q}*(3-2*{Q}))"
b.layer("wall", f"-60-46*{s_}{DRIFT(7,21,0)}", f"-300-60*{s_}{DRIFT(9,25,1)}",
        enable=(0, 6.7), fades=[("in", 0.0, 0.8), ("out", 6.0, 0.5)])
b.layer("cluster_b", f"(W-900)/2+90*{s_}{DRIFT(8,19,0)}", f"469{DRIFT(10,23,1)}",
        enable=(0, 3.55), fades=[("in", 0.3, 0.7), ("out", 3.1, 0.45)])
b.layer("cluster", f"(W-900)/2+90*{s_}{DRIFT(8,19,0)}", f"469{DRIFT(10,23,1)}",
        enable=(3.15, 6.7), fades=[("in", 3.15, 0.45), ("out", 6.0, 0.5)])
b.layer("cl_left", f"120-360*{s_}{DRIFT(14,17,2)}", f"600{DRIFT(16,21,0)}",
        enable=(0, 6.7), fades=[("in", 0.5, 0.7), ("out", 6.0, 0.5)])
b.layer("cl_right", f"820+330*{s_}{DRIFT(14,17,1)}", f"690{DRIFT(15,23,2)}",
        enable=(0, 6.7), fades=[("in", 0.62, 0.7), ("out", 6.0, 0.5)])
b.layer("cl_bottom", f"300{DRIFT(18,19,1)}", f"1330+520*{s_}",
        enable=(0, 5.9), fades=[("in", 0.8, 0.7), ("out", 5.35, 0.5)])
b.layer("bokeh", f"-80-560*{s_}{DRIFT(26,15,0)}", f"120-240*{s_}", extra="gblur=sigma=8",
        enable=(0, 5.7), fades=[("in", 1.0, 0.8), ("out", 5.3, 0.4)])
lw, lh = Image.open("plates_v3/lab_corridor.png").size
b.layer("lab_corridor", f"(W-{lw})/2", f"150{DRIFT(3,12,0)}", enable=(0.5, 6.7),
        fades=[("in", 0.5, 0.5), ("out", 6.1, 0.4)])
hw, hh = Image.open("plates_v3/hero.png").size
b.layer("hero_b", f"(W-{hw})/2", f"1150{DRIFT(5,14,0)}", enable=(4.0, 6.7),
        fades=[("in", 4.0, 0.45), ("out", 6.1, 0.4)])
b.layer("hero", f"(W-{hw})/2", f"1150{DRIFT(5,14,0)}", enable=(4.35, 6.7),
        fades=[("in", 4.35, 0.5), ("out", 6.1, 0.4)])
idx_c1 = b.emit()

# ---- B2 6.6-13.4 orbit card + whip in/out ----------------------------------
b = Blk("c2", 6.6, 6.8)
WIP = f"clip((t-6.6)/0.4,0,1)"
b.layer("beam", f"0{DRIFT(6,23,0)}", f"0{DRIFT(8,27,1)}", enable=(6.55, 13.5),
        fades=[("in", 6.6, 0.5), ("out", 13.0, 0.5)])
b.layer("shaftc", f"540{DRIFT(10,19,0)}", f"80{DRIFT(8,23,1)}", enable=(6.6, 13.5),
        fades=[("in", 6.7, 0.7), ("out", 13.0, 0.5)])
b.layer("dustA", f"-40{DRIFT(16,17,2)}", "200", enable=(6.6, 13.5),
        fades=[("in", 6.8, 0.8), ("out", 13.0, 0.5)])
# clock card: 3-phase perspective rock + whip entrance x from +850
ROCK = f"(sin(2*PI*(t-6.6)/5.4))"
b.layer("card_l", f"140+(1-{WIP})*820{DRIFT(7,19,0)}", f"430{DRIFT(9,23,1)}",
        enable=(6.55, 13.0), fades=[("in", 6.6, 0.3), ("out", 8.9, 0.55)])
b.layer("card", f"140+(1-{WIP})*820{DRIFT(7,19,0)}", f"430{DRIFT(9,23,1)}",
        enable=(8.6, 13.5), fades=[("in", 8.6, 0.55), ("out", 11.4, 0.45)])
b.layer("card_r", f"140+(1-{WIP})*820{DRIFT(7,19,0)}", f"430{DRIFT(9,23,1)}",
        enable=(11.2, 13.5), fades=[("in", 11.2, 0.45), ("out", 13.05, 0.3)])
lw2, lh2 = Image.open("plates_v3/lab_orbit.png").size
b.layer("lab_orbit", f"(W-{lw2})/2", f"150{DRIFT(3,12,1)}", enable=(7.1, 13.5),
        fades=[("in", 7.1, 0.5), ("out", 13.0, 0.4)])
# whip smear sweep + leak flash at entrance
b.layer("smear", f"-400+(1-{WIP})*1250", "720", enable=(6.55, 7.35), fades=[("in", 6.58, 0.1)])
b.layer("leak", "0", "0", enable=(6.55, 7.1), fades=[("in", 6.6, 0.08), ("out", 6.75, 0.35)])
# exit whip: leak re-flash + layers handled by fade-outs; smear exit
WIP2 = f"clip((t-12.85)/0.4,0,1)"
b.layer("smear", f"-400+{WIP2}*1250", "820", enable=(12.8, 13.45), fades=[("out", 13.3, 0.1)])
idx_c2 = b.emit()

# ---- B3 13.4-20.6 living mosaic + impact shake -----------------------------
b = Blk("c3", 13.4, 7.2)
ACC = f"exp(-7*max(0,(t-16.0)))*sin(2*PI*14*max(0,(t-16.0)))"
b.layer("wall_b", f"-30{DRIFT(6,19,0)}", f"-220{DRIFT(8,23,1)}", enable=(13.35, 16.05),
        fades=[("in", 13.4, 0.6), ("out", 15.6, 0.5)])
b.layer("wall", f"-30+9*{ACC}{DRIFT(6,19,0)}", f"-220+13*{ACC}{DRIFT(8,23,1)}",
        enable=(15.7, 20.7), fades=[("in", 15.7, 0.5), ("out", 20.2, 0.5)])
b.layer("dustB", f"180+14*{ACC}{DRIFT(18,21,2)}", "340", enable=(13.4, 20.7),
        fades=[("in", 13.6, 0.8), ("out", 20.2, 0.5)])
lw3, _ = Image.open("plates_v3/lab_mosaic.png").size
b.layer("lab_mosaic", f"(W-{lw3})/2+6*{ACC}", f"150{DRIFT(3,12,0)}", enable=(13.9, 20.7),
        fades=[("in", 13.9, 0.5), ("out", 20.2, 0.4)])
# breathing cross-fade: wall→wall_lg subtle at 17.5
b.layer("wall_lg", f"-86+9*{ACC}", f"-327+13*{ACC}", enable=(17.4, 20.7),
        fades=[("in", 17.4, 1.4), ("out", 20.2, 0.5)])
idx_c3 = b.emit()

# ---- B4 20.6-27.2 pullback reveal + living CTA ------------------------------
b = Blk("c4", 20.6, 6.6)
PL = f"clip((t-20.6)/1.6,0,1)*clip((t-20.6)/1.6,0,1)*(3-2*clip((t-20.6)/1.6,0,1))"
b.layer("wall_sm", f"(W-{840})/2{DRIFT(6,21,0)}", f"(H-{1498})/2-240*{PL}{DRIFT(8,25,1)}",
        enable=(20.55, 27.3), fades=[("in", 20.6, 0.6), ("out", 26.4, 0.6)])
b.layer("dustA", f"-60{DRIFT(16,19,2)}", "260", enable=(20.6, 27.3),
        fades=[("in", 20.8, 0.8), ("out", 26.4, 0.6)])
lw4, _ = Image.open("plates_v3/lab_end.png").size
b.layer("lab_end", f"(W-{lw4})/2", f"210{DRIFT(3,12,0)}", enable=(21.4, 27.3),
        fades=[("in", 21.4, 0.5), ("out", 26.4, 0.5)])
# CTA overshoot: sm → full via cross-fade pair + up-expo
PUP = f"(1-pow(2,-10*clip((t-22.2)/0.6,0,1)))"
b.layer("cta_sm", f"(W-{780})/2+{200*(1-0)+0}*0", f"1210-80*{PUP}{DRIFT(4,16,0)}",
        enable=(22.2, 23.0), fades=[("in", 22.2, 0.3), ("out", 22.85, 0.3)])
b.layer("cta", f"(W-{780})/2", f"1210-80*{PUP}{DRIFT(4,16,0)}", enable=(22.75, 27.3),
        fades=[("in", 22.75, 0.3), ("out", 26.4, 0.6)])
b.layer("bokeh", f"100{DRIFT(30,13,1)}", f"700{DRIFT(26,15,2)}", extra="gblur=sigma=8",
        enable=(21.0, 27.3), fades=[("in", 21.0, 1.0), ("out", 26.4, 0.6)])
b.dip(26.4, 27.2, dd=0.5)
idx_c4 = b.emit()

# ---- runner -----------------------------------------------------------------
names = {"c1": (idx_c1, 0.0, 6.6), "c2": (idx_c2, 6.6, 6.8),
         "c3": (idx_c3, 13.4, 7.2), "c4": (idx_c4, 20.6, 6.6)}
sh = ["#!/usr/bin/env bash", "set -e", 'cd "$(dirname "$0")"', "FF=./ffmpeg", "mkdir -p reels_v3"]
for nm, (idx, t0, dur) in names.items():
    ins = ["-f lavfi -i color=c=black:s=1080x1920:r=30:d=%.2f" % dur]
    for p, i in sorted(idx.items(), key=lambda kv: kv[1]):
        ins.append("-loop 1 -framerate 30 -t %.2f -i plates_v3/%s.png" % (dur, p))
    sh.append("$FF -y " + " ".join(ins) +
              f" -/filter_complex graph3_{nm}.txt -map '[vf]' -t {dur:.2f} "
              f"-q:v 2 -start_number 0 -f image2 reels_v3/{nm}_%05d.jpg")
Path("run_v3.sh").write_text("\n".join(sh) + "\n")
print("graphs:", ", ".join(names))
