---
name: smart-router
description: Central dispatcher for every creation/editing task in this repo — routes an intent (recreate a style, premium motion graphics, code-driven animation, AI short-video factory, human matting, design QA, slide decks) to the right skill and tool, with precedence rules and durability notes. Consult FIRST on any media-creation request.
---

# Smart Router — intent → skill → tool

Read this before starting any creation, editing, motion-graphics, or design task. It picks the right skill, the right tool chain, and the fallback when a tool is unavailable (missing API key, blocked host, wiped sandbox).

## Routing table

| If the user wants… | Route to skill | Tool chain | When it fails |
|---|---|---|---|
| Recreate the editing style of a reference video ("make it in this style", "watch their editing") | `video-style-recreation` | ffmpeg filtergraph + PIL plates after atomic teardown | Teardown missing → do teardown first; no exceptions |
| Short premium motion graphic (kinetic type, count-up stat, logo sting, lower-third, chart hit, animated card/map) | `motion-graphix` | hyperframes CLI if Node present, else GSAP/HTML + ffmpeg capture, else pure ffmpeg filtergraph | No Node → GSAP lane; no browser → ffmpeg lane |
| Programmatic/composed video in React, premium animation, data-driven video | `remotion-studio` | Remotion CLI render (Chrome headless) | Chrome deps missing → fall back to `motion-graphix` GSAP/record or ffmpeg lane |
| True 3D camera work, WebGL worlds, product-in-3D | `motion-graphix` → three.js lane | three.js + headless capture → ffmpeg | No browser GPU → fake-3D lane (ffmpeg perspective/rotate/zoompan) |
| Explainer deck, carousel, presentation video | `motion-graphix` → slides lane (frontend-slides references) | HTML deck → per-slide capture → ffmpeg assembly | — |
| Bulk AI short videos (script→voice→footage→captions) | `ai-video-factory` | MoneyPrinterTurbo (`outputs/tools/MoneyPrinterTurbo/`) | No LLM/TTS/Pexels keys → generate locally: our VO + plates + ffmpeg (style-recreation route) |
| Cut a person/subject out of video (no green screen), recolor/replace background | `video-matting` | RobustVideoMatting (`outputs/tools/RVM/`) → alpha plates → filtergraph overlay | Weights/torch missing → classic chroma-key path (style-recreation skill) |
| Design audit ("does this look premium?", Apple-grade polish review) | `motion-graphix` → design-review lane | apple-design checklist inside motion-graphix | — |
| Sound design, VO duck, loudness delivery | `video-style-recreation` (audio recipe) | ffmpeg audio graph | — |

## Precedence rules

1. **Reference video present?** Teardown always wins (video-style-recreation). Premium techniques from `motion-graphix` are *added on* only after the measured grammar is satisfied.
2. **Short design-led piece (<30s, no VO)** → `motion-graphix` categories beat everything else.
3. **True 3D vs fake 3D**: pick true 3D only when user explicitly wants depth/parallax worlds AND a browser is available; otherwise eased perspective/zoompan ladders (verified approach in this repo).
4. **Tool that needs keys** (MoneyPrinterTurbo, cloud video-gen) is a *bonus lane*, never the blocking path. Local VO+plates+ffmpeg always ships.
5. **Durability**: after any work worth keeping → commit to this branch. Sandbox wipes are expected; `outputs/` is disposable, `skills/` is forever.

## Durability & provenance

- Vendored references live next to their skills with upstream LICENSE + NOTIFICATION files. Licenses: hyperframes Apache-2.0, frontend-slides MIT (vendored OK). OpenMontage is AGPL-3.0 and apple-design-skill has no license — those are **indexed, not copied**; clone paths are in `motion-graphix/library/INDEX-upstream.md`.
- Tools (pip/npm weights >1MB) live in `outputs/tools/` (gitignored). Rebuild commands are in each skill's SKILL.md. After a wipe: `git reset --hard <tip>` + rerun install commands from the skill docs.
- Current tool installs (working): Pillow + static **ffmpeg 7.0.2** via `pip --target outputs/pylibs imageio-ffmpeg` (symlink `outputs/demo/ffmpeg`); gallery server `skills/video-style-recreation/server/`.

## Never do

- Never route style-recreate work anywhere but through a measured teardown.
- Never let an un-keyed external service (no API key configured) be on the critical path.
- Never vendor AGPL/unlicensed upstream content into this repo.
- Never ship a render without viewing QA frames (every skill inherits this guardrail).
