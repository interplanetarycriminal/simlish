# Asset validation

Every 3D asset is checked twice: inside Blender, where the geometry, UVs, materials and rig can be measured, and inside the consumer, where scale, up axis, skin and clips must survive the trip. Both checks exist in this catalogue and both were **tested** on [fixtures/blender-glb](../../fixtures/blender-glb/make_asset.py) with Blender 5.2.2 LTS and three r187.

## Run the Blender validator

From the catalogue root:

```
blender --background --factory-startup --python-exit-code 1 --python scripts/blender/validate_asset.py -- ASSET [REPORT.json]
```

- `ASSET` is a `.glb`, `.gltf`, `.fbx` or `.obj`. The script imports it into an empty scene. `--factory-startup` keeps user add-ons and preferences out of the result.
- `REPORT.json` is optional. The report is always printed to stdout, followed by a `PASS` or `FAIL floor checks:` line naming any failed Floor checks.
- Exit code `0` means every Floor check passed; `1` means at least one failed. Use the exit code in scripts and CI.
- With no `ASSET`, the script checks the open scene. To check a `.blend`, open it on the command line (`blender --background scene.blend --python-exit-code 1 --python scripts/blender/validate_asset.py`) and capture stdout; the report path is only read as the second argument after an asset.
- With an `ASSET`, the script resets Blender to an empty factory scene first. Do not run it that way inside a live session with unsaved work.
- Bone display shapes are excluded. Blender's glTF importer adds an `Icosphere` helper mesh for bone display; the script finds every pose bone's custom shape and lists it under `ignored_helpers` instead of checking it.

The source is [scripts/blender/validate_asset.py](../../scripts/blender/validate_asset.py). Its report follows the [mesh quality report](../../templates/mesh-quality-report.md) template.

## Floor checks: a failure blocks release

| Check | What the script measures | Why it matters |
| --- | --- | --- |
| `has_geometry` | At least one mesh object besides bone helpers | An empty or failed import |
| `no_non_manifold_edges` | Edges that are neither manifold nor boundary: three or more faces on one edge, or wire edges with no face | Breaks booleans, baking, 3D printing and some importers |
| `no_degenerate_faces` | Faces with area below 1e-12 (in mesh units) | Zero-area faces produce bad normals and NaNs in tangents |
| `consistent_normals` | Manifold edges whose two faces wind in opposite directions | Flipped faces render inside-out or black |
| `no_loose_vertices` | Vertices with no edges | Stray points inflate bounds and confuse tools |
| `has_uvs` | Every mesh has at least one UV layer | No textures can be applied or baked |
| `colour_spaces_valid` | Each image's Color output is traced through converter nodes. An sRGB image must not reach a data input, and a Non-Color image must not reach only color inputs. Alpha outputs are not traced. | Data maps read as color shade wrongly, and color maps read as data look washed out; see below |
| `rig_weights_normalised` | For skinned meshes: no vertex without deform weight, and every vertex's deform weights sum to 1 within 0.001 | Unweighted vertices stay behind; unnormalised ones scale or drift |

## Reflex checks: fix or record a written reason

| Check | What the script measures | Why it matters |
| --- | --- | --- |
| `unit_scale` | Every mesh object's scale is 1 on all axes (within 1e-4) | Unapplied scale breaks physics, modifiers and some exporters |
| `max_4_influences` | No vertex has more than 4 deform bones above 1e-6 weight | glTF skins carry four joints per vertex set; extra weights need more sets or are lost |
| `watertight` | Zero boundary edges **after welding** coincident vertices (1e-6) on a copy | Open meshes fail volume, print and some bake workflows |
| `no_ngons` | No face with more than four vertices | Ngons triangulate unpredictably on export |

## Reported but not gated

`vertices`, `faces`, `triangles`, raw `boundary_edges`, `zero_length_edges`, object `scale`, world-space `bbox_m` in meters, UV layer names and `outside_0_1` share, materials with each image's color space and the sockets it feeds, rig `hierarchy` and `roots`, and `animations` with frame ranges. Compare these with the brief's budgets and the [asset manifest](../../templates/asset-manifest.json) by hand.

Know what the script does not do. It reads mesh data without evaluating modifiers, so a `.blend` with unapplied Mirror or Subdivision modifiers is checked as its base mesh. It checks object scale but not rotation. It measures sizes in Blender's Z-up space after import. It does not check edge flow, self-intersections, silhouettes or deformation; those stay manual (see [retopology](retopology.md#inspection-list) and [rigging](rigging-and-skinning.md#inspection-list)).

### How the color-space check works

The script follows each image's **Color** output through converter nodes (Normal Map, Bump, Displacement, Separate Color, Math, Map Range, Invert, Mix, color ramps and reroutes) to the input it finally drives. It then applies two rules:

- An **sRGB** image that reaches a data input (Roughness, Metallic, Normal, Alpha, Height, Displacement, Occlusion, coat and transmission weights) fails: set it to Non-Color.
- A **Non-Color** image that reaches only color inputs (Base Color, Emission Color, Subsurface Color, tints) fails: set it to sRGB.

An image's **Alpha** output is not traced, because Blender never color-manages alpha, so a base-color texture whose alpha drives opacity is correct.

This is **tested**. `fixtures/blender-glb/colorspace_test.py` builds six materials. Four are wired wrongly on purpose: an sRGB normal map through a Normal Map node, sRGB packed roughness and metallic through Separate Color, sRGB height through a Bump node, and a base-color image set to Non-Color. Two are correct: base color with its alpha driving opacity, and Non-Color roughness. The check flags exactly the four ([evidence](../../fixtures/blender-glb/out/colorspace-test.json)).

```sh
blender --background --factory-startup --python-exit-code 1 --python fixtures/blender-glb/colorspace_test.py
```

The check still has limits:

- It does not follow node groups other than the glTF importer's occlusion output.
- It cannot tell whether an emission texture was meant to be HDR data.

When in doubt, list every image's color space in Blender's Python console:

```python
for m in bpy.data.materials:
    for n in (m.node_tree.nodes if m.use_nodes else []):
        if n.type == "TEX_IMAGE" and n.image:
            print(m.name, n.image.name, n.image.colorspace_settings.name)
```

Compare the output with the color-space table in [UVs and materials](uv-and-materials.md#pbr-maps-and-color-spaces).

**Blender exits 0 when a `--python` script raises** unless `--python-exit-code 1` is passed. Every command in this catalogue passes it, so a crashed validator can never look like a pass.

## What the fixture's real reports showed

Both exports of the 0.3 m rigged limb passed every Floor and Reflex check ([GLB report](../../fixtures/blender-glb/out/report-glb.json), [FBX report](../../fixtures/blender-glb/out/report-fbx.json)).

| Field | GLB | FBX | What it teaches |
| --- | --- | --- | --- |
| `vertices` | 430 | 314 | glTF splits vertices at UV seams and hard edges |
| `faces` / `triangles` | 624 / 624 | 336 / 624 | glTF stores triangles; FBX kept the quads. Compare triangle counts across formats |
| `boundary_edges` / `boundary_edges_welded` | 224 / 0 | 0 / 0 | The GLB only looks open. Judge watertightness after welding |
| `bbox_m.size` | 0.09, 0.09, 0.3 | 0.09, 0.09, 0.3 | Meters and scale survived both formats |
| `ignored_helpers` | `Icosphere` | none | The glTF importer's bone-display mesh was excluded |
| Rig | 3 bones, root `root`, 0 unweighted, 0 non-normalized, 0 over 4 | same | Limit and normalize before export held |
| `animations` | `bend`, frames 1-48 | `toy_rig\|toy_rig\|bend`, frames 1-48 | FBX round trip renamed the clip |
| Materials | `toy_plastic`, no textures | same | Color-space check not exercised |

## Run the Three.js check

[`check.mjs`](../../fixtures/blender-glb/check.mjs) loads the GLB in headless Chrome with three r187 (from the jsDelivr CDN, via [viewer.html](../../fixtures/blender-glb/viewer.html)) and checks the handoff contract.

```
cd fixtures/blender-glb
node check.mjs [--file out/toy_limb.glb]
```

It needs Node.js, Chrome (set `CHROME` to its path if it is not in a standard location) and `ffmpeg` on the PATH for the contact sheet. It serves the fixture folder on 127.0.0.1, so `--file` must be a path inside that folder. It writes `out/three-check.json` and `out/three-sheet.png` and exits 0 when every check passes.

| Check | Passes when | Fixture result |
| --- | --- | --- |
| `loads` | At least one mesh | 1 mesh |
| `skinned` | Exactly 1 skinned mesh and 3 bones | root, mid, tip |
| `clip` | A clip matching `bend` lasts 47/24 s within 0.05 s | `bend`, 2.0 s, 9 tracks |
| `metersAndYUp` | Height 0.3 m within 3 mm, and Y is the longest axis | 0.09 × 0.3 × 0.09 m, Y up |
| `animationDeforms` | The tip bone moves more than 1 cm between t = 0 and 0.5 s | Moved about 6 cm |
| `seekRepeatable` | Seeking back to 0.5 s returns the identical tip position | Identical |

The expected values are specific to the fixture. To check another asset, copy the fixture folder and change the bone count, clip name, duration and height to the values in that asset's manifest. To rebuild the fixture asset itself: `blender --background --factory-startup --python-exit-code 1 --python fixtures/blender-glb/make_asset.py -- fixtures/blender-glb/out`.

## Evidence to keep

For each delivered asset version:

- The validator report JSON for every delivered format, named after the asset version.
- The consumer check output (`three-check.json` or equivalent) and its contact sheet.
- The exact commands, Blender version, three version and Chrome version (the reports record Blender; `three-check.json` records Chrome and three).
- A SHA-256 hash of the checked file, so the evidence is tied to one file.
- Test-pose renders for rigged assets and the lighting contact sheet for textured ones.
- A filled [mesh quality report](../../templates/mesh-quality-report.md), and a [rig validation report](../../templates/rig-validation-report.md) for skinned assets, linked from the [asset manifest](../../templates/asset-manifest.json).

Apply the tiers as defined in the [quality gates](../../QUALITY_GATES.md): Floor failures block release, Reflex failures need a fix or a written reason from the creative owner.
