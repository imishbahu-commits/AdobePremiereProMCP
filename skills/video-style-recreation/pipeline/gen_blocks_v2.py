#!/usr/bin/env python3
"""gen_blocks_v2 — per-block filtergraphs for the 60s recreation.
Each block renders standalone (memory-bounded) with its own plate subset,
then reels concat + global grade + audio. Times are re-based to block-local.
Blocks: b1 0-9.4 | b2 9-22.4 | b3 22-38.4 | b4 38-50.5 | b5 49.85-60.0
"""
import re
from pathlib import Path
from PIL import Image

W, H = 1080, 1920
DRIFT = lambda amp, period, ph: f"+{amp}*sin(2*PI*t/{period}+{ph})"
size = lambda n: Image.open(f"plates_v2/{n}.png").size

class Block:
    def __init__(self, name, t0, dur, closetime=None):
        self.name, self.t0, self.dur = name, t0, dur
        self.lines, self.ch = [], "0:v"
        self.uses = {}          # plate name (and 'BLACKdip') -> count
        self.layers = []
        self.warm_dip = []

    def use(self, plate):
        self.uses[plate] = self.uses.get(plate, 0) + 1
        return self.uses[plate] - 1

    def layer(self, plate, x, y, enable=None, fades=(), enable_point=None):
        k = self.use(plate)
        tag = f"{plate.replace('.', '_')}_{k}"
        fx = [f"fade=t={t}:st={max(0.0, st - self.t0)}:d={d}:alpha=1" for t, st, d in fades] or ["null"]
        self.lines.append(f"[w_{tag}]" + ",".join(fx) + f"[e_{tag}]")
        def _rebase(m):
            d = float(m.group(1)) - self.t0
            return f"(t+{-d:.4f})" if d < 0 else f"(t-{d:.4f})"
        x = re.sub(r"\(t-([0-9]+(?:\.[0-9]+)?)\)", _rebase, x)
        y = re.sub(r"\(t-([0-9]+(?:\.[0-9]+)?)\)", _rebase, y)
        en = ""
        if enable:
            en = f":enable='between(t,{max(0.0, enable[0]-self.t0):.3f},{enable[1]-self.t0:.3f})'"
        elif enable_point is not None:
            en = f":enable='{enable_point}'"
        self.lines.append(f"[{self.ch}][e_{tag}]overlay='{x}':'{y}'{en}[{self.ch}_n]")
        self.ch += "_n"

    def dip(self, st_in, st_out, d=0.22):
        self.layer("BLACKdip", "0", "0",
                   enable=(st_in - 0.05, st_out + 0.35),
                   fades=[("in", st_in, d), ("out", st_out, d)])

    def emit(self):
        dip_labels = [f"w_BLACKdip_{k}" for k in range(self.uses.get("BLACKdip", 0))]
        canvas_tabs = len(dip_labels) + 1
        head = ["[0:v]format=rgba,split=%d[cv0]%s" % (canvas_tabs, "" if not dip_labels else "".join(f"[{l}]" for l in dip_labels))]
        plate_idx = {}
        plates = [p for p in self.uses if p != "BLACKdip"]
        for i, p in enumerate(plates):
            plate_idx[p] = i + 1
            cnt = self.uses[p]
            labs = [f"w_{p}_{k}" for k in range(cnt)]
            body = f"[{i+1}:v]format=rgba"
            if cnt > 1:
                body += f",split={cnt}"
            body += "".join(f"[{l}]" for l in labs)
            head.append(body)
        body_lines = []
        for l in self.lines:
            l = re.sub(r"\[0:v(?:_n)*\]", lambda m: "[cv0" + "_n" * m.group(0).count("_n") + "]", l)
            body_lines.append(l)
        body_lines[-1] = re.sub(r"\[[\w:]+\]\s*$", "[vpre]", body_lines[-1])
        grade = [
            "[vpre]split[v_src][v_bm]",
            "[v_bm]gblur=sigma=26[v_bmg]",
            "[v_src][v_bmg]blend=all_mode='screen':all_opacity=0.20[v_bb]",
            "[v_bb]eq=contrast=1.07:brightness=0.004:saturation=0.97,vignette=angle=PI/4.7,format=yuv420p[vf]",
        ]
        all_lines = head + body_lines + grade
        Path(f"graph_{self.name}.txt").write_text(";\n".join(all_lines) + "\n")
        return plate_idx


# ---------------- scene registrations (absolute global times; layer() rebases) ----------------
def scene_b1(b):
    b.layer("shaft", f"60{DRIFT(9,11,0)}", f"0{DRIFT(6,13,1)}", fades=[("in", 0.0, 0.7), ("out", 8.4, 0.5)])
    b.layer("dustA", f"0{DRIFT(14,17,0)}", "-60", enable=(0, 9.2), fades=[("in", 0.3, 0.9), ("out", 8.4, 0.6)])
    b.layer("dustB", f"220{DRIFT(18,23,2)}", "250", enable=(0, 9.2), fades=[("in", 0.5, 0.9), ("out", 8.4, 0.6)])
    b.layer("moonA", f"790{DRIFT(6,19,1)}", f"300{DRIFT(8,15,2)}", enable=(0, 9.2), fades=[("in", 0.8, 0.8), ("out", 8.4, 0.5)])
    b.layer("moonB", f"150{DRIFT(6,17,3)}", f"1380{DRIFT(8,21,0)}", enable=(0, 9.2), fades=[("in", 1.1, 0.8), ("out", 8.4, 0.5)])
    b.layer("clock_a", f"90{DRIFT(9,19,2)}", f"430-46*(1-pow(2,-10*clip((t-0.35)/0.8,0,1))){DRIFT(12,23,1)}",
            enable=(0, 9.2), fades=[("in", 0.35, 0.9), ("out", 8.4, 0.55)])
    b.layer("label1", "80", f"640{DRIFT(4,12,0)}", fades=[("in", 1.0, 0.4), ("out", 8.4, 0.4)])
    b.layer("title5_blur", "120", f"840{DRIFT(5,15,0)}", fades=[("in", 1.15, 0.45), ("out", 8.3, 0.5)])
    b.layer("title5", "120", f"840{DRIFT(5,15,0)}", fades=[("in", 1.6, 0.55), ("out", 8.3, 0.5)])
    b.dip(8.55, 8.95)

def scene_b2(b):
    barw, barh = size("chatbar"); cwl, cwh = size("chatlabel")
    b.layer("chatlabel", f"(W-{cwl})/2", f"150{DRIFT(4,13,0)}", enable=(9, 22.4), fades=[("in", 9.15, 0.4), ("out", 21.5, 0.5)])
    b.layer("chatbar", f"(W-{barw})/2", f"960+24*(1-pow(2,-10*clip((t-9.3)/0.5,0,1))){DRIFT(3,15,1)}",
            enable=(9, 22.4), fades=[("in", 9.3, 0.45), ("out", 21.5, 0.5)])
    for k, i in enumerate(("dots_0", "dots_1", "dots_2")):
        st = 9.75 + k * 0.3
        b.layer(i, f"(W-{barw})/2+60", "985", enable=(9.7 + k * 0.3, 10.6),
                fades=[("in", st, 0.12), ("out", st + 0.5, 0.12)])
    aw, ah = size("answertext")
    b.layer("answertext", f"(W-{aw})/2", f"640-18*(1-pow(2,-10*clip((t-10.55)/0.45,0,1))){DRIFT(2,14,2)}",
            enable=(10.5, 22.4), fades=[("in", 10.55, 0.25), ("out", 21.5, 0.5)])
    b.layer("cover", f"(W-{aw})/2+(clip((t-10.6)/1.5,0,1))*{aw+40}",
            f"640-18*(1-pow(2,-10*clip((t-10.55)/0.45,0,1)))", enable=(10.6, 12.2))
    cw = size("chip_0")[0]; chips_x = f"(W-(3*{cw}+2*56))/2"
    for k, i in enumerate(("chip_0", "chip_1", "chip_2")):
        T = 12.9 + k * 0.07
        b.layer(i, f"{chips_x}+({cw}+56)*{k}", f"1135-22*(1-pow(2,-10*clip((t-{T})/0.45,0,1))){DRIFT(2,13,k)}",
                enable=(T, 22.4), fades=[("in", T, 0.25), ("out", 21.5, 0.5)])
    b.dip(21.6, 22.0)

def scene_b3(b):
    b1w, b1h = size("bigT1"); flw, flh = size("floorword"); lblw, lblh = size("floorlabel")
    b.layer("floorgrad", "0", f"1200{DRIFT(6,21,0)}", enable=(22, 38.4), fades=[("in", 22.25, 0.6), ("out", 37.4, 0.7)])
    b.layer("bigT1", f"150-140*clip((t-29)/4.5,0,1){DRIFT(5,17,0)}", f"560{DRIFT(6,19,1)}",
            enable=(22, 38.4), fades=[("in", 22.3, 0.5), ("out", 33.6, 0.6)])
    b.layer("bigT2", f"620-(620-140)*clip((t-29)/4.5,0,1)+140*clip((t-33.5)/4,0,1){DRIFT(5,15,2)}", f"560{DRIFT(6,19,0)}",
            enable=(28.9, 38.4), fades=[("in", 30.6, 0.5), ("out", 37.4, 0.7)])
    b.layer("floorword", f"(W-{flw})/2", f"900{DRIFT(4,16,1)}", enable=(22, 38.4), fades=[("in", 22.45, 0.5), ("out", 37.4, 0.7)])
    b.layer("floorlabel", f"(W-{lblw})/2", f"220{DRIFT(3,13,0)}", enable=(22, 38.4), fades=[("in", 22.5, 0.4), ("out", 37.4, 0.6)])
    for x0, y0, ph, name, T in ((150, 1240, 1.0, "cardA", 23.3), (430, 1335, 1.6, "cardB", 23.39), (700, 1430, 2.3, "cardC", 23.48)):
        b.layer(name, f"{x0}+34*clip((t-22.5)/15,0,1){DRIFT(5, 14 + ph, ph)}",
                f"{y0}-26*(1-pow(2,-10*clip((t-{T})/0.6,0,1))){DRIFT(6,17,ph)}",
                enable=(T, 38.4), fades=[("in", T, 0.5), ("out", 37.4, 0.7)])
    rw, rh = size("ribbon")
    for k in range(2):
        b.layer("ribbon", f"-mod((t-22)*85,{rw})+{rw}*{k}", f"1690{DRIFT(3,18,1)}",
                enable=(22.9, 38.4), fades=[("in", 22.9, 0.5), ("out", 37.4, 0.6)])
    b.dip(37.55, 37.95)

def scene_b4(b):
    l4w, l4h = size("label4"); t3w, t3h = size("title3"); bx = int((W - t3w) / 2)
    b.layer("wall_full", f"0{DRIFT(8,23,1)}", f"-15+ (t-38)*0.9", enable=(38, 50.4), fades=[("in", 38.2, 0.7), ("out", 49.6, 0.6)])
    b.layer("dustA", f"-40{DRIFT(16,19,2)}", "300", enable=(38, 50.4), fades=[("in", 38.5, 0.9), ("out", 49.6, 0.6)])
    b.layer("label4", f"(W-{l4w})/2", f"190{DRIFT(3,12,0)}", enable=(38, 50.4), fades=[("in", 38.6, 0.4), ("out", 49.6, 0.5)])
    b.layer("title3_blur", f"{bx}", f"700{DRIFT(4,14,0)}", enable=(38, 50.4), fades=[("in", 38.75, 0.45), ("out", 49.6, 0.5)])
    b.layer("title3", f"{bx}", f"700{DRIFT(4,14,0)}", enable=(38, 50.4), fades=[("in", 39.2, 0.55), ("out", 49.6, 0.5)])

def scene_b5(b):
    cgw, cgh = size("collage"); rlw, rlh = size("redlabel"); r4w, r4h = size("red4"); ctw, cth = size("cta")
    b.layer("collage", f"(W-{cgw})/2{DRIFT(6,19,1)}", f"300{DRIFT(7,23,2)}", enable=(50.2, 60.2), fades=[("in", 50.2, 0.5), ("out", 59.4, 0.6)])
    b.layer("redlabel", f"(W-{rlw})/2", f"115{DRIFT(3,12,0)}", enable=(51.0, 60.2), fades=[("in", 51.0, 0.4), ("out", 59.4, 0.5)])
    b.layer("red4", f"(W-{r4w})/2-6*(1-pow(2,-10*clip((t-51.2)/0.6,0,1)))", f"760{DRIFT(4,15,1)}",
            enable=(51.0, 60.2), fades=[("in", 51.2, 0.5), ("out", 59.4, 0.5)])
    b.layer("cta", f"(W-{ctw})/2", f"1240-30*(1-pow(2,-10*clip((t-53.4)/0.7,0,1))){DRIFT(4,16,0)}",
            enable=(53.3, 60.2), fades=[("in", 53.4, 0.6), ("out", 59.4, 0.6)])
    b.layer("tear", "0", f"-{H-40}+(t-49.85)*{H+300}/1.35", enable=(49.85, 51.55))
    b.dip(59.5, 61.0, d=0.5)

# render plan: b1 done already; rest split into <=7s segments
PLAN = [
    ("b2a", 9.0, 6.6, scene_b2), ("b2b", 15.6, 6.8, scene_b2),
    ("b3a", 22.0, 8.2, scene_b3), ("b3b", 30.2, 8.3, scene_b3),
    ("b4a", 38.0, 6.3, scene_b4), ("b4b", 44.3, 6.3, scene_b4),
    ("b5", 49.85, 10.35, scene_b5),
]
names = {}
for nm, t0, dur, fn in PLAN:
    b = Block(nm, t0, dur)
    fn(b)
    names[nm] = (b.emit(), t0, dur)

# ---- run script ------------------------------------------------------
sh = ["#!/usr/bin/env bash", "set -e", 'cd "$(dirname "$0")"', "FF=./ffmpeg", "mkdir -p reels_v2"]
for nm, (idx, t0, dur) in names.items():
    ins = ["-f lavfi -i color=c=black:s=1080x1920:r=30:d=%.2f" % dur]
    for p, i in sorted(idx.items(), key=lambda kv: kv[1]):
        ins.append("-loop 1 -framerate 30 -t %.2f -i plates_v2/%s.png" % (dur, p))
    sh.append("$FF -y " + " ".join(ins) +
              f" -/filter_complex graph_{nm}.txt -map '[vf]' -t {dur:.2f} "
              f"-q:v 2 -start_number 0 -f image2 reels_v2/{nm}_%05d.jpg")
Path("run_blocks2.sh").write_text("\n".join(sh) + "\n")
print("wrote", ", ".join(f"graph_{n}.txt" for n in names))
