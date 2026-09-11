# AE Magic for Agents — 3D Camera, Parallax, Transitions Playbook

Goal: produce "feels alive" video — the look top editors get from After
Effects' 3D camera + 2.5D parallax rigs — using only agent tools: PIL plates,
ffmpeg filtergraphs, easing math. This doc = (1) the toolkit analysis,
(2) AE-feature → agent-recipe translation, (3) the motion grammar that
separates alive from dead, (4) the build spec for `v3_depth_magic`.

---

## 1. What the AE "magic" actually is (decompiling the illusion)

AE's 3D camera trick is **2.5D**: every layer is a flat card in Z-space,
one perspective camera moves through them. There is no real 3D geometry —
the *brain* does the reconstruction from 4 depth cues:

| depth cue | how editors use it | why it sells "alive" |
|---|---|---|
| **Relative motion** (parallax) | near planes move faster than far planes under camera drift/with moves | strongest cue; camera feels physical |
| **Focus separation** | rack focus: near blur → far blur swaps during moves | simulates lens DOF; forces eye attention |
| **Scale falloff** | near planes larger + exit frame edges on push-ins | spatial tunnel = "camera travels through" |
| **Occlusion & drift phase** | planes occlude each other; each drifts on its own sin phase | layer independence = air between planes |
| **Motion blur** | editors enable layer motion blur; fast moves smear | speed = quality hallmark |
| **Overlap/follow-through** | nothing stops when something starts; counters overlap | "alive" = no dead frames, inertia readable |
| **Anticipation & settle** | 1–3 frame tick backward before a reveal; overshoot+settle after | gestures feel intentional, animate |
| **Light anchoring** | bloom, leaks, shafts respond to camera, screen-blend | light = physics = reality |

Rigs editors actually build: **(a)** null-object camera rig (one camera
parented to a null, all animation on the null, camera just follows);
**(b)** 2.5D parallax comp (split a still into 3–7 depth planes, pin them
in Z, drift camera); **(c)** cube/orbit card (6 planes rotated in 3D, or
a single card rolling on Y with perspective); **(d)** speed-ramp + whip
(transition hidden inside 200-500% speed burst with directional blur).

## 2. AE feature → agent recipe

All recipes proven in this repo's pipeline (PIL plates + ffmpeg 7).

| AE | agent recipe | ffmpeg primitive |
|---|---|---|
| Camera push-in (dolly) | eased zoom into focus point `: z` driven over time | `zoompan=z='1+P*IN(clip((t-T0)/D,0,1))':x='iw/2-(iw/2)/zoom+FX*iw/zoom/2'...:d=D*fps:s=WxH` |
| Abandoned-zoom-crop dolly | crop window narrows over time | `crop=w='iw*(1-P*q)':h='ih*(1-P*q)':x=...,scale=WxH` |
| Orbit around subject | subject pinned center; background plane slides far slower opposite dir ± rotate tiny | `overlay` on bg with `x=-P*W*0.1`, `rotate=a='0.04*q'` |
| Parallax planes | N plates at zᵢ, each overlay x/y = base + zᵢ-scaled share of one camera term `q(t)` | per-plane `overlay='X0+F_i*Q':'Y0+G_i*Q'` with `Q=q eased` |
| Rack focus | two duplicate planes, one blurred; cross-fade their alpha over time | `gblur=sigma=S` on alt + `fade=alpha=1` each |
| Handheld drift | tiny sinusoidal+2nd harmonic on EVERYTHING, phase-offset | `x='X+A*sin(2*PI*t/T1)+B*sin(2*PI*t/T2+φ)'` |
| Whip-pan transition | fast crop-window pan (5–7 frames) + strong mechanical directional blur + light-flash plate | `crop=x='f(t)' + gblur plane wide + overlay flash at alpha spike` |
| Speed ramp smear | apply zoom/pan inside eased envelope (never linear) | envelope `q=clip(...)` then `smooth=1-pow(2,-10*q)` expo-out, or `q*q*(3-2*q)` |
| 3D card orbit (perspective) | animate 4 corner coords of plane over time (perspective filter takes keyframed corners) | `perspective=x0=...:y0=...:sense=0` per-frame via API; cheap alt: pre-render 3–5 perspective plates in PIL, cross-fade |
| Cube transition | two scenes on faces of a rotating card | PIL pre-rotate into 5-7 intermediate perspective plates, cross-fade |
| Light leak overlay | warm/white streak plate at 20–40% alpha, screens in at cut point | `overlay` + `fade alpha` + bloom pass |
| Motion blur feel | directional smear plate behind fast element; or duplicate element offset 1–2 frames at 30% alpha | `blend` normal/screen of two offset streams |
| Bloom/lens glow | global: split → gblur σ20–30 → screen 0.15–0.25 | as in v2 grade |
| Vignette+contrast | crushed blacks, mid-tone contrast, edge falloff | `eq,vignette` final pass |
| Shake accent (impact) | 2–4 frame ±6–10px translate pulse decaying | overlay x/y with `exp(-k*(t-T))*sin(2*PI*F*(t-T))` |

**Easing law for every keyframe pair**: expo-out `1−2^(−10p)` for reveals,
cubic `p²(3−2p)` for travels, overshoot `1+2.7(p−1)³+1.7(p−1)²` for pops.
Never linear except the perpetual handheld drift.

## 3. The grammar of "alive" (checklist pinned to every build)

1. **No still frames. Ever.** Every visible layer moves, always. Even 2px/s.
2. **Phases differ.** No two layers share sin period/phase — synchronized
   drift reads as "attached to one card".
3. **Fingerprints of physics**: decays (shake accents), inertia (expo-out
   settles), anticipation (tiny counter-move first).
4. **Transitions carry velocity**: a cut at zero motion is a dead cut.
   Enter every transition at mid-speed, exit at mid-speed; hide seam in
   whip blur or 2-frame light flash.
5. **Depth = 3 cues minimum**: relative motion + focus + scale.
6. **Text is a light source**: titles bloom (they're lights), enter via
   defocus-in (σ large→0), never fade from black top-level.
7. **Camera never teleports**: every reframing is a move with ease + decay.
8. **End frames breathe**: the final card holds its drift + handheld for
   1.5–2s before any fade, so the logo/CTA "lives".

## 4. Build spec — `v3_depth_magic` (27 s, 1080×1920 @ 30)

One continuous-feel camera journey, 4 segments ≤7s (OOM rule):

| seg | span | scene | hero techniques |
|---|---|---|---|
| B1 | 0–6.6 | **Parallax corridor**: 5 depth planes of floating screens receding; camera pushes in 9%; foreground planes fly past frame edges | per-plane eased overlay motion from one `q`; rack-focus σ swap near→far at t≈3.4; hero title defocus-in at 4.2 |
| B2 | 6.6–13.4 | **Orbit + whip**: chrome-clock card on perspective-rocking card; camera orbits (bg counter-slide + zoompan shadow); whip-pan burst 7→7.25s with directional smear + light flash | perspective keyframe plates ×3 cross-fade; whip via crop-pan + blur plate + 2-frame leak |
| B3 | 13.4–20.6 | **Mosaic alive**: tile wall (photo wall art) breathing tiles at staggered phases; slow push; mid push: impact shake accent + cards drift apart then reunite | per-tile phase drift; accent pulse `exp decay`; rubric label letter-track |-
| B4 | 20.6–27 | **Pullback reveal + living endframe**: mosaic scales down revealing full wall + "LET'S BUILD" card grows from center with overshoot; handheld lives to 27s, fade 26.2 | eased cubic pullback, overshoot pop on CTA, no still frame till end |

Audio: dark pad bed + soft whoosh riser into whip (sin sweep 120→600 Hz,
0.3s, −24 LUFS peak) + low thump under shake accent (54 Hz burst 0.15s).

## 5. Agent execution notes (this codebase)

- Producing code: `PIL` plate factory → depth planes as RGBA PNGs.
- Graph emitters reuse `Block` class from `gen_blocks_v2.py` (label
  bookkeeping, time rebase, fades/enable clamps).
- New techniques live in `gen_blocks_v3.py`: `q(t)` shared-camera term,
  per-plane depth coefficients, `gblur` rack-focus pairs faded by alpha,
  whip-pan via crop-window pan expression + smear plate, impact accent
  `exp(-k(t-T))sin(2πf(t-T))` translations.
- Render ≤7s segments → JPEG sequences → contiguous concat → x264 crf 19.
- QA: per-segment frame sheets; check seam frames at every boundary.
