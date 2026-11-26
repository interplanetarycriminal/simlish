#!/usr/bin/env python3
"""silencecut: remove silences from a talking video, with click-free cuts and a self-check.

    python silencecut.py input.mp4 --noise -35dB --min-silence 0.4 --pad 0.08 --out out/cut.mp4

Steps:
  1. FFmpeg silencedetect finds the silent stretches of the first audio stream.
  2. The rest becomes speech segments. Each is padded, snapped to whole video frames and merged
     with its neighbours where they touch. The segment list is written as an EDL (JSON).
  3. One FFmpeg pass trims every segment from the video and audio, puts a short fade in and out
     on the audio of each segment (default 30 ms), and concatenates them.
  4. The render is checked: video and audio durations must match the EDL sum within one frame,
     and the decoded audio must have no step discontinuity at any cut.

Writes <out>, <out minus extension>.edl.json and <out minus extension>.report.json.
Exit codes: 0 = rendered and self-check passed, 1 = self-check failed, 2 = error.
Needs ffmpeg and ffprobe on PATH, and numpy.
"""
from __future__ import annotations

import argparse
import json
import math
import re
import subprocess
import sys
from fractions import Fraction
from pathlib import Path

import numpy as np


def run(args: list[str], binary: bool = False):
    p = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if p.returncode != 0:
        raise RuntimeError(f"{args[0]} failed ({p.returncode}): {p.stderr.decode('utf-8', 'replace')[-1500:]}")
    return p if binary else p.stdout.decode("utf-8", "replace")


def probe(path: Path, count_frames: bool = False) -> dict:
    args = ["ffprobe", "-v", "error"]
    if count_frames:
        args += ["-count_frames"]
    args += ["-show_entries", "stream=index,codec_type,codec_name,r_frame_rate,avg_frame_rate,nb_read_frames,"
             "sample_rate,channels,duration,start_time,width,height:format=duration", "-of", "json", str(path)]
    info = json.loads(run(args))
    v = next((s for s in info["streams"] if s["codec_type"] == "video"), None)
    a = next((s for s in info["streams"] if s["codec_type"] == "audio"), None)
    return {"video": v, "audio": a, "duration": float(info["format"]["duration"])}


def parse_db(text: str) -> float:
    m = re.fullmatch(r"\s*(-?\d+(?:\.\d+)?)\s*(?:dB)?\s*", text, re.I)
    if not m:
        raise argparse.ArgumentTypeError(f"noise level must look like -35dB, got {text!r}")
    return float(m.group(1))


def detect_silences(path: Path, noise_db: float, min_silence: float, duration: float) -> list[tuple[float, float]]:
    p = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(path), "-map", "0:a:0",
                        "-af", f"silencedetect=noise={noise_db}dB:d={min_silence}", "-f", "null", "-"],
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if p.returncode != 0:
        raise RuntimeError("silencedetect failed: " + p.stderr.decode("utf-8", "replace")[-800:])
    silences, start = [], None
    for line in p.stderr.decode("utf-8", "replace").splitlines():
        if m := re.search(r"silence_start:\s*(-?[\d.]+(?:e-?\d+)?)", line):
            start = max(0.0, float(m.group(1)))
        elif (m := re.search(r"silence_end:\s*([\d.]+(?:e-?\d+)?)", line)) and start is not None:
            silences.append((start, min(duration, float(m.group(1)))))
            start = None
    if start is not None:  # silence that runs to the end of the file
        silences.append((start, duration))
    return silences


def plan_segments(silences, duration, pad, fps: Fraction, n_frames, min_speech):
    """Speech = complement of silences, padded, snapped to the frame grid, merged."""
    speech, t = [], 0.0
    for s, e in silences:
        if s > t:
            speech.append((t, s))
        t = max(t, e)
    if t < duration:
        speech.append((t, duration))
    frames = []
    for s, e in speech:
        if e - s < min_speech:
            continue
        a = max(0, math.floor((s - pad) * fps + 1e-6))
        b = min(n_frames, math.ceil((e + pad) * fps - 1e-6))
        if b <= a:
            continue
        if frames and a <= frames[-1][1]:
            frames[-1][1] = max(frames[-1][1], b)  # padded neighbours touch: merge
        else:
            frames.append([a, b])
    return [(a, b) for a, b in frames]


def build_filter(segments, sr: int, fps: Fraction, fade: float, has_video: bool) -> str:
    lines, labels = [], []
    for i, (a, b) in enumerate(segments):
        s0, s1 = round(a * sr / fps), round(b * sr / fps)
        dur = (s1 - s0) / sr
        chain = f"[0:a:0]atrim=start_sample={s0}:end_sample={s1},asetpts=PTS-STARTPTS"
        f = min(fade, dur / 2)
        if f > 0:
            chain += f",afade=t=in:st=0:d={f:.6f}:curve=hsin,afade=t=out:st={dur - f:.6f}:d={f:.6f}:curve=hsin"
        lines.append(chain + f"[a{i}]")
        if has_video:
            lines.append(f"[0:v:0]trim=start_frame={a}:end_frame={b},setpts=PTS-STARTPTS[v{i}]")
            labels.append(f"[v{i}][a{i}]")
        else:
            labels.append(f"[a{i}]")
    v = 1 if has_video else 0
    lines.append("".join(labels) + f"concat=n={len(segments)}:v={v}:a=1" + ("[vout][aout]" if has_video else "[aout]"))
    return ";\n".join(lines)


def decode_pcm(path: Path, sr: int, channels: int) -> np.ndarray:
    raw = run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-i", str(path), "-map", "0:a:0",
               "-f", "f32le", "-ac", str(channels), "-ar", str(sr), "-"], binary=True).stdout
    return np.frombuffer(raw, dtype="<f4").reshape(-1, channels)


def boundary_steps(pcm: np.ndarray, sr: int, times: list[float]) -> list[dict]:
    """Peak sample-to-sample jump at each cut versus the signal's own jumps 40-80 ms away."""
    d = np.abs(np.diff(pcm, axis=0)).max(axis=1)
    k, near, far = int(0.002 * sr), int(0.040 * sr), int(0.080 * sr)
    out = []
    for t in times:
        b = int(round(t * sr))
        lo, hi = max(0, b - k), min(len(d), b + k)
        peak = float(d[lo:hi].max()) if hi > lo else 0.0
        ctx = np.concatenate([d[max(0, b - far):max(0, b - near)], d[min(len(d), b + near):min(len(d), b + far)]])
        ref = float(ctx.max()) if ctx.size else 0.0
        click = peak > max(3.0 * ref, 0.002)
        out.append({"t": round(t, 4), "peakStep": round(peak, 6), "contextStep": round(ref, 6), "click": bool(click)})
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Cut silences out of a video with click-free joins.")
    ap.add_argument("input", type=Path)
    ap.add_argument("--noise", type=parse_db, default=-35.0, help="silence threshold, e.g. -35dB")
    ap.add_argument("--min-silence", type=float, default=0.4, help="shortest silence to remove, seconds")
    ap.add_argument("--pad", type=float, default=0.08, help="speech kept on each side of a cut, seconds")
    ap.add_argument("--fade", type=float, default=0.03, help="audio fade at every cut, seconds (0 = none)")
    ap.add_argument("--min-speech", type=float, default=0.05, help="drop speech bursts shorter than this, seconds")
    ap.add_argument("--crf", type=int, default=20)
    ap.add_argument("--out", type=Path, default=Path("out/cut.mp4"))
    ap.add_argument("--edl-only", action="store_true", help="write the EDL and stop")
    args = ap.parse_args(argv)

    src = args.input
    if not src.exists():
        print(f"input not found: {src}", file=sys.stderr)
        return 2
    info = probe(src)
    if not info["audio"]:
        print("input has no audio stream", file=sys.stderr)
        return 2
    v, a = info["video"], info["audio"]
    sr, channels = int(a["sample_rate"]), int(a["channels"])
    # Audio-only input: use a 100 Hz grid in place of video frames.
    fps = Fraction(v["r_frame_rate"]) if v else Fraction(100)
    duration = info["duration"]
    n_frames = math.floor(duration * fps + 1e-6)

    silences = detect_silences(src, args.noise, args.min_silence, duration)
    segs = plan_segments(silences, duration, args.pad, fps, n_frames, args.min_speech)
    if not segs:
        print("no speech found above the noise threshold", file=sys.stderr)
        return 2

    out = args.out
    out.parent.mkdir(parents=True, exist_ok=True)
    stem = out.with_suffix("")
    edl_path, report_path = Path(f"{stem}.edl.json"), Path(f"{stem}.report.json")
    seg_rows, t_out = [], Fraction(0)
    for i, (fa, fb) in enumerate(segs):
        d = Fraction(fb - fa) / fps
        seg_rows.append({"index": i, "in": float(fa / fps), "out": float(fb / fps), "duration": float(d),
                         "inFrame": fa, "outFrame": fb, "outputStart": float(t_out)})
        t_out += d
    total = float(t_out)
    edl = {"version": 1, "source": src.name, "sourceDuration": duration, "fps": str(fps) if v else None,
           "grid": "video frames" if v else "10 ms", "sampleRate": sr, "channels": channels,
           "params": {"noiseDb": args.noise, "minSilence": args.min_silence, "pad": args.pad, "fade": args.fade, "minSpeech": args.min_speech},
           "silences": [{"start": round(s, 4), "end": round(e, 4)} for s, e in silences],
           "segments": seg_rows, "totalDuration": total}
    edl_path.write_text(json.dumps(edl, indent=2) + "\n", encoding="utf-8")
    print(f"{len(silences)} silences, {len(segs)} segments, {duration:.3f} s -> {total:.3f} s; EDL {edl_path}")
    if args.edl_only:
        return 0

    # The filter graph goes through a file so long EDLs do not hit command-line limits.
    graph_path = Path(f"{stem}.filter.txt")
    graph_path.write_text(build_filter(segs, sr, fps, args.fade, bool(v)), encoding="utf-8")
    cmd = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(src), "-filter_complex_script", str(graph_path)]
    if v:
        cmd += ["-map", "[vout]", "-c:v", "libx264", "-preset", "medium", "-crf", str(args.crf), "-pix_fmt", "yuv420p", "-r", str(fps)]
    cmd += ["-map", "[aout]", "-c:a", "aac", "-b:a", "192k", "-ar", str(sr), "-movflags", "+faststart", str(out)]
    try:
        run(cmd)
    finally:
        graph_path.unlink(missing_ok=True)

    # Self-check.
    tol = float(1 / fps) + 1e-6
    p = probe(out, count_frames=True)
    checks, details = {}, {}
    if v:
        vframes = int(p["video"]["nb_read_frames"])
        vdur = vframes / float(fps)
        checks["videoDuration"] = abs(vdur - total) <= tol
        details["videoFrames"], details["videoDuration"] = vframes, vdur
    adur = float(p["audio"].get("duration") or p["duration"])
    checks["audioDuration"] = abs(adur - total) <= tol
    details["audioDuration"] = adur
    pcm = decode_pcm(out, sr, channels)
    details["decodedAudioSeconds"] = len(pcm) / sr
    joins = [r["outputStart"] for r in seg_rows[1:]]
    steps = boundary_steps(pcm, sr, joins)
    checks["clickFree"] = not any(s["click"] for s in steps)
    report = {"tool": "silencecut", "input": src.name, "output": out.name, "edl": edl_path.name,
              "segments": len(segs), "silences": len(silences), "sourceDuration": duration, "edlDuration": total,
              "toleranceSeconds": tol, "checks": checks, **details, "boundaries": steps,
              "pass": all(checks.values())}
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    for k, ok in checks.items():
        print(f"{'PASS' if ok else 'FAIL'}  {k}")
    print(("OK: " if report["pass"] else "SELF-CHECK FAILED: ") + str(out))
    return 0 if report["pass"] else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except RuntimeError as e:
        print(e, file=sys.stderr)
        sys.exit(2)
