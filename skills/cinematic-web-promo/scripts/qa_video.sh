#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 1 ]]; then
  echo "Usage: qa_video.sh path/to/video.mp4" >&2
  exit 2
fi

video="$1"
if [[ ! -f "$video" ]]; then
  echo "Video not found: $video" >&2
  exit 2
fi

ffprobe_bin="${FFPROBE_BIN:-$(command -v ffprobe || true)}"
ffmpeg_bin="${FFMPEG_BIN:-$(command -v ffmpeg || true)}"
if [[ -z "$ffprobe_bin" || -z "$ffmpeg_bin" ]]; then
  echo "ffmpeg and ffprobe are required (or set FFMPEG_BIN and FFPROBE_BIN)." >&2
  exit 2
fi

echo "== Media metadata =="
"$ffprobe_bin" -v error \
  -show_entries format=duration,size,bit_rate:stream=index,codec_name,codec_type,width,height,r_frame_rate,sample_rate,channels \
  -of json "$video"

echo "== Audio peak and silence candidates =="
"$ffmpeg_bin" -hide_banner -i "$video" -map 0:a:0 \
  -af "volumedetect,silencedetect=noise=-45dB:d=0.8" -f null - 2>&1 \
  | grep -E "mean_volume|max_volume|silence_(start|end)" || true

echo "== Freeze candidates (review intentional holds manually) =="
"$ffmpeg_bin" -hide_banner -i "$video" \
  -vf "freezedetect=n=-60dB:d=0.25" -an -f null - 2>&1 \
  | grep -E "freeze_(start|end|duration)" || true

echo "== Decoder pass =="
"$ffmpeg_bin" -v error -i "$video" -f null -
echo "QA command pass complete. Perform the manual checks in references/qa-checklist.md."
