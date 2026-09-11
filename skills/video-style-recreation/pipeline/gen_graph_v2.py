#!/usr/bin/env python3
"""gen_graph_v2 — emits filtergraph_v2.txt for the dark-premium recreation.
Structure (60s @30fps, 1080x1920):
  B1 0-9    spotlight title      (shaft/clock/dust/moons, defocus-in 'Text 5')
  B2 9-22   chat UI reveal       (bar -> typing dots -> bubble wipe -> 3 chips)
  B3 22-38  3D floor gallery     (outlined T1/T2, cards, ribbon marquee, dolly)
  B4 38-50  cobalt photo wall    (AI wall art, dust, defocus-in 'Text 3')
  B5 50-60  torn-paper wipe      -> collage -> 'Text 4' + CTA card
Laws: constant sin micro-drift on every layer (no holds), expo-out +
(1-pow(2,-10*p)) reveals, 70ms staggers, blur->sharp pairs, dips-to-black
between blocks, global screen bloom + vignette grade."""
from pathlib import Path
from PIL import Image

W, H = 1080, 1920

P = "plates_v2"
size = lambda n: Image.open(f"{P}/{n}.png").size

LINES = []
CH = "0:v"

def inp(i, extra=""):
    LINES.append(f"[{i}:v]format=rgba{extra}[w{i}]")

def layer(inp_i, x, y, enable=None, fades=(), extra_filter="", pre=None):
    """overlay plate input inp_i onto the running canvas chain."""
    global CH
    fx = []
    if pre: fx.append(pre)
    for t, st, d in fades:
        fx.append(f"fade=t={t}:st={st}:d={d}:alpha=1")
    if extra_filter: fx.append(extra_filter)
    if not fx: fx = ["null"]
    src = next(LABELS[inp_i])
    tag = f"e{src}_{len(LINES)}"
    el = f"[{src}]" + (",".join(fx) if fx else "") + f"[{tag}]"
    en = f":enable='between(t,{enable[0]},{enable[1]})'" if enable else ""
    LINES.append(el)
    LINES.append(f"[{CH}][{tag}]overlay='{x}':'{y}'{en}[{CH}_n]")
    CH = CH + "_n"

# ---------------------------------------------------------------- helpers
def dip(st_in, st_out, d=0.22):
    """full-frame dip-to-black using the BLACK input (38)."""
    layer(38, "0", "0", enable=(st_in - 0.05, st_out + 0.35),
          fades=[("in", st_in, d), ("out", st_out, d)])

DRIFT = lambda amp, period, ph: f"+{amp}*sin(2*PI*t/{period}+{ph})"

# ================================================================ B1 0-9s
# shaft sweeping upper-right + dust + moons + chrome clock + defocus title
COUNTS = {38: 4, 29: 2, 4: 2}     # inputs overlaid multiple times (dip black, marquee ribbon)
LABELS = {}
for i in [38] + list(range(1, 38)):
    n = COUNTS.get(i, 1)
    labs = [f"w{i}_{k}" for k in range(n)]
    body = f"[{i}:v]format=rgba"
    if n > 1:
        body += f",split={n}"
    body += "".join(f"[{l}]" for l in labs)
    LINES.append(body)
    LABELS[i] = iter(labs)

layer(3, f"60{DRIFT(9,11,0)}", f"0{DRIFT(6,13,1)}", fades=[("in", 0.0, 0.7), ("out", 8.4, 0.5)])
layer(4, f"0{DRIFT(14,17,0)}", "-60", enable=(0, 9.2), fades=[("in", 0.3, 0.9), ("out", 8.4, 0.6)])        # dustA
layer(5, f"220{DRIFT(18,23,2)}", "250", enable=(0, 9.2), fades=[("in", 0.5, 0.9), ("out", 8.4, 0.6)])      # dustB
layer(6, f"790{DRIFT(6,19,1)}", f"300{DRIFT(8,15,2)}", enable=(0, 9.2), fades=[("in", 0.8, 0.8), ("out", 8.4, 0.5)])
layer(7, f"150{DRIFT(6,17,3)}", f"1380{DRIFT(8,21,0)}", enable=(0, 9.2), fades=[("in", 1.1, 0.8), ("out", 8.4, 0.5)])
# clock: slow settle-in (expo) + micro-drift
layer(1, f"90{DRIFT(9,19,2)}",
      f"430-46*(1-pow(2,-10*clip((t-0.35)/0.8,0,1))){DRIFT(12,23,1)}",
      enable=(0, 9.2), fades=[("in", 0.35, 0.9), ("out", 8.4, 0.55)])
layer(8, "80", f"640{DRIFT(4,12,0)}", fades=[("in", 1.0, 0.4), ("out", 8.4, 0.4)])                         # label1
layer(9, "120", f"840{DRIFT(5,15,0)}", fades=[("in", 1.15, 0.45), ("out", 8.3, 0.5)])                      # title5 blur
layer(10, "120", f"840{DRIFT(5,15,0)}", fades=[("in", 1.6, 0.55), ("out", 8.3, 0.5)])                      # title5 sharp
dip(8.55, 8.95)

# ================================================================ B2 9-22s
cwl, cwh = size("chatlabel")
layer(11, f"(W-{cwl})/2", f"150{DRIFT(4,13,0)}", enable=(9, 22.4), fades=[("in", 9.15, 0.4), ("out", 21.5, 0.5)])
barw, barh = size("chatbar")
layer(12, f"(W-{barw})/2", f"960+24*(1-pow(2,-10*clip((t-9.3)/0.5,0,1))){DRIFT(3,15,1)}",
      enable=(9, 22.4), fades=[("in", 9.3, 0.45), ("out", 21.5, 0.5)])
# typing dots cycle (0.9s)
for k, i in enumerate((13, 14, 15)):
    layer(i, f"(W-{barw})/2+60", "985", enable=(9.75 + k * 0.3, 10.05 + k * 0.3) if False else (9.7 + k * 0.3, 10.6),
          fades=[("in", 9.75 + k * 0.3, 0.12), ("out", 10.25 + k * 0.3, 0.12)])
# bubble + text: wipe-typing reveal. answer plate slides up expo; black cover slides right
aw, ah = size("answertext")
layer(16, f"(W-{aw})/2", f"640-18*(1-pow(2,-10*clip((t-10.55)/0.45,0,1))){DRIFT(2,14,2)}",
      enable=(10.5, 22.4), fades=[("in", 10.55, 0.25), ("out", 21.5, 0.5)])
cvw, cvh = size("cover")
layer(17, f"(W-{aw})/2+(clip((t-10.6)/1.5,0,1))*{aw+40}", f"640-18*(1-pow(2,-10*clip((t-10.55)/0.45,0,1)))",
      enable=(10.6, 12.2), fades=[])
# chips staggered 70ms, expo grow
cw = size("chip_0")[0]
chips_x = f"(W-(3*{cw}+2*56))/2"
for k, i in enumerate((18, 19, 20)):
    T = 12.9 + k * 0.07
    layer(i, f"{chips_x}+({cw}+56)*{k}",
          f"1135-22*(1-pow(2,-10*clip((t-{T})/0.45,0,1))){DRIFT(2,13,k)}",
          enable=(T, 22.4), fades=[("in", T, 0.25), ("out", 21.5, 0.5)])
dip(21.6, 22.0)

# ================================================================ B3 22-38s
fw, fh = size("floorgrad")
layer(21, "0", f"{1080 + 120}{DRIFT(6,21,0)}", enable=(22, 38.4), fades=[("in", 22.25, 0.6), ("out", 37.4, 0.7)])
slow = 30 * 0  # placeholder; dolly via lateral parallax below
b1w, b1h = size("bigT1"); b2w, b2h = size("bigT2")
# outlined numerals: T1 exits left, T2 enters right mid-block
layer(22, f"150-140*clip((t-29)/4.5,0,1){DRIFT(5,17,0)}", f"560{DRIFT(6,19,1)}",
      enable=(22, 38.4), fades=[("in", 22.3, 0.5), ("out", 33.6, 0.6)])
layer(23, f"620-(620-140)*clip((t-29)/4.5,0,1)+140*clip((t-33.5)/4,0,1){DRIFT(5,15,2)}", f"560{DRIFT(6,19,0)}",
      enable=(28.9, 38.4), fades=[("in", 30.6, 0.5), ("out", 37.4, 0.7)])
flw, flh = size("floorword")
layer(24, f"(W-{flw})/2", f"900{DRIFT(4,16,1)}", enable=(22, 38.4), fades=[("in", 22.45, 0.5), ("out", 37.4, 0.7)])
lblw, lblh = size("floorlabel")
layer(25, f"(W-{lblw})/2", f"220{DRIFT(3,13,0)}", enable=(22, 38.4), fades=[("in", 22.5, 0.4), ("out", 37.4, 0.6)])
# cards: staggered-anchored perspective cards with parallax dolly
card_pos = [(26, 150, 1240, 1.0), (27, 430, 1335, 1.6), (28, 700, 1430, 2.3)]
for i, X0, Y0, ph in card_pos:
    T = 23.3 + (i - 26) * 0.09
    cw2, chh = size({26: "cardA", 27: "cardB", 28: "cardC"}[i])
    layer(i, f"{X0}+34*clip((t-22.5)/15,0,1){DRIFT(5, 14 + ph, ph)}",
          f"{Y0}-26*(1-pow(2,-10*clip((t-{T})/0.6,0,1))){DRIFT(6,17,ph)}",
          enable=(T, 38.4), fades=[("in", T, 0.5), ("out", 37.4, 0.7)])
# ribbon marquee (two copies for seamless wrap)
rw, rh = size("ribbon")
P_ = rw
for k in range(2):
    layer(29, f"-mod((t-22)*85,{P_})+{P_}*{k}", f"1690{DRIFT(3,18,1)}",
          enable=(22.9, 38.4), fades=[("in", 22.9, 0.5), ("out", 37.4, 0.6)])
dip(37.55, 37.95)

# ================================================================ B4 38-50s
layer(2, f"0{DRIFT(8,23,1)}", f"-15+ (t-38)*0.9", enable=(38, 50.4), fades=[("in", 38.2, 0.7), ("out", 49.6, 0.6)])
layer(4, f"-40{DRIFT(16,19,2)}", "300", enable=(38, 50.4), fades=[("in", 38.5, 0.9), ("out", 49.6, 0.6)])
l4w, l4h = size("label4")
layer(30, f"(W-{l4w})/2", f"190{DRIFT(3,12,0)}", enable=(38, 50.4), fades=[("in", 38.6, 0.4), ("out", 49.6, 0.5)])
t3w, t3h = size("title3")
bx = int((W - t3w) / 2)
layer(31, f"{bx}", f"700{DRIFT(4,14,0)}", enable=(38, 50.4), fades=[("in", 38.75, 0.45), ("out", 49.6, 0.5)])
layer(32, f"{bx}", f"700{DRIFT(4,14,0)}", enable=(38, 50.4), fades=[("in", 39.2, 0.55), ("out", 49.6, 0.5)])

# ---- torn-paper sweep (replaces dip): tear plate slides down past frame ----
tw, th = size("tear")
layer(33, "0", f"-{H - 40}+(t-49.85)*{H + 300}/1.35", enable=(49.85, 51.55))

# ================================================================ B5 50-60s
cgw, cgh = size("collage")
layer(34, f"(W-{cgw})/2{DRIFT(6,19,1)}", f"300{DRIFT(7,23,2)}", enable=(50.2, 60.2), fades=[("in", 50.2, 0.5), ("out", 59.4, 0.6)])
rlw, rlh = size("redlabel")
layer(35, f"(W-{rlw})/2", f"115{DRIFT(3,12,0)}", enable=(51.0, 60.2), fades=[("in", 51.0, 0.4), ("out", 59.4, 0.5)])
r4w, r4h = size("red4")
layer(36, f"(W-{r4w})/2-6*(1-pow(2,-10*clip((t-51.2)/0.6,0,1)))",
      f"760{DRIFT(4,15,1)}", enable=(51.0, 60.2), fades=[("in", 51.2, 0.5), ("out", 59.4, 0.5)])
ctw, cth = size("cta")
layer(37, f"(W-{ctw})/2", f"1240-30*(1-pow(2,-10*clip((t-53.4)/0.7,0,1))){DRIFT(4,16,0)}",
      enable=(53.3, 60.2), fades=[("in", 53.4, 0.6), ("out", 59.4, 0.6)])

# ---- final fade to black + global grade: bloom -> contrast -> vignette ----
layer(38, "0", "0", enable=(59.5, 60.2), fades=[("in", 59.5, 0.5, ), ("out", 60.0, 0.02)])
LINES.append(f"[{CH}]split[v_src][v_bm]")
LINES.append("[v_bm]gblur=sigma=26[v_bmg]")
LINES.append("[v_src][v_bmg]blend=all_mode='screen':all_opacity=0.20[v_bb]")
LINES.append("[v_bb]eq=contrast=1.07:brightness=0.004:saturation=0.97,"
             "vignette=angle=PI/4.7,format=yuv420p[vf]")

Path("filtergraph_v2.txt").write_text(";\n".join(LINES) + "\n", encoding="utf-8")
print("graph lines:", len(LINES))
