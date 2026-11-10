# Music library

Drop tracks into the mood folders as `Artist - Title.mp3`, then run `python3 tools/music.py index`.

| Folder | Use for | Audio Library filters |
|---|---|---|
| `sensual/` | default bed for creator/model profiles, rise stories | Genre: R&B & Soul, Mood: Romantic or Calm |
| `calm/` | AI-influencer explainers, money breakdowns | Genre: Ambient or Hip Hop & Rap, Mood: Calm |
| `tension/` | drama, downfall, exposed | Mood: Dark or Dramatic |
| `upbeat/` | countdowns, hype Shorts | Mood: Bright or Funky |

Allowed sources (no credit needed, safe for monetization): YouTube Audio Library tracks marked "Attribution not required", and Mixkit (mixkit.co free license; name files `Mixkit - Title.mp3`). Uppbeat free tracks need a credit link in the description. Candidates waiting for review are in `_candidates/`.
`python3 tools/music.py pick videos/<slug>/scenes.json --mood sensual` assigns the least-used track, so videos don't all sound the same.
