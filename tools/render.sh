#!/usr/bin/env bash
# Render a video: tools/render.sh <slug> [--still FRAME]
# Picks the Short (1080x1920) or Long (1920x1080) composition from scenes.json "format".
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SLUG="${1:?usage: tools/render.sh <slug> [--still FRAME]}"
FORMAT=$(python3 -c "import json,sys;print(json.load(open('$ROOT/videos/$SLUG/scenes.json'))['format'])")
COMP=$([ "$FORMAT" = "short" ] && echo Short || echo Long)
mkdir -p "$ROOT/videos/$SLUG/out"
cd "$ROOT/remotion"
if [ "${2:-}" = "--still" ]; then
  npx remotion still "$COMP" "../videos/$SLUG/out/frame_${3:-30}.png" --frame="${3:-30}" --props="{\"slug\":\"$SLUG\"}"
else
  OUT="../videos/$SLUG/out/$SLUG.mp4"
  npx remotion render "$COMP" "$OUT.raw.mp4" --props="{\"slug\":\"$SLUG\"}"
  # Loudness-normalise to YouTube's reference (-14 LUFS, -1 dBTP); video stream copied untouched.
  ffmpeg -v error -y -i "$OUT.raw.mp4" -c:v copy -af loudnorm=I=-14:TP=-1:LRA=11 -c:a aac -b:a 192k -ar 48000 -movflags +faststart "$OUT"
  rm "$OUT.raw.mp4"
  echo "done -> videos/$SLUG/out/$SLUG.mp4"
fi
