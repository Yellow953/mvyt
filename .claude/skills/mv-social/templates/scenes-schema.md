# scenes.json schema

This is the contract between scripting and editing. Remotion compositions will read it directly, so keep it valid JSON with no comments in the real file.

```json
{
  "slug": "sky-bri-streamers",
  "format": "short",                // "short" (1080x1920) | "long" (1920x1080)
  "title": "Why Every Streamer Invites Sky Bri",
  "voice": { "engine": "kokoro", "voice": "af_heart", "speed": 1.05 },
  "framing": "4:5",                     // Shorts default: landscape footage in a 4:5 window on black (alt: "fill" | "1:1")
  "music": { "mood": "sensual" },        // sensual | calm | tension | upbeat → file picked by tools/music.py
  "pron": { "Sky Bri": "Sky Bree" },   // phonetic hints for TTS
  "scenes": [
    {
      "id": "s01",
      "section": "hook",               // hook | context | block-N | mid-cta | rehook | climax | outro | cta | loop
      "vo": "Every big streamer has had Sky Bri on. That's not an accident.",
      "text": "NOT an accident.",        // on-screen text (null if none); captions are auto from vo
      "visual": {
        "type": "clip",                // clip | image | graphic | stat | split | text-card
        "query": "Sky Bri Adin Ross stream clip",   // what to find
        "source": null,                // URL once found (filled in by footage stage)
        "in": null, "out": null,       // trim points in seconds
        "treatment": "zoom-punch",     // ken-burns | zoom-punch | blur-bg-fill | split | shake | none
        "zoom": 1.3, "anchor": "top"   // optional (vertical clips): push burned-in source text/subs out of the caption zone (~y 1300–1440). top → text moves down into the Shorts UI zone; bottom → moves up (e.g. keep a comment card visible above captions)
      },
      "sfx": "bass-hit",               // optional: whoosh | bass-hit | riser | record-scratch | ding | silence
      "poster": { "wiki": "Knives Out" },   // optional: only in a quick filmography run, poster slides in top-right.
                                       // Use the exact English Wikipedia page title (e.g. "Yesterday (2019 film)").
      "est_sec": 3.2
    }
  ]
}
```

Rules:
- **Posters only during a filmography run**: the quick-fire stretch where the VO lists a person's films ("Then came Blade Runner. Knives Out. A Bond movie."). Not on every film mention, not on the hook, and not on story scenes. This is the user's rule.
- A **Short has 10–18 scenes, 1.5–3.5s each.** A **long-form has 60–150 scenes, 3–8s each.** One scene equals one visual.
- `vo` across all scenes, concatenated, is the full script. Don't put VO anywhere else.
- `est_sec` ≈ words ÷ 2.5. Duration after TTS is the source of truth.
- `visual.query` must be specific enough to search (a person + an event + the platform), not "b-roll".
- `graphic` and `stat` scenes put their content in `text`. For example a stat card: `"text": "$2.3M | 11 months"`.
