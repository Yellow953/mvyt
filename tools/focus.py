#!/usr/bin/env python3
"""Auto-reframe helper: find where the subject (faces) sits horizontally in each clip/image so the
9:16 crop of a 16:9 source keeps them in frame. Writes visual.focus (0 = left edge, 0.5 = centre, 1 = right).

Usage: .venv/bin/python tools/focus.py videos/<slug>/scenes.json [--force]
Scenes with a manually set visual.focus are left alone unless --force.
"""
import argparse
import json
import os
import statistics

import cv2

CASCADE = cv2.CascadeClassifier(os.path.join(cv2.data.haarcascades, "haarcascade_frontalface_default.xml"))
PROFILE = cv2.CascadeClassifier(os.path.join(cv2.data.haarcascades, "haarcascade_profileface.xml"))


def faces_in(img):
    g = cv2.equalizeHist(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY))
    h, w = g.shape
    min_side = max(24, int(h * 0.08))
    found = list(CASCADE.detectMultiScale(g, 1.1, 6, minSize=(min_side, min_side)))
    if not found:
        found = list(PROFILE.detectMultiScale(g, 1.1, 6, minSize=(min_side, min_side)))
    return [(x + fw / 2) / w for (x, y, fw, fh) in found], [fw * fh for (x, y, fw, fh) in found]


def focus_for(path, samples=8):
    xs = []
    if path.lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
        img = cv2.imread(path)
        frames = [img] if img is not None else []
    else:
        cap = cv2.VideoCapture(path)
        n = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) or 1
        frames = []
        for i in range(samples):
            cap.set(cv2.CAP_PROP_POS_FRAMES, int((i + 0.5) * n / samples))
            ok, f = cap.read()
            if ok:
                frames.append(f)
        cap.release()
    for f in frames:
        if f.shape[1] > 1280:  # speed: detect on a downscaled copy
            f = cv2.resize(f, (1280, int(f.shape[0] * 1280 / f.shape[1])))
        cx, areas = faces_in(f)
        if cx:
            xs.append(cx[areas.index(max(areas))])  # biggest face = subject
    return round(statistics.median(xs), 3) if xs else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("scenes")
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args()
    base = os.path.dirname(os.path.abspath(a.scenes))
    spec = json.load(open(a.scenes))
    for sc in spec["scenes"]:
        v = sc.get("visual") or {}
        if not v.get("file") or ("focus" in v and not a.force):
            continue
        f = focus_for(os.path.join(base, v["file"]))
        v["focus"] = f if f is not None else 0.5
        print("%-5s focus=%s%s" % (sc["id"], v["focus"], "" if f is not None else "  (no face found → centre)"))
    json.dump(spec, open(a.scenes, "w"), indent=2, ensure_ascii=False)


if __name__ == "__main__":
    main()
