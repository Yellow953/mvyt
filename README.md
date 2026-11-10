# mvyt

Agentic YouTube pipeline for the ModelVault channel. It researches ideas, writes scripts, sources footage, generates the voiceover with local TTS (Kokoro), and edits Shorts and long-form videos with Remotion.

- `CLAUDE.md`: pipeline overview and conventions
- `channel/profile.md`: channel positioning, pillars, voice, red lines
- `.claude/skills/`: `mv-research`, `mv-social`, `mv-produce` (plus the official Remotion skills)
- `tools/`: `fetch.py` (footage + posters), `tts.py` (Kokoro), `focus.py` (auto-framing), `music.py`, `render.sh`
- `remotion/`: data-driven `Short` / `Long` compositions
- `videos/<slug>/`: per-video `scenes.json`, `script.md`, `sources.md`, `upload.md` (media files are git-ignored)
