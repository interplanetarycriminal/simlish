# ink (inkle)

Use for writing branching interactive narrative in the ink scripting language, compiling it to JSON with inklecate, and running it in a game through the C# runtime or inkjs.

> #55 · Game development · Source E (games) · smoke test: **passed**

## Evidence and maintenance

- [Canonical reference](https://github.com/inkle/ink)
- Verified 2026-11-27 against default branch `master` at [`4011b8c0a018`](https://github.com/inkle/ink/commit/4011b8c0a01828c61dd2331613c1038a3a5f294b).
- GitHub reports archive state **false** and a repository push at `2026-11-16T16:21:09Z`. Push activity is a maintenance signal, not a quality rating.
- Attribution: Listed in the game-development post (source E, transcript supplied by the user on 2026-11-27).

- [README.md](https://github.com/inkle/ink/blob/4011b8c0a01828c61dd2331613c1038a3a5f294b/README.md)
- [RunningYourInk.md](https://github.com/inkle/ink/blob/4011b8c0a01828c61dd2331613c1038a3a5f294b/Documentation/RunningYourInk.md)
- [CommandLineTool.cs](https://github.com/inkle/ink/blob/4011b8c0a01828c61dd2331613c1038a3a5f294b/inklecate/CommandLineTool.cs)
- [inklecate.csproj](https://github.com/inkle/ink/blob/4011b8c0a01828c61dd2331613c1038a3a5f294b/inklecate/inklecate.csproj)
- [ink-engine-runtime.csproj](https://github.com/inkle/ink/blob/4011b8c0a01828c61dd2331613c1038a3a5f294b/ink-engine-runtime/ink-engine-runtime.csproj)

## Runtime, hardware and setup

- **Type** framework. Primary language C#.
- **Platforms** Windows, Linux, macOS.
- **Runtime** .NET SDK 6.0 or newer to build; .NET Runtime 6.0 or newer to run the binaries. inklecate targets net6.0; the runtime engine targets netstandard1.0 and netstandard2.0 (version 1.2.1).
- **Execution** local.
- **Agent paths** Generic coding agent via project files. Client claims describe documentation and remain untested here unless the smoke test says otherwise.
- **Configuration** inklecate flags: -o output file, -p play mode, -j JSON output for tools, -s story stats, -c count all visits, -k keep running, -x compiler plugin directory. Games talk to stories through tags, variables and external functions.
- **Credentials and services** None.

Review the source and pin the version before running the upstream-documented command. It was read in the pinned documentation; execution is recorded only under Smoke test.

```sh
Download inklecate from https://github.com/inkle/ink/releases, then: ./inklecate -p myStory.ink (Mac/Linux) or inklecate.exe -p myStory.ink (Windows). From source: cd inklecate; dotnet build -c Release
```

## Contracts and selection

| Boundary | Contract |
| --- | --- |
| Input | .ink text files (with INCLUDE files) |
| Output | compiled story JSON (ink JSON runtime format), play-mode text in the console, story stats JSON (-s), save state JSON via story.state.ToJson() |
| Primary | Narrative |
| Supporting | Prototyping |

Skip if you need a complete narrative game engine with UI; ink is designed to slot into your own game and UI, not to be an end-to-end engine. Consider the existing project toolchain. Complementary tools include [godot](godot.md), [phaser](phaser.md), [bevy](bevy.md), [colyseus](colyseus.md).

## Craft notes

- The runtime loop is small: new Story(json), while canContinue call Continue(), then show currentChoices and call ChooseChoiceIndex.
- Integrations named in the pinned README are Inky (editor), ink-unity-integration (Unity plugin with auto-compile) and inkjs (community JavaScript port, usually one major version behind); no Godot integration is listed there.
- External functions are treated as actions by default and stop glue lookahead, a subtle behavior the RunningYourInk guide warns about.

## Examples

1. **Independent** Write a three-scene branching dialogue in ink and compile it to JSON with inklecate.
2. **Combined** Proposed handoff: compile an ink story to JSON and drive dialogue in a Phaser game through inkjs.

For both, save the inputs and output evidence with the selected version. Use a small authorized fixture first and review the actual render or inspection result before expanding scope.

## Smoke test

**passed**. fixtures/game-dev ink-branches: inkjs 2.4.0 compiles an original story with 0 errors; 4 choice paths reach all 3 endings, a gated choice hides correctly, and a mid-story save loads into a new Story with identical choices and text.

## Security, privacy and licensing

- The -x flag loads compiler plugins from a directory; load only plugins you trust.
- Runs locally; no network calls described.

**Software license** MIT.

**Commercial use** MIT license: commercial use is allowed; inkle says it does not require attribution but would like to hear about projects.

## Evidence quotes

| Field | Upstream wording and file |
| --- | --- |
| hardware | No hardware section; build needs '.NET SDK 6.0 or newer' (README.md) |
| installation | '**Mac or Linux:** `./inklecate -p myStory.ink`' (README.md) |
| license | '**ink** is released under the MIT license.' (README.md) |
| model_license | Not a model tool. |
| inputs | 'Usage: inklecate <options> <ink file>' (inklecate/CommandLineTool.cs) |
| outputs | 'If you want to get a compiled `.json` file, just remove the `-p` option' (README.md) |
| inkjs | 'inkjs is a JavaScript port of the ink engine, useful for powering web-based game.' (README.md) |
| save_state | 'string savedJson = _inkStory.state.ToJson();' (Documentation/RunningYourInk.md) |
