---
name: shot-planning
description: Plan, render and finish a short film from web pages, 3D scenes or footage with one timeline authority, then encode and verify it. Use for promo videos, explainers, product films, screen-capture films and edits of talking-head footage.
---

# Shot planning

Our own stand-in for Video Shotcraft's shot planning, HyperFrames and Remotion rendering, and Video Use's editing pass. It plans with the catalogue's shot list, renders with [framecap](../../framecap/README.md), and edits with [silencecut](../../silencecut/README.md).

## 1. Plan

Fill the [shot list](../../../templates/shot-list.md) before rendering anything: resolution, frame rate, duration, then one row per shot with framing, camera move and curve, assets, transition and audio cue. Every asset row names its version.

Rules of thumb:

- One idea per shot.
- A shot under 1.5 s needs a reason.
- Cut on action, or on a word.
- Never cut mid-motion of the subject.
- Hold the final frame at least 1 s.

## 2. Build each shot as a seekable page

Each shot is an HTML page whose state is a function of time. Either expose `window.__scene.seek(t)` (the catalogue's [time contract](../../../docs/contracts/time-contract.md)), or use only CSS and Web Animations, which framecap can seek itself. Rewrite `requestAnimationFrame` loops as functions of `t` first.

## 3. Render

```sh
node kit/framecap/framecap.mjs shot1.html --duration 4 --fps 30 --size 1920x1080 --out out/shot1.mp4
node kit/framecap/framecap.mjs title.html --duration 3 --alpha --out out/title.mov   # overlays with transparency
```

framecap checks frame count, size, frame rate and duration with ffprobe, and fails if they differ.

## 4. Edit footage, if there is any

```sh
python kit/silencecut/silencecut.py talk.mp4 --noise -35dB --min-silence 0.4 --pad 0.08 --out out/talk_cut.mp4
```

Review the EDL before accepting it. silencecut cuts silence, not filler words or bad takes; those need a person.

## 5. Assemble and encode

Use one timeline authority. Concatenate in shot-list order with FFmpeg, overlaying the alpha titles. Encode once to the delivery format; never re-encode an already lossy master twice. Check the result:

```sh
ffprobe -v error -count_frames -show_entries stream=codec_name,width,height,r_frame_rate,nb_read_frames:format=duration -of json final.mp4
```

## 6. Review

Watch the full film at full speed once, and step through every cut frame by frame. Fill the [execution report](../../../templates/execution-report.md).
