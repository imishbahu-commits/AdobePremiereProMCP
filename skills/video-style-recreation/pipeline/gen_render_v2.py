#!/usr/bin/env python3
"""gen_render_v2 — dark-premium 3D-mockup recreation (STYLE_ANALYSIS_v2).
Stages: PIL plates -> filtergraph_v2.txt (ffmpeg 7). Vertical 1080x1920 @ 60s.
Motion laws honored: zero holds (micro-drift everywhere), expo-out reveals,
blur->sharp defocus-in, grow-from-anchor, 70ms staggers, bloom+crushed blacks."""
from __future__ import annotations
import math, random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps

W, H = 1080, 1920
OUT = Path("plates_v2"); OUT.mkdir(exist_ok=True)
ROOT = Path(".")
INK = "#EDEDEF"; GRAY = "#D9D9D9"; DIM = "#8E8E93"; BAR = "#2F2F31"; BUB = "#3A3A3C"
BLUE = "#2E63FF"; RED = "#E4363B"; PAPER = "#F4F1EA"
random.seed(7)
FB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FS = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"

def font(p, s): return ImageFont.truetype(p, s)
def rgba(w=W, h=H, c=(0,0,0,0)): return Image.new("RGBA", (w, h), c)
def save(im, name): im.save(OUT / name)

def text_plate(txt, fnt, fill, name, fs, stroke=0, sf=(0,0,0,255), ls=0, anchor="la", cap=False):
    f = font(fnt, fs)
    s = txt.upper() if cap else txt
    bb = ImageDraw.Draw(rgba(1,1)).textbbox((0,0), s, font=f, stroke_width=stroke)
    w, h = bb[2]-bb[0], bb[3]-bb[1]
    im = rgba(w+2*ls+20, h+2*ls+20); d = ImageDraw.Draw(im)
    d.text((ls+10, ls+10+ (0 if anchor=="la" else 0)), s, font=f, fill=fill, stroke_width=stroke, stroke_fill=sf)
    save(im, name); return (w, h)

def letterspaced(txt, fnt, fill, name, fs, ls):
    f = font(fnt, fs)
    widths = [ImageDraw.Draw(rgba(1,1)).textlength(ch, font=f) for ch in txt]
    w = int(sum(widths) + ls*(len(txt)-1)) + 12; h = int(fs*1.6)
    im = rgba(w, h); d = ImageDraw.Draw(im); x = 6
    for ch, cw in zip(txt, widths):
        d.text((x, fs*0.2), ch, font=f, fill=fill); x += cw + ls
    save(im, name); return (w, h)

# ---------- assets for Block 1: spotlight title ----------
im = rgba()
d = ImageDraw.Draw(im, "RGBA")
# volumetric shaft: rotated soft triangle from top-right
shaft = rgba()
ds = ImageDraw.Draw(shaft, "RGBA")
for i in range(40):
    a = int(3.2 * (1 - i/40) ** 2 * 10)
    ds.polygon([(W*0.62 - i*8, 0), (W*1.02 - i*4, 0), (W*0.52 + i*6, H*0.68), (W*0.18 + i*2, H*0.68)], fill=(255, 252, 246, a))
shaft = shaft.rotate(-14, resample=Image.BICUBIC, center=(W*0.7, 0))
save(shaft.filter(ImageFilter.GaussianBlur(30)), "shaft.png")

# dust motes x2 parallax layers
for nm, cnt, rmin, rmax, amax in [("dustA", 90, 1, 3, 60), ("dustB", 40, 2, 5, 90)]:
    im = rgba(); d = ImageDraw.Draw(im)
    for _ in range(cnt):
        x, y = random.uniform(0, W), random.uniform(0, H)
        r = random.uniform(rmin, rmax); a = random.randint(amax//3, amax)
        d.ellipse([x-r, y-r, x+r, y+r], fill=(255, 250, 240, a))
    save(im, f"{nm}.png")

# crescent moons
def crescent(R, name, tone=(228,228,232)):
    im = rgba(R*3, R*3); d = ImageDraw.Draw(im)
    d.ellipse([R//2, R//2, R*5//2, R*5//2], fill=tone + (230,))
    d.ellipse([R//2 - R//3, R//2 - R//9, R*5//2 - R//3, R*5//2 - R//9], fill=(0,0,0,235))
    im = im.filter(ImageFilter.GaussianBlur(2))
    save(im, name)
crescent(55, "moonA.png"); crescent(34, "moonB.png", (200,200,206))

# ---------- Block 2: chat UI ----------
letterspaced("C H A T G P T", FR, GRAY, "chatlabel.png", 34, 6)
# input bar
im = rgba(860, 110); d = ImageDraw.Draw(im)
d.rounded_rectangle([0, 0, 859, 109], radius=55, fill=BAR + "FF", outline=(70,70,72,255), width=2)
d.text((45, 34), "Ask anything", font=font(FR, 32), fill=(120,120,122,255))
save(im, "chatbar.png")
# typing dots (three phases)
for i in range(3):
    im = rgba(150, 60); d = ImageDraw.Draw(im)
    ys = [22, 34 if i == 0 else 26, 34 if i == 1 else 26, 34 if i == 2 else 26]
    for k, cx in enumerate([38, 75, 112]):
        d.ellipse([cx-8, ys[k]-8, cx+8, ys[k]+8], fill=(200,200,202,255))
    save(im, f"dots_{i}.png")
# answer text
text_plate("Main Text 1 — the idea, delivered.", FR, INK, "answertext.png", 40)
# chips
for i, t in enumerate(["Audio", "Search", "Study"]):
    f = font(FR, 30); tw = int(ImageDraw.Draw(rgba(1,1)).textlength(t, font=f))
    im = rgba(tw + 70, 64); d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, tw+69, 63], radius=32, outline=(110,110,114,255), width=2, fill=(28,28,30,255))
    d.text((35, 15), t, font=f, fill=(190,190,194,255))
    save(im, f"chip_{i}.png")

# ---------- Block 3: gallery floor ----------
im = rgba(); d = ImageDraw.Draw(im, "RGBA")
# floor: gradient from black to subtle sheen
for y in range(H):
    yy = y / H
    if yy > 0.55:
        v = int(14 * (yy - 0.55) / 0.45)
        d.line([(0, y), (W, y)], fill=(v, v, v+2, 255))
save(im, "floorgrad.png")
# giant outlined numerals
def outlined(txt, name, fs):
    f = font(FB, fs)
    bb = ImageDraw.Draw(rgba(1,1)).textbbox((0,0), txt, font=f, stroke_width=4)
    im = rgba(bb[2]+30, bb[3]+30); d = ImageDraw.Draw(im)
    d.text((15, 15 - bb[1]), txt, font=f, fill=(0,0,0,0), stroke_width=4, stroke_fill=(230,230,234,235))
    save(im, name)
outlined("T1", "bigT1.png", 560); outlined("T2", "bigT2.png", 560)
text_plate("Text 1", FB, INK, "floorword.png", 210)
text_plate("Main Text 3", FR, DIM, "floorlabel.png", 44)
# floating cards
def card(txt, sub, name, ang):
    im = rgba(430, 150); d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, 429, 149], radius=22, fill=(24,24,26,240), outline=(95,95,100,220), width=2)
    d.text((28, 26), txt, font=font(FB, 38), fill=(225,225,228,255))
    d.text((28, 84), sub, font=font(FR, 28), fill=(140,140,145,255))
    im = im.rotate(ang, expand=True, resample=Image.BICUBIC)
    save(im, name)
card("Main Text 2", "Subtext · detail", "cardA.png", -7)
card("Main Text", "Subtext", "cardB.png", 5)
card("Main Text 5", "3 hours ago", "cardC.png", -4)
# marquee ribbon
f = font(FB, 44); seg = " PREMIUM HOOKS · MADE TO MEASURE ·"
sw = int(ImageDraw.Draw(rgba(1,1)).textlength(seg, font=f))
im = rgba(sw*3, 92); d = ImageDraw.Draw(im)
d.rectangle([0, 0, sw*3-1, 91], fill=(235,235,238,255))
for k in range(3): d.text((k*sw, 20), seg, font=f, fill=(18,18,20,255))
save(im, "ribbon.png")

# ---------- Block 5: torn paper + collage ----------
n = 200
pts = [(0, -10)]
x = 0
while x < W:
    pts.append((x, random.randint(120, 300)))
    x += random.randint(6, 22)
pts += [(W, -10)]
im = rgba(); d = ImageDraw.Draw(im)
d.polygon(pts, fill=(244,241,234,255))
im = im.filter(ImageFilter.GaussianBlur(1.2))
# fibrous shadow under tear
sh = rgba(); ds = ImageDraw.Draw(sh)
for i in range(6):
    ds.polygon([(p[0], p[1]+10+i*7) for p in pts], fill=(0,0,0, 8))
im = Image.alpha_composite(sh.filter(ImageFilter.GaussianBlur(10)), im)
save(im, "tear.png")
# collage wall
im = Image.new("RGB", (W, H), (16,16,17)); d = ImageDraw.Draw(im)
for _ in range(46):
    cw, ch = random.randint(140, 300), random.randint(160, 340)
    x, y = random.randint(-40, W-60), random.randint(-40, H-60)
    g = random.randint(90, 190)
    d.rectangle([x, y, x+cw, y+ch], fill=(g-8, g-8, g-6), outline=(236,236,238), width=6)
    for k in range(3):
        gg = random.randint(max(60, g-70), min(235, g+30))
        d.rectangle([x+22, y+26, x+cw-22, y+26 + int((ch-70)*(0.3+0.25*k))], fill=(gg,gg,gg+2))
im = im.filter(ImageFilter.GaussianBlur(0.6))
im.save(OUT / "collage.png")
text_plate("Text 4", FS, RED, "red4.png", 300)
text_plate("Main Text 5", FR, DIM, "redlabel.png", 44)
# CTA card
im = rgba(760, 330); d = ImageDraw.Draw(im)
d.rounded_rectangle([0, 0, 759, 329], radius=30, fill=(244,241,234,255))
d.text((58, 62), "LET'S BUILD", font=font(FB, 92), fill=(18,18,20,255))
d.text((60, 188), "premium hooks, made to measure", font=font(FR, 40), fill=(90,90,94,255))
d.rounded_rectangle([58, 252, 330, 308], radius=28, fill=(18,18,20,255))
d.text((88, 262), "START NOW", font=font(FB, 30), fill=(244,241,234,255))
save(im, "cta.png")

# blur/sharp pairs for defocus-in titles
text_plate("Text 5", FB, INK, "title5.png", 300)
t5 = Image.open(OUT/"title5.png").filter(ImageFilter.GaussianBlur(26)); save(t5, "title5_blur.png")
text_plate("Text 3", FB, INK, "title3.png", 260)
t3 = Image.open(OUT/"title3.png").filter(ImageFilter.GaussianBlur(24)); save(t3, "title3_blur.png")
letterspaced("M A I N  T E X T  1", FR, DIM, "label1.png", 40, 8)
letterspaced("M A I N  T E X T  4", FR, DIM, "label4.png", 40, 8)

print("plates:", len(list(OUT.glob('*.png'))))

# ── AI asset prep: clock → luminance-alpha cutout · tvwall → 1080 full-frame ──
def asset_prep():
    # clock: black art → RGBA with luminance key, bbox-crop, resize
    im = Image.open(ROOT / "assets/v2_clock.png").convert("RGB")
    px = im.load()
    alpha = Image.new("L", im.size, 0)
    ap = alpha.load()
    for yy in range(im.height):
        for xx in range(im.width):
            r, g, b = px[xx, yy]
            lum = max(r, g, b)
            ap[xx, yy] = 255 if lum >= 26 else (int((lum - 10) * 16) if lum > 10 else 0)
    rgba = im.convert("RGBA"); rgba.putalpha(alpha)
    bbox = alpha.getbbox()
    pad = 30
    bx = (max(0, bbox[0]-pad), max(0, bbox[1]-pad), min(im.width, bbox[2]+pad), min(im.height, bbox[3]+pad))
    rgba = rgba.crop(bx)
    k = 900 / rgba.width
    rgba.resize((900, int(rgba.height * k)), Image.LANCZOS).save(OUT / "clock_a.png")

    # tvwall: opaque full-frame 1080x1920 center crop
    wall = Image.open(ROOT / "assets/v2_tvwall.png").convert("RGB")
    k = 1080 / wall.width
    wall = wall.resize((1080, int(wall.height * k)), Image.LANCZOS)
    top = max(0, (wall.height - 1920) // 2)
    wall.crop((0, top, 1080, top + 1920)).save(OUT / "wall_full.png")
    # soft cover plate for typewriter reveal (black, same tone as bubble? -> black bar over text area)
    Image.new("RGBA", (980, 300), (0, 0, 0, 255)).save(OUT / "cover.png")
    print("assets prepped")

asset_prep()
