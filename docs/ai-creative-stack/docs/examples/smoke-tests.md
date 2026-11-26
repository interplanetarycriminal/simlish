# Smoke tests

What was actually run for this catalogue on 2026-11-26, on Windows 11 with Node 24, Python 3.14, uv, Chrome 158, FFmpeg 7.1 and Blender 5.2.2. Everything else in the catalogue is documented, not tested. Each guide's "Smoke test" section and the registry's `smoke_test` field carry the same status.

| Reference or handoff | Status | What ran | Result |
| --- | --- | --- | --- |
| [Three.js](../repositories/three-js.md) | Passed | [Seekable scene fixture](../../fixtures/seekable-scene/README.md): 600 frames rendered over DevTools from a time-driven scene | Seekable, repeatable, pause-to-play and stream checks pass |
| Blender → GLB → [Three.js](../repositories/three-js.md) | Passed | [Blender GLB fixture](../../fixtures/blender-glb/README.md): build, validate, load, seek | All Floor checks and all six Three.js checks pass |
| Validator color-space check | Passed | `fixtures/blender-glb/colorspace_test.py`: six materials, four wired wrongly on purpose | Exactly the four wrong ones flagged |
| [FFmpeg](../repositories/ffmpeg.md) | Passed | The [media delivery example](media-delivery.md) exactly as written | 640×360 MPEG-4, 24/1 fps, 48 decoded frames, 2.000 s, after a stream-copy remux |
| [Rough.js](../repositories/rough-js.md) | Passed | `roughjs@4.6.6` in Node via `bundled/rough.cjs.js`; three rectangles with seeds 42, 42 and 7 | Same seed gives identical paths; another seed differs. The `bin/` ES modules use extensionless imports that Node's ESM loader rejects, so use a bundler or the bundled build. |
| [Spec Kit](../repositories/spec-kit.md) | Passed | `uvx --from specify-cli specify init demo --integration claude --script sh --non-interactive --ignore-agent-tools` | specify-cli 1.4.5 created `.specify/` with constitution, spec, plan, tasks and checklist templates and listed the `/speckit-*` commands |
| [Blender MCP](../repositories/blender-mcp.md) | Not run | Blender itself was tested; the MCP add-on and server were not installed | — |
| SAM 3D Objects, Stable Fast 3D, TRELLIS.2, MeshAnything V2, UniRig, Dream Textures, ComfyUI-3D-Pack, Gaussian Splatting | Not feasible here | Gated or multi-gigabyte weights, or 24–32 GB of VRAM | Requirements recorded in [HARDWARE.md](../../HARDWARE.md) |
| All hosted services (Stitch, 21st MCP, Figma API, ElevenLabs, fal.ai, HeyGen cloud) | Not run | Needs accounts and sends data off the machine | — |

## Reproduce

```sh
node fixtures/seekable-scene/render.mjs
cd fixtures/blender-glb
blender --background --factory-startup --python-exit-code 1 --python make_asset.py -- out
blender --background --factory-startup --python-exit-code 1 --python ../../scripts/blender/validate_asset.py -- out/toy_limb.glb out/report-glb.json
node check.mjs
```

Run the FFmpeg, Rough.js and Spec Kit checks in a new empty folder each, never inside this repository.
