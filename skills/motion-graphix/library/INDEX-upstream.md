# Upstream index — skills cataloged but NOT vendored (license-safe)

These catalogs are referenced by name and capability only. Nothing below is copied
from the upstream repos (OpenMontage is AGPL-3.0, apple-design-skill ships no
license); to read the material itself, shallow-clone upstream:

```bash
git clone --depth 1 https://github.com/calesthio/OpenMontage
git clone --depth 1 https://github.com/dickwu/apple-design-skill
git clone --depth 1 https://github.com/nexu-io/open-design
git clone --depth 1 https://github.com/PeterL1n/RobustVideoMatting
git clone --depth 1 https://github.com/harry0703/MoneyPrinterTurbo
```

Vendored here instead (permissively licensed, LICENSE files beside them):
`hyperframes/` (Apache-2.0, © heygen-com), `frontend-slides/` (MIT, © Zara Zhang).

## OpenMontage catalog — capability map (`<repo>/.agents/skills/…`)

Motion/animation lanes:
- `gsap-core` `gsap-timeline` `gsap-plugins` `gsap-scrolltrigger` `gsap-utils` `gsap-frameworks` `gsap-react` `gsap-performance` — GSAP animation recipes: timelines, staggers, scroll choreography, plugin surface, perf discipline, framework bindings.
- `framer-motion` — React animation via Framer Motion variants/springs/layout animations.
- `threejs-fundamentals` `threejs-animation` `threejs-geometry` `threejs-materials` `threejs-lighting` `threejs-textures` `threejs-shaders` `threejs-postprocessing` `threejs-interaction` `threejs-loaders` `threejs-world-generation` — full three.js lane: scene→material→light→shader→post, camera animation, asset loading, world building.
- `lottie-bodymovin` — After-Effects→Lottie vector animation playback.
- `manim-composer` `manimce-best-practices` `manimgl-best-practices` — Manim (Community + GL) math/explainer animation.
- `canvas-procedural-animation` — raw 2D canvas particle/procedural systems.
- `svg-character-animation` — SVG rigged character motion.
- `motion-graphics` — generic motion-graphics dispatch concepts.
- `hyperframes-*` family — mirror of heygen hyperframes skills (vendored originals under `library/hyperframes/`).
- `remotion` `remotion-best-practices` `remotion-to-hyperframes` — Remotion authoring and migration notes (see our `remotion-studio` skill).
- `css/design`: `tailwind-design-system`, `web-design-guidelines`, `vercel-composition-patterns`, `vercel-react-best-practices` — layout/design-system craft.

Video/editing lanes:
- `video-edit` `video-toolkit` `ffmpeg` — edit planning, ffmpeg recipe collections.
- `video-understand` — analyzing incoming footage (the natural companion to our teardown skill).
- `synthetic-screen-recording` — generated product/screen recordings.
- `sound-effects` `music` `music-to-video` `media-use` — audio beds, beat-matching, asset sourcing.
- `video-download` `video-translate` — acquisition/translation utilities.

Generative/external lanes (need API keys — treated as optional bonus lanes per router):
- `ai-video-gen`, `kling-official`, `seedance-2-0/2-5`, `ltx2`, `minimax-h3`, `flux-best-practices`, `bfl-api`, `grok-media`, `gemini-omni`, `dashscope`, `doubao-tts`, `elevenlabs`, `azure-*`, `fish-audio-tts`, `heygen`, `avatar-video`, `faceswap`, `comfyui`, `3d-asset-generation`, `character-rigging`, `character-animation-qa`, `pose-library-design`, `acestep`, `lyria`, `mermaid`/`beautiful-mermaid`, `d3-viz`, `create-video`, `atlas-cloud`, `setup-api-key`, `agents`.

## apple-design-skill (no LICENSE — facts only)

Design reviewer grounded in Apple's HIG corpus (~122 pages from developer.apple.com);
audits Flutter / React Native / Tauri / Electron / SwiftUI / UIKit / AppKit UIs and
translates Apple's vocabulary per platform. Install path upstream suggests
`npx skills add dickwu/apple-design-skill`. Our distilled checklist lives in
`../SKILL.md` §8 (design-review lane) — written from capability facts, not copied text.

## open-design (source-available app)

Electron design app ("open Claude Design alternative") with `.claude/skills/od-contribute`
(contributor-facing only). Value to this repo: design-system token thinking; used as
inspiration, nothing vendored.

## RobustVideoMatting (GPL-3.0) & MoneyPrinterTurbo (MIT)

Installed as sandbox tools under `outputs/tools/` (never vendored); usage docs in
`skills/video-matting` and `skills/ai-video-factory`.
