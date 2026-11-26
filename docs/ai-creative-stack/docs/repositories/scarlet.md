# Scarlet

Use when a human needs a desktop editing timeline alongside an agent.

> Video composition and post-production · Source B · smoke test: **not run**

## Evidence and maintenance

- [Canonical reference](https://github.com/Forward-Future/scarlet)
- Verified 2026-11-26 against default branch `main` at [`fcb077e0eef0`](https://github.com/Forward-Future/scarlet/commit/fcb077e0eef08922226fdd43f50077267fc3e2b4).
- GitHub reports archive state **false** and a repository push at `2026-11-26T06:11:45Z`. Push activity is a maintenance signal, not a quality rating.
- Attribution: Provisional. Sources A and B were recovered from likely matching mirrored posts; the posts themselves were not readable here. The A/B split follows the order of the seed list (simlish README) and catalogue v1.

- [README.md](https://github.com/Forward-Future/scarlet/blob/fcb077e0eef08922226fdd43f50077267fc3e2b4/README.md)
- [LICENSE](https://github.com/Forward-Future/scarlet/blob/fcb077e0eef08922226fdd43f50077267fc3e2b4/LICENSE)
- [package.json](https://github.com/Forward-Future/scarlet/blob/fcb077e0eef08922226fdd43f50077267fc3e2b4/package.json)

## Runtime, hardware and setup

- **Type** desktop video editor. Primary language TypeScript.
- **Platforms** macOS, Windows, Ubuntu 24.04 x86-64 preview.
- **Runtime** macOS and Windows, with a separate Ubuntu 24.04 preview. Source tooling includes pnpm, CMake and local media helpers.
- **Execution** local or hosted.
- **Agent paths** Claude Code, Codex. Client claims describe documentation and remain untested here unless the smoke test says otherwise.
- **Configuration** Connect the approved agent through Settings → General and duplicate the timeline before experimentation.
- **Credentials and services** Existing agent subscription for AI editing per upstream.

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
Use the desktop release linked from upstream. Linux preview is separate from the standard macOS and Windows release.
```

## Contracts and selection

| Boundary | Contract |
| --- | --- |
| Input | Footage and editing instructions |
| Output | Edited timeline and exported media |
| Primary | Video editing |
| Supporting | Animation |

Skip for headless-only delivery or if agent access to original footage is restricted. Consider [video-use](video-use.md), [hyperframes](hyperframes.md). Complementary tools include [ffmpeg](ffmpeg.md).

The pinned README documents /motion-graphics rendering HTML to transparent ProRes 4444 through bundled headless Chrome, and edits through Claude Code or Codex over MCP.

## Craft notes

- A desktop editor where Claude Code or Codex edits the cut list over MCP and Scarlet re-renders only the affected seconds. Target an edit by voice, text or drawing on the frame.
- Built-in workflows include /dialogue-pass, /add-captions and /motion-graphics, which renders HTML, CSS and JavaScript to transparent ProRes 4444 through bundled headless Chrome.

## Examples

1. **Independent** Open a sample clip, review an agent-suggested cut and export a preview.
2. **Combined** Export a reviewed master and use FFmpeg to check streams and remux for delivery.

For both, save the inputs and output evidence with the selected version. Use a small authorized fixture first and review the actual render or inspection result before expanding scope.

## Smoke test

**not run**. No run is recorded.

## Security, privacy and licensing

- Review app downloads, agent permissions, and media data boundaries.
- The connected agent (Claude Code or Codex) receives transcripts and frame markups.

**Software license** MIT.

**Commercial use** Preserve applicable license and notice obligations. Verify the rights to bundled or downloaded assets, services and generated inputs separately.
