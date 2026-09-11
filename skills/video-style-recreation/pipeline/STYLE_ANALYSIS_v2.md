# Atomic-Level Style Teardown v2 — Reference `uploads/16702.mp4`

*(Measured from the file itself: 13.26s, 720×1600, VFR ~28fps storage on a 60fps
timeline, BT.709, mono audio. The file is a phone screen recording of the user
browsing AutoAE template previews — the artifacts inside it are five real premium
template looks incl. replays; telemetry below extracts their grammar.)*

## 0. What this style IS

**"Dark premium 3D-mockup" hook motion graphics** — near-black stages where
volumetric spotlights, drifting 3D props, reflective floors, and UI/chat mockups
carry one idea per scene. Buttery After-Effects motion: everything eased, nothing
snaps, deep defocus settles, dust drifts in light shafts. Monochrome stages with a
single restraint-broken color accent.

Audio fingerprint: track measures **−70 LUFS integrated = effectively silent**
(these previews play muted; motion must carry 100% of the premium feel).

## 1. Telemetry

| Metric | Value |
|---|---|
| Duration / raster | 13.26s (5 template looks + replays) / 720×1600 (~9:20) |
| Hard scene events (scdet t=8) | transition band **6.06s–6.29s** (blue photo-wall entrance), secondary motion events 7.01–7.28 (paper-tear) |
| Pose holds (freezedetect) | none ≥0.25s — **continuous motion everywhere** (drift永远) |
| Loudness | −70 LUFS — silent visual-only |
| Camera (vidstabdetect, 4353 samples) | slow drift velocities everywhere; no shake; no cuts |

## 2. The five looks (scene-by-scene micro-anatomy)

**A — Spotlight 3D title (0.0–2.0s, replay 7.6–10.4s)**
Pure black. Crescent moons + stony 3D clock tumble slowly (constant slow velocity,
slight rotation). Diagonal volumetric light shaft top-right→center carrying dust
motes. Type: small-caps label ("Main Text 1") + giant bold sans ("Text 5") that
settles **heavy-blur→sharp** in ~0.5–0.7s (defocus-in, expo tail). Second drift
prop lower-right.

**B — Chat UI mockup reveal (2.0–4.4s, replay 10.4–11.9s)**
Pure black, thin "ChatGPT" label top-center. Dark rounded input bar materializes
(fade+slight scale ~0.95→1). Typing-dots animate (~3 dots, 0.9s cycle). Response
bubble **grows upward from bar top edge** (height expansion, slight overshoot-less
expo settle ~0.45s), text types in, then **3 pill chips stagger-pop ~50–80ms**
below the bubble. Palette: black/#2F2F2F/#D9D9D9/white only.

**C — 3D typographic gallery floor (4.4–7.0s, replay 11.9–13.0s)**
Black reflective floor (mirror reflection fading with depth). Floating rounded
cards angled in perspective ("Main Text X / Subtext"). Long ribbon marquee strip
with tiny repeating dark inscription. **Giant stroke-only outlined numerals ("T1 T2")**
standing on floor + solid bold white word overlapping. Bloom on key type. Slow
dolly drift (near-constant, ease at extremes). Dust motes in air.

**D — Blue photo wall (6.1–7.0s, replay 13.0–13.3s)**
The ONLY color: cobalt/electric blue backlight washing a floating grid of
white-bordered photo cards; vintage TV prop left with screen glow;
"Main Text 4 / Text 3". Blue rim on card edges; black stays crushed.

**E — Torn-paper collage (7.3–7.6s)**
White **torn paper wipe** (ragged fibrous edge sweeps the frame) → grayscale
archival photo collage with red italic serif accent ("Text 4"). Only burst
transition in the set; texture replaces lighting as the premium carrier.

## 3. Micro-motion laws (the "buttery AE" recipe, measured)

1. **No holds ≥0.25s, ever** — even "static" scenes drift at 2–8 px/s equivalent;
   constant micro-velocity is the premium tell (matches v1's 1.1s micro-freeze
   law being absent here: this family never freezes).
2. **Camera = slow constant-velocity drifts** with ease only at move
   start/stop; velocities ~3% frame-width/s max; direction changes are rarer
   than one per 3s.
3. **Defocus-in for text**: σ ≈ 20–30px → 0 over 0.5–0.7s, expo-out tail;
   opacity rides 0→1 over the first 60% of the same window.
4. **Object reveals = grow-from-anchor** (chat bubble from its input bar's top
   edge), expo settle ≤0.5s, no overshoot (corporate, not playful).
5. **Stagger 50–80ms** on group reveals (3 chips); tighter than the 66ms
   v1 stair-step.
6. **Easing signature**: expo-out / smooth (AE "Eazy Ease 33%") on everything;
   impacts expressed via blur/scale, never via hard spatial jumps. Effects are
   time-symmetric (slow-in AND slow-out on drifts).
7. **Bloom + crushed blacks**: highlights roll into soft bloom instead of small
   bright cores; shadow floor 0–5% IRE; stroke-outlined giant type reads via
   thin white 1–2px lines.

## 4. Color grade

- Base: pure black `#000`–`#050505` canvas, `#0A0A0B` scene floor gradients.
- Neutrals: `#2F2F2F` (chat bar), `#3A3A3C` bubbles, `#D9D9D9`/`#FFFFFF` type.
- Spotlight shaft: warm-neutral white at ~6–12% luminance, gaussian feather.
- Single accent: **cobalt blue backlight** (~#1E4FFF/#2E63FF) — one hue, one scene.
- Red accent only in archival collage (#E4363B-ish italic serif).
- Grade: crushed blacks, bloom-rolled highlights, neutral WB, zero lift-noise.

## 5. Recreation spec (what we will build — `v2` sample)

Vertical **1080×1920@30**, ~60s, 5 blocks honoring the laws above:

1. **0–9s Spotlight title** — drifting 3D clock prop (AI plate on black, screen-blended), shaft+dust, blur→sharp giant title.
2. **9–22s Chat UI reveal** — bar → typing dots (0.9s) → bubble grow-from-edge → type-in → 3 chips @70ms stagger.
3. **22–38s Gallery floor** — perspective cards + outlined giant numerals + marquee ribbon + faded mirror floor, slow dolly.
4. **38–50s Blue photo wall** — cobalt backlit card grid, TV prop, text settle.
5. **50–60s Finale** — torn-paper wipe (procedural ragged mask) → CTA card on paper-collage → fade.

Build lane: proven PIL plates + ffmpeg 7 filtergraph. Key techniques: **black-art
screen/lighten compositing** (dark-scene props need no chroma), opacity-crossed
blur/sharp plate pairs for defocus-in, overlay drift expressions for constant
micro-velocity, zoompan pockets for dollies, alpha-composited grow-from-anchor
windows, marquee ribbon via scrolling tiled strip, procedural torn-edge mask
(PIL noise-threshold boundary) as a transition matte.

Audio: visual-first like the reference; we add an optional very-low ambient bed
(≈−28 LUFS target, dark pad + sparse ticks) since the reference itself is silent —
keep it sub-audible by default, flag for user choice.
