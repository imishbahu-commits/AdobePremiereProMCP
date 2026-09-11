# Deep Style Analysis — References 16732 / 16735 / 16738 / 16741

Four long-form user references (uploaded 2026‑09‑11). All are **narrated
content videos**, not mograph reels. They split cleanly into **two style
families**:

| ID | Length | Format | Family | Content |
|----|--------|--------|--------|---------|
| 16732 | 16:47 | 640×360@30, h264+aac | **A — Flat 2D Explainer** | finance story (banks, savings) |
| 16738 | 12:31 | 640×360@30 | **A — Flat 2D Explainer** | career/business story |
| 16735 | 03:55 | 640×360@30 | **B — VideoScribe Whiteboard** | "Psychology of Money" book summary |
| 16741 | 07:42 | 640×360@30 | **B — VideoScribe Whiteboard** | investing: DCA / Buy-the-Dip / Lump-Sum |

---

## FAMILY A — Flat 2D Explainer (16732, 16738)

### Look
- **Palette (sampled):** paper cream `#FAF4D2` background; teal `#0D6161`
  as the single hero color (bodies, props, boards); charcoal `#3B3227` for
  "dark" scenes/characters; white faces; occasional beige scene panels
  (`#C9B08C`) and small saturated accent objects (yellow stand, red apple).
  2–4 flat fills per sprite, **zero gradients, zero shadows native to layer**
  (contact shadow = flat ellipse only).
- **Characters:** noodle-limb stick-adults — ellipse head, capsule torso,
  2-bone arms, no leg articulation while sliding. Expressions via mouth/eye
  swap. Outfits differentiator only (tie, cap, vest).
- **Composition:** full-frame tableau, eye-level camera, character rows
  L→R; props enter from edges; wide empty air above (space for every new prop).

### Motion signature (from 6fps micro-strips + freeze/scdet telemetry)
- **Idle bob:** ±2–4 px vertical, ~0.5 s period, 2–4 key loop. EVERYTHING idles.
- **Gestures:** arm rotation arcs 0.8–1.5 s, eased (out-cubic feel);
  finger-point, palm-up "present", head tilt.
- **Prop/icon pop-in:** 0.1–0.2 s scale-pop (settle), sometimes with a small
  float-up; icons appear *on* boards (e.g. "$" coin on blackboard).
- **Walk = lateral slide** (no leg cycle), 1.5–3 s constant speed, bob continues.
- **Rhythm:** pose holds of 1–2.4 s between action beats (freeze windows measured
  at 7.27–8.3 s, 14.6–16.0 s, 16.2–18.6 s …). Breath-paced narrative, NOT the
  zero-hold mograph law from the v2/v3 reels. This is deliberate: viewer must read.
- **Transitions between tableaus:** hard cut (occasionally a snappy push/zoom
  punch-in ×1.15 reframing, e.g. teacher close-up). Camera otherwise static.
- Scene event cadence ≈ 1.9–2.0 s mean activity interval (scdet p95 peaks);
  tableau lifetime 10–25 s.

### Audio
- Continuous male VO narration, integrated −18.1 / −17.7 LUFS; a few 1–2 s
  silence breaths (16732: 10 runs ≥1.2 s @−35 dB). Sparse/raised audio bed
  under VO if any (music never competes).
- Voice drives EVERYTHING: each new prop/gesture lands on the phrase that
  names it.

---

## FAMILY B — VideoScribe Whiteboard (16735, 16741)

### Look
- **Palette (sampled):** pure white `#FFFFFF` canvas; ink line art
  (~`#1E1E1E` black, 2–3 px weight, wobbly hand line, hatching fills);
  accent inks red `#C0392B` (X marks, "30" years) and teal/green
  `#2EAD8F`; 16741 adds **pastel label cards** (mint `#8FE3A0`,
  cyan `#6FDEDC`) as pre-stamp section tabs.
- **Layer collage:** ink drawings + pasted bitmaps (book cover, US flag-map,
  real bar/line charts with 300–600 px drop) + arrow/underline ink.
- **The hand:** dark-skin male right hand gripping white/silver pen; serves
  as camera-focus pointer even when not drawing.

### Motion signature (from 6fps micro-strips)
- **Draw reveal:** every element appears by progressive left→right (or
  following-path) ink reveal; small icons complete in 0.3–0.5 s; a full
  sentence writes in ~3–4 s; a panel diagram in 1–4 s.
- **Hand trace:** pen tip rides the wavefront of the reveal; between elements
  the hand hops to the next anchor (0.3–0.5 s hops), exits bottom-right,
  re-enters. In 16735 the hand also *idles-presses* on finished areas while
  narration continues.
- **Pauses:** ~1.0 s dead stops between draw bursts (freeze windows
  33.6–34.8, 39.3–40.3, 44.2–45.3 s) — thinking beats on phrase ends.
- **Camera:** static while inking; between panels = cut to fresh white canvas
  (t≈33–45 s cadence in 16735) **or** slow 5–10 % drift/zoom reframe as the
  page fills (16741 rows). No fast whip/push energy — calm docudrama pace.
- Event cadence: draw-burst every ~1.2 s (scdet activity peaks 1.17–1.23 s
  median) — the listener must see a new mark roughly every second.
- Persistent watermark logo bottom-right (channel bug).

### Audio
- Nonstop male VO: −20.8 / −24.3 LUFS integrated, ZERO ≥1.2 s silences
  @−35 dB. Words and wrist are 1:1 — every sentence = ≥1 new visible element.

---

## Translation into our ffmpeg/pillow pipeline (feasibility)

### Family A (explainer) — build as "puppetPNG" kit
1. Pillow sprite factory: noodle-character rig (head/torso/2-bone arms/legs) in
   teal-on-cream palette; mouth/eye expression sheets; outfit swaps.
2. Scene builder: tableau PNG (bg + characters + board/props) → per-beat
   variant PNGs (arm angles, prop pop states).
3. ffmpeg render: still bursts + `zoompan`-free simple xfade/pop cross‑fades,
   scale 1.00→1.03 drift across tableau, hard cuts between tableaus; character
   bob via overlay `y='..-2*abs(sin(2*PI*t))'` dithering trick or
   pre-rendered 2-frame bob frames loop spliced.
4. VO: user supplies script; we can synth a scratch VO via the speech tool or
   use aevalsrc "ticking" placeholder — final needs real narration.

### Family B (whiteboard) — build as "scribe" kit
1. Assets: hand PNG (pen) — generate once, reuse; ink sprites drawn in Pillow
   (vector-ish strokes w/ wobble), pastel label cards, chart bitmaps.
2. **Reveal engine:** per-element mask wipe — render element PNG, then create
   progressive reveal via crop-wipe head x(t) matching the hand anchor; hand
   overlaid at `x=head, y=stroke_baseline` (both driven from ONE timeline
   JSON). Text: render each glyph cluster, reveal in reading order.
3. Camera: static during ink; cut-away to clean canvas per idea page;
   optional 1.00→1.06 slow zoom while page accumulates.
4. VO same requirement as A.

**Both families are 100 % reproducible in our existing pipeline.**
The labor difference: A needs a small character-rig library (2–3 figures +
8 poses) ≈ one focused build; B needs the wipe-reveal + hand-trace engine
(≈ comparable effort, leverages our existing overlay programming skill).

### Deliverable mapping
- These are LONG-form styles (4–17 min). For portfolio parity with
  earlier requests, propose **60 s demo episodes** per family (or one
  combined A/B sampler): 3–5 beats, 640×360→ we render 1280×720 for
  crispness, 30 fps, scratch VO + light music bed (user replaceable).
