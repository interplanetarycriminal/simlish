# Mesh quality report

Generate the numbers with the validator, then add judgement:

```sh
blender --background --factory-startup --python-exit-code 1 --python scripts/blender/validate_asset.py -- ASSET.glb report.json
```

| Field | Value |
| --- | --- |
| Asset id and version | |
| File and SHA-256 | |
| Blender version | |
| Report JSON | |

## Floor checks (any failure blocks delivery)

| Check | Result | Notes |
| --- | --- | --- |
| Has geometry | | |
| No non-manifold edges | | |
| No degenerate faces | | |
| Consistent normals | | |
| No loose vertices | | |
| Has UVs | | |
| Texture color spaces valid | | Roughness, metallic, normal and alpha maps must be Non-Color. |
| Rig weights normalized, none unweighted | | Only if rigged. |

## Reflex checks (fix, or record a reason)

| Check | Result | Reason if waived |
| --- | --- | --- |
| Unit scale applied | | |
| At most 4 influences per vertex | | |
| Watertight after welding | | Imported glTF splits vertices at UV seams; read `boundary_edges_welded`. |
| No n-gons | | |

## Measurements

| Measure | Value | Budget |
| --- | --- | --- |
| Triangles | | |
| Bounding box (m) | | |
| Texture resolution | | |
| File size | | |

## Visual review

Attach a turntable or three stills under two lighting set-ups. Note silhouette problems, shading artifacts and texture seams.

## Verdict

Pass, pass with recorded waivers, or fail. Name who decided.
