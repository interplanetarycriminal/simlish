# Rig validation report

A predicted rig is a starting point. This report decides whether it ships.

| Field | Value |
| --- | --- |
| Asset id and rig version | |
| Rig source | UniRig (commit, checkpoint), Blender manual, or other |
| Validator report | `scripts/blender/validate_asset.py` JSON |

## Structure

| Check | Result | Notes |
| --- | --- | --- |
| Single root, sensible hierarchy | | List the chain. |
| Joints at anatomical or mechanical pivots | | |
| Bone roll and orientation consistent | | |
| Rest pose matches the bind mesh | | |
| Deform bones limited to what moves | | |

## Weights

| Check | Result | Notes |
| --- | --- | --- |
| No unweighted vertices | | |
| Weights normalized | | |
| At most 4 influences per vertex (glTF) | | |

## Test poses

Pose every joint to the limits the animation needs, and attach a still of each. Weight sums can pass while a joint still creases: the catalogue's own fixture shows a crease at the middle joint with automatic weights.

| Pose | Volume loss | Creases or candy-wrapping | Mesh penetration | Verdict |
| --- | --- | --- | --- | --- |

## Export

| Target | Format | Clip names after re-import | Scale and up axis | Verdict |
| --- | --- | --- | --- | --- |
| Three.js | GLB | | | |
| Engine or DCC | FBX | | FBX can rename actions (`bend` became `toy_rig\|toy_rig\|bend`). | |

## Verdict

Pass, refine (list the fixes), or fail. Name who decided.
