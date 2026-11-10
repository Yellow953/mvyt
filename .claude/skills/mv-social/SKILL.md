---
name: mv-social
description: ModelVault's YouTube-only creative engine (Shorts + long-form). Use it to generate and score video ideas, write viral YouTube Shorts scripts (30–45s), write retention-engineered long-form scripts (6–12 min), write titles, thumbnail concepts and hooks, turn one long-form into several Shorts, or critique and rewrite a script. Triggers include "video ideas", "write a short", "write a script", "long video about X", "hooks for X", "titles", "thumbnail", "repurpose into shorts", "critique this script".
---

# mv-social

Turns research into ideas and ideas into scripts that the edit stage (Remotion) can build directly.

**Always read first:** `channel/profile.md` (pillars, voice, red lines) and the latest `research/*/report.md` that's relevant. If a script is about a real person or event and there's no `dossier.md`, run `/mv-research` dossier mode first. No dossier means no script.

## Core principles
0. **YouTube only.** We publish nowhere else. Optimize every choice for YouTube's surfaces (Browse, Suggested, Search, Shorts Feed) and its rules (`references/youtube-upload.md`). Ignore TikTok and Reels conventions (trending sounds, TikTok-style captions, Reels "sends"), even when research comes from those platforms.
1. **The idea is the hook.** If you can't write 3 strong hooks for an idea, the idea isn't ready. Kill it or reframe it.
2. **Title, thumbnail, first frame and first line form one contract.** The first sentence pays off the title. The first shot pays off the thumbnail. Bait-and-switch gets punished.
3. **Specific beats vague.** "$2.3M in 11 months" beats "a lot of money". Name the category of the payoff even when you withhold the answer.
4. **Story = but/therefore, never "and then".** Every beat should turn or raise the stakes.
5. **Write for the ear and for mute viewers.** Our VO is local TTS, so short sentences and no tongue-twisters. Spell names phonetically in `pron` hints. On-screen text carries the hook for the roughly 70% who watch muted.
6. **Visual reset every 2–3s (Shorts) and every 5–8s (long-form)**: a new clip, zoom, text pop, graphic or SFX. AI narration over static visuals is how faceless channels die.
7. **Patterns, not promises.** Never claim a video will go viral.

## Modes

### `ideas`: generate and score a batch
1. Pull leads from the latest research report(s) and the pillars.
2. Produce **10 idea cards** spread across at least 3 pillars and at least 3 hook archetypes. Mix safe bets (Investigator, Countdown) with high-ceiling swings (Contrarian, Downfall).
3. Score each card with the rubric in `references/packaging.md`. Keep the top 5 and append them to `ideas/backlog.md` (newest on top) using `templates/idea-card.md`.
4. For each long-form idea, include 2–3 Shorts spin-offs. Every Short should point to a long-form.

### `script short`: 30–45s Short
Follow `references/shorts.md`. Output `videos/<slug>/script.md` (from `templates/short-script.md`) **plus** `videos/<slug>/scenes.json` (schema in `templates/scenes-schema.md`).
- Write 3 hook variants (different archetypes), pick one, and keep the others in the file for A/B testing.
- The VO is 75–110 words (about 2.5 words per second).
- Design the loop.
- Name the long-form for the Shorts **"Related video" link** (YouTube's official Shorts → long-form bridge).

### `script long`: 6–12 min long-form
Follow `references/longform.md` and pick the format skeleton from `references/formats.md`. Output `script.md` (from `templates/long-script.md`) plus `scenes.json`.
- Word count ≈ minutes × 150 (±10%).
- Include 3 title options, 3 thumbnail concepts (for Test & Compare), a description with chapters, tags, the end-screen target, a playlist and a pinned comment. Follow `references/youtube-upload.md`.
- Include a Shorts cut-list: 3–5 moments that stand alone, each with its own new hook.

### `hooks` / `titles` / `thumbnail`
Produce 8–10 options across archetypes (`references/hooks.md`, `references/packaging.md`). Rank them and give a one-line reason for each.

### `repurpose`: long-form to Shorts
For each Short, write a **new** 0–3s hook. Never open a Short on the long-form's mid-sentence VO. Each Short gets its own `scenes.json`, ends with "full story on the channel", and loops.

### `critique`: review a script
Run it through the checklist in `references/shorts.md` or `references/longform.md`. Name each anti-pattern (`references/hooks.md`) and **rewrite** the weak beats rather than just flagging them.

## Final self-check (every script)
- [ ] Every factual claim about a real person is in the dossier as *confirmed*. Allegations are attributed.
- [ ] Nothing sexualizes a real person, and every person featured is verified 18+.
- [ ] The first line pays off the title, and the first frame pays off the thumbnail.
- [ ] No "hey guys", no logo intro, no "subscribe" in the first 30s or anywhere in a Short.
- [ ] A visual reset at least every 3s (Short) or 8s (long).
- [ ] Every scene in `scenes.json` has a footage plan (a specific clip or search), not "b-roll of her".
- [ ] The word count matches the target length.
