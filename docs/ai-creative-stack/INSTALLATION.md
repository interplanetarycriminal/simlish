# Modular installation

Never install the whole catalogue. Install one tool when the [toolchain plan](templates/toolchain-plan.md) shows a gap the existing stack cannot close.

## Steps

1. **Read the guide.** Open the tool's guide from the [index](REPOSITORIES.md). Read its pinned documentation, license, hardware table and craft notes.
2. **Check the hardware.** Compare the guide's VRAM, OS and CUDA needs with the machine you actually have. See [HARDWARE.md](HARDWARE.md). If it does not fit, stop and choose an alternative or authorized remote compute.
3. **Confirm the package.** Check the package identity, version and release provenance. The guide's commit anchors the evidence; resolve the release you install separately. Watch for look-alike names (Graphify is `graphifyy` on PyPI).
4. **Review before running.** Read manifests, lockfiles, lifecycle and install scripts, permissions and the external hosts they contact. [SECURITY.md](SECURITY.md) lists installers that need a closer look.
5. **Isolate.** Light tools go in the project's own package manager. Each model gets its own conda environment, venv or container. ComfyUI-3D-Pack gets its own ComfyUI install. Never install a model into Blender's bundled Python or the system Python. Never replace a working GPU driver to suit one tool.
6. **Inject credentials privately.** Use the host's secret mechanism. Keep MCP permissions and installed skills scoped to the project.
7. **Download weights only for a real job.** Documentation and planning never need multi-gigabyte checkpoints. Record each checkpoint's source and SHA-256.
8. **Run a fixture first.** Run the guide's independent example on a synthetic or authorized fixture, then inspect the output. For 3D output, run `scripts/blender/validate_asset.py`.
9. **Record it.** Record versions, hashes and results in the [execution report](templates/execution-report.md). Review the lockfile and config diff, and keep the minimal working set.

## What needs nothing installed

The catalogue's own scripts use only the Python standard library (`jsonschema` is used when present). The fixtures need only Node 22+, Chrome or Chromium, FFmpeg and, for the 3D fixture, Blender. The game-development fixture installs its pinned npm packages with `npm ci --ignore-scripts --legacy-peer-deps`; the expressive-motion fixture loads pinned modules from esm.sh and installs nothing.

```sh
python scripts/validate-registry.py
python scripts/validate-documentation.py
node fixtures/seekable-scene/render.mjs
(cd fixtures/game-dev && npm ci --ignore-scripts --legacy-peer-deps && node run.mjs)
(cd fixtures/expressive-motion && node run.mjs)
```

No setup script in this catalogue installs any of the catalogued tools.
