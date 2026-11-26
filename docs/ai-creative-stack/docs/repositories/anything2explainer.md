# anything2explainer

Use for turning a topic or article into a sourced, narrated 2-8 minute black-canvas motion-graphics explainer video drawn in Remotion by parallel coding agents.

> Motion films, explainers and engines · Added by the user · smoke test: **not run**

## Evidence and maintenance

- [Canonical reference](https://github.com/Vincentwei1021/anything2explainer)
- Verified 2026-11-26 against default branch `main` at [`ddf03a5f2b92`](https://github.com/Vincentwei1021/anything2explainer/commit/ddf03a5f2b920526a7460a6d1a35fb94dfcbc15d).
- GitHub reports archive state **false** and a repository push at `2026-11-25T10:01:20Z`. Push activity is a maintenance signal, not a quality rating.
- Attribution: Added directly by the user on 2026-11-26.

- [README.md](https://github.com/Vincentwei1021/anything2explainer/blob/ddf03a5f2b920526a7460a6d1a35fb94dfcbc15d/README.md)
- [LICENSE](https://github.com/Vincentwei1021/anything2explainer/blob/ddf03a5f2b920526a7460a6d1a35fb94dfcbc15d/LICENSE)
- [SKILL.md](https://github.com/Vincentwei1021/anything2explainer/blob/ddf03a5f2b920526a7460a6d1a35fb94dfcbc15d/SKILL.md)
- [package.json](https://github.com/Vincentwei1021/anything2explainer/blob/ddf03a5f2b920526a7460a6d1a35fb94dfcbc15d/template/package.json)

## Runtime, hardware and setup

- **Type** skill. Primary language TypeScript.
- **Platforms** macOS, Linux.
- **Runtime** Node >=18 (template pins remotion 4.0.507, @remotion/cli 4.0.507, react 19.2.8, TypeScript 5.9.3); ffmpeg; Python 3 venv with edge-tts==7.2.8, numpy, pillow, scipy; for English narration kokoro + soundfile + espeak-ng. Linux ARM needs system Chromium via REMOTION_BROWSER_EXECUTABLE.
- **Execution** local.
- **Agent paths** Claude Code, Codex. Client claims describe documentation and remain untested here unless the smoke test says otherwise.
- **Configuration** src/config.ts sets lang ('zh' or 'en') and bg ('dots' or 'stars'); TTS engine is chosen with TTS_ENGINE (edge, kokoro, kokoro_onnx, piper) or by supplying your own audio and timeline.
- **Credentials and services** No API keys by default. The Chinese default voice (edge-tts) is an unauthenticated cloud call to a Microsoft endpoint; bring-your-own TTS such as Volcengine needs your own account.

Review the source and pin the version before running the upstream-documented command. It was read in the pinned documentation; execution is recorded only under Smoke test.

```sh
git clone https://github.com/Vincentwei1021/anything2explainer.git
ln -s "$PWD/anything2explainer" ~/.claude/skills/anything2explainer   # Claude Code
ln -s "$PWD/anything2explainer" ~/.codex/skills/anything2explainer    # Codex
pip install 'edge-tts==7.2.8' numpy pillow scipy
pip install kokoro soundfile && brew install espeak-ng
```

## Contracts and selection

| Boundary | Contract |
| --- | --- |
| Input | Topic sentence, Article or document to adapt, Chosen length and language (Chinese or English), Optional finished narration audio (public/assets/<slug>/audio.wav) with hand-filled timeline |
| Output | 1280x720 30 fps H.264 MP4 with voiceover, subtitles, chapter cards, HUD and progress bar, Research doc with source URLs, Narration script and frame-accurate timeline, Storyboard, Per-shot Remotion TSX source, QC reports and delivery notes |
| Primary | Video composition, Animation |
| Supporting | Shot planning, Design critique, Media processing |

Skip if you need vertical 9:16 video, a visual style other than its black-canvas look, live action or a talking presenter. Consider [huashu-motion](huashu-motion.md), [lemo-opuscar](lemo-opuscar.md), [motion-canvas](motion-canvas.md), [hyperframes](hyperframes.md). Complementary tools include [remotion](remotion.md), [remotion-skills](remotion-skills.md), [ffmpeg](ffmpeg.md).

Renders with Remotion 4.0.507.

- Skip for commercial use of the toolkit unless the author has authorized it.

## Craft notes

- Fixed house style: black canvas with dot-field or star-field backdrop, white line art with purple accents, 44 px subtitles and a chapter progress bar; only the backdrop is switchable.
- Nine stages with four human checkpoints (length/language, narration sign-off, voice, first 30 s); once narration is voiced, frame numbers are hard-coded so any word change re-times the film.
- A 3-5 min film is 40-50 shots built by about 8 agents in about 2 h; every animation is a pure function of the frame with seeded randomness, so re-renders are identical.

## Examples

1. **Independent** Ask the agent to 'make me an explainer video about vector databases' at 3-5 minutes in English and approve the first 30-second preview.
2. **Combined** Proposed handoff: install remotion-skills alongside it so build agents consult remotion-markup best practices while writing each shot component.

For both, save the inputs and output evidence with the selected version. Use a small authorized fixture first and review the actual render or inspection result before expanding scope.

## Smoke test

**not run**. No run is recorded.

## Security, privacy and licensing

- Runs many build agents in parallel that bundle Remotion and execute shell scripts; past about 12 tmux panes it dispatches in waves.
- edge-tts is pinned because it tracks a Microsoft endpoint that breaks across upgrades.
- Chinese narration text is sent to Microsoft's edge-tts endpoint by default; English Kokoro runs locally.
- The research stage browses the web and records source URLs for every on-screen fact.

**Software license** PolyForm Noncommercial License 1.0.0 (toolkit); bundled fonts SIL OFL 1.1.

**Commercial use** Noncommercial use of the toolkit is free; any commercial use of the toolkit needs prior authorization from the author. Videos you make belong to you. Remotion has its own company license terms (remotion.dev/license).

## Evidence quotes

| Field | Upstream wording and file |
| --- | --- |
| hardware | 'No. Remotion renders through headless Chromium on the CPU.' (README.md FAQ, GPU question) |
| installation | 'git clone https://github.com/Vincentwei1021/anything2explainer.git' then ln -s into ~/.claude/skills (README.md) |
| license | 'PolyForm Noncommercial License 1.0.0' and 'any commercial use of the toolkit requires prior authorization' (LICENSE) |
| model_license | Not a model; uses kokoro-82m and edge-tts voices (README.md) |
| inputs | 'a topic ("explain vector databases"), or an article / document you want turned into a video' (README.md) |
| outputs | 'a 1280x720 H.264 MP4 with synchronized voiceover, word-boundary-aligned subtitles' (README.md) |
| renderer | 'remotion 4.0.507' pinned in template/package.json |
