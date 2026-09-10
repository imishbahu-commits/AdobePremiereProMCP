---
name: video-matting
description: Human video matting without a green screen via RobustVideoMatting (temporal recurrent nets) — cut subjects out of footage into alpha plates for compositing, background replacement, duotone re-worlding. Use when a style needs real footage composited into flat/duotone worlds. GPL-3.0 tool, installed in sandbox, never vendored.
---

# Video Matting (RobustVideoMatting)

## Why

Our plate pipelines key on `#00FF00` chroma. RVM removes the *need* for the green screen: a recurrent net mattes people from ANY video with temporal memory (no per-frame flicker), producing alpha foregrounds we can composite into duotone worlds, sunbursts, infographic scenes. Upstream: github.com/PeterL1n/RobustVideoMatting (GPL-3.0 — tool install only, do not vendor into this repo).

Published capabilities (facts): HD real-time on GPU (paper reports ~104fps HD / 76fps 4K on a 1080Ti); CPU works but much slower (plan seconds-per-frame at 1080p in this sandbox — batch accordingly); model `rvm_mobilenetv3` (small, fastest) and resnet50 variant.

## Install (sandbox; rerun after a wipe)

```bash
mkdir -p outputs/tools/RVM && cd outputs/tools/RVM
python3 -m venv .venv
./.venv/bin/pip install -q torch torchvision --index-url https://download.pytorch.org/whl/cpu
./.venv/bin/pip install -q av pims
# weights (~14MB) from the GitHub release; if objects.githubusercontent.com is blocked,
# retry via a mirror or fetch in a later session — the skill doc records the URL:
curl -L -o rvm_mobilenetv3.pth \
  https://github.com/PeterL1n/RobustVideoMatting/releases/download/v1.0.0/rvm_mobilenetv3.pth
```

## Recipe — footage → alpha plate → filtergraph

1. Matte: load the `.pth` (torch.jit or torchhub `torch.hub.load("PeterL1n/RobustVideoMatting","rvm_mobilenetv3")`), iterate frames, keep recurrent state; write foreground RGBA PNG sequence (or green-screen mp4 with `--output-type green_background` for compatibility with our `colorkey` chains).
2. Composite the RGBA plates directly with `overlay` (skip colorkey when true alpha exists) or chroma-key the green plate via the despill recipe in `video-style-recreation`.
3. Style it: flat outline stroke (dilate alpha 6px, composite ink underlay) to sit the subject into the duotone world convincingly.
4. Edge discipline: despill + 1px erode on alpha kills halo; temporal flicker is handled by RVM's recurrent state — never matte frames independently.

## Guardrails

- GPL-3.0: install/use as a tool, never copy its code/weights into this git history.
- CPU sandbox: pre-scale to the smallest workable raster (720p→matte→upscale alpha) before compositing at 1080p.
- RVM mattes humans; for objects, fall back to chroma or hand masks.
