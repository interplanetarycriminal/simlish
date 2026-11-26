"""Build a small rigged, animated test asset in Blender and export it as GLB and FBX.

  blender --background --factory-startup --python-exit-code 1 --python make_asset.py -- OUT_DIR

The asset is a 0.3 m segmented column (a stand-in for a toy limb) with:
  - ring topology with height loops, so it can bend
  - Smart UV Project UVs and one Principled BSDF material
  - a three-bone armature, automatic weights, then normalised and limited to 4 influences
  - one 48-frame action, "bend", that swings the middle and tip bones
Everything is created from code, so the fixture carries no binary source files.
"""
import math
import os
import sys

import bmesh
import bpy

out = sys.argv[sys.argv.index("--") + 1]
os.makedirs(out, exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.unit_settings.system = "METRIC"
scene.unit_settings.scale_length = 1.0
scene.render.fps = 24

# Geometry: rings of 24 vertices every 2.5 cm, capped with triangle fans.
RINGS, SEG, R, H = 13, 24, 0.045, 0.3
me = bpy.data.meshes.new("limb")
bm = bmesh.new()
rings = []
for i in range(RINGS):
    z = H * i / (RINGS - 1)
    r = R * (1 - 0.25 * (i / (RINGS - 1)))  # slight taper
    rings.append([bm.verts.new((r * math.cos(2 * math.pi * k / SEG), r * math.sin(2 * math.pi * k / SEG), z)) for k in range(SEG)])
for a, b in zip(rings, rings[1:]):
    for k in range(SEG):
        bm.faces.new((a[k], a[(k + 1) % SEG], b[(k + 1) % SEG], b[k]))
bottom, top = bm.verts.new((0, 0, 0)), bm.verts.new((0, 0, H))
for k in range(SEG):
    bm.faces.new((rings[0][(k + 1) % SEG], rings[0][k], bottom))
    bm.faces.new((rings[-1][k], rings[-1][(k + 1) % SEG], top))
bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
bm.to_mesh(me)
bm.free()
limb = bpy.data.objects.new("toy_limb", me)
scene.collection.objects.link(limb)
bpy.context.view_layer.objects.active = limb
limb.select_set(True)

bpy.ops.object.mode_set(mode="EDIT")
bpy.ops.mesh.select_all(action="SELECT")
bpy.ops.uv.smart_project(angle_limit=math.radians(66), island_margin=0.02)
bpy.ops.object.mode_set(mode="OBJECT")
bpy.ops.object.shade_smooth()

mat = bpy.data.materials.new("toy_plastic")
mat.use_nodes = True
bsdf = mat.node_tree.nodes["Principled BSDF"]
bsdf.inputs["Base Color"].default_value = (0.70, 0.38, 0.05, 1)
bsdf.inputs["Roughness"].default_value = 0.42
limb.data.materials.append(mat)

# Armature: root -> mid -> tip along +Z.
arm_data = bpy.data.armatures.new("limb_rig")
arm = bpy.data.objects.new("toy_rig", arm_data)
scene.collection.objects.link(arm)
bpy.context.view_layer.objects.active = arm
bpy.ops.object.mode_set(mode="EDIT")
prev = None
for name, z0, z1 in (("root", 0.0, 0.1), ("mid", 0.1, 0.2), ("tip", 0.2, 0.3)):
    b = arm_data.edit_bones.new(name)
    b.head, b.tail = (0, 0, z0), (0, 0, z1)
    if prev:
        b.parent, b.use_connect = prev, True
    prev = b
bpy.ops.object.mode_set(mode="OBJECT")

bpy.ops.object.select_all(action="DESELECT")
limb.select_set(True)
arm.select_set(True)
bpy.context.view_layer.objects.active = arm
bpy.ops.object.parent_set(type="ARMATURE_AUTO")

# Normalise and limit influences so the export contract holds.
bpy.ops.object.select_all(action="DESELECT")
limb.select_set(True)
bpy.context.view_layer.objects.active = limb
bpy.ops.object.mode_set(mode="WEIGHT_PAINT")
bpy.ops.object.vertex_group_limit_total(group_select_mode="BONE_DEFORM", limit=4)
bpy.ops.object.vertex_group_normalize_all(group_select_mode="BONE_DEFORM", lock_active=False)
bpy.ops.object.mode_set(mode="OBJECT")

# One action: bend the limb and come back.
action = bpy.data.actions.new("bend")
arm.animation_data_create()
arm.animation_data.action = action
for frame, angle in ((1, 0), (13, 35), (25, 0), (37, -35), (48, 0)):
    for bone, k in (("mid", 1.0), ("tip", 0.8)):
        pb = arm.pose.bones[bone]
        pb.rotation_mode = "XYZ"
        pb.rotation_euler = (math.radians(angle * k), 0, 0)
        pb.keyframe_insert("rotation_euler", frame=frame)
scene.frame_start, scene.frame_end = 1, 48

glb = os.path.join(out, "toy_limb.glb")
fbx = os.path.join(out, "toy_limb.fbx")
bpy.ops.object.select_all(action="SELECT")
bpy.ops.export_scene.gltf(filepath=glb, export_format="GLB", export_animations=True, export_skins=True, export_yup=True)
bpy.ops.export_scene.fbx(filepath=fbx, use_selection=False, add_leaf_bones=False, bake_anim=True)
print("wrote", glb, fbx)
