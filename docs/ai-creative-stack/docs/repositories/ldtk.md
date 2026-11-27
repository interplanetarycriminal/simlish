# LDtk (Level Designer Toolkit)

Use for designing 2D game levels with tile, auto-tile, IntGrid and entity layers, and exporting them as documented JSON or simple PNG/CSV files for any engine.

> #52 · Game development · Source E (games) · smoke test: **not run**

## Evidence and maintenance

- [Canonical reference](https://github.com/deepnight/ldtk)
- Verified 2026-11-27 against default branch `master` at [`2b7b5512f2f8`](https://github.com/deepnight/ldtk/commit/2b7b5512f2f88fa281cb6492debbb26ead7838d4).
- GitHub reports archive state **false** and a repository push at `2026-11-24T17:02:03Z`. Push activity is a maintenance signal, not a quality rating.
- Attribution: Listed in the game-development post (source E, transcript supplied by the user on 2026-11-27).

- [README.md](https://github.com/deepnight/ldtk/blob/2b7b5512f2f88fa281cb6492debbb26ead7838d4/README.md)
- [JSON_DOC.md](https://github.com/deepnight/ldtk/blob/2b7b5512f2f88fa281cb6492debbb26ead7838d4/docs/JSON_DOC.md)
- [CHANGELOG.md](https://github.com/deepnight/ldtk/blob/2b7b5512f2f88fa281cb6492debbb26ead7838d4/docs/CHANGELOG.md)
- [package.json](https://github.com/deepnight/ldtk/blob/2b7b5512f2f88fa281cb6492debbb26ead7838d4/app/package.json)
- [electron-builder.json](https://github.com/deepnight/ldtk/blob/2b7b5512f2f88fa281cb6492debbb26ead7838d4/app/electron-builder.json)
- [LICENSE](https://github.com/deepnight/ldtk/blob/2b7b5512f2f88fa281cb6492debbb26ead7838d4/LICENSE)

## Runtime, hardware and setup

- **Type** application. Primary language Haxe.
- **Platforms** Windows, Linux, macOS.
- **Runtime** Prebuilt Electron app (Electron ^24.1.2) from ldtk.io. Building from source needs an up-to-date Haxe compiler and NPM (Node.js). It can also run in NW.js or inside the Hide editor.
- **Execution** local.
- **Agent paths** Generic coding agent via project files. Client claims describe documentation and remain untested here unless the smoke test says otherwise.
- **Configuration** Project settings choose separate level files (.ldtkl), the Super Simple export (PNG per layer, composite PNG, JSON and CSV per level), multi-worlds and world layout.
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
| Notes | No hardware requirements are stated. |

Review the source and pin the version before running the upstream-documented command. It was read in the pinned documentation; execution is recorded only under Smoke test.

```sh
Get the latest version from https://ldtk.io. From source: haxe setup.hxml; cd app; npm i; haxe main.debug.hxml; haxe renderer.debug.hxml; npm run start
```

## Contracts and selection

| Boundary | Contract |
| --- | --- |
| Input | tileset images (PNG; Aseprite images are referenced in the changelog), existing .ldtk projects, enum definitions (Haxe enum import; CastleDB enums when embedded in Hide) |
| Output | .ldtk project JSON (format 1.5.3, JSON schema published), .ldtkl per-level JSON when separate level files are on, Super Simple export: one PNG per layer, a composite PNG per level, an optional simple JSON per level, a CSV per IntGrid layer, Tiled TMX export (mentioned in older changelog entries) |
| Primary | Level design |
| Supporting | Pixel art, Prototyping |

Skip when you need 3D level layout or an in-engine editor; LDtk is a standalone 2D editor and your engine still needs a loader for its JSON. Consider the existing project toolchain. Complementary tools include [godot](godot.md), [phaser](phaser.md), [bevy](bevy.md), [pixelorama](pixelorama.md), [pixelfx](pixelfx.md), [godot-mcp](godot-mcp.md).

## Craft notes

- The JSON format is documented field by field (JSON_DOC.md, version 1.5.3) with a JSON schema and QuickType-generated parsers for C++, C#, Go, JavaScript, Python and Rust.
- Super Simple export writes a PNG per layer, a composite PNG and a CSV per IntGrid layer, so a game can load levels without writing a full importer.
- The pinned repository names only the Haxe API as an official loader; it does not list Godot or Phaser importers, and older importers may break on multi-world projects.

## Examples

1. **Independent** Lay out a 10-room GridVania world with an auto-tiled IntGrid layer and export it with separate .ldtkl level files.
2. **Combined** Proposed handoff: export LDtk Super Simple PNGs and CSVs and load them into a Phaser scene as background images and collision grids.

For both, save the inputs and output evidence with the selected version. Use a small authorized fixture first and review the actual render or inspection result before expanding scope.

## Smoke test

**not run**. No run is recorded.

## Security, privacy and licensing

- Desktop Electron app; open project files only from sources you trust.
- The pinned files describe no telemetry.

**Software license** MIT.

**Commercial use** MIT license: commercial use is allowed with the copyright notice kept. Sample tileset images have their own terms (see app/extraFiles/samples/README.md).

## Evidence quotes

| Field | Upstream wording and file |
| --- | --- |
| hardware | Not stated in README.md. |
| installation | 'Visit LDtk.io to get latest version.' and '`haxe setup.hxml`' (README.md) |
| license | 'MIT License Copyright (c) 2020, Sébastien Benard - Deepnight Games' (LICENSE) |
| model_license | Not a model tool. |
| inputs | 'Added an error message when exporting to Tiled while having unsupported Aseprite images.' (docs/CHANGELOG.md) |
| outputs | 'One PNG per layer in each level ... A very simple ... JSON file per level' (docs/CHANGELOG.md, 1.1.0) |
| json_format | '# LDtk Json structure (version 1.5.3)' (docs/JSON_DOC.md) |
| ldtkl | 'level data is stored in separate standalone `.ldtkl` files (one per level)' (docs/JSON_DOC.md) |
| platforms | scripts 'pack-win', 'pack-macos', 'pack-linux-x86', 'pack-linux-arm64' (app/package.json) |
