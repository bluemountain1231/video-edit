#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = ["static-ffmpeg>=3.0", "numpy"]
# ///
"""物料工厂抠图：把一张白底多物料图切格子并抠成透明 PNG。

用法（任意目录，依赖由 uv 按上方内联声明自动解决）：
    uv run ~/.claude/skills/koubo-edit/scripts/cutout.py sheet.png --grid 2x2 -o output/dir --prefix prop

一张 gpt-image 生成的白底物料图（要求 prompt 里写明 evenly spaced grid、pure white
background、每格一个物件）→ 按网格切开 → 白色变透明 → 按内容自动裁边 → prop_1.png...
无 Pillow 依赖：ffmpeg 管道解码 + numpy 处理 + ffmpeg 编码。
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

import numpy as np


def ffmpeg_paths() -> tuple[str, str]:
    ffmpeg, ffprobe = shutil.which("ffmpeg"), shutil.which("ffprobe")
    if ffmpeg and ffprobe:
        return ffmpeg, ffprobe
    from static_ffmpeg import run as static_run

    return static_run.get_or_fetch_platform_executables_else_raise()


def read_rgba(path: Path) -> np.ndarray:
    ffmpeg, ffprobe = ffmpeg_paths()
    probe = subprocess.run(
        [ffprobe, "-v", "error", "-show_entries", "stream=width,height", "-of", "json", str(path)],
        capture_output=True, text=True, timeout=30,
    )
    stream = json.loads(probe.stdout)["streams"][0]
    w, h = int(stream["width"]), int(stream["height"])
    proc = subprocess.run(
        [ffmpeg, "-v", "error", "-i", str(path), "-f", "rawvideo", "-pix_fmt", "rgba", "-"],
        capture_output=True, timeout=60,
    )
    return np.frombuffer(proc.stdout, dtype=np.uint8).reshape(h, w, 4).copy()


def write_rgba(img: np.ndarray, path: Path) -> None:
    ffmpeg, _ = ffmpeg_paths()
    h, w = img.shape[:2]
    proc = subprocess.run(
        [ffmpeg, "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{w}x{h}",
         "-i", "-", "-frames:v", "1", str(path)],
        input=img.tobytes(), capture_output=True, timeout=60,
    )
    if proc.returncode != 0 or not path.exists():
        sys.exit(f"错误：写出 {path} 失败：{proc.stderr.decode()[-200:]}")


def white_to_alpha(img: np.ndarray, floor: int = 12, softness: float = 4.0) -> np.ndarray:
    """接近纯白 → 透明；彩色/深色 → 不透明；边缘按离白距离渐变。
    floor 以内的浅噪点（生成图常见的纸纹）直接归零，避免深色底上出现雾状残留。"""
    rgb = img[:, :, :3].astype(np.int16)
    dist = 255 - rgb.min(axis=2)          # 离纯白的距离（0=纯白）
    alpha = np.clip((dist - floor) * softness, 0, 255).astype(np.uint8)
    out = img.copy()
    out[:, :, 3] = alpha
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("sheet", type=Path)
    parser.add_argument("--grid", default="1x1", help="行x列，如 2x2；1x1 表示整图单物料")
    parser.add_argument("-o", "--outdir", type=Path, required=True)
    parser.add_argument("--prefix", default="prop")
    parser.add_argument("--pad", type=int, default=10, help="裁边后保留的透明边距像素")
    args = parser.parse_args()

    rows, cols = (int(x) for x in args.grid.lower().split("x"))
    img = white_to_alpha(read_rgba(args.sheet))
    h, w = img.shape[:2]
    args.outdir.mkdir(parents=True, exist_ok=True)

    index = 0
    for r in range(rows):
        for c in range(cols):
            cell = img[r * h // rows:(r + 1) * h // rows, c * w // cols:(c + 1) * w // cols]
            mask = cell[:, :, 3] > 20
            if mask.sum() < 400:          # 空格子跳过
                continue
            ys, xs = np.where(mask)
            y0, y1 = max(0, ys.min() - args.pad), min(cell.shape[0], ys.max() + args.pad)
            x0, x1 = max(0, xs.min() - args.pad), min(cell.shape[1], xs.max() + args.pad)
            index += 1
            out = args.outdir / f"{args.prefix}_{index}.png"
            write_rgba(np.ascontiguousarray(cell[y0:y1, x0:x1]), out)
            print(f"{out}  {x1 - x0}x{y1 - y0}")
    if index == 0:
        sys.exit("错误：没有切出任何物料，确认图是白底且 --grid 正确")
    print(f"完成：{index} 个物料 → {args.outdir}")


if __name__ == "__main__":
    main()
