# Colyseus

Use for building an authoritative Node.js multiplayer server with rooms, matchmaking and automatic binary state sync to web, Unity, Godot and other clients.

> #56 · Game development · Source E (games) · smoke test: **passed**

## Evidence and maintenance

- [Canonical reference](https://github.com/colyseus/colyseus)
- Verified 2026-11-27 against default branch `master` at [`8ddb8531da21`](https://github.com/colyseus/colyseus/commit/8ddb8531da217eb100054fd8d869cf109cbc72ce).
- GitHub reports archive state **false** and a repository push at `2026-11-25T01:37:33Z`. Push activity is a maintenance signal, not a quality rating.
- Attribution: Listed in the game-development post (source E, transcript supplied by the user on 2026-11-27).

- [README.md](https://github.com/colyseus/colyseus/blob/8ddb8531da217eb100054fd8d869cf109cbc72ce/README.md)
- [package.json](https://github.com/colyseus/colyseus/blob/8ddb8531da217eb100054fd8d869cf109cbc72ce/package.json)
- [package.json](https://github.com/colyseus/colyseus/blob/8ddb8531da217eb100054fd8d869cf109cbc72ce/bundles/colyseus/package.json)
- [package.json](https://github.com/colyseus/colyseus/blob/8ddb8531da217eb100054fd8d869cf109cbc72ce/packages/core/package.json)
- [package.json](https://github.com/colyseus/colyseus/blob/8ddb8531da217eb100054fd8d869cf109cbc72ce/packages/sdk/package.json)

## Runtime, hardware and setup

- **Type** framework. Primary language TypeScript.
- **Platforms** Unverified.
- **Runtime** Node.js >= 22 for the server (colyseus 0.18.12, @colyseus/core 0.18.30, @colyseus/schema ^5.0.8). The TypeScript client @colyseus/sdk 0.18.10 declares Node >= 12. The monorepo uses pnpm >= 8.15.0.
- **Execution** local or hosted.
- **Agent paths** Generic coding agent via project files. Client claims describe documentation and remain untested here unless the smoke test says otherwise.
- **Configuration** Define room classes and a schema state on the server; drivers and presence (Redis, Mongoose, Drizzle) and transports (ws, uWebSockets, Bun websockets, H3) are separate packages.
- **Credentials and services** None to self-host. Colyseus Cloud is an optional paid hosting service.

Review the source and pin the version before running the upstream-documented command. It was read in the pinned documentation; execution is recorded only under Smoke test.

```sh
npm create colyseus-app@latest ./my-server
cd my-server
npm start
```

## Contracts and selection

| Boundary | Contract |
| --- | --- |
| Input | client messages over WebSocket (or other transports), TypeScript room and schema definitions |
| Output | delta-compressed, binary-encoded room state synced to clients, matchmaking and reconnection |
| Primary | Multiplayer |
| Supporting | Game engine |

Skip if you need accounts, leaderboards, storage and social features out of the box; Colyseus focuses on rooms, state sync and matchmaking. Consider [nakama](nakama.md). Complementary tools include [phaser](phaser.md), [godot](godot.md), [react-three-fiber](react-three-fiber.md), [babylonjs](babylonjs.md), [matter-js](matter-js.md), [rapier](rapier.md), [jolt-physics](jolt-physics.md), [ink](ink.md).

## Craft notes

- State defined on the server syncs automatically to all clients, delta-compressed and binary-encoded through @colyseus/schema.
- Client SDKs listed: TypeScript (@colyseus/sdk), React (@colyseus/react), Unity, Godot, GameMaker, Defold, Construct, Haxe and a C static library.
- The README claims scaling from 10 to 10,000+ CCU with Redis and load balancers; version 1.0 is still on the public roadmap (current 0.18.x).

## Examples

1. **Independent** Scaffold a room-based server with npm create colyseus-app and sync player positions for a four-player match.
2. **Combined** Proposed handoff: run a Colyseus room for a react-three-fiber racing prototype using the @colyseus/react client.

For both, save the inputs and output evidence with the selected version. Use a small authorized fixture first and review the actual render or inspection result before expanding scope.

## Smoke test

**passed**. fixtures/game-dev colyseus-room: @colyseus/core 0.18.30 on 127.0.0.1 with two @colyseus/sdk 0.18.10 clients; identical server-owned state, a teleport rejected, an oversized move clamped, a dropped client reconnected with its token and kept its position.

## Security, privacy and licensing

- Game logic runs on the server (authoritative model), which limits client cheating; you still must validate every client message.
- Self-hosted servers keep player data on your infrastructure; Colyseus Cloud is a third-party host.

**Software license** MIT.

**Commercial use** MIT license, described in the README as free 'even for commercial games'.

## Evidence quotes

| Field | Upstream wording and file |
| --- | --- |
| hardware | 'Go from 10 to 10,000+ CCU by scaling vertically or horizontally with Redis' (README.md) |
| installation | 'npm create colyseus-app@latest ./my-server' (README.md) |
| runtime_requirements | '"engines": { "node": ">= 22.x"' (bundles/colyseus/package.json) |
| license | 'MIT licensed, even for commercial games.' (README.md) |
| model_license | Not a model tool. |
| inputs | Transport packages ws-transport, uwebsockets-transport, bun-websockets, h3-transport (repository tree) |
| outputs | 'automatically synchronizes to all clients, delta-compressed and binary-encoded.' (README.md) |
