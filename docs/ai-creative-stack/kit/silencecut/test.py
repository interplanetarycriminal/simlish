#!/usr/bin/env python3
"""Test for silencecut.py. Synthesizes its own 10 s test video, runs the tool, checks the result.

    python test.py   -> out/cut.mp4, out/cut.edl.json, out/cut.report.json, out/result.json

Fixture: testsrc2 picture, 30 fps, 48 kHz audio with three 440 Hz tone bursts (1.5 s, 1.0 s, 2.0 s)
separated by 1.5 s gaps. The gaps are not digital silence: a quiet 103.7 Hz hum (-40 dBFS) runs under
everything, so a cut without fades lands on a live waveform and would click. A white square in
the top-left corner is lit exactly while a tone plays, which lets the test check A/V sync.

Checks:
  segments      3 speech segments found
  duration      output duration = tone durations + pads (within frame snapping) and = EDL sum
  selfCheck     silencecut's own render check passed (durations, click-free joins)
  clickFree     independent check: no step at any join in the decoded output
  avSync        every on/off edge of the white square matches the tone edge within 1 frame
  controlClicks with --fade 0 the same cuts DO click, so the click detector is not blind
Exit code 0 only on pass.
"""
from __future__ import annotations

import json
import subprocess
import sys
import wave
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
OUT = HERE / "out"
SR, FPS, W, H = 48000, 30, 320, 240
TONES = [(1.0, 2.5), (4.0, 5.0), (6.5, 8.5)]
PAD = 0.08


def sh(args, **kw):
    return subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False, **kw)


def make_fixture(path: Path):
    t = np.arange(10 * SR) / SR
    x = 0.01 * np.sin(2 * np.pi * 103.7 * t)
    for a, b in TONES:
        m = (t >= a) & (t < b)
        x[m] += 0.5 * np.sin(2 * np.pi * 440 * (t[m] - a))
    wav = OUT / "fixture.wav"
    with wave.open(str(wav), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((np.clip(x, -1, 1) * 32767).astype("<i2").tobytes())
    lit = "+".join(f"gte(t,{a})*lt(t,{b})" for a, b in TONES)
    vf = (f"drawbox=x=0:y=0:w=64:h=64:color=black:t=fill,"
          f"drawbox=x=0:y=0:w=64:h=64:color=white:t=fill:enable='{lit}'")
    p = sh(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-f", "lavfi", "-i", f"testsrc2=size={W}x{H}:rate={FPS}:duration=10",
            "-i", str(wav), "-vf", vf, "-c:v", "libx264", "-crf", "30", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k",
            "-shortest", str(path)])
    wav.unlink()
    if p.returncode:
        raise RuntimeError(p.stderr.decode())


def runs(flags: np.ndarray) -> list[tuple[int, int]]:
    edges, start = [], None
    for i, f in enumerate(flags):
        if f and start is None:
            start = i
        if not f and start is not None:
            edges.append((start, i))
            start = None
    if start is not None:
        edges.append((start, len(flags)))
    return edges


def main() -> int:
    OUT.mkdir(exist_ok=True)
    for f in OUT.iterdir():
        if f.is_file():
            f.unlink()
    src = OUT / "fixture.mp4"
    make_fixture(src)
    result = {"tool": "silencecut", "checks": {}}
    C = result["checks"]

    tool = [sys.executable, str(HERE / "silencecut.py")]
    p = sh(tool + [str(src), "--noise", "-35dB", "--min-silence", "0.4", "--pad", str(PAD), "--out", str(OUT / "cut.mp4")])
    print(p.stdout.decode(), p.stderr.decode())
    edl = json.loads((OUT / "cut.edl.json").read_text())
    rep = json.loads((OUT / "cut.report.json").read_text())
    segs = edl["segments"]

    C["segments"] = {"pass": len(segs) == 3, "found": len(segs),
                     "segments": [[s["in"], s["out"]] for s in segs],
                     "silences": [[s["start"], s["end"]] for s in edl["silences"]]}

    expected = sum(b - a for a, b in TONES) + 2 * PAD * len(TONES)
    total = edl["totalDuration"]
    edl_sum = sum(s["duration"] for s in segs)
    # Snapping each segment's ends outward to whole frames can add up to 2 frames per segment.
    slack = 2 * len(TONES) / FPS + 0.02
    C["duration"] = {"pass": abs(total - edl_sum) < 1e-9 and abs(total - expected) <= slack
                     and abs(rep["videoDuration"] - total) <= 1 / FPS and abs(rep["audioDuration"] - total) <= 1 / FPS,
                     "expectedTonesPlusPads": round(expected, 4), "edlTotal": round(total, 4), "allowedSlack": round(slack, 4),
                     "videoDuration": rep["videoDuration"], "audioDuration": rep["audioDuration"]}
    C["selfCheck"] = {"pass": p.returncode == 0 and rep["pass"], "exitCode": p.returncode, "checks": rep["checks"]}

    # Independent decode of the output.
    raw = sh(["ffmpeg", "-hide_banner", "-loglevel", "error", "-i", str(OUT / "cut.mp4"), "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"]).stdout
    pcm = np.frombuffer(raw, dtype="<f4")
    d = np.abs(np.diff(pcm))
    joins = [s["outputStart"] for s in segs[1:]]
    worst = []
    for j in joins:
        b = int(round(j * SR))
        worst.append(float(d[b - 96:b + 96].max()))
    hum_step = 0.01 * 2 * np.pi * 103.7 / SR
    C["clickFree"] = {"pass": all(w < 0.002 for w in worst), "joinSeconds": joins, "peakStepAtJoins": [round(w, 6) for w in worst],
                      "humNaturalStep": round(hum_step, 6), "limit": 0.002}

    # A/V sync: per output frame, is the square lit, and is the tone sounding?
    vraw = sh(["ffmpeg", "-hide_banner", "-loglevel", "error", "-i", str(OUT / "cut.mp4"), "-f", "rawvideo", "-pix_fmt", "gray", "-"]).stdout
    frames = np.frombuffer(vraw, dtype=np.uint8).reshape(-1, H, W)
    lit = frames[:, 8:56, 8:56].mean(axis=(1, 2)) > 128
    spf = SR // FPS
    n = min(len(lit), len(pcm) // spf)
    rms = np.sqrt((pcm[: n * spf].reshape(n, spf) ** 2).mean(axis=1))
    tone = rms > 0.1
    rv, ra = runs(lit[:n]), runs(tone)
    edge_err = [max(abs(x[0] - y[0]), abs(x[1] - y[1])) for x, y in zip(rv, ra)] if len(rv) == len(ra) else [99]
    C["avSync"] = {"pass": len(rv) == 3 and len(ra) == 3 and max(edge_err) <= 1,
                   "videoRuns": rv, "audioRuns": ra, "worstEdgeFrames": int(max(edge_err)),
                   "mismatchedFrames": int((lit[:n] != tone).sum()), "frames": int(n)}

    # Control: the same cuts without fades must be caught as clicks.
    pc = sh(tool + [str(src), "--pad", str(PAD), "--fade", "0", "--out", str(OUT / "control.mp4")])
    crep = json.loads((OUT / "control.report.json").read_text())
    C["controlClicks"] = {"pass": pc.returncode == 1 and not crep["checks"]["clickFree"],
                          "exitCode": pc.returncode, "boundaries": crep["boundaries"]}
    for f in ["control.mp4", "control.edl.json", "control.report.json", "fixture.mp4"]:
        (OUT / f).unlink(missing_ok=True)

    result["outBytes"] = sum(f.stat().st_size for f in OUT.iterdir() if f.is_file())
    result["pass"] = all(c["pass"] for c in C.values())
    (OUT / "result.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    for k, c in C.items():
        print(f"{'PASS' if c['pass'] else 'FAIL'}  {k}")
    print("All checks passed" if result["pass"] else "Some checks failed")
    return 0 if result["pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
