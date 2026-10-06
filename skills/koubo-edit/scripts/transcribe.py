#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "mlx-whisper>=0.4.3; sys_platform == 'darwin' and platform_machine == 'arm64'",
#     "faster-whisper>=1.0.3; sys_platform != 'darwin' or platform_machine != 'arm64'",
#     "static-ffmpeg>=3.0",
#     "numpy",
# ]
# ///
"""口播视频本机转写：抽音轨 → Whisper → 带时间戳的字幕素材 JSON。

跨平台：Apple Silicon Mac 自动用 MLX Whisper（最快）；Windows / Linux /
Intel Mac 自动降级 faster-whisper（CTranslate2，CPU 可跑，不依赖 PyTorch）。
依赖按平台自动选择，无需手动安装任何转写方案。

用法（任意目录，依赖由 uv 按上方内联声明自动解决）：
    uv run ~/.claude/skills/koubo-edit/scripts/transcribe.py <口播视频> -o <输出.json>

输出 JSON 结构：
    {
      "metadata": {"duration_ms", "width", "height", "fps"},
      "transcript": "整段口播文字",
      "segments": [{"start_ms", "end_ms", "text"}],   # whisper 原生分段
      "words":    [{"w", "start_ms", "end_ms"}]        # 词级时间戳，用于精细分页
    }
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
import wave
from pathlib import Path

# 模型托管在 Hugging Face；国内无外网环境直连不通，默认走 hf-mirror 国内镜像
# （已设 HF_ENDPOINT 则尊重用户配置；离线模型包用 --model <本地目录> 可完全不联网）。
os.environ.setdefault("HF_ENDPOINT", "https://hf-mirror.com")

INITIAL_PROMPT = "以下是普通话中文短视频口播，请使用简体中文准确转写产品名、数字和关键词。"

# 通用模型名 → MLX 社区仓库名（faster-whisper 直接吃通用名）
MLX_REPOS = {
    "tiny": "mlx-community/whisper-tiny-mlx",
    "small": "mlx-community/whisper-small-mlx",
    "medium": "mlx-community/whisper-medium-mlx",
    "large-v3": "mlx-community/whisper-large-v3-mlx",
    "large-v3-turbo": "mlx-community/whisper-large-v3-turbo",
}


def ffmpeg_paths() -> tuple[str, str]:
    ffmpeg, ffprobe = shutil.which("ffmpeg"), shutil.which("ffprobe")
    if ffmpeg and ffprobe:
        return ffmpeg, ffprobe
    from static_ffmpeg import run as static_run

    return static_run.get_or_fetch_platform_executables_else_raise()


def probe(path: Path) -> dict:
    _ffmpeg, ffprobe = ffmpeg_paths()
    # -show_streams 全量拿流信息：手机竖拍的旋转标记在 stream 的 side_data_list 里，
    # 用 -show_entries 白名单会把它漏掉，导致竖屏视频被当成横屏。
    proc = subprocess.run(
        [ffprobe, "-v", "error", "-show_streams", "-show_format", "-of", "json", str(path)],
        capture_output=True, text=True, timeout=40,
    )
    payload = json.loads(proc.stdout or "{}")
    video = next((s for s in payload.get("streams", []) if s.get("codec_type") == "video"), {})
    duration = float(payload.get("format", {}).get("duration") or 0)
    rate = video.get("avg_frame_rate") or "30/1"
    try:
        num, den = rate.split("/")
        fps = round(float(num) / float(den or 1), 3)
    except (ValueError, ZeroDivisionError):
        fps = 30.0
    if not video or duration <= 0:
        sys.exit("错误：读不到视频画面或时长，请确认是正常的 MP4/MOV/WebM 文件")

    width, height = int(video.get("width") or 0), int(video.get("height") or 0)
    # 手机竖拍视频常按横向存储 + 旋转元数据，播放端才转正；
    # 按显示方向换算画幅，否则成片会横竖颠倒。
    rotation = 0
    for side_data in video.get("side_data_list") or []:
        if isinstance(side_data, dict) and side_data.get("rotation") is not None:
            try:
                rotation = int(round(float(side_data["rotation"])))
            except (TypeError, ValueError):
                pass
    try:
        rotation = int(round(float((video.get("tags") or {}).get("rotate") or rotation)))
    except (TypeError, ValueError):
        pass
    if abs(rotation) % 180 == 90:
        width, height = height, width

    return {
        "duration_ms": int(duration * 1000),
        "width": width,
        "height": height,
        "rotation": rotation,
        "fps": fps,
    }


def extract_wav(video: Path, wav: Path) -> None:
    ffmpeg, _ = ffmpeg_paths()
    proc = subprocess.run(
        [ffmpeg, "-y", "-i", str(video), "-vn", "-ac", "1", "-ar", "16000",
         "-c:a", "pcm_s16le", str(wav)],
        capture_output=True, text=True, timeout=300,
    )
    if proc.returncode != 0 or not wav.exists() or wav.stat().st_size == 0:
        sys.exit(f"错误：抽取音轨失败：{(proc.stderr or '')[-300:]}")


def pick_backend(requested: str) -> str:
    if requested != "auto":
        return requested
    try:
        import mlx_whisper  # noqa: F401
        return "mlx"
    except ImportError:
        return "faster"


def transcribe_mlx(wav: Path, model: str) -> dict:
    import mlx_whisper
    import numpy as np

    repo = model if "/" in model else MLX_REPOS.get(model, f"mlx-community/whisper-{model}-mlx")
    # mlx-whisper 收到路径时会去 shell 调全局 ffmpeg；直接喂标准化后的
    # 16kHz 单声道 PCM 采样，保持自包含（与 fanout video_editor 同一做法）。
    with wave.open(str(wav), "rb") as source:
        audio = np.frombuffer(
            source.readframes(source.getnframes()), dtype="<i2"
        ).astype(np.float32) / 32768.0
    return mlx_whisper.transcribe(
        audio, path_or_hf_repo=repo, language="zh", task="transcribe",
        word_timestamps=True, verbose=False, initial_prompt=INITIAL_PROMPT,
    )


def transcribe_faster(wav: Path, model: str) -> dict:
    from faster_whisper import WhisperModel

    name = model.removeprefix("mlx-community/whisper-").removesuffix("-mlx")
    # 离线优先：skill 自带 models/faster-whisper-<name>/ 时直接用，完全不联网
    bundled = Path(__file__).resolve().parent.parent / "models" / f"faster-whisper-{name}"
    if bundled.is_dir():
        name = str(bundled)
    engine = WhisperModel(name, device="cpu", compute_type="int8")
    seg_iter, _info = engine.transcribe(
        str(wav), language="zh", task="transcribe",
        word_timestamps=True, initial_prompt=INITIAL_PROMPT,
    )
    segments = []
    for seg in seg_iter:
        segments.append({
            "start": seg.start,
            "end": seg.end,
            "text": seg.text,
            "words": [
                {"word": w.word, "start": w.start, "end": w.end}
                for w in (seg.words or [])
            ],
        })
    return {"text": "".join(s["text"] for s in segments), "segments": segments}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("video", type=Path)
    parser.add_argument("-o", "--out", type=Path, required=True)
    parser.add_argument("--model", default="small",
                        help="通用模型名（tiny/small/medium/large-v3-turbo），"
                             "识别不准时可换 large-v3-turbo；两个后端自动映射；"
                             "也可传离线模型包解压后的本地目录，完全不联网")
    parser.add_argument("--backend", default="auto", choices=["auto", "mlx", "faster"],
                        help="auto=Apple Silicon 用 MLX，其余平台用 faster-whisper")
    args = parser.parse_args()
    if not args.video.exists():
        sys.exit(f"错误：找不到视频 {args.video}")

    backend = pick_backend(args.backend)
    metadata = probe(args.video)
    with tempfile.TemporaryDirectory(prefix="koubo-edit-") as tmp:
        wav = Path(tmp) / "speech.wav"
        extract_wav(args.video, wav)
        if backend == "mlx":
            result = transcribe_mlx(wav, args.model)
        else:
            result = transcribe_faster(wav, args.model)

    segments, words = [], []
    for seg in result.get("segments", []) or []:
        text = str(seg.get("text") or "").strip(" ，,。！？!?；;\n\t")
        if not text:
            continue
        segments.append({
            "start_ms": int(float(seg.get("start") or 0) * 1000),
            "end_ms": int(float(seg.get("end") or 0) * 1000),
            "text": text,
        })
        for word in seg.get("words", []) or []:
            token = str(word.get("word") or "").strip()
            if token:
                words.append({
                    "w": token,
                    "start_ms": int(float(word.get("start") or 0) * 1000),
                    "end_ms": int(float(word.get("end") or 0) * 1000),
                })

    payload = {
        "metadata": metadata,
        "transcript": str(result.get("text") or "").strip(),
        "segments": segments,
        "words": words,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"转写完成（{backend}）：{len(segments)} 段 / {len(words)} 词，"
          f"时长 {metadata['duration_ms'] / 1000:.1f}s，"
          f"画幅 {metadata['width']}x{metadata['height']} → {args.out}")


if __name__ == "__main__":
    main()
