#!/usr/bin/env python3
import argparse
import json

import librosa
import numpy as np


def parse_cuts(raw: str) -> list[float]:
    if not raw:
        return []
    return [float(x.strip()) for x in raw.split(",") if x.strip()]


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze a music file and measure edit cuts against its beat grid.")
    parser.add_argument("audio")
    parser.add_argument("--cuts", default="", help="Comma-separated cut times in seconds")
    parser.add_argument("--fps", type=float, default=30.0)
    parser.add_argument("--subdivision", type=int, default=2, choices=(1, 2, 4), help="Beat grid subdivision")
    args = parser.parse_args()

    y, sr = librosa.load(args.audio, sr=22050, mono=True)
    tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)
    beat_times = librosa.frames_to_time(beat_frames, sr=sr)
    if args.subdivision > 1 and len(beat_times) > 1:
        grid = []
        for left, right in zip(beat_times[:-1], beat_times[1:]):
            grid.extend(np.linspace(left, right, args.subdivision, endpoint=False))
        grid.append(beat_times[-1])
        edit_grid = np.asarray(grid)
    else:
        edit_grid = beat_times
    cuts = parse_cuts(args.cuts)
    matches = []
    for cut in cuts:
        nearest = float(edit_grid[int(np.argmin(np.abs(edit_grid - cut)))])
        delta = nearest - cut
        matches.append({
            "cut_seconds": round(cut, 4),
            "nearest_beat_seconds": round(nearest, 4),
            "delta_seconds": round(delta, 4),
            "delta_frames": round(delta * args.fps, 2),
            "within_three_frames": abs(delta * args.fps) <= 3,
        })

    print(json.dumps({
        "duration_seconds": round(len(y) / sr, 4),
        "tempo_bpm": round(float(np.atleast_1d(tempo)[0]), 3),
        "beat_count": len(beat_times),
        "edit_grid_subdivision": args.subdivision,
        "first_beats_seconds": [round(float(x), 4) for x in beat_times[:32]],
        "cut_matches": matches,
    }, indent=2))


if __name__ == "__main__":
    main()
