#!/usr/bin/env python3
"""Video-1 style recreator: 78s animated workout explainer.

Implements the STYLE_ANALYSIS.md spec:
  - duotone lavender world / yellow hero / deep-violet tiles
  - zero-cut grammar (ONE hard cut: the sponsor boundary at t=43)
  - pose-hold discipline (0.45s down / 0.9s up loop), rep-counter numeral pops
  - progression-ladder infographic with back-ease chip pops
  - sunburst sponsor hero with AD tag + coupon pop
  - finale impact stutter + GOLD SET, space outro
Outputs: plates/, filtergraph_v1.txt, render command + audio mix command.
"""
from __future__ import annotations
import math

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "pylibs"))
from PIL import Image, ImageDraw, ImageFont  # noqa: E402

HERE = Path(__file__).resolve().parent
ASSETS = HERE / "assets"
PLATES = HERE / "plates"
PLATES.mkdir(exist_ok=True)

W, H, FPS, DUR = 1920, 1080, 30, 78.0
SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
VIOLET = "#4B2B8C"; LAV = "#D6CEEA"; LAV_MID = "#9887C6"; CREAM = "#F6F1DE"
WHITE = "#F7F4FF"; GOLD = "#F6C945"; INK = "#241B33"

S = lambda k: round(k)  # scale helper (stage == 1080p)


# ── text/plate factory ────────────────────────────────────────────────────────

def slab_text(text, size, fill, file, shear=0.22, stroke=0, pad=26):
    """Chunky italic-slab numeral/word on transparent plate."""
    font = ImageFont.truetype(SERIF, size)
    tmp = Image.new("RGBA", (10, 10), (0, 0, 0, 0))
    d = ImageDraw.Draw(tmp)
    bb = d.textbbox((0, 0), text, font=font, stroke_width=stroke)
    w, h = bb[2] - bb[0], bb[3] - bb[1]
    img = Image.new("RGBA", (w + pad * 2 + int(h * abs(shear)), h + pad * 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.text((pad - bb[0], pad - bb[1]), text, font=font, fill=fill,
           stroke_width=stroke, stroke_fill=fill)
    if shear:
        img = img.transform(img.size, Image.AFFINE, (1, shear, int(-h * shear * 0.5), 0, 1, 0))
    img.save(PLATES / file)
    return img.size


def card(w, h, bg, file, radius=28, outline=None, ow=8):
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([0, 0, w - 1, h - 1], radius, fill=bg,
                        outline=outline, width=ow)
    return img, d


def text_card(text, sub, w, h, bg, fg, file, size=64, subsize=40):
    img, d = card(w, h, bg, file, outline=INK, ow=10)
    f = ImageFont.truetype(SANS, size)
    bb = d.textbbox((0, 0), text, font=f)
    d.text(((w - (bb[2] - bb[0])) / 2, h / 2 - (bb[3] - bb[1]) - (subsize if sub else 0)),
           text, font=f, fill=fg)
    if sub:
        f2 = ImageFont.truetype(SANS, subsize)
        bb2 = d.textbbox((0, 0), sub, font=f2)
        d.text(((w - (bb2[2] - bb2[0])) / 2, h / 2 + 24), sub, font=f2, fill=fg)
    img.save(PLATES / file)


def title_card():
    img = Image.new("RGBA", (W, H), VIOLET)
    d = ImageDraw.Draw(img)
    f = ImageFont.truetype(SANS, 210)
    bb = d.textbbox((0, 0), "PUSH-UPS", font=f)
    d.text(((W - bb[2] + bb[0]) / 2, (H - bb[3] + bb[1]) / 2 - 30), "PUSH-UPS", font=f, fill=WHITE)
    img.save(PLATES / "title.png")


def sunburst(name, phase=0):
    img = Image.new("RGBA", (W, H), LAV_MID)
    d = ImageDraw.Draw(img)
    import math
    cx, cy = W // 2, int(H * 0.46)
    for i in range(12):
        a0 = math.radians(i * 30 + phase)
        a1 = math.radians(i * 30 + 30 * 0.52 + phase)
        pts = [(cx, cy),
               (cx + 1600 * math.cos(a0), cy + 1600 * math.sin(a0)),
               (cx + 1600 * math.cos(a1), cy + 1600 * math.sin(a1))]
        d.polygon(pts, fill="#F3DAD9")
    img.save(PLATES / name)


def ladder():
    img = Image.new("RGBA", (620, 900), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    line = dict(fill="#F7F4FF", width=22)
    d.line([(70, 890), (70, 240)], **line)
    d.line([(550, 890), (550, 240)], **line)
    d.arc([70, 20, 550, 460], 180, 360, fill="#F7F4FF", width=22)
    for i, y in enumerate([300, 420, 540, 660, 780]):
        d.line([(70, y), (550, y)], fill="#F7F4FF", width=16)
    img.save(PLATES / "ladder.png")


def white_plate():
    Image.new("RGBA", (W, H), (255, 255, 255, 255)).save(PLATES / "white.png")


# ── numerals 4..18, chips, cards ─────────────────────────────────────────────
for n in range(4, 19):
    slab_text(str(n), 150, VIOLET, f"num_{n}.png", stroke=2)
for i, chip in enumerate(["6x", "8x", "10x", "12x", "15x"]):
    text_card(chip, None, 170, 92, VIOLET, WHITE, f"chip_{i}.png", size=60)
text_card("+27%", "MASS", 300, 150, CREAM, VIOLET, "bubble.png", size=64, subsize=36)
text_card("10% OFF", "CODE: VOLT10", 560, 240, CREAM, VIOLET, "coupon.png", size=88, subsize=44)
text_card("ADVERTISEMENT", None, 380, 64, GOLD, INK, "adtag.png", size=34)
text_card("PULLPRO", None, 460, 100, WHITE, VIOLET, "brand.png", size=64)
gs = slab_text("GOLD SET", 120, GOLD, "goldset.png", shear=0.15, stroke=3)
from PIL import ImageDraw as _ID
from PIL import Image as _I
im0 = _I.open("plates/goldset.png").convert("RGBA")
x_max = max(x for x in range(im0.width) for y in range(0, im0.height, 4) if im0.getpixel((x,y))[3] > 40)
R, r, gap = 80, 32, 30
im = _I.new("RGBA", (x_max + gap + 2*R + 10, im0.height), (0,0,0,0))
im.paste(im0, (0,0)); d = _ID.Draw(im)
cx, cy = x_max + gap + R, im.height//2
pts = []
for i in range(10):
    ang = -math.pi/2 + i*math.pi/5; rad = R if i%2==0 else r
    pts.append((cx+rad*math.cos(ang), cy+rad*math.sin(ang)))
d.polygon(pts, fill=GOLD, outline=INK, width=6)
im.save("plates/goldset.png")
slab_text("fin.", 110, WHITE, "fin.png", shear=0.0)
title_card(); sunburst("burst_a.png", 0); sunburst("burst_b.png", 15); ladder(); white_plate()

# ── green plate bboxes ────────────────────────────────────────────────────────
def content_bbox(p):
    im = Image.open(p).convert("RGB")
    w, h = im.size
    px = im.load(); xs, ys = [], []
    for y in range(0, h, 3):
        for x in range(0, w, 3):
            r, g, b = px[x, y]
            if not (g > 120 and g > r * 1.35 and g > b * 1.35):
                xs.append(x); ys.append(y)
    return (min(xs), min(ys), max(xs) + 3, max(ys) + 3)

bb = {k: content_bbox(ASSETS / f"v1_{k}.png")
      for k in ("hero_down", "hero_up", "hamster", "bar", "box", "jag")}

# stage sizes
def scaled(bbox, width):
    cw, ch = bbox[2] - bbox[0], bbox[3] - bbox[1]
    return width, round(ch * width / cw)

HERO_W, HERO_HH = scaled(bb["hero_up"], 860)
HERO_DOWN_W, HERO_DOWN_H = scaled(bb["hero_down"], 880)
HAM_W, HAM_H = scaled(bb["hamster"], 430)
BAR_W, BAR_H = scaled(bb["bar"], 660)
BOX_W, BOX_H = scaled(bb["box"], 620)
JAG_W, JAG_H = scaled(bb["jag"], 320)

FLOOR_Y = 875            # room plate floor line on 1080p stage (612/768*1080 ≈ 861 + margin)
HERO_X = 420             # hero left (side-view faces right)
HERO_UP_Y = FLOOR_Y - HERO_HH + 30
HAM_X = 1330
HAM_Y = FLOOR_Y - HAM_H + 8

plan = {
    "video": "v1_recreation_cut1.mp4", "fps": FPS, "dur": DUR,
    "structure": "cold 0-6 / title 6-8.2 / room 8.2-30 / ladder 30-43 / "
                 "SPONSOR(cut) 43-58 / finale 58-70 / space outro 70-78",
    "numerals": {str(n): [] for n in range(4, 19)},
}
(HERE / "v1_plan.json").write_text(json.dumps(plan, indent=2))

# ── keyframe expression helpers (reuse semantics from gen_render.py) ─────────
def track_expr(keys):
    kv = lambda k: (k[0], k[1], k[2] if len(k) > 2 else "smooth")
    expr = f"{kv(keys[-1])[1]:g}"
    for i in reversed(range(len(keys) - 1)):
        t0, v0, _ = kv(keys[i]); t1, v1, ease = kv(keys[i + 1])
        c = f"((t-{t0:g})/{t1 - t0:g})"
        if ease == "back":
            e = f"(1+2.70158*pow({c}-1,3)+1.70158*pow({c}-1,2))"
        elif ease == "in":
            e = f"pow({c},3)"
        elif ease == "out":
            e = f"(1-pow(1-{c},3))"
        else:
            e = f"(3*pow({c},2)-2*pow({c},3))"
        seg = f"({v0:g}+({v1:g}-{v0:g})*{e})"
        expr = f"if(lt(t,{t1:g}),{seg},{expr})"
    return expr

def wins(pairs):  # enable windows
    return "+".join(f"between(t,{a:g},{b:g})" for a, b in pairs)

ON = "(on/30)"
def sub_t(expr):
    return expr.replace("lt(t,", f"lt({ON},").replace("(t-", f"({ON}-").replace("t*", f"{ON}*")

# rep schedule: (time_of_down→up_switch, numeral, x)
reps = []
t = 0.9
for n, tt in [(4, 0.9), (5, 2.3), (6, 3.7), (7, 5.1),          # cold open
              (9, 9.2), (10, 10.8), (11, 12.4), (12, 14.0),     # room B
              (13, 16.0), (14, 18.0),
              (15, 58.6), (16, 60.2), (17, 61.8), (18, 66.2)]:  # finale
    reps.append((tt, n))

# hero pose windows: down from rep_t-0.45 to rep_t+0.45; up otherwise within
# [0,30) and [58,67]. Generate alternating windows.
down_w, up_w = [], []
scene_bounds = [(0.0, 29.9), (57.9, 66.6)]
for s, e in scene_bounds:
    cur = s
    for tt, _ in reps:
        if not (s <= tt < e):
            continue
        up_w.append((cur, tt - 0.45))
        down_w.append((tt - 0.45, tt + 0.45))
        cur = tt + 0.45
    up_w.append((cur, e))
up_w = [(a, b) for a, b in up_w if b - a > 0.02]

cam_z = [(0, 1.0), (6, 1.05), (8.2, 1.05), (30, 1.08), (31.5, 1.12), (42, 1.12),
         (43, 1.02), (58, 1.02), (59, 1.05), (66.2, 1.05), (67.6, 1.24),
         (69.5, 1.24), (70.2, 1.06), (78, 1.1)]
cam_x = [(0, 960), (30, 960), (31.5, 1085), (43, 1085), (43.05, 960), (58, 960),
         (66.2, 960), (67.6, 900), (70.2, 960), (78, 960)]
cam_y = [(0, 540), (31.5, 540), (42, 500), (43, 500), (43.05, 540),
         (67.6, 520), (70.2, 540), (78, 530)]

zc, xc, yc = (sub_t(track_expr(k)) for k in (cam_z, cam_x, cam_y))

# title slide (full-frame overlay x position, stage units)
title_x = track_expr([(0, W + 10), (6.0, W + 10), (6.5, 0, "out"),
                      (7.6, 0), (8.2, -W - 10, "in"), (99, -W - 10)])
# ladder + chips zone (chips ascend rungs left of ladder plate)
lad_x = 1310
chip_specs = [(31.0, 0), (33.5, 1), (36.0, 2), (38.5, 3), (41.0, 4)]
rung_y = [780, 660, 540, 420, 300]

lines = []
add = lines.append
add(f"[0:v]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},fps={FPS}[bg];")
add(f"[6:v]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},fps={FPS}[space];")
# room -> space swap
add(f"[bg][space]overlay=0:0:enable='gte(t,70)'[s_bg];")

def keyed(idx, bbox, width):
    x0, y0, x1, y1 = bbox
    return (f"[{idx}:v]crop={x1 - x0}:{y1 - y0}:{x0}:{y0},"
            f"colorkey=0x00FF00:0.36:0.10,scale={width}:-1,format=rgba")

prev = "s_bg"
def ov(prev, chain, x, y, enable="", name="", eval="frame"):
    en = f":enable='{enable}'" if enable else ""
    out = f"[{name}]" if name else ""
    add(f"{chain}; [{prev}][{chain.split('[')[-1].split(']')[0]}]overlay=x='{x}':y='{y}':eval={eval}{en}{out};")
    return name

add(keyed(1, bb["hero_down"], HERO_DOWN_W) + "[hd];")
add(keyed(2, bb["hero_up"], HERO_W) + "[hu];")
add(keyed(3, bb["hamster"], HAM_W) + "[hm];")
add(keyed(4, bb["bar"], BAR_W) + "[br];")
add(keyed(5, bb["box"], BOX_W) + "[bx0];")
add("[bx0]split=2[bx][bxO];")
add(keyed(7, bb["jag"], JAG_W) + "[jg0];")
add("[jg0]split=3[jg][jgS][jgF];")
# hero shadow: soft ellipse via box alpha? skip — pose plates already grounded.

add(f"[s_bg][hu]overlay=x='{HERO_X}+3*sin(t*2.1)'"
    f":y='{HERO_UP_Y}+4*sin(t*2.1)':enable='{wins(up_w)}'[s_hu];")
down_y = FLOOR_Y - HERO_DOWN_H + 30
add(f"[s_hu][hd]overlay=x='{HERO_X - 10}+2*sin(t*2.1)'"
    f":y='{down_y}+3*sin(t*2.1)':enable='{wins(down_w)}'[s_hd];")
# hamster: running bounce + rotate jiggle, then the 14.5s "falls off" gag
ham_y = track_expr([(0, HAM_Y), (14.5, HAM_Y), (14.75, HAM_Y + 120, "in"),
                    (15.0, HAM_Y + 80, "out"), (99, HAM_Y + 80)])
ham_enable = wins([(0, 29.9)])
add(f"[hm]rotate=a='0.03*sin(9*t)':ow=rotw(0):oh=roth(0):fillcolor=none[hmr];")
add(f"[s_hd][hmr]overlay=x='{HAM_X}':y='({ham_y})+4*abs(sin(t*11))'"
    f":enable='{ham_enable}'[s_hm];")
add(f"[s_hm][jg]overlay=x='{HAM_X + 60}':y='{HAM_Y - 90}':enable='between(t,14.5,14.68)'[s_j1];")

# numerals pop (each kept 1.15s, y-drop settle)
prev = "s_j1"
for i, (tt, n) in enumerate(reps):
    ypop = track_expr([(0, 250), (tt, 250), (tt + 0.12, 300, "out"), (tt + 99, 300)])
    out = f"s_n{i}"
    add(f"[{prev}][{i + 8}:v]overlay=x='{HERO_X + 430}':y='{ypop}'"
        f":enable='between(t,{tt + 0.42:g},{tt + 1.5:g})'[{out}];")
    prev = out

# infographic: ladder + chips + bubble (hero exits left by then)
add(f"[{prev}][22:v]overlay=x='{lad_x}':y='60':enable='between(t,30,42.9)'[s_lad];")
prev = "s_lad"
for i, (tt, k) in enumerate(chip_specs):
    ypop = track_expr([(0, rung_y[k] + 46), (tt, rung_y[k] + 46),
                       (tt + 0.22, rung_y[k], "back"), (99, rung_y[k])])
    out = f"s_c{i}"
    add(f"[{prev}][{23 + i}:v]overlay=x='{lad_x + 225 - 85}':y='{ypop}'"
        f":enable='between(t,{tt:g},42.9)'[{out}];")
    prev = out
bub_pop = track_expr([(0, 900), (39.5, 900), (39.85, 545, "back"), (99, 545)])
add(f"[{prev}][28:v]overlay=x='{lad_x - 330}':y='{bub_pop}':enable='between(t,39.5,42.9)'[s_bub];")

# ── SPONSOR (the single hard cut at 43) ──
burst_cycle = f"lt(mod(t,0.56),0.28)"  # flick the two ray phases
add(f"[s_bub][29:v]overlay=0:0:enable='between(t,43,58)*{burst_cycle}'[s_ba];")
add(f"[s_ba][30:v]overlay=0:0:enable='between(t,43,58)*(1-{burst_cycle})'[s_bb];")
add(f"[s_bb][bx]overlay=x='650':y='{FLOOR_Y - BOX_H + 40}':enable='between(t,43,58)'[s_b1];")
add(f"[s_b1][32:v]overlay=x='730':y='{FLOOR_Y - BOX_H + 150}':enable='between(t,43.4,58)'[s_b2];")
bar_y = track_expr([(0, 250), (43, 250), (58, 250)])
add(f"[br]rotate=a='0.05*sin(1.6*t)':ow=rotw(0):oh=roth(0):fillcolor=none[brr];")
add(f"[s_b2][brr]overlay=x='630':y='({bar_y})+14*sin(2.2*t)':enable='between(t,43.2,58)'[s_b3];")
add(f"[s_b3][33:v]overlay=x='1510':y='985':enable='gte(t,43)*lt(t,58)'[s_b4];")
coup_y = track_expr([(0, 1300), (52.5, 1300), (52.95, 640, "back"), (99, 640)])
add(f"[s_b4][31:v]overlay=x='180':y='{coup_y}':enable='between(t,52.5,58)'[s_b5];")
# gag: bar slips when VO says "basically free gainz" (~56.5s)
add(f"[s_b5][jgS]overlay=x='1030':y='330':enable='between(t,55.85,56.05)'[s_b6];")

# title card wipe (above everything in its window)
add(f"[s_b6][34:v]overlay=x='{title_x}':y='0':eval=frame[s_tt];")
# finale stutter jag + GOLD SET + flashes
add(f"[s_tt][jgF]overlay=x='700':y='300':enable='between(t,66.2,66.45)'[s_st];")
gs_y = track_expr([(0, 1300), (66.45, 1300), (66.8, 330, "back"), (99, 330)])
add(f"[s_st][35:v]overlay=x='620':y='{gs_y}':enable='gte(t,66.45)*lt(t,70)'[s_gs];")
add(f"[36:v]split=2[wfA][wfB];")
add(f"[s_gs][wfA]overlay=0:0:enable='between(t,66.2,66.26)'[s_f1];")
add(f"[s_f1][wfB]overlay=0:0:enable='between(t,66.38,66.44)'[s_f2];")
# space outro extras: floating box + fin
box_x = track_expr([(0, -700), (70, -700), (73.5, 620, "out"), (78, 680)])
box_y2 = track_expr([(0, 330), (78, 300)])
add(f"[s_f2][bxO]overlay=x='{box_x}':y='({box_y2})+10*sin(1.4*t)':enable='gte(t,70)'[s_ob];")
fin_a = track_expr([(0, 1300), (74, 1300), (74.5, 880, "out"), (99, 880)])
add(f"[s_ob][37:v]overlay=x='884':y='{fin_a}':enable='gte(t,74)'[s_fin];")
# camera + grain + out
add(f"[s_fin]zoompan=z='{zc}':x='({xc})-iw/zoom/2':y='({yc})-ih/zoom/2'"
    f":d=1:s=1920x1080:fps={FPS},noise=alls=3:allf=t,"
    f"fade=t=out:st=76.4:d=1.6,format=yuv420p[out]")

graph = "\n".join(l for l in lines)
(HERE / "filtergraph_v1.txt").write_text(graph)
print("plates:", len(list(PLATES.glob('*.png'))), "| graph lines:", len(lines))
