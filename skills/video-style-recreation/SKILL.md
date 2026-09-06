---
name: video-style-recreation
description: Analyze a reference video at the atomic level — cuts, pose holds, motion signatures, palette, loudness, story structure — then recreate an exact-style episode with a PIL + ffmpeg filtergraph pipeline. Use when the user supplies reference videos and asks to "create in that style", clone an editing style, build lookalike animated episodes, or ship a flat-2D explainer with measured (not guessed) style rules.
---

# Video Style Recreation

Two-phase discipline: **measure the style first, then build**. Never write a frame of the recreation until the reference has been torn down into hard numbers. Every rule in the build must trace back to a measurement.

## Phase 1 — Atomic style teardown

Run telemetry on each reference before any creative work:

1. **Probe**: duration, raster, fps, streams (`ffprobe`/`ffmpeg -i`).
2. **Cut census**: scene-cut detection plus manual frame-stepping; record timestamp of every hard cut. Short-form explainers in this genre are *zero-cut*: cuts only at meaning shifts (sponsor boundary) and stutter accents. Compute cuts/min.
3. **Pose-hold census**: count freezes ≥ 0.8s, take median + max (this genre: 1.1–1.4s median holds every 2–14s — economical animation reading as "beat, beat, beat").
4. **Shot inventory**: hero's % of frame in masters vs close-ups (measured: 0.4–2% wide masters; close-ups rationed for emphasis). Rule extracted: *stay wide, punch in only to land a point.*
5. **Loop timing**: exercise cycles run 0.8–1.2s/rep on a dead-still camera.
6. **Signatures**: catalog recurring motion-design atoms (see measured table in `docs/STYLE_ANALYSIS.md`): numeral pops high-center, sunburst product hero + yellow ADVERTISEMENT tag, 3–6-frame white motion-jags, violet ALL-CAPS title card, ladder/stat infographics, comic side-character mirroring the hero.
7. **Palette**: sample hex values per role (base/mid/deep/hero/paper) per scene — this genre uses per-scene duotones, not global grading.
8. **Audio**: EBU R128 integrated loudness + LRA (refs measured −22.8/−23.9 LUFS); log VO gap cadence (0.6–0.8s gaps every 3–6s).
9. **Structure**: timestamp the blocks — cold open → B-story gag → title card → A/B beats → infographic (~55%) → sponsor skit (~60%) → payoff → outro.

Write it all to a STYLE_ANALYSIS.md with contact sheets. If a rule isn't measured, mark it as an assumption.

## Phase 2 — Recreation pipeline

Stage order is load-bearing (see `pipeline/run_v1.sh`):

1. **Voice-over first** — narration durations lock the timeline. Place VO drops on the beat map *before* building video.
2. **Plates** — generate all art as flat PNG plates (PIL or image model) on pure `#00FF00` chroma: backgrounds full-frame, characters/props keyed. Keep plates reusable across scenes.
3. **Filtergraph** — one ffmpeg `filter_complex` assembles the whole episode: `colorkey` each plate, then `overlay` with time-windowed `enable` expressions; camera moves via `zoompan` (2018 static ffmpeg: crop-as-camera is a dead end). Numerals, chips, jags, titles are all overlay atoms with pop-in easings.
4. **Audio mix** — separate script (see below), then mux with `-c:v copy`.
5. **QA** — extract stills at *every named beat* and view them. Never ship from logs alone.

Shipped reference implementation (78s episode): cold open with hamster gag + numeral → title card → rep room (reps 9–14, jag gag) → progression-ladder infographic (chips 6x→15x, +27% MASS bubble) → sponsor sunburst skit → finale (freeze + double white flash + GOLD SET ★ + punch zoom ×1.24) → space outro. Timeline + telemetry in `docs/STYLE_ANALYSIS.md`.

## Editing grammar (the measured rules)

- **Zero-cut default.** Transitions are animated camera travel — follow-pans, whip-pans, punch-zooms — never cuts. Reserve hard cuts for meaning shifts only (sponsor segment boundary). Stutter double-frames are impact accents, not errors.
- **Pose holds 1.1–1.4s** around punchlines and technique cues; cluster, don't distribute evenly.
- **Stay wide.** Masters keep the hero tiny (≤2% frame). Punch in (6–10 frame zoom) only to inspect or land a gag, then settle back.
- **Loops on locked camera** — 0.8–1.2s per rep; no drift.
- **Impact frames** for gags: 3–6 frame white motion-jags at contact points, stutters, sunburst behind the object.
- **Infographics replace the scene** at ~55% through; **sponsor skit** at ~60% with a rotating sunburst, branded open box, and yellow ADVERTISEMENT tag — the only sanctioned hard cut.
- **Window-gate scene furniture** (`enable='between(t,start,end)'`) so infographic elements never bleed into the finale/outro.
- **Duotone worlds**: lavender base `#D6CEEA`, mid `#9887C6`, deep `#492488`, hero yellow `#F6D370`, paper `#F6F4F5` — swap worlds per scene, keep the hero constant.

## ffmpeg / tooling craft (hard-won, do not relearn the hard way)

- **Filter labels are single-use.** A label consumed twice → `Invalid stream specifier: <name>` (reports only the FIRST re-used label). Clone with `split=2`/`split=3` per extra consumer; leave no unconnected intermediate labels.
- **2018 static ffmpeg quirks** (bundled binary in `pipeline/`): no `amix normalize=` (compensate with post-`volume`, amix pre-attenuates 1/n — VO mixes need ≈ ×4.5); `apad whole_dur=` absent → `whole_len=<samples>`; `acompressor threshold` is linear (0.13 ≈ −18dB; dB values rejected); `scdet` absent.
- **"Failed to inject frame" into amix = rate/layout mismatch.** Prefix every source (including lavfi `aevalsrc`/`anoisesrc`) with `aformat=sample_rates=44100:channel_layouts=stereo`.
- **Debug loops**: smoke-test with `-t 1`, grep `-iE "error|invalid|not found|fail" | head` — never pipe stderr through `tail` (it hides the first, real error).
- **Mux gotcha**: `-shortest` truncates to the shorter stream. If the render outlives the audio, extend audio instead: `-af "afade=t=out:st=T:d=D,apad" -t <dur>`.
- **Delivery**: `-movflags +faststart`, verify with `ebur128` Integrated, then poster frame at the payoff moment.
- **zoompan time** works in frames: expressions use `on` (output frame n), so write `t` as `on/30`.

## Chroma & plate craft

- `colorkey=0x00FF00:similarity:blend` — start 0.28/0.06; raise similarity to ~0.36 for soft glow edges. If fringe survives, **despill the PNG per-pixel instead of cranking similarity** (which eats the art):
  - `greenness = G − max(R,B)`; `> 60` → rewrite pure `#00FF00` (key removes it cleanly);
  - `> 0` near art → set `(m,m,m)`, `m = max(R,B)` — hue-free monochrome glow (kills speckle against dark backgrounds);
  - 0.8px Gaussian blur pass at the end.
- **Never trust font glyph coverage** (DejaVu lacks ★ → tofu box baked into plates). For symbols, draw polygons directly; place them by measuring the text's alpha bbox, extending the canvas, and compositing with a gap — never guess x offsets.
- Verify fixed plates as *image crops before committing to a full render* — a 10-minute render cycle to discover a bad plate is self-inflicted.

## Audio recipe (reference mix)

- VO drops locked at 1.0 / 30.8 / 43.8 / 58.2s via `adelay` (ms, per channel).
- Bed: `aevalsrc` 128bpm kick + 55Hz sub + pad, `anoisesrc` hats; `sidechaincompress` duck 8:1 (threshold 0.03, attack 8ms, release 450) keyed by VO.
- Chain: normalize all sources → `amix` → post-`volume` → `acompressor` (linear threshold 0.13, ratio 3) → `loudnorm I=-15:TP=-1.5:LRA=9` → verify Integrated lands ≈ −14.7 LUFS; fade the tail, then `apad` to full duration.
- Full working graph: `pipeline/aud_v1.txt`.

## Server tooling

`server/server.mjs` + `server/public/index.html`: zero-dependency gallery + chunked uploader. PUT 8MB chunks (id `[A-Za-z0-9-]{8,64}`), POST complete with size verification, auto-poster at 1.5s, recursive video scan keyed by basename. Serve video via URLs **relative to the scan root** — absolute host paths break the browser (the browser is not the sandbox).

## Guardrails

- Never create before measuring: no STYLE_ANALYSIS.md, no build.
- A cut is a meaning shift, not a beat. If the recreation has more hard cuts than the reference's census, the style is wrong.
- View QA frames at every beat; "ffmpeg exited 0" is not visual correctness.
- Videos, QA stills, uploads, and regenerable plates stay out of git (repo ignore convention: `outputs/*`); only the skill, scripts, and small graphs are committed.
- Long renders: do the smallest render that verifies the change (plates as PNG first, `-t 1` smoke tests, single-beat probes).
