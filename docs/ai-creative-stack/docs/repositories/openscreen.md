# OpenScreen

Use for recording a screen or window and turning the take into a polished product demo with auto-zooms, cursor effects, captions and GPU export, by hand or from a coding agent through its CLI and MCP server.

> Motion films, explainers and engines · Added by the user · smoke test: **not run**

## Evidence and maintenance

- [Canonical reference](https://github.com/getopenscreen/openscreen)
- Verified 2026-11-26 against default branch `main` at [`c174dc0669d0`](https://github.com/getopenscreen/openscreen/commit/c174dc0669d070249bc24e2b6c96892bd48514b7).
- GitHub reports archive state **false** and a repository push at `2026-11-26T08:44:58Z`. Push activity is a maintenance signal, not a quality rating.
- Attribution: Added directly by the user on 2026-11-26.

- [README.md](https://github.com/getopenscreen/openscreen/blob/c174dc0669d070249bc24e2b6c96892bd48514b7/README.md)
- [package.json](https://github.com/getopenscreen/openscreen/blob/c174dc0669d070249bc24e2b6c96892bd48514b7/package.json)

## Runtime, hardware and setup

- **Type** application. Primary language TypeScript.
- **Platforms** Linux, Windows, macOS.
- **Runtime** Electron desktop app. Windows 1903+ (build 18362); macOS 13 Ventura+ (ScreenCaptureKit); Linux X11, or Wayland with xdg-desktop-portal and PipeWire (PipeWire also for system audio). Building from source: Node 22.22.1 per package.json engines.
- **Execution** local.
- **Agent paths** Claude Code, Codex, Cursor, MCP clients. Client claims describe documentation and remain untested here unless the smoke test says otherwise.
- **Configuration** Grant Screen Recording and Accessibility on macOS; for agents, register the MCP server with 'claude mcp add openscreen -- "<executable>" mcp'. AI editing needs a provider key you add; nothing is enabled by default.
- **Credentials and services** None for recording, editing or export. The optional AI editing assistant needs your own key for Claude, OpenAI, Gemini, Mistral, OpenRouter, MiniMax or an OpenAI-compatible endpoint.

| Hardware | Documented value |
| --- | --- |
| GPU | GPU-accelerated export (Metal on macOS, D3D11 on Windows, Vulkan on Linux) with automatic CPU fallback |
| Minimum VRAM | Not documented |
| Recommended VRAM | Not documented |
| System RAM | 8 GB |
| Storage | Not documented |
| CPU fallback | documented |
| Training versus inference | Not documented |
| Notes | 8 GB RAM minimum, 16 GB recommended. Windows minimum Intel 8th Gen / AMD Ryzen 2000; recommended Windows 11 with Intel 12th Gen / Ryzen 4000. On ARM64 Windows use the ARM64 build; x64 under emulation records poorly. |

Review the source and pin the version before running the upstream-documented command. It was read in the pinned documentation; execution is recorded only under Smoke test.

```sh
brew install --cask openscreen
winget install --source msstore OpenScreen
nix run github:getopenscreen/openscreen
npx skills add getopenscreen/openscreen --skill openscreen-demo -y
```

## Contracts and selection

| Boundary | Contract |
| --- | --- |
| Input | Whole-screen or window capture, Microphone and system audio, Webcam (picture-in-picture), Background images, .openscreen project JSON (editable by CLI) |
| Output | MP4, GIF, .openscreen project file, Editable transcript and captions |
| Primary | Video editing, Media processing |
| Supporting | Video composition, Shot planning |

Skip when you need a fully synthetic, code-drawn film rather than a recording of a real screen. Consider the existing project toolchain. Complementary tools include [onetake](onetake.md), [huashu-motion](huashu-motion.md), [ffmpeg](ffmpeg.md).

Headless CLI, MCP server and skills let agents drive recording and export.

- Skip if you need a stable project format; the README warns the .openscreen format and CLI may change.

## Craft notes

- Auto-zoom follows the cursor, with cursor smoothing, click effects and post-recording path smoothing, in the Screen Studio style of polished demos.
- Deleting a sentence in the transcript cuts it from the video; the chat assistant applies cuts, zooms, speed ramps and annotations to the timeline.
- Headless CLI ('openscreen record', 'openscreen export') emits NDJSON with --json, so agents can record, edit the project JSON and render without windows.

## Examples

1. **Independent** Run 'openscreen record --duration 20 --project demo.openscreen --json' then 'openscreen export demo.openscreen -o demo.mp4 --json' to attach a feature demo to a PR.
2. **Combined** Proposed handoff: record a real UI walkthrough in OpenScreen, then use it as reference footage for an onetake launch film that rebuilds the UI in HTML.

For both, save the inputs and output evidence with the selected version. Use a small authorized fixture first and review the actual render or inspection result before expanding scope.

## Smoke test

**not run**. No run is recorded.

## Security, privacy and licensing

- The standalone Windows .exe is not code-signed (SmartScreen warning); the Microsoft Store build is signed. Install only from the official Releases, Store or Homebrew cask.
- Needs Screen Recording and Accessibility permissions on macOS; Wayland click capture needs read access to mouse devices via a udev rule or the input group.
- The demo skill drafts an X post but publishes only once you say yes.
- Captions are transcribed on-device with no upload and work offline.
- When AI editing is enabled, edit requests go to the provider whose key you supply.
- Recordings capture everything visible in the chosen screen or window.

**Software license** MIT.

**Commercial use** MIT; the README states it is 100% free for personal and commercial use with nothing behind a paywall.

## Evidence quotes

| Field | Upstream wording and file |
| --- | --- |
| hardware | 'RAM: 8 GB minimum, 16 GB recommended' (README.md) |
| gpu | 'rendered and encoded on the GPU (Metal on macOS, D3D11 on Windows, Vulkan on Linux) with an automatic CPU fallback' (README.md) |
| installation | 'brew install --cask openscreen' (README.md) |
| license | 'This project is licensed under the MIT License' (README.md) |
| model_license | Not a model tool (README.md) |
| inputs | 'Record a specific window, or your whole screen.' and 'Record microphone and system audio.' (README.md) |
| outputs | 'Export to MP4 or GIF in multiple aspect ratios and resolutions' (README.md) |
