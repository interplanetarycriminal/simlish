# Pixelorama

Use for drawing and animating pixel art sprites and tilesets, then exporting PNG sprite sheets, GIF/APNG, Aseprite files or video for a game engine.

> #50 · Game development · Source E (games) · smoke test: **not run**

## Evidence and maintenance

- [Canonical reference](https://github.com/Orama-Interactive/Pixelorama)
- Verified 2026-11-27 against default branch `master` at [`9d8823a7bb1d`](https://github.com/Orama-Interactive/Pixelorama/commit/9d8823a7bb1ddaf5ea23fe0c4bc640de770cea7a).
- GitHub reports archive state **false** and a repository push at `2026-11-27T00:57:45Z`. Push activity is a maintenance signal, not a quality rating.
- Attribution: Listed in the game-development post (source E, transcript supplied by the user on 2026-11-27).

- [README.md](https://github.com/Orama-Interactive/Pixelorama/blob/9d8823a7bb1ddaf5ea23fe0c4bc640de770cea7a/README.md)
- [Export.gd](https://github.com/Orama-Interactive/Pixelorama/blob/9d8823a7bb1ddaf5ea23fe0c4bc640de770cea7a/src/Autoload/Export.gd)
- [OpenSave.gd](https://github.com/Orama-Interactive/Pixelorama/blob/9d8823a7bb1ddaf5ea23fe0c4bc640de770cea7a/src/Autoload/OpenSave.gd)
- [Main.gd](https://github.com/Orama-Interactive/Pixelorama/blob/9d8823a7bb1ddaf5ea23fe0c4bc640de770cea7a/src/Main.gd)

## Runtime, hardware and setup

- **Type** application. Primary language GDScript.
- **Platforms** Windows, Linux, macOS.
- **Runtime** Prebuilt app for Windows, Linux, macOS and a Web build. Running from source needs Godot 4.7.1 (older versions will not work). Video export (MP4, AVI, OGV, MKV, WebM) needs FFMPEG installed.
- **Execution** local.
- **Agent paths** Generic coding agent via project files. Client claims describe documentation and remain untested here unless the smoke test says otherwise.
- **Configuration** Export settings (format, scale, frame range, tag, direction, sheet layout, optional JSON) are set in the Export dialog or by command-line flags such as --export, --spritesheet, --output, --scale, --tag and --json.
- **Credentials and services** None.

| Hardware | Documented value |
| --- | --- |
| GPU | unverified |
| Minimum VRAM | Not documented |
| Recommended VRAM | Not documented |
| System RAM | Not documented |
| Storage | Not documented |
| CPU fallback | not documented |
| Training versus inference | Not documented |
| Notes | No hardware requirements are stated. It is a Godot desktop and web app. |

Review the source and pin the version before running the upstream-documented command. It was read in the pinned documentation; execution is recorded only under Smoke test.

```sh
winget install pixelorama
```

## Contracts and selection

| Boundary | Contract |
| --- | --- |
| Input | .pxo Pixelorama projects, PNG and other images, .aseprite/.ase, .kra (Krita), .ora (OpenRaster), .psd, .piskel, .gpl palettes, glTF/GLB models for 3D layers, audio for timeline sync |
| Output | PNG, WebP, JPEG, SVG, EXR, GIF, APNG, .aseprite, MP4/AVI/OGV/MKV/WebM (via FFMPEG), PNG sprite sheets (columns, rows, or one row/column per tag), optional JSON of the serialized project data, .pxo projects |
| Primary | Pixel art, Animation |
| Supporting | Illustration, Level design, Visual effects |

Skip when you need hand-coded, parametric effects that render headlessly in Node; pixelfx fits that better. Consider the existing project toolchain. Complementary tools include [ldtk](ldtk.md), [godot](godot.md), [phaser](phaser.md), [pixelfx](pixelfx.md), [jsfxr](jsfxr.md), [godot-mcp](godot-mcp.md), [bevy](bevy.md), [blockbench](blockbench.md).

- The JSON export is Pixelorama's own serialized project data, not an Aseprite-style atlas, so engines that expect Aseprite JSON need the .aseprite export or a converter.

## Craft notes

- Built for pixel art: perfect pixel lines, indexed mode, and pixel-aware rotation and scaling (cleanEdge, OmniScale, rotxel).
- Tilemap layers support rectangular, isometric and hexagonal tiles, and layers, frames and cels can carry custom user metadata for game pipelines.
- Batch export is scriptable from the command line (--export, --spritesheet, --frames, --tag, --split-layers, --json), but video formats fail unless FFMPEG is installed.

## Examples

1. **Independent** Animate a 12-frame walk cycle with onion skinning and export it as a PNG sprite sheet with one row per animation tag.
2. **Combined** Proposed handoff: draw a tileset in Pixelorama's tilemap layer, export it as PNG, and lay out levels with it in LDtk.

For both, save the inputs and output evidence with the selected version. Use a small authorized fixture first and review the actual render or inspection result before expanding scope.

## Smoke test

**not run**. No run is recorded.

## Security, privacy and licensing

- Extensions are community-made code that runs inside the app; review them before installing.
- Runs locally; the pinned files describe no telemetry.

**Software license** MIT.

**Commercial use** MIT license: commercial use, modification and redistribution are allowed with the copyright notice kept. Bundled addons (for example gdgifexporter) carry their own LICENSE files.

## Evidence quotes

| Field | Upstream wording and file |
| --- | --- |
| hardware | No hardware section; README: 'Available on Windows, Linux, macOS and the Web' (repo description / README). |
| installation | 'WinGet (Windows) - `winget install pixelorama`' (README.md) |
| runtime_requirements | 'Pixelorama uses Godot 4.7.1 ... Older versions will not work.' (README.md) |
| license | 'licensed under the MIT license, guaranteeing free updates forever' (README.md) |
| model_license | Not a model tool. |
| inputs | OpenSave.gd branches on file_ext 'pxo', 'ora', 'kra', 'psd', 'piskel' (src/Autoload/OpenSave.gd) |
| outputs | 'enum FileFormat { PNG, WEBP, JPEG, SVG, EXR, GIF, ASE, APNG, MP4, AVI, OGV, MKV, WEBM }' (src/Autoload/Export.gd) |
| json_export | 'var json := JSON.stringify(project.serialize())' (src/Autoload/Export.gd) |
| ffmpeg | 'Video failed to export. Ensure that FFMPEG is installed correctly.' (src/Autoload/Export.gd) |
| cli | '["--export", "-e"] ... Indicates given project should be exported' (src/Main.gd) |
