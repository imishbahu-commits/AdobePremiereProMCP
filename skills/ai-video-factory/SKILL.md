---
name: ai-video-factory
description: Bulk AI short-video generation (script → voice → stock footage → captions → edit) via MoneyPrinterTurbo, plus the agentic production-stage map distilled from OpenMontage. Use for faceless/shorts pipelines, batch video generation, or when the user asks for MoneyPrinterTurbo-style automation. Bonus lane — never blocks local VO+plates+ffmpeg builds.
---

# AI Video Factory (MoneyPrinterTurbo + agentic stages)

## What MoneyPrinterTurbo is

One-stop AI short-video generator (MIT, github.com/harry0703/MoneyPrinterTurbo): you give a topic, an LLM writes the script, TTS voices it, stock-footage APIs (Pexels/Pixabay) supply visuals, then moviepy assembles subtitles + music + vertical/horizontal cuts. WebUI (Streamlit) + HTTP API (FastAPI).

## Production-stage map (agentic pipeline discipline, my distillation)

Every factory build decomposes into stages — keep them separable so any single stage can be swapped (e.g. our local VO instead of cloud TTS):

1. **Script** — LLM or hand-written; lock word count to target duration (~2.3 words/sec).
2. **Voice** — TTS (azure/elevenlabs/edge) or local VO like our voice-id pipeline; keep 0.6–0.8s gaps cadence.
3. **Visuals** — stock search (needs Pexels/Pixabay key) OR generated art plates OR matted subjects (video-matting skill).
4. **Edit/assembly** — moviepy (factory) or ffmpeg filtergraph (precise); subtitles styled per style grammar.
5. **Audio polish** — music bed + duck + loudnorm (style-recreation audio recipe).
6. **QC + delivery** — probe + QA frames + faststart; batch report (never claim without verify).

## Install (sandbox; `outputs/` is gitignored — rerun after a wipe)

```bash
cd outputs/tools 2>/dev/null || mkdir -p outputs/tools && cd outputs/tools
git clone --depth 1 https://github.com/harry0703/MoneyPrinterTurbo.git MPT || true
cd MPT && python3 -m venv .venv && ./.venv/bin/pip install -q -r requirements.txt
cp config.example.toml config.toml   # then edit keys
```

Run: `./.venv/bin/python webui.py` (Streamlit, port 8501 — bind 0.0.0.0 for Arena preview) or `./.venv/bin/python main.py` (API :8080 conflicts with our gallery — export a different port).

## Required keys & fallbacks (per smart-router rule 4)

| Needs | Purpose | If absent |
|---|---|---|
| LLM key (OpenAI/Gemini/DeepSeek/Qwen/Moonshot…) | script writing | hand-write scripts |
| Pexels/Pixabay | stock footage | generated plates / local assets |
| TTS (azure speech key helps; edge-tts is keyless) | voiceover | our local VO recipe (voice-00 .mp3 drops) |
| Subtitle: faster-whisper optional (local, heavy) | auto captions | skip or hand-time |

## Guardrails

- Keyless fallbacks are first-class: a factory build with zero keys still ships via local assets.
- Vertical (9:16) vs horizontal must match the brief; factory defaults drift to 9:16.
- Generated scripts: fact-check before voicing any claims.
- Never commit `config.toml` (secrets) — it's gitignored by convention; keep keys in env, not files, where possible.
- Upstream ideas worth mirroring locally: OpenAI-style task queue states (pending ≠ done — echo of our delivery guardrail), per-stage artifacts on disk for resumability.
