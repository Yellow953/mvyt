#!/usr/bin/env python3
"""Pull the auto/manual English transcript of a YouTube video (or Short) as plain text via yt-dlp.

Usage: python3 yt_transcript.py URL [--out file.txt] [--timestamps]
"""
import argparse
import glob
import os
import re
import subprocess
import sys
import tempfile


def vtt_to_lines(path, stamps):
    out, last = [], None
    ts = None
    for line in open(path, encoding="utf-8", errors="ignore"):
        line = line.strip()
        m = re.match(r"(\d+):(\d+):(\d+)\.\d+ -->", line)
        if m:
            h, mi, s = map(int, m.groups())
            ts = "%d:%02d" % (h * 60 + mi, s)
            continue
        if not line or line.startswith(("WEBVTT", "Kind:", "Language:", "NOTE")) or line.isdigit():
            continue
        text = re.sub(r"<[^>]+>", "", line).strip()
        if text and text != last:
            out.append(("[%s] " % ts if stamps and ts else "") + text)
            last = text
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("url")
    ap.add_argument("--out")
    ap.add_argument("--timestamps", action="store_true")
    a = ap.parse_args()
    tmp = tempfile.mkdtemp()
    subprocess.run(["yt-dlp", "--skip-download", "--write-auto-subs", "--write-subs", "--sub-langs", "en.*,en",
                    "--sub-format", "vtt", "--no-warnings", "-o", os.path.join(tmp, "t.%(ext)s"), a.url],
                   capture_output=True, text=True, timeout=120)
    files = sorted(glob.glob(os.path.join(tmp, "*.vtt")))
    if not files:
        sys.exit("no transcript available")
    text = "\n".join(vtt_to_lines(files[0], a.timestamps))
    if a.out:
        os.makedirs(os.path.dirname(a.out) or ".", exist_ok=True)
        open(a.out, "w").write(text)
    print(text)


if __name__ == "__main__":
    main()
