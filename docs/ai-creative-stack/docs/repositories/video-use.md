# Video Use

Use for agent-driven shell editing with approved transcription access.

> Video composition and post-production · Source B · smoke test: **not run**

## Evidence and maintenance

- [Canonical reference](https://github.com/browser-use/video-use)
- Verified 2026-11-26 against default branch `main` at [`43cfc5668335`](https://github.com/browser-use/video-use/commit/43cfc566833548093455c9d4a46bd69913b7e552).
- GitHub reports archive state **false** and a repository push at `2026-10-08T22:17:01Z`. Push activity is a maintenance signal, not a quality rating.
- Attribution: Provisional. Sources A and B were recovered from likely matching mirrored posts; the posts themselves were not readable here. The A/B split follows the order of the seed list (simlish README) and catalogue v1.

- [README.md](https://github.com/browser-use/video-use/blob/43cfc566833548093455c9d4a46bd69913b7e552/README.md)
- [LICENSE](https://github.com/browser-use/video-use/blob/43cfc566833548093455c9d4a46bd69913b7e552/LICENSE)
- [pyproject.toml](https://github.com/browser-use/video-use/blob/43cfc566833548093455c9d4a46bd69913b7e552/pyproject.toml)

## Runtime, hardware and setup

- **Type** skill and Python editing workflow. Primary language Python.
- **Platforms** Unverified.
- **Runtime** Python via uv and FFmpeg. yt-dlp optional.
- **Execution** local or hosted.
- **Agent paths** Claude Code, Codex, Hermes, OpenClaw. Client claims describe documentation and remain untested here unless the smoke test says otherwise.
- **Configuration** Register the reviewed skill with the host and inject ELEVENLABS_API_KEY privately.
- **Credentials and services** ElevenLabs API key for documented transcription setup.

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
uv sync
```

## Contracts and selection

| Boundary | Contract |
| --- | --- |
| Input | Raw footage and edit brief |
| Output | Edited final.mp4 and analysis artifacts |
| Primary | Video editing |
| Supporting | Media processing |

Skip if speech data cannot be submitted to a remote provider. Consider [scarlet](scarlet.md). Complementary tools include [ffmpeg](ffmpeg.md), [hyperframes](hyperframes.md), [remotion](remotion.md), [video-shotcraft](video-shotcraft.md).

The pinned README documents FFmpeg processing and animation overlays generated with HyperFrames or Remotion.

## Craft notes

- The agent reads footage instead of watching it: a word-level transcript plus filmstrip and waveform images on demand.
- Generates animation overlays with HyperFrames, Remotion, Manim or PIL in parallel sub-agents, and checks every cut boundary of the render before showing it. Transcription uses ElevenLabs.

## Examples

1. **Independent** Use consented footage, review proposed cuts against its transcript and preview before export.
2. **Combined** Pass final.mp4 to ffprobe for delivery checks. The upstream workflow already uses FFmpeg.

For both, save the inputs and output evidence with the selected version. Use a small authorized fixture first and review the actual render or inspection result before expanding scope.

## Smoke test

**not run**. No run is recorded.

## Security, privacy and licensing

- Review clips sent to transcription, permission to download source media and credential handling.
- Audio is sent to ElevenLabs for transcription. Footage frames reach the agent's model provider when inspected.

**Software license** MIT.

**Commercial use** Preserve applicable license and notice obligations. Verify the rights to bundled or downloaded assets, services and generated inputs separately.
