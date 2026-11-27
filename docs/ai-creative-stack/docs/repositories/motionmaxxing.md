# motionmaxxing

Use for directing and rendering short motion-graphics films (launch videos, promos, brand stings, kinetic type) as HTML on a seek-safe GSAP runtime, then checking the render with scripted gates.

> #71 · Expressive motion · Source F (expressive motion) · smoke test: **not run**

## Evidence and maintenance

- [Canonical reference](https://github.com/Tejashmakwana/motionmaxxing)
- Verified 2026-11-27 against default branch `main` at [`8c8ec0f2a6f6`](https://github.com/Tejashmakwana/motionmaxxing/commit/8c8ec0f2a6f6c9a0da15cd24f7b1298ab298368c).
- GitHub reports archive state **false** and a repository push at `2026-10-06T18:20:43Z`. Push activity is a maintenance signal, not a quality rating.
- Attribution: Listed in the expressive-animation post (source F, transcript supplied by the user on 2026-11-27).

- [README.md](https://github.com/Tejashmakwana/motionmaxxing/blob/8c8ec0f2a6f6c9a0da15cd24f7b1298ab298368c/README.md)
- [SKILL.md](https://github.com/Tejashmakwana/motionmaxxing/blob/8c8ec0f2a6f6c9a0da15cd24f7b1298ab298368c/SKILL.md)
- [NOTICE](https://github.com/Tejashmakwana/motionmaxxing/blob/8c8ec0f2a6f6c9a0da15cd24f7b1298ab298368c/NOTICE)
- [KNOWN-LIMITS.md](https://github.com/Tejashmakwana/motionmaxxing/blob/8c8ec0f2a6f6c9a0da15cd24f7b1298ab298368c/docs/KNOWN-LIMITS.md)

## Runtime, hardware and setup

- **Type** skill. Primary language JavaScript.
- **Platforms** Unverified.
- **Runtime** Node 22+, Python 3, ffmpeg and Google Chrome (or Chromium). Optional: ELEVENLABS_API_KEY for voice, sound effects and music; the Codex CLI with image generation for surface plates. Vendored GSAP 3.12.5, three.js r186 and opentype.js 1.3.4.
- **Execution** local.
- **Agent paths** Claude Code, Any agent that reads SKILL.md with shell access. Client claims describe documentation and remain untested here unless the smoke test says otherwise.
- **Configuration** install.sh checks requirements and links or copies the folder (--dir, --copy, --force); scripts/providers.sh reports Chrome, ffmpeg, key, Codex and disk. Set ELEVENLABS_API_KEY to enable sound.
- **Credentials and services** None for silent films. ElevenLabs API key (ELEVENLABS_API_KEY) for voice, sfx and music; Codex CLI login for generated plates.

| Hardware | Documented value |
| --- | --- |
| GPU | unverified |
| Minimum VRAM | Not documented |
| Recommended VRAM | Not documented |
| System RAM | Not documented |
| Storage | providers.sh reports free disk; no figure given |
| CPU fallback | documented |
| Training versus inference | Not documented |
| Notes | hero3d WebGL scenes render at about 7-11 fps at 1080p on an Apple GPU; software GL works but is slower and differs slightly (about 38 dB PSNR). |

Review the source and pin the version before running the upstream-documented command. It was read in the pinned documentation; execution is recorded only under Smoke test.

```sh
git clone https://github.com/Tejashmakwana/motionmaxxing ~/.claude/skills/motionmaxxing
bash ~/.claude/skills/motionmaxxing/install.sh
```

## Contracts and selection

| Boundary | Contract |
| --- | --- |
| Input | brief in plain language, website URL (brand capture), existing draft.mp4 and index.html to rate and repair |
| Output | film/final.mp4, film/index.html (editable source on the Motion runtime), film/STORYBOARD.md, film/NOTE.md with G0-G5 gate numbers, brand.json, BRAND.md, board.png from brand capture, contact sheets |
| Primary | Video composition, Animation, Creative direction |
| Supporting | Design critique, Shot planning, 3D rendering, Visual effects |

Skip when you need a commercial product that lets end users build animations, unless GSAP's Standard License terms are cleared, because GSAP is vendored under its own non-open license. Consider [remotion](remotion.md), [motion-canvas](motion-canvas.md), [huashu-motion](huashu-motion.md), [remotion-skills](remotion-skills.md). Complementary tools include [gsap](gsap.md), [three-js](three-js.md), [ffmpeg](ffmpeg.md), [hyperframes](hyperframes.md).

## Craft notes

- Timing comes from measurement: about 4,300 moves from 53 pro moments gave 12 named eases (softLand, snapSettle, accelExit) and rules such as a median move of 10 frames and landing decelerates, leaving accelerates.
- Gates G0-G5 are scripted where possible: look.py fails more than 3 consecutive flat frames (G2) and an end hold over 1.4 s (G3); lint.mjs (G5) flags page chrome but cannot see text inside canvas, WebGL or images, and G1/G4 are judged by eye.
- render.mjs renders frame by frame through Chrome and ffmpeg, and Motion.selfTest proves every frame is a pure function of time; ElevenLabs music often misses requested tempo or length.

## Examples

1. **Independent** Make a silent 6-second kinetic-type sting for one line with a hero3d extruded logo and report the G0-G5 numbers.
2. **Combined** Proposed handoff: build the film in motionmaxxing's HTML runtime and finish edits with ffmpeg, as the skill already renders through ffmpeg.

For both, save the inputs and output evidence with the selected version. Use a small authorized fixture first and review the actual render or inspection result before expanding scope.

## Smoke test

**not run**. No run is recorded.

## Security, privacy and licensing

- brand.mjs and fetch_logo.mjs fetch third-party websites, SVGL and Simple Icons in headless Chrome.
- scripts/imagegen.py calls the Codex CLI; voice.py calls ElevenLabs.
- Scripts, voice-over text and music prompts go to ElevenLabs when a key is set.
- Captured brand pages, logos and screenshots are stored locally; brands in the showcase belong to their owners.

**Software license** Apache-2.0 (original work); bundled GSAP is under the GreenSock Standard License, not open source.

**Commercial use** Apache-2.0 for the skill's original files, and the README says 'ship it commercially'. Bundled GSAP 3.12.5 keeps the GreenSock Standard 'No Charge' License, which is not open source and has its own conditions (for example on tools that let end users build visual animations). three.js and opentype.js are MIT; Inter is SIL OFL 1.1. Keep the NOTICE.

## Evidence quotes

| Field | Upstream wording and file |
| --- | --- |
| hardware | 'A hero3d scene renders at about 7-11 fps at 1080p on an Apple GPU' (docs/KNOWN-LIMITS.md) |
| runtime_requirements | '**Requirements:** Node 22+, Python 3, ffmpeg, Google Chrome. Optional: an ElevenLabs key' (README.md) |
| installation | 'git clone https://github.com/Tejashmakwana/motionmaxxing ~/.claude/skills/motionmaxxing' (README.md) |
| license | 'This product is licensed under the Apache License, Version 2.0' (NOTICE) |
| gsap_license | 'This is NOT an open-source license.' (NOTICE, GSAP 3.12.5 entry) |
| model_license | Not a model tool. |
| inputs | 'Give it a website and it captures the brand' (README.md) |
| outputs | '`film/final.mp4` / The film, with sound when a key is set' (README.md) |
