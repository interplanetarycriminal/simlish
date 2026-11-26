# Animation and physics

Animate only what the brief needs. Every animated stage adds files to version, caches to bake and checks to run. This page covers Blender keyframes, constraints and simulations, how to freeze them into something another tool can replay, and how to keep playback seekable for the web.

Blender keyframe export to GLB and seekable playback in Three.js were **tested** in [fixtures/blender-glb](../../fixtures/blender-glb/make_asset.py). Simulations, constraints and caches were not run here; that guidance is general practice.

## What each Blender tool makes, and what survives export

| Blender feature | Use it for | Survives to GLB? | How to deliver it (general practice) |
| --- | --- | --- | --- |
| Keyframes on objects | Rigid parts, cameras, props | Yes, as node translation, rotation and scale tracks | Export directly |
| Keyframes on bones (actions) | Skinned characters | Yes, as skin animation. Tested in the fixture | Export directly; check clip names |
| Shape keys | Facial shapes, corrective shapes | Yes, as morph targets | Export; keep the count small for the web |
| Constraints (IK, Track To, Child Of, Copy Rotation) | Posing and rig control | No. glTF has no constraints | Pose > Animation > Bake Action with Visual Keying, then export the baked action |
| Drivers | Linked properties | No | Bake to keyframes |
| Rigid body (Bullet) | Falling, stacking, collisions | No, until baked | Object > Rigid Body > Bake To Keyframes, then export object tracks |
| Cloth and soft body | Fabric, flags, jelly | No | Point cache for renders; for interactive use, a short morph-target or vertex-cache loop, or a rendered clip |
| Fluid (Mantaflow) | Liquid, smoke, fire | No | Render to frames; mesh sequences are usually too heavy for the web |
| Particles and hair | Debris, sparks, grass | No (instancing is outside core glTF) | Render to frames, or rebuild in the browser with seeded particles under the time contract |

## Bake caches and record versions

Simulation results depend on the Blender version, solver settings, substeps and sometimes thread count. A re-simulation on another machine may not match the approved take. Bake once, approve the bake, and ship the bake.

1. Set the scene frame rate and frame range first. Changing them after a bake invalidates it.
2. Bake every cache to disk in the project folder, not a temporary directory: Physics properties > Cache > Bake, and the fluid domain cache directory.
3. Record in the [asset manifest](../../templates/asset-manifest.json): Blender version, cache path, frame range, frame rate, substeps or quality steps, any random seed, and the date of the bake.
4. Treat the baked cache as a versioned stage (`animated`) in [export contracts](export-contracts.md#versioned-stages). Never re-bake over an approved cache; write a new version.
5. For delivery, convert the bake to keyframes, morph targets or rendered frames as in the table above, and record which conversion you used.

## Seekable playback for the web

A scene that plays live and also renders to film must keep the [time contract](../contracts/time-contract.md): state is a function of time, not of elapsed frames.

- **Set absolute time, never advance by delta.** The fixture's [viewer](../../fixtures/blender-glb/viewer.html) calls `mixer.setTime(t)` on a Three.js `AnimationMixer` for every frame it shows. A render loop that calls `mixer.update(delta)` is a stepped clock and cannot seek.
- **Baked simulations become seekable.** A simulation is a stepped clock while it runs. Once baked to keyframes or morph targets it becomes a function of time and can be scrubbed, paused and rendered out of order.
- **Prove it.** [check.mjs](../../fixtures/blender-glb/check.mjs) seeks the GLB to t = 0, 0.5 and 1.5 s, then seeks back to 0.5 s and requires the same tip-bone position. It passed: the tip moved from (0, 0.2, 0) to (0, 0.1826, 0.05637) m at 0.5 s, and the repeat matched exactly ([three-check.json](../../fixtures/blender-glb/out/three-check.json)).
- **Record durations as the consumer sees them.** The fixture's action runs from frame 1 to 48 at 24 fps. Three.js reported clip `bend` as 2.0 s; the check accepts any value within 0.05 s of 47/24 s. Exporters sample and pad differently, so write down the duration the consumer reports, not the one you expect.

## Clip names are part of the contract

**Lesson from the fixture:** exported to FBX and imported back, the action named `bend` became `toy_rig|toy_rig|bend` ([FBX report](../../fixtures/blender-glb/out/report-fbx.json)). The GLB kept `bend`. Code that plays a clip by name breaks silently when the name changes.

- Name every action for what it does: `walk`, `idle`, `open_lid`. Avoid Blender defaults such as `ArmatureAction.001`.
- List the expected clip names and durations in the [asset manifest](../../templates/asset-manifest.json).
- After every export, import the file and compare names. `validate_asset.py` lists them under `animations`; the Three.js check lists them under `stats.animations`.
- If a consumer renames clips, map names explicitly in code and record the mapping, rather than matching by substring.

## Before exporting animation

General practice for Blender actions going to GLB or FBX:

1. **One action per clip.** Keep each clip as its own action, or push actions down to NLA strips, so the exporter writes them as separate named clips instead of one long merged track.
2. **Start clips where they should start.** Set each action's frame range explicitly. The fixture's `bend` spans frames 1 to 48, and the validator reports that range under `animations`.
3. **Bake what the format cannot carry.** Constraints, drivers and simulations become plain keyframes first (table above).
4. **Apply transforms on the armature and mesh** before animating, not after. Animation recorded on an unapplied scale or rotation plays wrongly once the transform is applied.
5. **Keep loops closed.** For cyclic clips, make the first and last poses match, as the fixture's `bend` does (0 degrees at frames 1, 25 and 48).
6. **Re-run both checks after export**: the [validator](asset-validation.md) for clip names and frame ranges, and the consumer check for duration, deformation and seeking.

## Rendered frames

When the deliverable is film rather than a live scene:

- Render numbered frames with fixed zero padding (`shot010_v002_0001.exr`). Use EXR for compositing (linear, high bit depth, multiple passes) and PNG for direct encoding.
- Record the frame rate next to the frames. FFmpeg needs it explicitly (`-framerate 24`), as the time contract's driver table notes.
- Check the master with ffprobe against the declared size, frame rate, frame count and duration ([motion and video gate](../../QUALITY_GATES.md)).
- Keep one timeline authority for the final edit. See [FFmpeg](../repositories/ffmpeg.md), [Remotion](../repositories/remotion.md) and [HyperFrames](../repositories/hyperframes.md).

## Acceptance

Floor: clips play, seek and repeat in the consumer; names and durations match the manifest; bakes are on disk with recorded versions. Reflex: no constraint, driver or live simulation left unbaked in a delivery file. Record evidence with the [quality gates](../../QUALITY_GATES.md).
