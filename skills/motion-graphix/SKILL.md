---
name: motion-graphix
description: Premium, design-led motion graphics — kinetic typography, stat count-ups, logo stings, lower-thirds, chart hits, animated cards/maps, deck videos — with a measured feel-system (effect→feeling), easing dictionary, keyframe pose-contract, camera grammar, and three tool lanes (HTML/GSAP, three.js, ffmpeg filtergraph). Use for any short piece where motion is the message. Routes through smart-router when unsure.
---

# Motion Graphix — the premium-feel system

Premium motion graphics are not more effects — they are **matched feel, disciplined easing, verified pixels**. This skill distills the upstream libraries in `library/` (hyperframes Apache-2.0, frontend-slides MIT, plus an index of the AGPL OpenMontage catalog and unlicensed apple-design checker) into one build procedure.

## 1. Feel first — the effect→feeling matrix

Pick the feeling BEFORE picking animations. Mismatched feel is the #1 "cheap" smell.

| Feeling | Motion recipe | Visual cues |
|---|---|---|
| Dramatic / cinematic | slow fades 1–1.5s, scale 0.9→1.0, parallax layers | dark ground, spotlight, full-bleed image |
| Techy / futuristic | glitch/scramble text, grid reveals, particle drift, neon glow strokes | grid patterns, mono accents, cyan/magenta/electric blue |
| Playful / friendly | spring-physics bounce, overshoot pops, bobbing | rounded corners, pastel/bright, hand-drawn |
| Professional / corporate | subtle FAST moves 200–300ms, no bounce | navy/slate/charcoal, precise spacing, data focus |
| Calm / minimal | very slow subtle drift, gentle fades | high whitespace, muted palette, serif |
| Editorial / magazine | staggered text reveals, image-text interplay | strong type hierarchy, pull quotes, grid breaks |

**Speed law:** corporate reads *fast* (≤300ms entrances); expressive reads *springy* (overshoot); dramatic reads *slow* (≥1s fades). Wrong speed = wrong genre.

## 2. Easing dictionary (use named intent, not defaults)

| Intent | Curve | Use for |
|---|---|---|
| Settle-in | expo-out (CSS `cubic-bezier(0.16,1,0.3,1)`) | entrances, text atoms, cards — the premium default |
| Anticipate | ease-in then snap | exits, wipes feeding a cut |
| Impact | set/step or ≤3-frame tween | punches, stutters, whip accents |
| Playful pop | spring (overshoot 1.05–1.2) | chips, badges, emoji, stickers |
| Camera | custom ease-in-out per segment, velocity continuous | keyframed moves (see pose contract) |
| Never | plain `linear` for visible moves, default `ease` mush | — |

## 3. Keyframe pose contract (from the hyperframes discipline)

A keyframe sequence is a **pose contract**: named subject, visible states, continuous identity, known final state, and *seek-safe* runtime (any timestamp renders correctly without playing from 0). Rules:

1. **One wrapper per subject** stays alive across the whole move; author states as a **pose ladder** — never kill+respawn the element mid-move (that pops).
2. Per-segment easing between poses; velocities should match at pose joins (no kinks).
3. Mechanism mapping (author truthfully): punch = short `scale` tween; smooth reframe = translate+scale ladder on the same wrapper; Ken Burns = slow translate+scale; crop reveal = `clip-path`/mask interpolation; wipe/iris = mask boundary across overlapping clips; match/whip = handoff with preserved direction+velocity.
4. Verify with snapshots at pose times (stills at exact keyframe instants), not vibes.

## 4. Camera grammar (2.5D/fake-3D and true-3D)

- **Punch-in/out** on a crop wrapper; hard punch ≤3 frames, smooth punch eased.
- **Truck/pedestal** = translate track; **dolly** = scale about a focus point; **roll** = rotate ±2–5°; combine as ladder on ONE wrapper.
- **3D feel without WebGL** (ffmpeg-proven in this repo): `perspective`/`rotate` animated + `zoompan` dolly; inputs must exceed output raster (overscan) so edges never empty.
- **True 3D** (three.js lane): real camera = dolly/truck/orbit on empties, lens 35–50mm for product honesty, DOF+bloom as post, lights: key + rim; never animate position AND look-at independents on the same beats (sea-sick).
- Motion blur sells speed: prefer blur strips/echo (3-frame ghosting at 30–50% alpha) over smearing every move.

## 5. Text atoms & infographic atoms

- Entrance recipes: fade+slide-up 30px/0.6s expo-out (most versatile); scale 0.9→1 expo; slide-x −50px; blur-in 10px→0/0.8s. Exit = faster than entrance (0.6×).
- Stagger children 40–90ms; tighter stagger (≤50ms) = corporate, wider = editorial.
- Stat grammar: count-up 0.8–1.2s with dynamic scale pulse at terminal value + optional ring fill; bar/fill grows from baseline anchor, not center.
- Kinetic type: words/chars pop on VO beats; hold ≥1.1s before exiting (inherited from style-recreate hold law).
- Lower-thirds/callouts: enter on montonic track (same direction every time in a piece), exit mirrored.

## 6. Categories (dispatch inside this skill)

kinetic-type · stat/count-up · charts/data · logo-reveal · lower-thirds/callout · animated map · webpage/UI scroll-reveal · news/headline card · tweet/social card · asset-fusion (real image geometry becomes the graphic) · deck-to-video (slides lane). Category picks the recipe; the feel matrix picks the dressing.

## 7. Tool lanes (router selects)

| Lane | Best for | Notes |
|---|---|---|
| **HTML/GSAP → capture** | decks, UI animation, type-driven pieces | `library/frontend-slides/*` recipes; deterministic timing via GSAP timeline labels; capture via headless browser record or per-frame screenshot→ffmpeg |
| **three.js** | true 3D cameras, product/world depth | `INDEX-upstream.md` → threejs family; post: bloom/DOF; render offscreen, frame-grab to ffmpeg |
| **Remotion** | React-composed, data-driven, parameterized video | see `remotion-studio` skill; `interpolate()` + spring() = pose contract in React |
| **ffmpeg filtergraph** | plate pipelines, exact-style recreation, batch assembly | proven in `video-style-recreation`: plates + overlay windows + zoompan/perspective + chroma-key; fastest when art is already plates |

## 8. Design-review lane (apple craft checklist, facts only)

Audit before ship: 44pt+ touch-equivalent titling hierarchy; one accent hue per scene; spacing on an 8pt grid; radii consistent (squircle family); contrast ≥4.5:1 for body; motion respects "reduce motion" taste (no gratuitous bounce on corporate); SF-geometry feel = optical not mathematical alignment (nudge glyphs ~1–2%); whitespace is a feature. Full checker: upstream `dickwu/apple-design-skill` (INDEX-upstream.md).

## 9. Build procedure

1. **Intent + feel**: name the piece, pick ONE feeling row, ONE category.
2. **Assets before design**: source real imagery/fonts first; design around what exists (asset-first discipline).
3. **Storyboard as pose ladder**: subject, states, joins, easings, camera lane.
4. **Build** in chosen lane. Time atoms to VO/music beats; hold law ≥1.1s on reads.
5. **Verify**: snapshots at every pose time + one full-contact sheet; check against feel row; run the design-review checklist.
6. **Audio** via the style-recreation recipe (duck under VO, loudnorm, fade+apad); premium pieces survive on sound more than pixels.
7. **Render last, gated**: only after checks pass; then faststart mp4 + poster + QA frames viewed.

## 10. Guardrails

- One wrapping subject per move; no respawn pops. Transform/opacity only in hot paths (filter/layout triggers banned except blur-in accents).
- Exits faster than entrances; entrances never faster than 200ms unless an impact frame.
- No unverified render ships; no library asset without its license file beside it (Apache-2.0/MIT vendored; AGPL OpenMontage and unlicensed apple-design are INDEX-only).
- Wipe policy: this folder (incl. `library/`) is the durable brain; tools in `outputs/` are disposable and reinstallable from each lane's section.
