# mvyt: ModelVault video pipeline

An agentic pipeline that researches, scripts, sources footage and edits (Remotion) YouTube Shorts and long-form videos for https://www.youtube.com/@ModelVault.
**YouTube is the only publishing platform.** TikTok, Instagram and Reddit are used only for trend signals and footage.

**Read `channel/profile.md` before any creative work.** It holds the positioning, pillars, voice and red lines.

## Pipeline
| Stage | Skill / tool | Output |
|---|---|---|
| 1. Research | `/mv-research` (yt-dlp outliers + transcripts, WebSearch, Claude in Chrome for TikTok/IG/Trends) | `research/<date>_<slug>/` |
| 2. Ideas | `/mv-social ideas` | `ideas/backlog.md` |
| 3. Script | `/mv-social script` | `videos/<slug>/script.md` + `scenes.json` |
| 4. Footage | `/mv-produce` → `python3 tools/fetch.py fill videos/<slug>/scenes.json` (yt-dlp: YouTube/TikTok/IG/X + direct images) | `videos/<slug>/assets/` + `sources.md` |
| 5. Voice | `.venv/bin/python tools/tts.py videos/<slug>/scenes.json` (Kokoro, local) | `videos/<slug>/audio/` voice.wav + timings.json (word timestamps) |
| 6. Edit | Remotion project in `remotion/` (compositions `Short` / `Long`, data-driven from scenes.json). Preview: `cd remotion && npx remotion studio`. Render: `tools/render.sh <slug>` | `videos/<slug>/out/<slug>.mp4` |
| 7. Upload pack | `/mv-produce` step 5 | `videos/<slug>/upload.md` |

Working examples: `videos/_demo` (Short) and `videos/_demo-long`. Shared SFX are in `videos/_lib/sfx`. Put music in `videos/_lib/music`. Remotion's public dir is `videos/`.

## Folder conventions
- `research/YYYY-MM-DD_<slug>/`: outliers.md/json, transcripts/, dossier.md, report.md
- `ideas/backlog.md`: scored idea cards, newest on top
- `videos/<slug>/`: everything for one video. Slugs are kebab-case.
- Every downloaded clip gets logged in `videos/<slug>/sources.md` (URL, creator, timestamp used). We need this for copyright disputes.

## Footage rules (keeps the channel monetizable)
- Clips are evidence for our commentary, not the content itself. Keep them short (≤5–8s each in long-form, ≤3s in Shorts), always under our VO or captions, cropped, reframed or zoomed.
- Strip TikTok watermarks (crop) before using clips in Shorts. Watermarks get demoted.
- No full reuploads. No clips with music we don't own as the main audio.

## Tools
- Python 3.9 (system) for stdlib-only scripts. Kokoro/ML scripts use `.venv/` (Python 3.12, created with uv). Run them with `.venv/bin/python`.
- Kokoro voice: **af_heart is the channel narrator (chosen 2026-11-10)**; always use it unless the user says otherwise. Set per video in `scenes.json` → `voice`. Mispronounced names go in `pron`.
- yt-dlp, uv, espeak-ng (brew), ffmpeg 9, node 26, Remotion 4.0.542.
- Official Remotion skills are in `.claude/skills/remotion-*`. Follow them when editing `remotion/src`.
