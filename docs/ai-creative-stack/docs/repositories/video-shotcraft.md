# Video Shotcraft

Use for having Claude Code or Codex turn real product page captures into an editable Remotion promo film with shot recipes, beat sync and sound design.

> Supplementary research candidates · Supplementary · smoke test: **not run**

## Evidence and maintenance

- [Canonical reference](https://github.com/Vincentwei1021/video-shotcraft)
- Verified 2026-11-26 against default branch `main` at [`1152363da5c8`](https://github.com/Vincentwei1021/video-shotcraft/commit/1152363da5c824b32dba6d8a2ef7f935b677e445).
- GitHub reports archive state **false** and a repository push at `2026-11-25T10:01:07Z`. Push activity is a maintenance signal, not a quality rating.
- Attribution: Not attributable to any source post. Identified during related research.

- [README.md](https://github.com/Vincentwei1021/video-shotcraft/blob/1152363da5c824b32dba6d8a2ef7f935b677e445/README.md)
- [SKILL.md](https://github.com/Vincentwei1021/video-shotcraft/blob/1152363da5c824b32dba6d8a2ef7f935b677e445/SKILL.md)
- [package.json](https://github.com/Vincentwei1021/video-shotcraft/blob/1152363da5c824b32dba6d8a2ef7f935b677e445/template/package.json)
- [publish-upload-post.md](https://github.com/Vincentwei1021/video-shotcraft/blob/1152363da5c824b32dba6d8a2ef7f935b677e445/references/publish-upload-post.md)
- [ATTRIBUTION.md](https://github.com/Vincentwei1021/video-shotcraft/blob/1152363da5c824b32dba6d8a2ef7f935b677e445/assets/audio/ATTRIBUTION.md)

## Runtime, hardware and setup

- **Type** skill. Primary language TypeScript.
- **Platforms** macOS, Linux.
- **Runtime** Node.js and npm (template pins remotion and @remotion/cli 4.0.484, React 19.2.7); ffmpeg/ffprobe; uv for BGM beat analysis; puppeteer for page capture (installed on demand); Remotion downloads its own headless Chrome.
- **Execution** local.
- **Agent paths** Claude Code, Codex. Client claims describe documentation and remain untested here unless the smoke test says otherwise.
- **Configuration** The skill first asks which of three modes to use (Ink Press template, autonomous free creation, guided co-creation) unless the user names the template or specific shot cards. Optional UPLOAD_POST_API_KEY enables social publishing.
- **Credentials and services** None for core use (Freesound CLI needs no key); an Upload-Post API key only for optional social publishing.

Review the source and pin the version before running the upstream-documented command. It was read in the pinned documentation; execution is recorded only under Smoke test.

```sh
npx skills add Vincentwei1021/video-shotcraft

or:
git clone https://github.com/Vincentwei1021/video-shotcraft.git
cd video-shotcraft
ln -s "$(pwd)" ~/.claude/skills/video-shotcraft   # Claude Code
ln -s "$(pwd)" ~/.codex/skills/video-shotcraft    # Codex
```

## Contracts and selection

| Boundary | Contract |
| --- | --- |
| Input | Frontend project path or URL to capture, Product screenshots, copy and logo, Screen recordings, Named shot cards from the Gallery, Existing video or shot (for SFX-only work), BGM track |
| Output | MP4 1920x1080, 30 fps, h264 with music and SFX, Remotion project source (each shot a React component), Motion Workbench browser editor session, Optional JianYing (CapCut CN) draft, Freesound credit manifests |
| Primary | Video composition, Shot planning, Animation |
| Supporting | Video editing, Media processing, Creative direction |

Skip if you want generated footage; it is not a video generator and every frame is drawn by code from your screenshots and copy. Consider [remotion](remotion.md), [hyperframes](hyperframes.md), [motion-canvas](motion-canvas.md). Complementary tools include [ffmpeg](ffmpeg.md), [video-use](video-use.md).

Outputs an editable Remotion project alongside the MP4, so Remotion is a documented handoff.

- SKILL.md is written in Chinese; Windows is not listed as tested and the Windows JianYing installer is marked untested.
- Remotion's license may require a paid company license for commercial teams.

## Craft notes

- 124 recipe cards / 150 shots across 10 categories (e.g. Typography 25, Light & Emphasis 23, UI Entrance 22, Transitions 19), each with a Remotion demo in demos/<category>/<card>/.
- Delivers editable output rather than a flat render: Motion Workbench splits shot, transition, caption and SFX tracks, and preview equals render frame for frame.
- Beat sync uses librosa-measured BPM; headless Linux renders need --concurrency=1, chrome-headless-shell and --browser-executable where remotion.media is blocked.

## Examples

1. **Independent** Make a launch film for this repo with the Ink Press template using its real page captures.
2. **Combined** Proposed handoff: render the film with video-shotcraft, then use ffmpeg to cut 9:16 social versions.

For both, save the inputs and output evidence with the selected version. Use a small authorized fixture first and review the actual render or inspection result before expanding scope.

## Smoke test

**not run**. No run is recorded.

## Security, privacy and licensing

- Page capture uses puppeteer, installed on demand, and Remotion downloads a headless Chrome on first render.
- Optional publisher posts to TikTok, Instagram, YouTube, LinkedIn, X via Upload-Post; the guide requires confirming caption and platforms and a --dry-run first.
- README warns to replace template screenshots and check whether product, customer or personal data needs anonymizing before publishing.
- Captured pages of your product become frames in the film; SFX search queries go to Freesound.

**Software license** Apache-2.0.

**Commercial use** Skill code and docs are Apache-2.0. Remotion has its own license: free for individuals and small teams, companies may need a paid license. Freesound SFX keep per-file CC0/CC BY terms with credits; bundled BGM is from Mixkit (one track's source could not be traced).

## Evidence quotes

| Field | Upstream wording and file |
| --- | --- |
| hardware | No GPU stated; 'Rendering on a headless Linux box (tested: 2 cores, Node 22)' (README.md) |
| installation | 'npx skills add Vincentwei1021/video-shotcraft' (README.md) |
| license | 'Code and docs: Apache-2.0' (README.md) |
| model_license | Not applicable; no models |
| inputs | 'The agent captures your real pages, picks shots from a library of tuned motion recipes' (README.md) |
| outputs | 'MP4, 1920x1080, 30 fps, h264, with music and sound design' (README.md) |
| commercial_use_notes | Remotion 'free for individuals and small teams, companies may need a paid license' (README.md) |
| supported_platforms | 'Tested on macOS; Linux works with the notes below.' (README.md) |
