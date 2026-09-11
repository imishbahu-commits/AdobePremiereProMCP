# Pipeline v2 — dark-premium 3D-mockup recreation (reference 16702.mp4)

Reference: `outputs/uploads/16702.mp4` (13.26s, 720×1600, silent screen-recording of
AutoAE template previews). Atomic teardown: `outputs/analysis/v2/STYLE_ANALYSIS_v2.md`
(5 looks A–E, motion laws, 60s recreation spec).

## Builders (this directory)

| file | role |
|---|---|
| `gen_render_v2.py` | PIL plate factory (shaft/dust/moons, chat UI set, floor gallery + outlined T1/T2, marquee ribbon, tear wipe, collage, CTA) + AI-asset prep (`clock_a.png` luminance-keyed cutout, `wall_full.png` 1080×1920) |
| `gen_graph_v2.py` | single-pass 60s filtergraph emitter (diagnostic; superseded by blocks) |
| `gen_blocks_v2.py` | production emitter: per-block graphs + run script. `Block` class: overlay chaining, time rebase (`t0`), enable/fade clamping, single-use label bookkeeping, split for multi-used inputs, global grade per block |
| `run_blocks.sh` / `run_blocks2.sh` | generated render commands (block → JPEG frame sequence) |

## Render & assemble

```bash
PYTHONPATH=outputs/pylibs python3 gen_render_v2.py   # plates
PYTHONPATH=outputs/pylibs python3 gen_blocks_v2.py   # graphs + run_blocks2.sh
bash run_blocks2.sh                                   # block JPEG sequences
# concat picks: b1[0,282) b2a[12,198) b2b[0,204) b3a[12,246) b3b[0,249)
#               b4a[15,189) b4b[0,166) b5[0,311)  -> reels_all/ (1806f = 60.2s)
ffmpeg -framerate 30 -i reels_all/%05d.jpg \
  -f lavfi -i "aevalsrc=<dark-pad>:s=44100:d=60.2" \
  -c:v libx264 -preset medium -crf 19 -pix_fmt yuv420p \
  -c:a aac -b:a 96k -movflags +faststart -t 60.18 v2_recreation.mp4
```

Deliverable: `outputs/demo/v2_recreation.mp4` → served by the gallery via
`outputs/uploads/v2_recreation.mp4` (+ poster in `server/public/posters/`).

## ffmpeg landmines hit this build (do not re-learn)

1. **filtergraph line breaks**: `write_text` must emit REAL newlines; a sed
   `\\n` replacement silently turned them into literal backslash-n →
   `No such filter: ''`. Verify with `od -c | head` before debugging filters.
2. **Labels are single-use**: reusing one `[wN]` label in two overlays
   degrades the error to `Invalid stream specifier: wN` far from the cause.
   Warm each input `format=rgba,split=N[wN_0..wN_k]` with N = overlay count.
3. **`-filter_complex_script` is deprecated but `-/filter_complex F` works**;
   the classic backslash-newline continuation in v1's graph still parses.
4. **libx264 lookahead hides progress**: at ~1.5 fps x264 emits "frame=0"
   for tens of seconds (buffered B-frames). It is rendering, not hung.
   Use image2/JPEG output for block renders; x264 only in the final pass.
5. **Duration-triggered OOM (ffmpeg 7.0.2-static)**: identical graph &
   inputs render fine at `-t 11` but OOM-kill (4 GB box) at `-t 13.6` —
   input prebuffering scales with declared `-t`, not processed frames.
   Mitigation: **render per-block at ≤7 s** and concat frames. Per-block
   runs sustain 15–30 fps at 1080×1920.
6. **PNG loop decode tax**: `-loop 1 -framerate 30` PNG inputs decode per
   frame; whole-frame plates are the dominant CPU cost. Thin plates with
   trim + explicit byte offsets beat 1080×1920 full-frame plates.
7. **Luminance-keyed AI art**: JPEG "black" AI backgrounds are lum 8–25;
   bbox from a threshold mask (≥64), alpha ramp from ≥30, else the cutout
   includes noise and the bbox spans the full frame.
8. **Time rebase on split blocks**: when blocks are split, clamp
   `fade st=max(0, st-t0)` and normalize `enable` bounds; expression
   `(t-X)` literals in overlay x/y must be rebased by the same `t0`
   (regex `\(t-([0-9.]+)\)`).

## Motion-law checklist verified in QA frames

- zero holds: every visible layer carries `±A·sin(2πt/T+φ)` drift
- expo-out reveals via `1-pow(2,-10·clip(p))`
- blur→sharp defocus-in pairs (t5, t3) with 0.45–0.55s cross-fade
- 70 ms chip stagger, dots typing at 0.3 s cycle steps
- grow-from-anchor wipes: driven paper tear, cover-slide typing
- dip-to-black transitions 0.22 s at block boundaries
- global grade: screen-blend bloom (gblur σ26 @0.20) → contrast 1.07 →
  vignette PI/4.7

Audio: reference is dead silent; a ≈−39 LUFS dark-pad bed was added
(optionally `--an` to match reference exactly).
