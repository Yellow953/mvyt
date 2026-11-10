#!/usr/bin/env python3
"""Footage downloader for ModelVault videos. Uses yt-dlp (YouTube, TikTok, Instagram, X, Reddit...) + direct image URLs.

Every download is logged to videos/<slug>/sources.md and videos/<slug>/assets/assets.json.
Videos are normalised to H.264/AAC MP4 (Remotion-safe).

Commands:
  search  "<query>" [-n 10]                               YouTube search with durations/views (TikTok/IG: find in Chrome)
  get     <slug> <url> [--from 12 --to 20] [--name x] [--scene s03] [--note "..."] [--cookies-from-browser chrome]
  fill    videos/<slug>/scenes.json [--cookies-from-browser chrome]
          downloads every scene whose visual.source is set and visual.file is empty, honouring visual.in/out,
          then writes visual.file back into scenes.json.

Instagram/TikTok sometimes require a logged-in session; --cookies-from-browser is opt-in only.
"""
import argparse
import datetime
import json
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG_EXT = (".jpg", ".jpeg", ".png", ".webp", ".gif", ".avif")
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130 Safari/537.36"


def vdir(slug):
    d = os.path.join(ROOT, "videos", slug)
    os.makedirs(os.path.join(d, "assets"), exist_ok=True)
    return d


def platform_of(url):
    for k in ("tiktok", "instagram", "youtube", "youtu.be", "twitter", "x.com", "reddit", "twitch", "kick"):
        if k in url:
            return {"youtu.be": "youtube", "x.com": "twitter"}.get(k, k)
    return "web"


def ffprobe(path):
    try:
        out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "stream=codec_type,codec_name,width,height:format=duration",
                              "-of", "json", path], capture_output=True, text=True).stdout
        d = json.loads(out)
        v = next((s for s in d.get("streams", []) if s.get("codec_type") == "video"), {})
        a = next((s for s in d.get("streams", []) if s.get("codec_type") == "audio"), None)
        return {"duration": round(float(d.get("format", {}).get("duration") or 0), 2), "width": v.get("width"),
                "height": v.get("height"), "vcodec": v.get("codec_name"), "has_audio": a is not None}
    except Exception:
        return {}


def detect_bars(path, info):
    """Return an ffmpeg crop filter if the clip has baked-in black bars (letterbox/pillarbox), else None."""
    dur = info.get("duration") or 0
    r = subprocess.run(["ffmpeg", "-hide_banner", "-ss", str(max(0, dur / 2 - 1)), "-t", "2", "-i", path,
                        "-vf", "cropdetect=limit=24:round=2:reset=0", "-f", "null", "-"], capture_output=True, text=True)
    found = re.findall(r"crop=(\d+):(\d+):(\d+):(\d+)", r.stderr)
    if not found or not info.get("width"):
        return None
    w, h, x, y = map(int, found[-1])
    W, H = info["width"], info["height"]
    if (H - h) < H * 0.04 and (W - w) < W * 0.04:  # under 4% → no real bars
        return None
    return "crop=%d:%d:%d:%d" % (w, h, x, y)


def normalise(path):
    """Re-encode to H.264/AAC if needed (Remotion/Chrome-safe) and strip baked-in black bars."""
    info = ffprobe(path)
    crop = detect_bars(path, info)
    if not crop and info.get("vcodec") in ("h264",) and path.endswith(".mp4"):
        return path, info
    out = os.path.splitext(path)[0] + ".h264.mp4"
    vf = ["-vf", crop] if crop else []
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", path] + vf + ["-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
                    "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", out], check=True)
    if crop:
        print("  removed black bars: %s" % crop)
    os.remove(path)
    final = os.path.splitext(path)[0] + ".mp4"
    os.replace(out, final)
    return final, ffprobe(final)


def download_image(url, dest_noext):
    # Wikimedia asks for a descriptive UA (browser-spoofing UAs get 429s); retry politely on rate limits.
    ua = "mvyt-video-pipeline/1.0" if "wikimedia.org" in url or "wikipedia.org" in url else UA
    for attempt in range(4):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": ua})
            with urllib.request.urlopen(req, timeout=60) as r:
                ctype = r.headers.get("Content-Type", "")
                data = r.read()
            break
        except urllib.error.HTTPError as e:
            if e.code != 429 or attempt == 3:
                raise
            time.sleep(3 * (attempt + 1))
    if not ctype.startswith("image/"):
        raise RuntimeError("not an image (%s)" % ctype)
    ext = "." + ctype.split("/")[1].split(";")[0].replace("jpeg", "jpg")
    path = dest_noext + ext
    open(path, "wb").write(data)
    return path


def download_video(url, dest_noext, t_from=None, t_to=None, cookies=None):
    cmd = ["yt-dlp", "--no-warnings", "--no-playlist", "--force-overwrites", "-f",
           "bv*[height<=2160]+ba/b[height<=2160]/b",  # up to 4K so 9:16 crops of 16:9 stay sharp
           "--merge-output-format", "mp4", "-o", dest_noext + ".%(ext)s", "--print", "after_move:filepath",
           "--print", "before_dl:%(uploader)s|||%(title)s"]
    if t_from is not None or t_to is not None:
        cmd += ["--download-sections", "*%s-%s" % (t_from or 0, t_to if t_to is not None else "inf"),
                "--force-keyframes-at-cuts"]
    if cookies:
        cmd += ["--cookies-from-browser", cookies]
    r = subprocess.run(cmd + [url], capture_output=True, text=True, timeout=600)
    lines = [l for l in r.stdout.strip().splitlines() if l.strip()]
    if r.returncode != 0 or not lines:
        raise RuntimeError((r.stderr or r.stdout).strip().splitlines()[-1] if (r.stderr or r.stdout).strip() else "yt-dlp failed")
    meta = next((l for l in lines if "|||" in l), "|||")
    creator, title = meta.split("|||", 1)
    return lines[-1], creator, title


def log(slug, entry):
    d = vdir(slug)
    man = os.path.join(d, "assets", "assets.json")
    items = json.load(open(man)) if os.path.exists(man) else []
    items = [i for i in items if i["file"] != entry["file"]] + [entry]
    json.dump(items, open(man, "w"), indent=1)
    src = os.path.join(d, "sources.md")
    if not os.path.exists(src):
        open(src, "w").write("# Sources\n\n| File | Platform | Creator | Segment | URL | Note | Fetched |\n|---|---|---|---|---|---|---|\n")
    seg = "%s–%s" % (entry.get("from", ""), entry.get("to", "")) if entry.get("from") is not None or entry.get("to") is not None else "full"
    with open(src, "a") as f:
        f.write("| %s | %s | %s | %s | %s | %s | %s |\n" % (entry["file"], entry["platform"], entry.get("creator", ""), seg,
                                                        entry["url"], entry.get("note", ""), entry["fetched"]))


def get(slug, url, t_from=None, t_to=None, name=None, scene=None, note="", cookies=None):
    d = vdir(slug)
    name = re.sub(r"[^a-z0-9_-]+", "-", (name or scene or "clip-%s" % datetime.datetime.now().strftime("%H%M%S")).lower())
    dest = os.path.join(d, "assets", name)
    creator, title = "", ""
    if url.lower().split("?")[0].endswith(IMG_EXT):
        path, kind = download_image(url, dest), "image"
        info = {k: v for k, v in ffprobe(path).items() if k in ("width", "height")}
    else:
        try:
            path, creator, title = download_video(url, dest, t_from, t_to, cookies)
            path, info = normalise(path)
            kind = "video"
        except RuntimeError as e:
            try:  # some "pages" are actually direct images
                path, kind = download_image(url, dest), "image"
                info = {k: v for k, v in ffprobe(path).items() if k in ("width", "height")}
            except Exception:
                raise e
    rel = os.path.relpath(path, d)
    entry = {"file": rel, "kind": kind, "url": url, "platform": platform_of(url), "creator": creator, "title": title,
             "from": t_from, "to": t_to, "scene": scene, "note": note,
             "fetched": datetime.date.today().isoformat()}
    entry.update(info)
    log(slug, entry)
    print("%s  %s  %s" % (rel, kind, json.dumps(info)))
    return rel


def fill(scenes_path, cookies=None):
    spec = json.load(open(scenes_path))
    slug = spec["slug"]
    ok = fail = 0
    for sc in spec["scenes"]:
        v = sc.get("visual") or {}
        if not v.get("source") or v.get("file"):
            continue
        try:
            v["file"] = get(slug, v["source"], v.get("in"), v.get("out"), scene=sc["id"], cookies=cookies,
                            note=v.get("query", ""))
            ok += 1
        except Exception as e:
            print("FAIL %s: %s" % (sc["id"], e), file=sys.stderr)
            fail += 1
        json.dump(spec, open(scenes_path, "w"), indent=2, ensure_ascii=False)
    # Posters: scene.poster = {"wiki": "Knives Out (film)"} → poster.file
    for sc in spec["scenes"]:
        p = sc.get("poster")
        if not p or not p.get("wiki") or p.get("file"):
            continue
        try:
            p["file"] = poster(slug, p["wiki"])
            ok += 1
        except Exception as e:
            print("FAIL poster %s (%s): %s" % (sc["id"], p["wiki"], e), file=sys.stderr)
            fail += 1
        json.dump(spec, open(scenes_path, "w"), indent=2, ensure_ascii=False)
    missing = [s["id"] for s in spec["scenes"] if (s.get("visual") or {}).get("type") in ("clip", "image")
               and not (s.get("visual") or {}).get("file")]
    print("fetched %d, failed %d, still missing footage: %s" % (ok, fail, ", ".join(missing) or "none"))


def _wiki(params):
    url = "https://en.wikipedia.org/w/api.php?" + urllib.parse.urlencode(dict(params, format="json", redirects=1))
    req = urllib.request.Request(url, headers={"User-Agent": "mvyt-video-pipeline/1.0"})
    return json.load(urllib.request.urlopen(req, timeout=30))


def poster(slug, wiki_title):
    """Download the poster / title card from a film or show's English Wikipedia infobox.
    Reads the article HTML (the API rate-limits anonymous clients hard); image comes from upload.wikimedia.org."""
    name = "poster-" + re.sub(r"[^a-z0-9]+", "-", wiki_title.lower()).strip("-")
    existing = [f for f in os.listdir(os.path.join(vdir(slug), "assets")) if f.startswith(name + ".")]
    if existing:  # same poster used in several scenes
        return "assets/" + existing[0]
    url = "https://en.wikipedia.org/wiki/" + urllib.parse.quote(wiki_title.replace(" ", "_"))
    req = urllib.request.Request(url, headers={"User-Agent": "mvyt-video-pipeline/1.0"})
    html = urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "ignore")
    i = html.find('class="infobox')
    m = re.search(r'//upload\.wikimedia\.org/[^"\s?]+\.(?:jpe?g|png|webp|gif)', html[i:i + 8000] if i >= 0 else "", re.I)
    if not m:
        m = re.search(r'//thumb\.wikimedia\.org/[^"\s?]+\.(?:jpe?g|png|webp|gif)', html[i:i + 8000] if i >= 0 else "", re.I)
    if not m:
        raise RuntimeError("no infobox image on Wikipedia page '%s'" % wiki_title)
    time.sleep(1)
    return get(slug, "https:" + m.group(0), name=name, note="poster: " + wiki_title)


def search(query, n):
    out = subprocess.run(["yt-dlp", "--flat-playlist", "-J", "--no-warnings", "ytsearch%d:%s" % (n, query)],
                         capture_output=True, text=True, timeout=120).stdout
    for e in (json.loads(out).get("entries") or []):
        dur = e.get("duration") or 0
        print("%6s  %10s views  %-60s  %s  (%s)" % ("%d:%02d" % (dur // 60, dur % 60), format(e.get("view_count") or 0, ","),
                                                   (e.get("title") or "")[:60], "https://youtu.be/" + e["id"], e.get("channel")))


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("search"); s.add_argument("query"); s.add_argument("-n", type=int, default=10)
    g = sub.add_parser("get"); g.add_argument("slug"); g.add_argument("url")
    g.add_argument("--from", dest="t_from", type=float); g.add_argument("--to", dest="t_to", type=float)
    g.add_argument("--name"); g.add_argument("--scene"); g.add_argument("--note", default="")
    g.add_argument("--cookies-from-browser")
    f = sub.add_parser("fill"); f.add_argument("scenes"); f.add_argument("--cookies-from-browser")
    a = ap.parse_args()
    if a.cmd == "search":
        search(a.query, a.n)
    elif a.cmd == "get":
        get(a.slug, a.url, a.t_from, a.t_to, a.name, a.scene, a.note, a.cookies_from_browser)
    else:
        fill(a.scenes, a.cookies_from_browser)


if __name__ == "__main__":
    main()
