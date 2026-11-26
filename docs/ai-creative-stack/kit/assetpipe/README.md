# assetpipe

Runs a reviewed 3D asset workflow over a batch of images. It writes a manifest per asset with every stage versioned and hashed, and rejects assets that fail validation.

**Stands in for:** [ComfyUI-3D-Pack](../../docs/repositories/comfyui-3d-pack.md) used as a repeatable batch pipeline. A JSON list of steps replaces the node graph, and each step runs one kit tool as its own process.

## How it works

- **A workflow is a JSON file of steps.** Each step names a `run` type: `inflate`, `remesh`, `autorig`, `validate` or `mesh2splat`. It can also give `params`, an `input` (an earlier step's id, defaulting to the previous main step) and `optional`.
- **Each stage is recorded.** The manifest stores the stage's id, the step it consumes, its parameters, input and output file names with SHA-256, run time and result. Every stage is a separate file, and nothing is overwritten.
- **Failures are explained.** A `validate` step reads [validate_asset.py](../../scripts/blender/validate_asset.py)'s report. A failed Floor check rejects the asset, and the manifest names the failing checks.
- **Optional steps are side outputs.** They may fail without stopping the asset, and they never become the next step's input or the delivery.
- **The batch has a summary.** `batch.json` lists accepted and rejected assets with reasons.

The included [toy-factory workflow](workflows/toy-factory.json) is: inflate → remesh to 2,400 faces → validate → autorig (4 bones, swim) → validate → Gaussian splat (optional).

## Use

```sh
python assetpipe.py run workflows/toy-factory.json toys/*.png --out out/batch
```

## Test

```sh
python test.py
```

The batch is two original drawn toys (a fish and a rocket) and one empty image, run twice. Result on 2026-11-26: **pass, 15 of 15 checks**.

- Fish and rocket are accepted. Every stage is versioned, each consumes the stage before it, and every output is hashed. Both rigs pass the Floor checks, and the delivery is the rigged GLB.
- The empty image is rejected with the reason `v1-original: No object found in the image.`
- A second run gives byte-identical `v1-original` and `v2-retopo` files.
- The optional splat step ran through [splatview's mesh2splat](../splatview/README.md). Its PLYs and the FBX files are deleted after the test to keep the committed evidence small; their hashes stay in the manifests.

## What it does not do

There is no graph editor, no caching of unchanged steps and no parallel execution. It runs only the kit's tools; a step that calls an upstream model would need a reviewed adapter added to `command()`.
