# remesh

Reduces a mesh to a face budget with quadric error metrics, keeping it closed and its UVs valid.

**Stands in for:** [MeshAnything V2](../../docs/repositories/meshanything-v2.md)'s low-poly output (its cap is 1,600 faces) and Blender decimation, as the retopology step of the asset factory.

## How it works

- **Error measure.** Each vertex carries the sum of the squared-distance quadrics of its faces, weighted by area. Collapsing an edge costs the combined quadric evaluated at the surviving vertex.
- **Half-edge collapse.** An edge always collapses onto one of its existing vertices. No new vertices are made, so every surviving vertex keeps its original UV and the texture is never resampled.
- **Safety checks on every collapse.**
  - The link condition keeps the mesh manifold: the two vertices may share only the edge's two opposite vertices.
  - A flip check rejects any collapse that would turn a face beyond `--max-flip`.
  - Open edges and UV seams get strong penalty planes, so silhouettes and seams stay in place.
- **Order.** Collapses come off a lazy priority queue with per-vertex versions, and the run stops at the budget.

## Use

```sh
python remesh.py in.glb out/low.glb --faces 1600
python remesh.py in.glb out/low.glb --faces 800 --keep-boundary 5000 --max-flip 0.3
```

A JSON report beside the output records the face and vertex counts and watertightness, before and after.

## Test

```sh
python test.py
```

The test decimates the [inflated toy fish](../inflate3d/README.md), 8,032 faces, to 1,600 and to 800. It measures surface error with its own exact point-to-triangle distance from 4,000 points sampled on the original. Result on 2026-11-26: **pass, 17 of 17 checks**.

| Budget | Faces | Watertight | Mean error | Max error | Volume kept | Time |
| --- | --- | --- | --- | --- | --- | --- |
| 1,600 | 1,600 | Yes | 0.044 % of size | 0.42 % | 99.4 % | 11 s |
| 800 | 800 | Yes | 0.084 % | 0.48 % | 98.8 % | 7 s |

The 1,600-face result also passes the [Blender validator](../../scripts/blender/validate_asset.py)'s Floor checks.

## What it does not do

It is a decimator, not a quad retopologiser. The output is triangles, and its edge flow is not laid out for deformation, so characters that bend still need deformation-aware topology (see [retopology](../../docs/3d-pipeline/retopology.md)). It is pure Python: about 10 seconds for 8,000 faces. Expect minutes above 100,000.
