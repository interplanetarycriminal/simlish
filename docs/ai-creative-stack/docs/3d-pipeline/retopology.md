# Retopology

Generated and scanned meshes arrive dense, triangulated and with arbitrary edge flow. Retopology rebuilds the surface with fewer faces and an edge layout that suits the job: deformation, clean UV seams, level of detail or a triangle budget. It is a new mesh, not a cleaned copy of the old one, and that has consequences for everything downstream.

## When to retopologize

| Asset use | What the topology must do | Usual route (general practice) |
| --- | --- | --- |
| Static web prop | Meet a triangle budget | Decimate, then bake normals from the dense source |
| Hero static model | Clean silhouette, tidy shading, sensible UV seams | Retopologize or decimate, then bake |
| Deforming character or creature | Edge loops around joints, mouth and eyes; quads where it bends | Manual or guided retopology in Blender |
| Background object or LOD | Fewer triangles at distance | Decimate per LOD |
| Physics collider | Simple, convex where possible | Separate proxy shapes, not the render mesh |

Order matters: **retopology, then UVs, then textures, then rig.** Retopologizing after any of those throws their work away (see the last section).

## MeshAnything V2 or Blender

| | [MeshAnything V2](../repositories/meshanything-v2.md) | Blender retopology |
| --- | --- | --- |
| Input | Mesh (`.obj` or `.ply`) or a point cloud `.npy` of shape (N, 6) with xyz and unit normals, at least 8,192 points | Any mesh in the scene |
| Output | Untextured triangle `.obj`, **at most 1,600 faces**, flat orange face colors, no UVs | Quads, triangles or mixed, any count |
| Scale | Inputs are normalized to a unit box; the result must be scaled and placed back on the original | Works in scene units (meters) |
| Edge flow | Artist-like triangle layout learned from training meshes | Whatever the artist draws: snapping to faces plus a Shrinkwrap modifier, the Remesh modifier (voxel or quad), or Decimate |
| Weak inputs | Soft or blobby meshes from feed-forward generators often give poor results; the authors suggest scans, SDS methods or Rodin output. Test SF3D or TRELLIS.2 output on it before relying on it | None specific |
| Hardware and speed | About 8 GB VRAM and 45 s per mesh on an A6000 (documented); Linux, tested on Ubuntu 22 with CUDA 11.8 | CPU, interactive |
| License | S-Lab License 1.0: **non-commercial code**. Hugging Face tags the weights MIT, but running them needs the S-Lab code. Treat commercial use as not allowed without the authors' permission | Blender is GPL; your output meshes are yours |
| Evidence | documented, not run | Blender export and validation tested in [fixtures/blender-glb](../../fixtures/blender-glb/make_asset.py); retopology itself not tested |

`registry/compatibility.json` classifies the two as a *recommended alternative* (documented): MeshAnything V2 can make a low-poly stand-in, but deformation topology for characters still needs Blender. Two generator-side options also exist: Stable Fast 3D's `--remesh_option triangle|quad` with `--target_vertex_count`, and TRELLIS.2's GLB export `decimation_target` and remesh options. Both are documented upstream and not run here. [Blender Skills](../repositories/blender-skills.md) documents a `blender-retopology-uv` skill for agent-driven work (not run).

MeshAnything V2 settings worth recording: `--input_type`, `--mc` (Marching Cubes preprocessing for meshes that did not come from Marching Cubes; takes several minutes), `--mc_level` (7 is 128³; 8 is 256³, slower but keeps fine detail). The README says +Y up gives better results, so orient the input before running and undo the rotation after.

## Inspection list

Run [`validate_asset.py`](../../scripts/blender/validate_asset.py) on the retopologized mesh and look at the rest by eye. Record both in the [mesh quality report](../../templates/mesh-quality-report.md).

| Check | How to look | Report field | Tier |
| --- | --- | --- | --- |
| Non-manifold edges | Edit Mode: Select > Select All by Trait > Non Manifold | `non_manifold_edges` | Floor |
| Degenerate faces | Mesh > Clean Up > Degenerate Dissolve, then re-check | `degenerate_faces`, `zero_length_edges` | Floor |
| Normals | Face Orientation overlay; Mesh > Normals > Recalculate Outside | `inconsistent_normal_edges` | Floor |
| Loose geometry | Select loose, delete | `loose_vertices` | Floor |
| Edge flow | Wireframe review: loops follow form; poles sit away from bending areas | not automated | Reflex |
| Self-intersections | Blender's 3D-Print Toolbox extension (general practice) | not automated | Reflex |
| Silhouette | Overlay the new mesh on the dense source from six or more views; compare render masks | not automated | Floor for hero assets |
| Budgets | Triangle and material counts against the brief | `triangles`, `ngons` | Reflex (`no_ngons`) |
| Deformation areas | Elbows, knees, fingers, shoulders, mouth: at least three loops across each bend (general practice) | not automated | Floor for rigged assets |
| Watertightness | Boundary edges after welding coincident vertices | `boundary_edges_welded` | Reflex (`watertight`) |
| Scale and transforms | Object scale 1, rotation applied, size in meters matches the source | `scale`, `bbox_m` | Reflex (`unit_scale`) |

### The glTF seam lesson

glTF stores one vertex per unique combination of position, normal and UV. A GLB therefore **splits vertices along UV seams and hard edges**. In the fixture, the same closed 0.3 m limb came back from GLB with 430 vertices and 224 boundary edges, and from FBX with 314 vertices and 0 boundary edges ([GLB report](../../fixtures/blender-glb/out/report-glb.json), [FBX report](../../fixtures/blender-glb/out/report-fbx.json)). The mesh was not open. Weld coincident vertices before judging watertightness: the validator does this on a copy and reports `boundary_edges_welded`, which was 0 for both files.

The same split is why every UV seam costs vertices in the delivered GLB. Place seams where they also earn their keep.

## Retopology breaks UVs and vertex correspondence

A retopologized mesh has new vertices in new places. Anything stored per vertex or per face corner on the old mesh is gone or wrong: UVs, vertex colors, skin weights, shape keys and morph targets. Plan to rebuild or transfer each one.

1. **Keep the dense source.** Save it as its own stage before retopology. See [export contracts](export-contracts.md#versioned-stages).
2. **Unwrap the new mesh.** See [UV and materials](uv-and-materials.md).
3. **Bake detail from dense to low.** Cycles Bake with Selected to Active: normal, base color and ambient occlusion, with a cage or extrusion distance set. Check the bake for projection errors at thin parts.
4. **Transfer what a transfer can carry.** The Data Transfer modifier moves vertex colors, custom normals and vertex groups by nearest surface. Inspect the result; it is an approximation.
5. **Re-skin after retopology.** If the asset was rigged, transfer or regenerate weights, then rerun the [test poses](rigging-and-skinning.md#test-poses).
6. **Shape keys do not transfer cleanly.** Rebuild them, or use a Surface Deform modifier as a starting point.

Never retopologize a rigged, textured asset unless the brief budgets for redoing UVs, textures and skinning.

[Mesh quality report template](../../templates/mesh-quality-report.md) · [Asset validation](asset-validation.md)
