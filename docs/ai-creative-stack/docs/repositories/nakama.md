# Nakama

Use for running a self-hosted game backend with accounts, storage, chat, leaderboards, tournaments, matchmaking and authoritative realtime matches.

> #57 · Game development · Source E (games) · smoke test: **not run**

## Evidence and maintenance

- [Canonical reference](https://github.com/heroiclabs/nakama)
- Verified 2026-11-27 against default branch `master` at [`e33f5e72c6fe`](https://github.com/heroiclabs/nakama/commit/e33f5e72c6fe82c45dc62a7a7bcee28a6647378e).
- GitHub reports archive state **false** and a repository push at `2026-11-26T20:29:56Z`. Push activity is a maintenance signal, not a quality rating.
- Attribution: Listed in the game-development post (source E, transcript supplied by the user on 2026-11-27).

- [README.md](https://github.com/heroiclabs/nakama/blob/e33f5e72c6fe82c45dc62a7a7bcee28a6647378e/README.md)
- [docker-compose.yml](https://github.com/heroiclabs/nakama/blob/e33f5e72c6fe82c45dc62a7a7bcee28a6647378e/docker-compose.yml)
- [docker-compose-postgres.yml](https://github.com/heroiclabs/nakama/blob/e33f5e72c6fe82c45dc62a7a7bcee28a6647378e/docker-compose-postgres.yml)
- [go.mod](https://github.com/heroiclabs/nakama/blob/e33f5e72c6fe82c45dc62a7a7bcee28a6647378e/go.mod)
- [main.go](https://github.com/heroiclabs/nakama/blob/e33f5e72c6fe82c45dc62a7a7bcee28a6647378e/main.go)
- [se.go](https://github.com/heroiclabs/nakama/blob/e33f5e72c6fe82c45dc62a7a7bcee28a6647378e/se/se.go)
- [match.lua](https://github.com/heroiclabs/nakama/blob/e33f5e72c6fe82c45dc62a7a7bcee28a6647378e/data/modules/match.lua)
- [README.md](https://github.com/heroiclabs/nakama/blob/e33f5e72c6fe82c45dc62a7a7bcee28a6647378e/sample_go_module/README.md)
- [CHANGELOG.md](https://github.com/heroiclabs/nakama/blob/e33f5e72c6fe82c45dc62a7a7bcee28a6647378e/CHANGELOG.md)
- [LICENSE](https://github.com/heroiclabs/nakama/blob/e33f5e72c6fe82c45dc62a7a7bcee28a6647378e/LICENSE)

## Runtime, hardware and setup

- **Type** application. Primary language Go.
- **Platforms** Unverified.
- **Runtime** Needs CockroachDB or another Postgres wire-compatible database. The pinned docker-compose uses cockroachdb/cockroach:latest-v24.1 (or postgres:16.8-alpine) with image heroiclabs/nakama:3.37.0; CHANGELOG top entry is 3.42.0. Building from source uses Go (go.mod: go 1.27.3) with vendored dependencies.
- **Execution** local or hosted.
- **Agent paths** Generic coding agent via project files. Client claims describe documentation and remain untested here unless the smoke test says otherwise.
- **Configuration** Settings come from flags or a config file (database address, logger, session token expiry, metrics port). Server logic is extended with Lua, TypeScript/JavaScript or Go modules.
- **Credentials and services** The server uses a server key (default 'defaultkey' in the example) and Console credentials; change defaults before production. Heroic Cloud is an optional paid host.

Review the source and pin the version before running the upstream-documented command. It was read in the pinned documentation; execution is recorded only under Smoke test.

```sh
docker-compose -f ./docker-compose.yml up
(binaries) nakama migrate up --database.address "root@127.0.0.1:26257"
nakama --database.address "root@127.0.0.1:26257"
```

## Contracts and selection

| Boundary | Contract |
| --- | --- |
| Input | gRPC and HTTP/JSON (REST) requests, WebSocket or rUDP realtime messages, Lua, TypeScript/JavaScript or Go runtime modules |
| Output | REST/gRPC API on port 7350 (gRPC 7349), web Console on port 7351, Prometheus metrics, realtime match state to clients |
| Primary | Multiplayer |
| Supporting | Game engine |

Skip if you cannot run a database; Nakama requires CockroachDB or a Postgres-compatible server even for local development. Consider [colyseus](colyseus.md). Complementary tools include [godot](godot.md), [phaser](phaser.md), [bevy](bevy.md), [rapier](rapier.md), [jolt-physics](jolt-physics.md).

## Craft notes

- Authoritative matches are written as handlers (match_init, match_join_attempt, match_join, match_leave, match_loop, match_terminate, match_signal) in Lua, TypeScript/JavaScript or Go; the tick counter increments only after match_loop.
- One server bundles users, storage, social graph, chat, leaderboards, tournaments, parties, purchase validation, notifications and a matchmaker, with a web Console at 127.0.0.1:7351.
- Client libraries named: .NET/C#, Unity, JavaScript, Java/Android, Unreal, Godot, Defold and Swift/iOS.

## Examples

1. **Independent** Start Nakama and CockroachDB with docker-compose and authenticate a device ID through the REST API with curl.
2. **Combined** Proposed handoff: run Nakama's matchmaker and leaderboards behind a Godot client using the Godot client library.

For both, save the inputs and output evidence with the selected version. Use a small authorized fixture first and review the actual render or inspection result before expanding scope.

## Smoke test

**not run**. No run is recorded.

## Security, privacy and licensing

- The example docker-compose runs CockroachDB with --insecure and uses the default server key; harden both before exposing the server.
- Telemetry is on by default: main.go sends start/end events to api.segment.io unless NAKAMA_TELEMETRY=0.
- Anonymous usage statistics (Go version, OS, architecture, Nakama version, a cookie ID) go to Segment by default; set NAKAMA_TELEMETRY=0 to opt out.
- Player accounts, chat and storage live in your database.

**Software license** Apache-2.0.

**Commercial use** Apache-2.0: commercial use is allowed with notice and license terms kept. The pinned files describe only the Apache-2.0 server and the paid Heroic Cloud host; they do not mention a separate enterprise license.

## Evidence quotes

| Field | Upstream wording and file |
| --- | --- |
| hardware | 'can be run on instance types as small as "g1-small" ... we recommend a minimum of "n1-standard-1"' (README.md) |
| database | 'Nakama server requires CockroachDB or another Postgres wire-compatible server' (README.md) |
| installation | 'Run `docker-compose -f ./docker-compose.yml up` to download container images and run the servers.' (README.md) |
| license | 'This project is licensed under the Apache-2 License.' (README.md) |
| model_license | Not a model tool. |
| inputs | 'For request/response it can use GRPC or the HTTP1.1+JSON fallback (REST)... WebSockets or rUDP.' (README.md) |
| outputs | 'You can navigate to it on your browser on http://127.0.0.1:7351.' (README.md) |
| match_handlers | 'develop authoritative multiplayer match handlers, RPC functions' (sample_go_module/README.md) |
| telemetry | 'telemetryEnabled := os.Getenv("NAKAMA_TELEMETRY") != "0"' (main.go) |
