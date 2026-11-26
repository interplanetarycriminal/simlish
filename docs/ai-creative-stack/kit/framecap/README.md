# framecap

Render a web page to a frame-exact video. It drives headless Chrome over the DevTools protocol, captures one screenshot per frame at an exact story time, encodes with FFmpeg and checks the result with ffprobe.

It stands in for the renderers of **HyperFrames** and **Remotion**: HTML in, deterministic MP4 out. It is our own code, written from the [time contract](../../docs/contracts/time-contract.md) and the catalogue's earlier [seekable scene renderer](../../fixtures/seekable-scene/render.mjs).

## How the clock works

Every frame `i` is captured at `t = i / fps`, never at wall-clock time.

- If the page defines `window.__scene` with `seek(t)` or `setTime(t)` (the time contract), framecap calls it for every frame.
- If the page loads [GSAP](../../docs/repositories/gsap.md), framecap pauses `gsap.globalTimeline` and sets its time to `t` plus the earliest tween start, so GSAP pages need no changes. HyperFrames lists GSAP among its animation runtimes, so this route may render many HyperFrames compositions; that is untested. Tested: a GSAP tween lands within 0.054 px of its position in every frame.
- Otherwise framecap pauses every animation in `document.getAnimations()` and sets its `currentTime` to `t`. This makes CSS animations, CSS transitions and Web Animations seekable with no change to the page. It asks for the list again every frame, so animations created later are caught too.

After seeking, it waits two animation frames, then captures until two consecutive captures match (see Determinism under load). CSS animations on a GSAP page are seeked as well.

## Usage

```sh
node framecap.mjs page.html --duration 4 --fps 30 --size 1280x720 --out out/film.mp4
node framecap.mjs https://example.test/scene --duration 10 --fps 60 --size 1920x1080 --audio music.wav --out out/film.mp4
node framecap.mjs page.html --duration 2 --size 640x360 --alpha --out out/overlay.mov            # ProRes 4444 with alpha
node framecap.mjs page.html --duration 2 --size 640x360 --alpha --format png --out out/frames    # RGBA PNG sequence
node framecap.mjs '<html>...</html>' --duration 1 --out out/inline.mp4                           # inline HTML
```

| Option | Default | Meaning |
| --- | --- | --- |
| `--duration` | 4 | Seconds. Frame count is `round(duration * fps)`. |
| `--fps` | 30 | Frame rate. |
| `--size` | 1280x720 | Viewport and output size. MP4 needs even numbers. |
| `--audio` | none | Audio file to mux. It is padded or trimmed to the video length. AAC in MP4, PCM in MOV. |
| `--alpha` | off | Transparent page background. Output is ProRes 4444 (`yuva444p10le`) `.mov`, or RGBA PNGs with `--format png`. The page itself must not paint a background. |
| `--format` | mp4, or mov with `--alpha` | `mp4` (H.264 `yuv420p`), `mov` (ProRes) or `png` (numbered frames in the `--out` folder). |
| `--out` | `out/film.<format>` | Output path. The report goes to `<out>.report.json`. |
| `--ready` | `document.readyState === 'complete' && window.__ready !== false` | JS expression that must be true before capture starts. A page that loads asynchronously should set `window.__ready = false` at the top and `true` when done, or you pass your own expression. |
| `--crf` | 18 | H.264 quality. |
| `--keep-frames` | off | Keep the PNG frames next to the video. |
| `--chrome` | auto | Chrome path. `CHROME` env also works. |

Local files are served over a temporary HTTP server on 127.0.0.1, so ES modules and `fetch` work.

The report holds the clock mode (`scene` or `animations`), the Chrome version, capture time and the ffprobe checks: decoded frame count, size, frame rate and duration within one frame. With audio it also checks the audio stream and its duration. framecap exits 0 only when all checks pass.

## Requirements

Node 22 or newer, Chrome or Chromium, `ffmpeg` and `ffprobe` on `PATH`. No npm packages. It uses the shared DevTools helper in `fixtures/lib/cdp.mjs`.

## What it does not do, compared with HyperFrames and Remotion

- No composition model, timeline editor, preview studio, React components or media sequencing. You bring a page that already animates.
- No parallel rendering across browser tabs. Capture is one screenshot at a time (about 8 to 9 frames per second at 1280x720 here).
- `requestAnimationFrame` loops, `setTimeout` timers, `<video>` elements and canvas code that reads `performance.now()` are not frozen. Such pages must use the time contract (`window.__scene.seek`) to be frame-exact.
- In animation mode each animation is seeked from its own start. An animation created by script 1 s after load is treated as starting at story time 0.
- One audio file only, no mixing or offsets.
- Pixel output is byte-stable only on the same machine, browser build and graphics backend (it uses SwiftShader through the shared helper).

## Test

```sh
node test.mjs
```

The test builds its own pages and audio in `out/pages/`, runs the CLI and decodes the outputs with FFmpeg:

| Check | What it proves | Result (26 Nov 2026, Chrome 158, FFmpeg 7.1) |
| --- | --- | --- |
| `cssPosition` | A CSS-only page (a 100 px box sliding 1180 px over 2 s, `linear`). In every one of the 60 decoded frames the box center (redness-weighted centroid) is within 2 px of the linear path. | pass, worst error 0.27 px |
| `alphaMov` | `--alpha` ProRes 4444: pixel format has alpha, all corners alpha 0, subject alpha 255 at the start and about 130 at the end (the page fades it to 0.5). | pass, corners 0, center 255 then 130 |
| `alphaPng` | `--alpha --format png`: PNG color type 6 (RGBA), corners transparent, 6 frames. | pass |
| `audioMux` | A generated 2 s, 440 Hz sine is muxed. ffprobe finds an AAC stream of 2.0 s (within one frame); decoded RMS is 0.088 (the sine's expected 0.088). | pass |
| `timeContract` | A canvas page with `window.__scene.seek(t)` and a delayed `__ready`. framecap picks the `scene` clock and the bar sits at `100 + 300 t` in every frame. | pass, worst error 0.11 px |

All outputs together are about 260 KB. `out/result.json` holds the numbers.

## Determinism under load

Chrome runs CSS opacity and transform animations on its compositor thread. There, a JavaScript `pause()` and `currentTime` seek does not reliably reach the next captured frame: under load, about half of the test runs captured frames from the wrong moment (one 10 frames late, one at 0.69 opacity instead of 1.0). Waiting longer only changed the odds. framecap now does two things:

- It launches Chrome with `--disable-threaded-animation`, so animations run on the main thread and the seek is what gets drawn. This is the actual fix: 6 runs out of 6 passed afterwards.
- It captures after each seek until two consecutive captures are byte-identical (at most 6). A paused, seeked page is static, so this only costs time when a frame was not yet settled. `settleCaptures` in the report counts the extra captures.

Pages that keep the [time contract](../../docs/contracts/time-contract.md) (`window.__scene.seek`) never had this problem, because they compute their state from `t` themselves.
