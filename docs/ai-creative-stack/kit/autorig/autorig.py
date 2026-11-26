"""autorig: predict a bone chain and skin weights for a mesh, then add a test clip. Runs inside Blender.

Our own stand-in for UniRig-style automatic rigging, for chain-shaped bodies (fish, tails, tentacles,
limbs, snakes, toy segments). It is not a learned humanoid rig predictor.

  blender --background --factory-startup --python-exit-code 1 --python autorig.py -- in.glb out_dir \
          [--bones 4] [--anim swim|bend|none] [--frames 48] [--amplitude 25] [--weights segment|heat] [--root auto|first|last]

1. The mesh's principal axis comes from PCA of its vertices.
2. The axis is sliced into equal spans; each joint is the centroid of the vertices in its slice, so the
   skeleton follows the body's centreline rather than a straight line.
3. The root goes at the thicker end (body thickness near each end); --root first|last overrides it.
4. Weights (segment mode, our own): inverse fourth power of each vertex's distance to each bone segment,
   kept for the three nearest bones, then normalised. Heat mode uses Blender's automatic weights.
5. Weights are limited to 4 influences and normalised, as glTF requires.
6. A looping clip: "swim" sends a travelling wave down the chain; "bend" curls it in one plane.

Writes out_dir/<name>.glb, out_dir/<name>.fbx and out_dir/<name>.rig.json.
"""
import json
import math
import os
import sys

import bpy
import numpy as np
from mathutils import Vector

argv = sys.argv[sys.argv.index("--") + 1:]
opts = {"--bones": "4", "--anim": "swim", "--frames": "48", "--amplitude": "25", "--weights": "segment", "--root": "auto"}
pos = []
i = 0
while i < len(argv):
    if argv[i] in opts:
        opts[argv[i]] = argv[i + 1]
        i += 2
    else:
        pos.append(argv[i])
        i += 1
src, out_dir = pos[0], pos[1]
n_bones, anim, frames = int(opts["--bones"]), opts["--anim"], int(opts["--frames"])
amplitude, weight_mode = float(opts["--amplitude"]), opts["--weights"]
name = os.path.splitext(os.path.basename(src))[0] + "_rigged"
os.makedirs(out_dir, exist_ok=True)

# Import and gather the mesh.
bpy.ops.wm.read_factory_settings(use_empty=True)
ext = os.path.splitext(src)[1].lower()
if ext in (".glb", ".gltf"):
    bpy.ops.import_scene.gltf(filepath=src)
elif ext == ".fbx":
    bpy.ops.import_scene.fbx(filepath=src)
else:
    bpy.ops.wm.obj_import(filepath=src)
meshes = [o for o in bpy.context.scene.objects if o.type == "MESH"]
bpy.ops.object.select_all(action="DESELECT")
for o in meshes:
    o.select_set(True)
bpy.context.view_layer.objects.active = meshes[0]
if len(meshes) > 1:
    bpy.ops.object.join()
body = bpy.context.view_layer.objects.active
body.parent = None
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
body.name = "body"

V = np.array([v.co[:] for v in body.data.vertices])
centre = V.mean(0)
_, _, vt = np.linalg.svd(V - centre, full_matrices=False)
axis = vt[0]
t = (V - centre) @ axis
lo, hi = np.percentile(t, 1), np.percentile(t, 99)
span = hi - lo
# Root at the thicker end: thickness through the body (the thinnest principal axis) near each end.
# Vertex counts mislead here: a wide, thin fin or tail tip holds many vertices but little body.
depth = (V - centre) @ vt[2]
end_lo = t < lo + 0.3 * span
end_hi = t > hi - 0.3 * span
thick_lo = np.ptp(depth[end_lo]) if end_lo.any() else 0.0
thick_hi = np.ptp(depth[end_hi]) if end_hi.any() else 0.0
root_opt = opts["--root"]
if root_opt == "last" or (root_opt == "auto" and thick_hi > thick_lo):
    axis, t = -axis, -t
    lo, hi = -hi, -lo

joints = []
for k in range(n_bones + 1):
    tk = lo + span * k / n_bones
    half = 0.5 * span / n_bones
    sel = np.abs(t - tk) <= half
    if sel.sum() < 3:
        sel = np.argsort(np.abs(t - tk))[:12]
    p = V[sel].mean(0)
    # Keep the joint's position along the axis exact; take the cross-section centroid from the slice.
    p = p + axis * (tk - (p - centre) @ axis)
    joints.append(p)
joints = np.array(joints)

# Armature.
arm_data = bpy.data.armatures.new("rig")
arm = bpy.data.objects.new("rig", arm_data)
bpy.context.scene.collection.objects.link(arm)
bpy.context.view_layer.objects.active = arm
bpy.ops.object.mode_set(mode="EDIT")
prev = None
bone_names = []
for k in range(n_bones):
    b = arm_data.edit_bones.new(f"seg_{k}")
    b.head, b.tail = Vector(joints[k]), Vector(joints[k + 1])
    if prev:
        b.parent, b.use_connect = prev, True
    prev = b
    bone_names.append(b.name)
bpy.ops.object.mode_set(mode="OBJECT")

# Weights.
bpy.ops.object.select_all(action="DESELECT")
body.select_set(True)
arm.select_set(True)
bpy.context.view_layer.objects.active = arm
if weight_mode == "heat":
    bpy.ops.object.parent_set(type="ARMATURE_AUTO")
else:
    bpy.ops.object.parent_set(type="ARMATURE_NAME")  # empty groups; we fill them
    a, b = joints[:-1], joints[1:]
    ab = b - a
    tt = np.clip(((V[:, None, :] - a[None]) * ab[None]).sum(-1) / (ab * ab).sum(-1)[None], 0, 1)
    closest = a[None] + tt[..., None] * ab[None]
    d = np.linalg.norm(V[:, None, :] - closest, axis=-1) + 1e-6
    w = 1.0 / d ** 4
    order = np.argsort(-w, axis=1)
    keep = np.zeros_like(w, bool)
    np.put_along_axis(keep, order[:, :3], True, axis=1)
    w = np.where(keep, w, 0)
    w /= w.sum(1, keepdims=True)
    for k, bn in enumerate(bone_names):
        g = body.vertex_groups.get(bn) or body.vertex_groups.new(name=bn)
        for vi in np.nonzero(w[:, k] > 1e-4)[0]:
            g.add([int(vi)], float(w[vi, k]), "REPLACE")

bpy.ops.object.select_all(action="DESELECT")
body.select_set(True)
bpy.context.view_layer.objects.active = body
bpy.ops.object.mode_set(mode="WEIGHT_PAINT")
bpy.ops.object.vertex_group_limit_total(group_select_mode="BONE_DEFORM", limit=4)
bpy.ops.object.vertex_group_normalize_all(group_select_mode="BONE_DEFORM", lock_active=False)
bpy.ops.object.mode_set(mode="OBJECT")

# A looping test clip. Swim: yaw about the axis perpendicular to the chain and to "up", with phase lag.
up = np.array([0.0, 0.0, 1.0])
if abs(axis @ up) > 0.9:
    up = np.array([0.0, 1.0, 0.0])
if anim != "none":
    action = bpy.data.actions.new("swim" if anim == "swim" else "bend")
    arm.animation_data_create()
    arm.animation_data.action = action
    scene = bpy.context.scene
    scene.render.fps = 24
    scene.frame_start, scene.frame_end = 1, frames
    keys = 8
    for kf in range(keys + 1):
        f = 1 + round((frames - 1) * kf / keys)
        phase = 2 * math.pi * kf / keys
        for k, bn in enumerate(bone_names):
            pb = arm.pose.bones[bn]
            pb.rotation_mode = "XYZ"
            grow = (k + 1) / n_bones  # stronger toward the free end
            if anim == "swim":
                ang = math.radians(amplitude) * grow * math.sin(phase - 1.1 * k)
            else:
                ang = math.radians(amplitude) * grow * math.sin(phase)
            # Bone-local Z points roughly sideways for a chain built along +Y in bone space; rotate about local X/Z.
            pb.rotation_euler = (0.0, 0.0, ang)
            pb.keyframe_insert("rotation_euler", frame=f)

glb = os.path.join(out_dir, name + ".glb")
fbx = os.path.join(out_dir, name + ".fbx")
bpy.ops.object.select_all(action="SELECT")
bpy.ops.export_scene.gltf(filepath=glb, export_format="GLB", export_animations=anim != "none", export_skins=True, export_yup=True)
bpy.ops.export_scene.fbx(filepath=fbx, use_selection=False, add_leaf_bones=False, bake_anim=anim != "none")

report = {
    "tool": "autorig", "input": os.path.basename(src), "bones": n_bones, "weights": weight_mode, "anim": anim, "frames": frames,
    "axis": np.round(axis, 4).tolist(), "joints_m": np.round(joints, 5).tolist(),
    "bone_lengths_m": np.round(np.linalg.norm(np.diff(joints, axis=0), axis=1), 5).tolist(),
    "root": root_opt, "thickness_ends_m": [round(float(thick_lo), 5), round(float(thick_hi), 5)], "vertices": len(V), "outputs": [os.path.basename(glb), os.path.basename(fbx)],
}
with open(os.path.join(out_dir, name + ".rig.json"), "w", encoding="utf-8", newline="\n") as fh:
    fh.write(json.dumps(report, indent=2) + "\n")
print(json.dumps(report))
