"""Negative test for the validator's colour-space check. Builds six materials, some wired wrongly on purpose,
and asserts that exactly the wrong ones are flagged.

  blender --background --factory-startup --python-exit-code 1 --python colorspace_test.py
"""
import importlib.util
import os
import sys

import bpy

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("validate_asset", os.path.join(HERE, "..", "..", "scripts", "blender", "validate_asset.py"))
va = importlib.util.module_from_spec(spec)
spec.loader.exec_module(va)  # the validator only runs main() when executed directly

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.mesh.primitive_plane_add()
obj = bpy.context.object


def image(name, colorspace):
    img = bpy.data.images.new(name, 8, 8)
    img.colorspace_settings.name = colorspace
    return img


def material(name, wire):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    bsdf = nt.nodes["Principled BSDF"]
    wire(nt, bsdf)
    obj.data.materials.append(m)


def tex(nt, img):
    n = nt.nodes.new("ShaderNodeTexImage")
    n.image = img
    return n


def normal_via_normal_map(nt, bsdf):  # WRONG: sRGB normal map through a Normal Map node
    t = tex(nt, image("normal_srgb", "sRGB"))
    nm = nt.nodes.new("ShaderNodeNormalMap")
    nt.links.new(t.outputs["Color"], nm.inputs["Color"])
    nt.links.new(nm.outputs["Normal"], bsdf.inputs["Normal"])


def packed_orm_via_separate(nt, bsdf):  # WRONG: sRGB packed roughness/metallic through Separate Color
    t = tex(nt, image("orm_srgb", "sRGB"))
    sep = nt.nodes.new("ShaderNodeSeparateColor")
    nt.links.new(t.outputs["Color"], sep.inputs["Color"])
    nt.links.new(sep.outputs["Green"], bsdf.inputs["Roughness"])
    nt.links.new(sep.outputs["Blue"], bsdf.inputs["Metallic"])


def base_colour_alpha(nt, bsdf):  # RIGHT: sRGB base colour; its alpha output drives Alpha
    t = tex(nt, image("albedo_srgb", "sRGB"))
    nt.links.new(t.outputs["Color"], bsdf.inputs["Base Color"])
    nt.links.new(t.outputs["Alpha"], bsdf.inputs["Alpha"])


def base_colour_noncolor(nt, bsdf):  # WRONG: colour image marked Non-Color
    t = tex(nt, image("albedo_noncolor", "Non-Color"))
    nt.links.new(t.outputs["Color"], bsdf.inputs["Base Color"])


def roughness_noncolor(nt, bsdf):  # RIGHT: Non-Color roughness straight in
    t = tex(nt, image("rough_noncolor", "Non-Color"))
    nt.links.new(t.outputs["Color"], bsdf.inputs["Roughness"])


def height_via_bump(nt, bsdf):  # WRONG: sRGB height through a Bump node
    t = tex(nt, image("height_srgb", "sRGB"))
    bump = nt.nodes.new("ShaderNodeBump")
    nt.links.new(t.outputs["Color"], bump.inputs["Height"])
    nt.links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])


cases = {"normal_via_normal_map": True, "packed_orm_via_separate": True, "base_colour_alpha": False,
         "base_colour_noncolor": True, "roughness_noncolor": False, "height_via_bump": True}
for name in cases:
    material(name, globals()[name])

issues = va.mesh_checks(obj)["colour_space_issues"]
flagged = {name: any(i.startswith(name + ":") for i in issues) for name in cases}
for name, expected in cases.items():
    print(f"{'PASS' if flagged[name] == expected else 'FAIL'}  {name}: expected {'flag' if expected else 'no flag'}, got {'flag' if flagged[name] else 'no flag'}")
import json
result = {"test": "colour-space check", "blender": bpy.app.version_string, "cases": {n: {"expected_flag": e, "flagged": flagged[n]} for n, e in cases.items()}, "issues": issues, "pass": flagged == cases}
with open(os.path.join(HERE, "out", "colorspace-test.json"), "w", encoding="utf-8", newline="\n") as f:
    f.write(json.dumps(result, indent=2) + "\n")
sys.exit(0 if flagged == cases else 1)
