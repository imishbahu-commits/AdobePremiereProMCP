---
name: remotion-studio
description: Programmatic video in React via Remotion — parameterized compositions, spring()/interpolate() pose contracts, data-driven batches, CLI rendering. Use for premium motion graphics that need real component reuse, data binding, or programmatic variant batches. Router fallback: motion-graphix GSAP/HTML or ffmpeg lanes.
---

# Remotion Studio

## When this lane

Choose Remotion when the piece is **parameterized** (data → video), **reused** (component library across episodes), or **batched** (N variants). For one-off exact-style recreation, our ffmpeg plate pipeline is faster. Judge by: will this composition render again with different data? If yes → Remotion.

## Concepts that map to the motion-graphix grammar

- `interpolate(frame, […], […], {easing})` = **pose ladder segments**; `spring()` = playful-pop easing; `Easing.bezier(0.16,1,0.3,1)` = expo-out settle (the premium default).
- `<Sequence from durationInFrames>` = scene/atom windows (our `enable='between(t,…)'` law, expressed declaratively).
- `useCurrentFrame()` per component = seek-safe pose contract: any frame renders correctly from pure state.
- `<OffthreadVideo>` for real footage; `<Img>` + `staticFile()` for plates (our chroma-prep recipes apply).
- Audio: `<Audio>` + `audioVolume` envelopes = duck/loudnorm equivalents; keep final loudness passes in ffmpeg (ebur128 verify) as usual.

## Install (sandbox; `outputs/` gitignored — rerun after wipe)

```bash
mkdir -p outputs/remotion-studio && cd outputs/remotion-studio
npm init -y
npm i -q remotion @remotion/cli @remotion/bundler @remotion/renderer react react-dom
npx remotion browser ensure   # downloads chrome-headless-shell (needs glibc deps; see notes)
```

Project shape: `src/index.ts` (registerRoot) + `src/Root.tsx` (`<Composition id width=1920 height=1080 fps=30 durationInFrames=…>`) + components. Preview: `npx remotion studio` (bind 0.0.0.0, port 3000 for Arena preview). Render: `npx remotion render <id> out.mp4 --codec h264`.

## Sandbox notes (verify honestly)

- Headless Chrome sandbox flags in containers: if render crashes, add `--browser-args="--no-sandbox"` via env `REMOTION_BROWSER_ARGS` or config override.
- Missing shared libs (libnss3/libatk…) kill Chrome — if apt is blocked, fall back to the motion-graphix GSAP/capture lane and document it.
- Chromium download comes from googleapis (usually reachable here); if blocked, retry later or use GSAP lane.

## Authoring guardrails

- Duration in FRAMES, not seconds (fps=30: a 60s piece = 1800 frames).
- Keep per-frame work pure: no DOM queries, no Date.now() in render path (kills frame determinism).
- Ease every visible move (matrix in motion-graphix §2); hold law ≥1.1s for reads applies here too.
- Batch variants via `--props` JSON, never by duplicating compositions.
- Audio master: still finish in ffmpeg (loudnorm + fade + apad + faststart) — Remotion's AAC is a stem, not a master.
