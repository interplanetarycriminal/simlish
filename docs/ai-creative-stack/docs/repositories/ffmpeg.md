# FFmpeg

Use for inspectable media transforms and delivery encoding.

> Video composition and post-production · Source B · smoke test: **passed**

## Evidence and maintenance

- [Canonical reference](https://github.com/FFmpeg/FFmpeg)
- Verified 2026-11-26 against default branch `master` at [`17de9f85972c`](https://github.com/FFmpeg/FFmpeg/commit/17de9f85972c89b5dd81378bea7b80b67b3af7f0).
- GitHub reports archive state **false** and a repository push at `2026-11-26T04:21:56Z`. Push activity is a maintenance signal, not a quality rating.
- Attribution: Provisional. Sources A and B were recovered from likely matching mirrored posts; the posts themselves were not readable here. The A/B split follows the order of the seed list (simlish README) and catalogue v1.

- [README.md](https://github.com/FFmpeg/FFmpeg/blob/17de9f85972c89b5dd81378bea7b80b67b3af7f0/README.md)
- [LICENSE.md](https://github.com/FFmpeg/FFmpeg/blob/17de9f85972c89b5dd81378bea7b80b67b3af7f0/LICENSE.md)

## Runtime, hardware and setup

- **Type** CLI and media libraries. Primary language C.
- **Platforms** Platform-specific packaged builds, C build environment.
- **Runtime** C toolchain for builds, or supported packaged binary
- **Execution** local.
- **Agent paths** Generic coding agent via shell. Client claims describe documentation and remain untested here unless the smoke test says otherwise.
- **Configuration** Set explicit stream mappings and choose codecs or stream copy for the target container.
- **Credentials and services** No API key for local media.

| Hardware | Documented value |
| --- | --- |
| GPU | unverified |
| Minimum VRAM | Not documented |
| Recommended VRAM | Not documented |
| System RAM | Not documented |
| Storage | Not documented |
| CPU fallback | not applicable |
| Training versus inference | Not documented |

Review the source and pin the version before running the upstream-documented command. It was read in the pinned documentation; execution is recorded only under Smoke test.

```sh
Use an approved packaged build or the compilation instructions linked from upstream. Confirm the features with ffmpeg -buildconf.
```

## Contracts and selection

| Boundary | Contract |
| --- | --- |
| Input | Media files, image sequences or streams |
| Output | Encoded, filtered, muxed or measured media |
| Primary | Media processing |
| Supporting | Video editing |

Skip re-encode when a compatible stream copy covers the request. Consider the existing project toolchain. Complementary tools include [hyperframes](hyperframes.md), [remotion](remotion.md), [motion-canvas](motion-canvas.md), [scarlet](scarlet.md), [video-use](video-use.md), [real-esrgan](real-esrgan.md), [line-art-animation](line-art-animation.md), [video-shotcraft](video-shotcraft.md), [huashu-motion](huashu-motion.md), [anything2explainer](anything2explainer.md), [openscreen](openscreen.md), [onetake](onetake.md), [lemo-opuscar](lemo-opuscar.md), [remotion-skills](remotion-skills.md).

No native integration with catalogue peers is asserted. Examples using another tool are proposed handoffs.

## Craft notes

- The delivery boundary for every route in this catalogue: encode, remux, filter and probe.
- Use ffprobe -count_frames to verify frame counts, and set -framerate explicitly when encoding numbered frames. Build flags decide licensing: enabling libx264 makes the build GPL.

## Examples

1. **Independent** Inspect a file using ffprobe and check dimensions, frame rates, duration and codecs.
2. **Combined** Inspect output from one compositor, then remux if the target container supports both codecs.

For both, save the inputs and output evidence with the selected version. Use a small authorized fixture first and review the actual render or inspection result before expanding scope.

## Smoke test

**passed**. FFmpeg 7.1: docs/examples/media-delivery.md fixture (640x360, 24 fps, 48 frames, 2.0 s) and the seekable-scene encode (600 frames, 1280x720, 30 fps).

## Security, privacy and licensing

- Review binary build options, codec licensing and untrusted media parsing. Keep input and output paths separate.
- No external service in the documented base workflow.

**Software license** LGPL-2.1-or-later baseline; build-dependent.

**Commercial use** Inspect the exact distribution build flags. GPL and nonfree options change redistribution terms. Codec patent obligations vary by use and jurisdiction.
