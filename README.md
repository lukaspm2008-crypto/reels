# reels

Automated animated psychology Shorts (English) for YouTube Shorts + TikTok.

- `RUNBOOK.md` – what every daily run does (analytics → 2 videos → upload → log)
- `engine/` – renderer (skia), voice (Kokoro TTS), sound effects + music, export
- `episodes/<id>/episode.py` – one folder per video (script, captions, scenes, sound cues)
- `state/` – channel memory (Keep/Kill/Test) and video log with metrics
