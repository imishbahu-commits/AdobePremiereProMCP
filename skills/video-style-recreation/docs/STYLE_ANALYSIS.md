# Atomic-Level Style Teardown — Reference Videos 16289 / 16293

*(Measured, not guessed. Every number below was extracted from the actual files in this sandbox.)*

## 0. What this style IS

Flat-2D animated **workout explainer** ("animated fitness story-tutorial"): a yellow
hero character performs real exercise progressions inside **monochrome duotone worlds**
while an explanatory/mythic B-story plays around him. Comedy via side characters
(hamster, Zeus, kraken). Pedagogy via infographics (rep cards, progression ladders,
week grids). Revenue via clearly-tagged sponsor skits.

## 1. Hard metrics

| Metric | 16289.mp4 | 16293.mp4 |
|---|---|---|
| Duration | 9:16.6 | 8:01.6 |
| Raster / fps | 640×360 (upload) / 29.97 | 640×360 / 29.97 |
| **Hard cuts — entire video** | **4** (76.4s, 76.5s, 86.9s, 526.8s) | **1** (211.6s) |
| Cut rate | ~0.4/min — effectively ZERO-cut editing | ~0.1/min |
| Pose-holds ≥ 0.8 s | 51 (69 s total) — median **1.1 s**, max 4.1 s | 33 (56 s) — median **1.4 s** |
| Loudness (EBU R128) | −22.8 LUFS int., LRA 6.2 | −23.9 LUFS int., LRA 6.5 |
| VO silence gaps | rhythm of 0.6–0.8 s gaps every ~3–6 s (narration cadence) | same |

**The "4 cuts, one of them a stutter" fingerprint:** at 76.4→76.5 s video 1 uses a
double-frame stutter as an *accent* — this editor cuts on IMPACT, not on beats.

## 2. Editing grammar (the "no-cut" system)

1. **Continuous-space transitions** — scenes connect by animated camera travel:
   horizontal follow-pans through the room, whip-pans, dolly/zoom into objects
   (medal close-up), not by cuts. The one hard cut in video 2 (211 s) marks the
   *sponsor segment* boundary — cuts are reserved for meaning shifts.
2. **Pose-hold rhythm** — 1–1.4 s micro-freezes every 2–14 s of motion: economical
   animation that reads as intentional "beat, beat, beat" timing. Holds cluster
   around punchlines and technique cues.
3. **Wide master dominance** — the hero occupies 0.4–2 % of frame in masters;
   close-ups (10–30 % yellow coverage) are rationed for emphasis gags (Zeus finger
   poke, stat callouts). Rule: *stay wide, punch in only to land a point.*
4. **Loop cycles** — exercise moves run as short seamless loops while VO explains;
   loop length ≈ 0.8–1.2 s per rep; camera holds dead still during loops.
5. **Impact frames** — gags get 2–4 frame accents: stutter cuts, motion-jag white
   speed-lines, radial sunburst behind objects.

## 3. Motion-design recipes (extracted signatures)

| Signature | Construction |
|---|---|
| **Rep counter pop** | Chunky italic numeral ("17", "27") scale-pops inline with each rep, sits high-center on the wall — never lower-third |
| **Sunburst hero** | Product/prop + open branded box + rotating radial rays — used for the GORNATION pull-up bar |
| **Motion-jag accents** | 2-stroke white zigzag at contact points (Zeus finger → back), 3–6 frames |
| **Title card** | Solid deep-violet `#4B2B8C` + ALL-CAPS white geometric bold (`PLANK`), subtle glow variant in-scene |
| **Follow-pan world** | Set slides L→R as character "travels"; foreground props pass faster (parallax) |
| **Punch-zoom inspect** | 6–10 frame zoom into framed medal / shelf contents, then settle back |
| **Comic side-character** | Hamster runs wheel mirroring hero's reps; Zeus hands intervene; kraken attacks during sea scene |
| **Infographic system** | Progression ladder shelf, rep chips (`8x/side`, `30s`, `20x`), warning signs, stat bubbles (`+16%`, `+39.2%`, `−3%`), PUSH/PULL/SQUAT 3-column compare, `WEEK 1` people-grid schedule |

## 4. Measured color system (per-scene duotones)

| Role | Hex | Usage share |
|---|---|---|
| Wall lavender | `#D6CEEA` | 43–70 % of typical frame |
| Mid lavender | `#9887C6` / `#9988C7` | 17–38 % (floor, props, sea) |
| Floor violet | `#B2A3D3`→`#746B7E` | shadow/props |
| **Deep violet** | `#492488` | night/space/title card (94 % of those frames) |
| Hero skin yellow | `#F6D370` (lit) / `#E2C792` (shadow) | 0.4–10 % (up to 30 % close-up) |
| Paper white | `#F6F4F5` | statues, clouds, title type |
| Ink | near-black `#2B2430` | all outlines |

Discipline: **one hue family per scene; the only warm color in the film is the hero
(and gold props: medal, dumbbells, plus-signs).** Complementary yellow-vs-violet pop
does all the attention steering — nothing else competes.

## 5. Craft details

- Thick black contour outlines; some elements get an inner white keyline
- Micro paper-grain/film texture over all flat fills (visible in zooms)
- Soft oval contact shadows under characters/props
- Set dressing on **thirds**: tall props (arched shelf, pendant lamp, plant) frame
  left/right edges; action lives center-bottom third
- Typography: (a) heavy italic slab — numerals/labels like `SQUAT`; (b) geometric
  bold caps — title cards; (c) tiny yellow `ADVERTISEMENT` corner tag with black keyline

## 6. Structure template (both videos mapped)

```
0:00  cold open — action already running, no logos
0:05  myth/setup B-story introduced (statues, Parthenon / room stakes)
0:20  TITLE CARD — one word, deep violet
0:25  tutorial A-story begins (first exercise, rep counter starts)
…     alternating A/B beats every ~20–40 s; holds & loops under VO
~55%  infographic block (progression ladder / schedule grid)
~60%  SPONSOR SKIT — hard boundary, sunburst product hero, AD tag,
      coupon + "brand 10%" card, 25–40 s, then snap back
…     final progression / myth payoff (kraken, Zeus, medal earned)
END   space/night outro gag + sponsor box floating, soft end
```

## 7. Recreation spec (how I rebuild this in the sandbox)

1. **Assets** (image generator, chroma-green plates): yellow hero in 5–6 pose plates
   per exercise + side character (hamster/bird), duotone room/sea/space backdrops,
   props (shelf, bar, medal, ladder), product + box for sponsor gag.
2. **Layered keyframe build** (same engine as the demo, upgraded):
   hero loop (2-frame position/scale alternate @ ~1 s), counter numeral pop curve
   (overshoot back-ease, per-rep retrigger), follow-pan world (parallax x-tracks
   at 0.35×/0.7×/1×), punch-zoom (1.15–1.3×, 8-frame smooth), sunburst rotate loop,
   motion-jag overlay flashes (3-frame enable windows).
3. **Discipline rules**: NO hard cuts except sponsor boundary + impacts; 1.1–1.4 s
   pose holds; hero coverage ≤ 2 % in masters; one hue family per scene; type only
   as numerals/title/AD-tag.
4. **Audio spec**: VO −23±1 LUFS base, sentence gaps 0.6–0.8 s; upbeat bed −14 LU
   under VO; whoosh+punch accents on pops/impacts.
5. **Premiere mapping**: pans/zooms = Motion/an Adjustment-layer Transform keyframes;
   numeral pops = MOGRT or Essential Graphics with keyframed scale; loops = nested
   sequences; sunburst = Rotation keyframes; holds = time-remap freeze segments;
   all via `premiere_add_keyframe`, `premiere_set_keyframe_interpolation`,
   `premiere_create_nested_sequence`, `premiere_set_time_remapping`, readback-verified.
```
```
