#!/usr/bin/env python3
"""Find outlier YouTube videos for a set of keywords using yt-dlp (free, no API key).

Outlier score = video views / median views of that channel's recent uploads.
A score of 5 means the video did 5x the channel's normal. That's the signal that the
TOPIC/PACKAGING worked, not just that the channel is big.

Usage:
  python3 yt_outliers.py --keywords "sky bri" "ai influencer" --out research/run1 [--per-query 25] [--top 15] [--shorts]
"""
import argparse
import json
import os
import statistics
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor


def ytdlp_json(args, timeout=120):
    cmd = ["yt-dlp", "--flat-playlist", "-J", "--no-warnings", "--ignore-errors"] + args
    try:
        out = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout).stdout
        d = json.loads(out) if out.strip() else {}
        return d if isinstance(d, dict) else {}
    except (subprocess.TimeoutExpired, json.JSONDecodeError):
        return {}


def search(query, n, shorts):
    q = query + (" #shorts" if shorts else "")
    data = ytdlp_json(["ytsearch%d:%s" % (n, q)])
    rows = []
    for e in data.get("entries") or []:
        if not e or not e.get("id"):
            continue
        rows.append({
            "id": e["id"],
            "title": e.get("title"),
            "url": "https://www.youtube.com/watch?v=" + e["id"],
            "views": e.get("view_count") or 0,
            "duration": e.get("duration"),
            "channel": e.get("channel") or e.get("uploader"),
            "channel_id": e.get("channel_id"),
            "channel_url": e.get("channel_url"),
            "query": query,
        })
    return rows


def channel_baseline(channel_url, shorts):
    if not channel_url:
        return None
    tab = "/shorts" if shorts else "/videos"
    data = ytdlp_json(["--playlist-end", "30", channel_url.rstrip("/") + tab], timeout=90)
    views = [e.get("view_count") for e in (data.get("entries") or []) if e and e.get("view_count")]
    if len(views) < 3:
        return None
    return {"median": statistics.median(views), "n": len(views)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--keywords", nargs="+", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--per-query", type=int, default=25)
    ap.add_argument("--top", type=int, default=15)
    ap.add_argument("--min-views", type=int, default=10000)
    ap.add_argument("--shorts", action="store_true", help="search Shorts and baseline against channel Shorts tab")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)

    with ThreadPoolExecutor(6) as ex:
        results = list(ex.map(lambda k: search(k, a.per_query, a.shorts), a.keywords))
    seen, vids = set(), []
    for rows in results:
        for r in rows:
            if r["id"] not in seen and r["views"] >= a.min_views:
                seen.add(r["id"])
                vids.append(r)
    print("candidates: %d" % len(vids), file=sys.stderr)

    chans = {v["channel_url"] for v in vids if v["channel_url"]}
    with ThreadPoolExecutor(8) as ex:
        base = dict(zip(chans, ex.map(lambda c: channel_baseline(c, a.shorts), chans)))

    for v in vids:
        b = base.get(v["channel_url"])
        v["channel_median"] = b["median"] if b else None
        v["outlier_score"] = round(v["views"] / b["median"], 2) if b and b["median"] else None

    scored = sorted([v for v in vids if v["outlier_score"]], key=lambda v: v["outlier_score"], reverse=True)
    top = scored[: a.top]
    with open(os.path.join(a.out, "outliers.json"), "w") as f:
        json.dump({"keywords": a.keywords, "shorts": a.shorts, "outliers": top, "all": scored}, f, indent=2)

    lines = ["| # | Score | Views | Chan median | Title | Channel |", "|---|---|---|---|---|---|"]
    for i, v in enumerate(top, 1):
        lines.append("| %d | %.1fx | %s | %s | [%s](%s) | %s |" % (
            i, v["outlier_score"], format(v["views"], ","), format(int(v["channel_median"]), ","),
            (v["title"] or "").replace("|", "/"), v["url"], v["channel"]))
    table = "\n".join(lines)
    with open(os.path.join(a.out, "outliers.md"), "w") as f:
        f.write(table + "\n")
    print(table)


if __name__ == "__main__":
    main()
