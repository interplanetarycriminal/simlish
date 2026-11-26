# Lemo Opuscar

Use for having Claude make a narrated, scored short film entirely in code in one of 99 named visual styles, or for turning a library style into your own reusable style.

> Motion films, explainers and engines · Added by the user · smoke test: **not run**

## Evidence and maintenance

- [Canonical reference](https://github.com/lemomo-ai/lemo-opuscar)
- Verified 2026-11-26 against default branch `main` at [`439b98af08b0`](https://github.com/lemomo-ai/lemo-opuscar/commit/439b98af08b04400f8fd8a8dd19cd773c0c96532).
- GitHub reports archive state **false** and a repository push at `2026-11-26T09:48:06Z`. Push activity is a maintenance signal, not a quality rating.
- Attribution: Added directly by the user on 2026-11-26.

- [README.md](https://github.com/lemomo-ai/lemo-opuscar/blob/439b98af08b04400f8fd8a8dd19cd773c0c96532/README.md)
- [LICENSE](https://github.com/lemomo-ai/lemo-opuscar/blob/439b98af08b04400f8fd8a8dd19cd773c0c96532/LICENSE)
- [TECHNIQUE.md](https://github.com/lemomo-ai/lemo-opuscar/blob/439b98af08b04400f8fd8a8dd19cd773c0c96532/TECHNIQUE.md)
- [package.json](https://github.com/lemomo-ai/lemo-opuscar/blob/439b98af08b04400f8fd8a8dd19cd773c0c96532/package.json)

## Runtime, hardware and setup

- **Type** plugin. Primary language JavaScript.
- **Platforms** macOS, Linux, Windows.
- **Runtime** Node 20+, ffmpeg 7+ (6.x rejected), Python 3.11+ or uv; npm deps playwright-core ^1.63.0 and three ^0.170.0. The agent installs the rest via setup.sh.
- **Execution** local.
- **Agent paths** Claude Code, Other agents by copying plugin/skills/lemo-opuscar/ into their skills folder. Client claims describe documentation and remain untested here unless the smoke test says otherwise.
- **Configuration** On first use it downloads guides, tools and style prompts to ~/lemo-opuscar; saved custom styles live in ~/lemo-my-styles/. Optional packs install with 'setup.sh deps voice music'.
- **Credentials and services** None for most styles. Three styles (Manga Panels, Text Flash Cuts, Comic History Cartoon) need an image generator you bring, such as the Codex CLI signed in to an account that can generate images. Chinese TTS uses online edge-tts without a key.

| Hardware | Documented value |
| --- | --- |
| GPU | Not required for most styles; 3D and shader-heavy styles want a GPU (three.js r170 via headless WebGL2) |
| Minimum VRAM | Not documented |
| Recommended VRAM | Not documented |
| System RAM | Not documented |
| Storage | Core ~350 MB; voice pack ~0.55 GB plus a Whisper model (~145 MB English, ~480 MB Chinese); music pack ~140 MB; each sample library 70-400 MB |
| CPU fallback | not documented |
| Training versus inference | Not documented |
| Notes | Developed on macOS (Apple silicon); Linux 'should work'; Windows via Git Bash or WSL. A film takes an agent about 30-60 minutes. |

Review the source and pin the version before running the upstream-documented command. It was read in the pinned documentation; execution is recorded only under Smoke test.

```sh
claude plugin marketplace add lemomo-ai/lemo-opuscar
claude plugin install lemo-opuscar@lemolab
```

## Contracts and selection

| Boundary | Contract |
| --- | --- |
| Input | Story or topic plus a style name (English, Chinese or folder name), Optional length and narrator choice, Your own photos, music, voice or other material, Public data such as laser-scan or satellite data |
| Output | MP4, 1920x1080 at 24 fps by default (some styles 30 fps; other sizes on request), .srt subtitles, Per-film source, audio stems and CREDITS, Saved custom style folder with STYLE.md and demo film |
| Primary | Video composition, Animation, Creative direction |
| Supporting | Illustration, 3D rendering, Media processing |

Skip if you are not using a Claude model; the README says other models may not reproduce the styles well. Consider [huashu-motion](huashu-motion.md), [onetake](onetake.md), [anything2explainer](anything2explainer.md), [hyperframes](hyperframes.md), [remotion](remotion.md). Complementary tools include [three-js](three-js.md), [ffmpeg](ffmpeg.md), [blender-mcp](blender-mcp.md).

Its own render(t) pages captured by headless Chrome, with three.js and ffmpeg.

- Skip if your build machine only has ffmpeg 6.x (for example stock Ubuntu 24.04) and you cannot install ffmpeg 7+.

## Craft notes

- Each style is a STYLE.md prompt plus a demo film; the agent reads DIRECTOR.md, TECHNIQUE.md and the style file, then renders a page exposing window.render(t) in headless Chrome frame by frame.
- Scores are written as timed note events and played by sampler.py from free libraries (VSCO 2 CE, VCSL, FreePats, Karoryfer, Salamander); the mix is loudness-normalized to -14 LUFS with ffmpeg.
- Capture speed comes from JPEG screenshots, one browser per worker and grain added in ffmpeg rather than in the page; tuned for Claude Fable, Opus and Sonnet at high effort.

## Examples

1. **Independent** Ask 'Make a 45-second film in the watercolor style about the coffee farm my family runs. Warm female narrator.'
2. **Combined** Proposed handoff: model a hero object with blender-mcp, export it, and stage it in one of the 3D & Miniature styles that use three-js.

For both, save the inputs and output evidence with the selected version. Use a small authorized fixture first and review the actual render or inspection result before expanding scope.

## Smoke test

**not run**. No run is recorded.

## Security, privacy and licensing

- Installs from a third-party Claude Code plugin marketplace (lemolab); auto-update is off unless you enable it.
- sampler.py downloads missing sample libraries automatically from npm, PyPI, GitHub Releases and Hugging Face unless LEMO_FETCH=0.
- For the three image-generator styles, prompts are sent to whatever image service you supply.
- Chinese narration text goes to Microsoft's edge-tts service; English Kokoro runs offline.

**Software license** Mixed: code MIT; all Markdown docs and image-generation prompts CC BY-NC 4.0 plus an extra permission to use them for your own films; demo films and stills CC BY 4.0; third-party assets under their own licenses.

**Commercial use** Films you make are yours, commercial films included, with no credit required. Following and adapting the docs for commercial or client films is allowed, but selling the docs or putting them into a commercial product or service needs a paid license from LemoLab. Clawd (Anthropic's character), third-party interfaces and six TTS narration tracks are excluded from all licenses. Pre-2.0.0 versions keep their earlier license.

## Evidence quotes

| Field | Upstream wording and file |
| --- | --- |
| hardware | '3D and shader-heavy styles want a GPU.' (TECHNIQUE.md) |
| installation | 'claude plugin marketplace add lemomo-ai/lemo-opuscar' then 'claude plugin install lemo-opuscar@lemolab' (README.md) |
| license | 'Docs: Creative Commons Attribution-NonCommercial 4.0' and 'Code: MIT License' (LICENSE) |
| model_license | Not a model tool; image models are user-supplied (TECHNIQUE.md) |
| inputs | 'Add a length, a narrator, your own photos or music if you like' (README.md) |
| outputs | 'Default output 1920x1080 at 24 fps' (README.md) |
| renderer | 'web page with render(t) -> headless Chrome, frame by frame -> video.mp4' (TECHNIQUE.md) |
