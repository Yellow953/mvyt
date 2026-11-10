#!/usr/bin/env python3
"""Background-music library for ModelVault.

Drop tracks into videos/_lib/music/<mood>/ (mp3/wav/m4a). Moods: sensual, calm, tension, upbeat.
Name files "Artist - Title.mp3" so credits are easy.

Commands:
  index                         scan folders -> videos/_lib/music/index.json (duration, mood, use count)
  list                          show the library
  pick videos/<slug>/scenes.json [--mood sensual]
                                set scenes.json "music" to the least-used track of that mood (mood defaults
                                to scenes.json music.mood, then "sensual"), and record the use
"""
import argparse
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LIB = os.path.join(ROOT, "videos", "_lib", "music")
INDEX = os.path.join(LIB, "index.json")
MOODS = ("sensual", "calm", "tension", "upbeat")
EXT = (".mp3", ".wav", ".m4a", ".aac", ".ogg")
DEFAULT_VOL = {"sensual": 0.16, "calm": 0.16, "tension": 0.14, "upbeat": 0.12}


def duration(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path],
                         capture_output=True, text=True).stdout.strip()
    try:
        return round(float(out), 1)
    except ValueError:
        return None


def load():
    return json.load(open(INDEX)) if os.path.exists(INDEX) else {"tracks": []}


def index():
    old = {t["file"]: t for t in load()["tracks"]}
    tracks = []
    for mood in MOODS:
        d = os.path.join(LIB, mood)
        os.makedirs(d, exist_ok=True)
        for f in sorted(os.listdir(d)):
            if not f.lower().endswith(EXT):
                continue
            rel = "_lib/music/%s/%s" % (mood, f)
            prev = old.get(rel, {})
            name = os.path.splitext(f)[0]
            artist, _, title = name.partition(" - ")
            tracks.append({"file": rel, "mood": mood, "title": title or artist, "artist": artist if title else "",
                           "duration": duration(os.path.join(d, f)), "uses": prev.get("uses", []),
                           "source": prev.get("source", "Mixkit free license (no attribution)" if artist.lower() == "mixkit" else "YouTube Audio Library"),
                           "attribution": prev.get("attribution", "")})
    json.dump({"tracks": tracks}, open(INDEX, "w"), indent=1)
    return tracks


def show():
    for t in index():
        print("%-8s %6ss  used %d×  %s" % (t["mood"], t["duration"], len(t["uses"]), t["file"]))


def pick(scenes, mood=None):
    spec = json.load(open(scenes))
    music = spec.get("music") or {}
    mood = mood or music.get("mood") or "sensual"
    tracks = [t for t in index() if t["mood"] == mood]
    if not tracks:
        sys.exit("no tracks in videos/_lib/music/%s/ (add some, then re-run)" % mood)
    t = sorted(tracks, key=lambda x: len(x["uses"]))[0]
    spec["music"] = {"file": t["file"], "mood": mood, "volume": music.get("volume", DEFAULT_VOL[mood]),
                     "title": t["title"], "artist": t["artist"]}
    json.dump(spec, open(scenes, "w"), indent=2, ensure_ascii=False)
    lib = load()
    for x in lib["tracks"]:
        if x["file"] == t["file"] and spec["slug"] not in x["uses"]:
            x["uses"].append(spec["slug"])
    json.dump(lib, open(INDEX, "w"), indent=1)
    print("%s -> %s (%s)" % (spec["slug"], t["file"], mood))


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("index"); sub.add_parser("list")
    p = sub.add_parser("pick"); p.add_argument("scenes"); p.add_argument("--mood", choices=MOODS)
    a = ap.parse_args()
    if a.cmd == "index":
        print("%d tracks indexed" % len(index()))
    elif a.cmd == "list":
        show()
    else:
        pick(a.scenes, a.mood)


if __name__ == "__main__":
    main()
