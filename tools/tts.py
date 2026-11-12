#!/usr/bin/env python3
"""Render voiceover for a video from its scenes.json with Kokoro (local, free).

Outputs in videos/<slug>/audio/:
  sNN.wav          one file per scene
  voice.wav        all scenes concatenated (with --gap seconds between scenes)
  timings.json     per-scene start/duration + word-level timestamps (for captions in Remotion)

Usage:
  .venv/bin/python tools/tts.py videos/<slug>/scenes.json [--voice af_heart] [--speed 1.05] [--gap 0.08]
  .venv/bin/python tools/tts.py --say "test line" --voice af_heart --out /tmp/test.wav
"""
import argparse
import json
import os
import re
import warnings

warnings.filterwarnings("ignore")
import numpy as np  # noqa: E402
import soundfile as sf  # noqa: E402
from kokoro import KPipeline  # noqa: E402

SR = 24000
_pipes = {}


def pipe_for(voice):
    lang = voice[0]  # a = American, b = British
    if lang not in _pipes:
        _pipes[lang] = KPipeline(lang_code=lang, repo_id="hexgrad/Kokoro-82M")
    return _pipes[lang]


def apply_pron(text, pron):
    for k, v in (pron or {}).items():
        text = re.sub(re.escape(k), v, text, flags=re.IGNORECASE)
    return text


def synth(text, voice, speed):
    """Return (audio float32 array, [{'word','start','end'}])."""
    chunks, words, offset = [], [], 0.0
    for r in pipe_for(voice)(text, voice=voice, speed=speed):
        audio = r.audio.cpu().numpy() if hasattr(r.audio, "cpu") else np.asarray(r.audio)
        for t in (r.tokens or []):
            if not t.text.strip():
                continue
            if not re.search(r"\w", t.text):  # punctuation → glue onto previous word
                if words and t.text.strip() in ".,!?;:":
                    words[-1]["word"] += t.text.strip()
                continue
            if t.start_ts is None:
                continue
            words.append({"word": t.text, "start": round(offset + t.start_ts, 3),
                          "end": round(offset + (t.end_ts or t.start_ts), 3)})
        chunks.append(audio)
        offset += len(audio) / SR
    return (np.concatenate(chunks) if chunks else np.zeros(1, dtype=np.float32)), words


def unpron_words(words, pron):
    """Map respellings back to the original spelling for captions.
    Same word count: word-by-word ("Anna day Armas" -> "Ana de Armas").
    Different count: merge the spoken run into one caption word ("twelve point seven" -> "12.7")."""
    rev, multi = {}, []
    for orig, said in (pron or {}).items():
        o, s = orig.split(), said.split()
        if len(o) == len(s):
            for a, b in zip(o, s):
                rev[b.lower()] = a
        else:
            multi.append(([x.lower() for x in s], orig))
    strip = lambda x: re.sub(r"[^\w']+$", "", x.lower())
    out, i = [], 0
    while i < len(words):
        for said, orig in multi:
            run = words[i:i + len(said)]
            if len(run) == len(said) and [strip(w["word"]) for w in run] == said:
                tail = re.search(r"[^\w']+$", run[-1]["word"])
                out.append(dict(run[0], word=orig + (tail.group(0) if tail else ""), end=run[-1]["end"]))
                i += len(said)
                break
        else:
            w = words[i]
            tail = re.search(r"[^\w']+$", w["word"])
            base = strip(w["word"])
            if base in rev:
                w["word"] = rev[base] + (tail.group(0) if tail else "")
            out.append(w)
            i += 1
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("scenes", nargs="?")
    ap.add_argument("--voice")
    ap.add_argument("--speed", type=float)
    ap.add_argument("--gap", type=float, default=0.08)
    ap.add_argument("--say")
    ap.add_argument("--out")
    a = ap.parse_args()

    if a.say:
        audio, _ = synth(a.say, a.voice or "af_heart", a.speed or 1.0)
        sf.write(a.out or "say.wav", audio, SR)
        print("wrote", a.out or "say.wav", "%.2fs" % (len(audio) / SR))
        return

    spec = json.load(open(a.scenes))
    vcfg = spec.get("voice") or {}
    voice = a.voice or vcfg.get("voice", "af_heart")
    speed = a.speed or vcfg.get("speed", 1.0)
    pron = spec.get("pron") or {}
    outdir = os.path.join(os.path.dirname(os.path.abspath(a.scenes)), "audio")
    os.makedirs(outdir, exist_ok=True)

    gap = np.zeros(int(a.gap * SR), dtype=np.float32)
    full, timings, t = [], [], 0.0
    for sc in spec["scenes"]:
        vo = (sc.get("vo") or "").strip()
        if not vo:
            dur = float(sc.get("est_sec") or 1.0)
            audio, words = np.zeros(int(dur * SR), dtype=np.float32), []
        else:
            audio, words = synth(apply_pron(vo, pron), voice, speed)
            words = unpron_words(words, pron)
        sf.write(os.path.join(outdir, sc["id"] + ".wav"), audio, SR)
        dur = len(audio) / SR
        timings.append({"id": sc["id"], "start": round(t, 3), "duration": round(dur, 3),
                        "words": [dict(w, start=round(w["start"] + t, 3), end=round(w["end"] + t, 3)) for w in words]})
        full += [audio, gap]
        t += dur + a.gap
        print("%-5s %5.2fs  %s" % (sc["id"], dur, vo[:70]))

    sf.write(os.path.join(outdir, "voice.wav"), np.concatenate(full), SR)
    json.dump({"voice": voice, "speed": speed, "sample_rate": SR, "total": round(t, 3), "scenes": timings},
              open(os.path.join(outdir, "timings.json"), "w"), indent=1)
    print("TOTAL %.2fs -> %s" % (t, outdir))


if __name__ == "__main__":
    main()
