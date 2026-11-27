# Artifact contracts

What each stage of a game hands to the next. A contract names the file, the fields that must be filled and who owns it. A downstream step reads the contract, never the upstream tool's private state.

These contracts are **proposed** catalogue guidance. No schema for them exists in [registry/contracts](../../registry/contracts/) yet. The fields are drawn from what [fixtures/game-dev](../../fixtures/game-dev/README.md) needed to record its **tested** results. Use `null` for an unknown value, never a guess.

| Artifact | File (suggested) | Owner | Read by |
| --- | --- | --- | --- |
| [Game design document](#game-design-document) | `GAME.md` | Creative owner | Every stage |
| [Asset manifest](#asset-manifest) | `asset-manifest.json` per asset | Asset author | Engine import, delivery |
| [Level](#level) | `levels/<id>.json` plus a level note | Level designer | Engine, playtest |
| [Audio](#audio) | `audio-manifest.json` | Sound owner | Engine, delivery |
| [Narrative](#narrative) | `story/*.ink` plus compiled JSON | Writer | Story runtime, playtest |
| [Multiplayer](#multiplayer) | `NETWORK.md` plus message schemas | Server owner | Client, server, tests |
| [Delivery](#delivery) | `release-manifest.json` | Release owner | Owner sign-off |

## Game design document

One file, one authority. Change it before the code changes, not after.

| Field | Example | Why |
| --- | --- | --- |
| Platforms and input | Web desktop and mobile; keyboard, touch | Drives engine and control choices |
| Core loop | Run, jump, collect, reach the exit | What the slice must prove |
| Runtime and pinned version | Phaser 4.2.1 | One runtime per game |
| Physics | Arcade, 1/60 s fixed step, pixels, collision matrix | One solver per world |
| Vertical slice acceptance | Controls, core loop, one level, start to finish, no blocking bugs, playtest notes from 3 players | The gate before more content |
| Scope cuts | What will not be built | Keeps the slice small |
| Performance budget | Target device, frame time, load time, bundle size | Measured at delivery |
| Accessibility | Remappable keys, mute, readable text, no flashing beyond limits | Checked at delivery |
| Rights | Who owns art, audio, fonts, code; third-party licenses | Required by the delivery gate |
| Online play | None, or a link to `NETWORK.md` | Optional stage |

Write acceptance criteria as observable checks, the way the fixture does: "the player lands on the platform", "a coin overlap adds 1 to the score", "a reload gives the same state trace".

## Asset manifest

Use the catalogue's [asset manifest template](../../templates/asset-manifest.json) for every model, sprite sheet and tileset. For game assets, fill these in addition to its core keys:

| Field | Sprites and tiles | Models |
| --- | --- | --- |
| Source file | `.pxo`, `.aseprite`, pixelfx effect id and options | `.blend`, `.bbmodel` |
| Export command and tool version | Pixelorama CLI flags, or `node tools/render.mjs <id> --sheet` | Blender or Blockbench export settings |
| Runtime file and hash | PNG sheet plus frame JSON | GLB |
| Frame size, frame count, durations, tags | Required | — |
| Pivot | Per animation | Model origin |
| Filtering | Nearest, no mipmaps | — |
| Scale | Pixels per world unit | Meters; bounding box after import |
| Collision shape | Shape and offset per frame or per sprite | Collider type |
| Clip names and durations | Tags | Animation clips as the engine reports them |
| Engine import check | Screenshot and result | Bounding box, bones, clips |

## Level

| Field | Notes |
| --- | --- |
| Source | `.ldtk` file and LDtk version; JSON format 1.5.3 at the pinned commit |
| Runtime export | `.ldtk` JSON, per-level `.ldtkl`, or Super Simple PNG and CSV |
| Loader | Engine importer, or a reviewed adapter with its version and commit |
| Layers | Names and types (tiles, auto-tiles, IntGrid, entities) |
| Counts | Tiles, IntGrid cells and entities per layer, before and after import |
| Collision source | Which IntGrid values or tiles are solid |
| Entities | Type, fields, required fields, spawn point |
| Playtest | Time to complete, where players got stuck |

## Audio

| Field | Notes |
| --- | --- |
| Owner | Engine audio or Howler.js (one per game) |
| Source per sound | jsfxr preset or parameter JSON plus seed; or the recording and its rights |
| Runtime file | Path, codec, sample rate, channels, duration (from `ffprobe`), hash |
| Level | RMS and peak; clipped samples |
| Use | The game event that plays it |
| Unlock | How audio is unlocked on the web (first input) |
| Volume groups | Music, effects, master; mute |

The fixture's jsfxr record has this shape: preset `jump`, seed 7, `pcm_s16le`, 44100 Hz, 1 channel, 0.312 s, RMS −12.2 dBFS, reproducible.

## Narrative

| Field | Notes |
| --- | --- |
| Source | `.ink` files and their `INCLUDE` list |
| Compiler and version | inklecate (with .NET version) or `inkjs/full` and version |
| Compiled JSON | Path and hash |
| Runtime and version | C# runtime or inkjs, one per game |
| Story version | Stored in every save |
| Variables the game reads or writes | Name, type, owner (story or game) |
| External functions | Name and what the game does |
| Endings | Names, and a test path that reaches each |
| Save format | Story state plus game state in one save |
| Test record | Compile errors, paths walked, endings reached, save and restore result |

## Multiplayer

Keep this in `NETWORK.md` next to the message schemas.

| Field | Notes |
| --- | --- |
| Server | Colyseus or Nakama, with versions |
| Authority matrix | For each piece of state (position, health, score, inventory, match timer): who owns it, who may request a change, how it is validated |
| Protocol version | Integer sent on join; bumped on any schema change |
| Tick rate | Server tick and physics step |
| Message schema | Every client-to-server message: name, fields, types, ranges, rate limit |
| State schema | What is synced to clients and how often |
| Authentication | How a player is identified before joining |
| Reconnect | Hold time and token handling |
| Rate limits | Per message and per client |
| Bind address and exposure | 127.0.0.1 by default; any public exposure and its written authorization |
| Data collected | None by default; any telemetry or analytics and its authorization |
| Test record | Two clients, invalid input, flooding, reconnect, version mismatch, latency and loss |

Example authority matrix row: `player.x` is owned by the server; the client may send `move {dx}` with `dx` in −1..1 at most 30 times a second; the server clamps to one step per tick.

## Delivery

| Field | Notes |
| --- | --- |
| Builds | One per target platform: file, size, hash, engine and export template versions |
| Build command | The exact command, run from a clean checkout and lockfile |
| Smoke test per build | Opened, played through the slice, result |
| Automated checks | Physics, input, story, audio and network checks with their evidence files |
| Playtest notes | Who played (role, not personal data), what they did, where they got stuck |
| Performance | Frame time and load time on the target device |
| Accessibility | Results for the design document's accessibility list |
| Rights | Every asset, font, sound and library license; third-party branding not reused (for example the Phaser logo and characters) |
| Trailer (optional) | Source capture, edit and encodes, made from real gameplay |
| Blocked checks | Named, with the reason |

Record gate outcomes with the [quality gates](../../QUALITY_GATES.md) and the [execution report](../../templates/execution-report.md).

Back to [game development](README.md).
