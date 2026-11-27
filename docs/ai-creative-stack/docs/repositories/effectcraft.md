# EffectCraft

Use for After Effects-style layered motion graphics and compositing (keyframes, 308 effects, 3D cameras and lights, render queue) that an agent can also drive headless through a CLI or MCP server.

> #38 · Motion films, explainers and engines · Source D (cinema) · smoke test: **not run**

## Evidence and maintenance

- [Canonical reference](https://github.com/storytold/effectcraft)
- Verified 2026-11-26 against default branch `main` at [`ff41f29c6a6e`](https://github.com/storytold/effectcraft/commit/ff41f29c6a6e60e7c09ba4298527b9c540c62c87).
- GitHub reports archive state **false** and a repository push at `2026-11-26T09:07:58Z`. Push activity is a maintenance signal, not a quality rating.
- Attribution: Listed in the cinematic post (source D, transcript supplied by the user on 2026-11-26); first added to this catalogue on 2026-11-26.

- [README.md](https://github.com/storytold/effectcraft/blob/ff41f29c6a6e60e7c09ba4298527b9c540c62c87/README.md)
- [agents.md](https://github.com/storytold/effectcraft/blob/ff41f29c6a6e60e7c09ba4298527b9c540c62c87/docs/agents.md)
- [architecture.md](https://github.com/storytold/effectcraft/blob/ff41f29c6a6e60e7c09ba4298527b9c540c62c87/docs/architecture.md)
- [footage.md](https://github.com/storytold/effectcraft/blob/ff41f29c6a6e60e7c09ba4298527b9c540c62c87/docs/footage.md)
- [Cargo.toml](https://github.com/storytold/effectcraft/blob/ff41f29c6a6e60e7c09ba4298527b9c540c62c87/crates/gpu/Cargo.toml)
- [Cargo.toml](https://github.com/storytold/effectcraft/blob/ff41f29c6a6e60e7c09ba4298527b9c540c62c87/crates/aep/Cargo.toml)

## Runtime, hardware and setup

- **Type** application. Primary language Rust.
- **Platforms** Linux, Windows, macOS.
- **Runtime** Prebuilt installers (universal macOS; Windows x64, x86, ARM64; Linux x86_64, aarch64, riscv64; FreeBSD; WebAssembly build). Building from source needs Rust 1.95+. No FFmpeg needed.
- **Execution** local.
- **Agent paths** Claude Code, Other MCP clients. Client claims describe documentation and remain untested here unless the smoke test says otherwise.
- **Configuration** Register the MCP server with 'claude mcp add effectcraft -- effectcraft-cli mcp' (headless) or add '--bridge 9877' to drive a running app started with 'effectcraft --control 9877'; the repo ships a ready .mcp.json.
- **Credentials and services** None; the README says no telemetry and no network access unless you ask for it.

| Hardware | Documented value |
| --- | --- |
| GPU | Optional wgpu GPU compositor (Metal, Vulkan, Direct3D 12, WebGPU); the CPU renderer is the reference |
| Minimum VRAM | Not documented |
| Recommended VRAM | Not documented |
| System RAM | Not documented |
| Storage | Optional model downloads: MobileSAM for Roto Brush (40 MB), MediaPipe Face Landmarker (3.8 MB) |
| CPU fallback | documented |
| Training versus inference | Not documented |
| Notes | Project setting chooses GPU acceleration (default) or Software Rendering; headless MCP uses the GPU compositor only with --gpu. macOS is the most tested platform. |

Review the source and pin the version before running the upstream-documented command. It was read in the pinned documentation; execution is recorded only under Smoke test.

```sh
git clone https://github.com/storytold/effectcraft
cd effectcraft
cargo run --release -p effectcraft
cargo run --release -p effectcraft-cli -- render --out intro.mp4
```

## Contracts and selection

| Boundary | Contract |
| --- | --- |
| Input | Footage and stills (PNG, JPEG, TIFF, OpenEXR incl. multi-layer, BMP, WebP sequences; MOV), PSD, SVG and PDF documents, Lottie .json / .lottie, glTF/GLB and OBJ/MTL models, .ecproj projects (versioned JSON), .aep/.aepx and timeline interchange (FCP7 XML, FCPXML, OTIO, EDL, AAF, OMF) per architecture docs |
| Output | H.264 MP4, ProRes MOV (Proxy to 4444 XQ with alpha), HEVC and AV1 MP4, WebM (VP9 with alpha, or AV1; Opus audio), PNG, JPEG, TIFF, Targa and 32-bit EXR sequences, Animated GIF, WAV/AIFF, Lottie .json / .lottie, .ecproj |
| Primary | Visual effects, Animation, Video composition |
| Supporting | 3D rendering, Media processing |

Skip when the job is production client work needing proven fidelity; the README calls it alpha and not yet recommended for that. Consider [motion-canvas](motion-canvas.md), [remotion](remotion.md), [hyperframes](hyperframes.md). Complementary tools include [blender-mcp](blender-mcp.md), [real-esrgan](real-esrgan.md).

effectcraft-cli with JSON output and an MCP server over stdio.

- Skip if you rely on After Effects SDK plug-ins; they are not supported.

## Craft notes

- Mirrors After Effects conventions closely: property shortcuts (A, P, S, R, T...), Graph Editor, expressions with wiggle/loopOut/thisComp, puppet pins, 38 blend modes and nine layer styles.
- All codecs are pure Rust (H.264, ProRes, HEVC, VP9, AV1, AAC, Opus); no FFmpeg inside, and the same render queue runs from the CLI.
- Docs disagree on project formats: the README says proprietary project formats are not supported, while docs/architecture.md describes an 'aep' crate that imports and exports .aep with a report of what is not carried over.

## Examples

1. **Independent** Run 'effectcraft-cli set Main '#1' transform/position '[100,360]' --time 0 main.ecproj --save' then 'effectcraft-cli render --comp Main --out main.mp4'.
2. **Combined** Proposed handoff: export a GLB from blender-mcp and import it into an EffectCraft Advanced 3D composition with cameras, lights and title layers.

For both, save the inputs and output evidence with the selected version. Use a small authorized fixture first and review the actual render or inspection result before expanding scope.

## Smoke test

**not run**. No run is recorded.

## Security, privacy and licensing

- The control channel ('--control 9877') accepts JSON lines that can run any command and click any widget; keep it local.
- Windows installers and executables are code-signed; macOS builds are signed and notarized.
- No telemetry and no network access unless you request it (for example the optional Roto Brush and face-tracking model downloads).

**Software license** MIT OR Apache-2.0 (dual, at your option); ArtCraft name and logos are trademarks under a separate brand license.

**Commercial use** MIT/Apache-2.0 permit commercial use. Forks must remove ArtCraft brand assets. The README says it is alpha and not yet recommended for production client work (about 45% of the way to full professional readiness).

## Evidence quotes

| Field | Upstream wording and file |
| --- | --- |
| hardware | 'The GPU compositor and GPU effects on wgpu compute shaders (Metal, Vulkan, Direct3D 12, WebGPU), checked against the CPU renderer' (docs/architecture.md) |
| installation | 'cargo run --release -p effectcraft' (README.md) |
| license | 'dual-licensed under MIT or Apache-2.0, at your option' (README.md) |
| model_license | Not a model tool; optional MobileSAM and MediaPipe downloads (README.md) |
| inputs | 'Stills of any format EffectCraft reads can form a sequence: PNG, JPEG, TIFF, OpenEXR, BMP and WebP' (docs/footage.md) |
| outputs | 'H.264 MP4 and ProRes MOV (Proxy to 4444 XQ with alpha) with audio, HEVC ... and AV1 MP4' (README.md) |
| agents | 'effectcraft-cli mcp speaks the Model Context Protocol over stdio, headless or bridged' (README.md) |
| aep_contradiction | README: 'Proprietary project formats and After Effects SDK plug-ins are not supported'; aep crate: 'import into an EffectCraft project and export back to .aep' |
