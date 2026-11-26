# OneTake

Use for short product launch films, teasers and feature demos that play as one continuous camera move, with continuity checked by an automatic oracle before a human watches.

> Motion films, explainers and engines · Added by the user · smoke test: **not run**

## Evidence and maintenance

- [Canonical reference](https://github.com/feitangyuan/onetake)
- Verified 2026-11-26 against default branch `main` at [`4e024be4c6c6`](https://github.com/feitangyuan/onetake/commit/4e024be4c6c696b260f39a35aee6bd56d303b679).
- GitHub reports archive state **false** and a repository push at `2026-11-19T06:06:40Z`. Push activity is a maintenance signal, not a quality rating.
- Attribution: Added directly by the user on 2026-11-26.

- [README.md](https://github.com/feitangyuan/onetake/blob/4e024be4c6c696b260f39a35aee6bd56d303b679/README.md)
- [SKILL.md](https://github.com/feitangyuan/onetake/blob/4e024be4c6c696b260f39a35aee6bd56d303b679/SKILL.md)
- [LICENSE](https://github.com/feitangyuan/onetake/blob/4e024be4c6c696b260f39a35aee6bd56d303b679/LICENSE)

## Runtime, hardware and setup

- **Type** skill. Primary language Python.
- **Platforms** Unverified.
- **Runtime** python3 with playwright (chromium), numpy, scipy, Pillow, matplotlib, fonttools + brotli; opencv-python for reference analysis; ffmpeg / ffprobe; node for library tests. Narration: faster-whisper and Kokoro (kokoro-onnx, soundfile, misaki[ja], unidic-lite).
- **Execution** local.
- **Agent paths** Claude Code, Codex, Other agents that read skills. Client claims describe documentation and remain untested here unless the smoke test says otherwise.
- **Configuration** Install as a skill folder; looks/looks.json provides six measured color-and-type looks, and render.py flags (--final, --gpu, --workers) select draft or 4K60 output.
- **Credentials and services** None documented; narration uses local Kokoro and faster-whisper.

| Hardware | Documented value |
| --- | --- |
| GPU | none required; WebGL compositions render with --gpu |
| Minimum VRAM | Not documented |
| Recommended VRAM | Not documented |
| System RAM | Not documented |
| Storage | Not documented |
| CPU fallback | documented |
| Training versus inference | Not documented |
| Notes | render.py runs parallel browser workers (default cores minus 2, max 8). WebGL comps use --gpu (Chromium on ANGLE/Metal); software SwiftShader costs about 4x. Drafts 1080p30, finals 4K60. |

Review the source and pin the version before running the upstream-documented command. It was read in the pinned documentation; execution is recorded only under Smoke test.

```sh
git clone https://github.com/feitangyuan/onetake.git ~/.claude/skills/onetake
```

## Contracts and selection

| Boundary | Contract |
| --- | --- |
| Input | Product screenshots (UI rebuilt in HTML), Real web pages driven by Playwright, Screen recordings, Reference video for numeric analysis, Narration script, Royalty-free music track, Blender-made GLB models for 3D films |
| Output | Single HTML composition with window.__seek(t), MP4 at 1920x1080 30 fps (draft) or 3840x2160 60 fps (final), Synthesised sound-effect and score WAVs, Timed subtitles |
| Primary | Animation, Video composition |
| Supporting | Shot planning, Design critique, Media processing |

Skip if the user names HyperFrames or Remotion; the skill itself says to use what they name. Consider [hyperframes](hyperframes.md), [remotion](remotion.md), [huashu-motion](huashu-motion.md), [lemo-opuscar](lemo-opuscar.md), [motion-canvas](motion-canvas.md). Complementary tools include [three-js](three-js.md), [blender-mcp](blender-mcp.md), [ffmpeg](ffmpeg.md), [openscreen](openscreen.md).

Its own Playwright Chromium renderer on a window.__seek(t) page: the same seekable-page idea as the catalogue's time contract.

- Skip for client or business work unless you buy the onetake Pro commercial license.

## Craft notes

- Designs the boundary between beats: something on screen must survive and become the next beat; probe.py scores 'carry' per boundary (accepted films 0.75 and 0.83, a rejected slideshow 0.00).
- About 38 measured moves in lib/motion.js, each a pure function of time; shot lengths must vary by at least 4x, and the oracle also fails uniform cadence, no stillness, clipped audio and fast moves without blur.
- Real 180-degree shutter motion blur by averaging several captures in linear light; moves over 80 px/frame strobe without it.

## Examples

1. **Independent** Ask for 'a 15 s launch video for my app' from three screenshots, pick one of three concepts, and render a 1080p30 draft with render.py.
2. **Combined** Documented in references/3d.md: model an object with blender-mcp, export GLB, and stage it in three-js inside the onetake composition.

For both, save the inputs and output evidence with the selected version. Use a small authorized fixture first and review the actual render or inspection result before expanding scope.

## Smoke test

**not run**. No run is recorded.

## Security, privacy and licensing

- Drives real pages in Playwright Chromium with clicks and scrolling to record footage; point it only at pages you control or trust.
- Recording real product pages can capture logged-in data shown on screen.

**Software license** PolyForm Noncommercial License 1.0.0.

**Commercial use** Commercial use is not permitted under the free license. 'onetake Pro' (onetakemotion.com) sells a commercial license plus every film's source for US$79 one time. Case films' source code is not included in the repo.

## Evidence quotes

| Field | Upstream wording and file |
| --- | --- |
| hardware | 'A WebGL comp renders with --gpu (Chromium on ANGLE/Metal)' and 'SwiftShader costs ~4x' (SKILL.md) |
| installation | 'git clone https://github.com/feitangyuan/onetake.git ~/.claude/skills/onetake' (README.md) |
| license | 'Required Notice: Copyright (c) 2026 Patrick. onetake is free for noncommercial use only.' (LICENSE) |
| model_license | Not a model tool (README.md) |
| inputs | 'the UI is rebuilt in HTML from screenshots instead of screen-recorded' (SKILL.md frontmatter) |
| outputs | '1080p30 draft by default, --final 4K60' (SKILL.md, render.py row) |
| renderer | 'without HyperFrames or Remotion. A single HTML composition where every value is a pure function of time' (SKILL.md) |
