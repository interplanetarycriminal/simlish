"""Validate a 3D asset inside Blender and write a machine-readable mesh and rig quality report.

Run headless:
  blender --background --factory-startup --python-exit-code 1 --python scripts/blender/validate_asset.py -- ASSET [REPORT.json]

ASSET may be .glb, .gltf, .fbx or .obj. With no ASSET, the open scene is checked.
The report follows templates/mesh-quality-report.md. Exit code 0 when every Floor check passes, 1 otherwise.
"""
import json
import math
import os
import sys

import bmesh
import bpy
from mathutils import Vector

args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
asset = args[0] if args else None
report_path = args[1] if len(args) > 1 else None

EPS_AREA = 1e-12
# Inputs that expect linear data, and inputs that expect colour. Images reach them directly or through converters.
DATA_SOCKETS = {"Roughness", "Metallic", "Normal", "Alpha", "Displacement", "Height", "Occlusion", "Specular IOR Level",
                "Coat Roughness", "Coat Normal", "Transmission Weight", "Subsurface Weight", "Sheen Roughness", "Anisotropic"}
COLOUR_SOCKETS = {"Base Color", "Emission Color", "Emission", "Subsurface Color", "Coat Tint", "Sheen Tint"}
PASS_THROUGH = {"SEPARATE_COLOR", "SEPRGB", "SEPARATE_RGB", "SEPARATE_XYZ", "MATH", "MAP_RANGE", "INVERT", "CLAMP",
                "VALTORGB", "RGB_CURVE", "CURVE_RGB", "GAMMA", "BRIGHTCONTRAST", "MIX", "MIX_RGB", "REROUTE"}


def trace(link, depth=0):
    """Yield the semantic input names an image link finally reaches."""
    node, socket = link.to_node, link.to_socket
    if node.type == "NORMAL_MAP":
        yield "Normal"
    elif node.type in ("BUMP", "DISPLACEMENT"):
        yield "Height" if node.type == "BUMP" else "Displacement"
    elif node.type in PASS_THROUGH and depth < 6:
        for out in node.outputs:
            for nxt in out.links:
                yield from trace(nxt, depth + 1)
    elif node.type == "GROUP" and "occlusion" in socket.name.lower():
        yield "Occlusion"  # the glTF importer's "glTF Material Output" group
    else:
        yield socket.name
MAX_INFLUENCES = 4  # glTF skins carry four joints per vertex set; more needs extra sets or loses weights


def load(path):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    ext = os.path.splitext(path)[1].lower()
    if ext in (".glb", ".gltf"):
        bpy.ops.import_scene.gltf(filepath=path)
    elif ext == ".fbx":
        bpy.ops.import_scene.fbx(filepath=path)
    elif ext == ".obj":
        bpy.ops.wm.obj_import(filepath=path)
    else:
        raise SystemExit(f"Unsupported asset type: {ext}")


def mesh_checks(obj):
    me = obj.data
    bm = bmesh.new()
    bm.from_mesh(me)
    bm.edges.ensure_lookup_table()
    boundary = [e for e in bm.edges if e.is_boundary]
    non_manifold = [e for e in bm.edges if not e.is_manifold and not e.is_boundary]
    inconsistent = [e for e in bm.edges if e.is_manifold and not e.is_contiguous]
    degenerate = [f for f in bm.faces if f.calc_area() < EPS_AREA]
    zero_edges = [e for e in bm.edges if e.calc_length() < 1e-9]
    loose = [v for v in bm.verts if not v.link_edges]
    tris = sum(len(f.verts) - 2 for f in bm.faces)
    # glTF splits vertices along UV seams and hard edges, so an imported GLB looks open.
    # Weld coincident vertices on a copy before judging watertightness.
    welded = bm.copy()
    bmesh.ops.remove_doubles(welded, verts=welded.verts, dist=1e-6)
    boundary_welded = sum(1 for e in welded.edges if e.is_boundary)
    welded.free()
    ngons = sum(1 for f in bm.faces if len(f.verts) > 4)
    bm.free()

    world = [obj.matrix_world @ Vector(c) for c in obj.bound_box]
    lo = [min(v[i] for v in world) for i in range(3)]
    hi = [max(v[i] for v in world) for i in range(3)]

    uv = {"layers": [l.name for l in me.uv_layers], "outside_0_1": None}
    if me.uv_layers:
        data = me.uv_layers.active.data
        outside = sum(1 for d in data if not (-1e-4 <= d.uv.x <= 1 + 1e-4 and -1e-4 <= d.uv.y <= 1 + 1e-4))
        uv["outside_0_1"] = round(outside / max(1, len(data)), 4)

    materials = []
    for slot in obj.material_slots:
        m = slot.material
        entry = {"name": m.name if m else None, "textures": []}
        if m and m.use_nodes:
            for node in m.node_tree.nodes:
                if node.type == "TEX_IMAGE" and node.image:
                    # Only the Color output is colour-managed; Alpha is always linear, so it is not traced.
                    feeds = sorted({s for out in node.outputs if out.name == "Color" for l in out.links for s in trace(l)})
                    entry["textures"].append({"image": node.image.name, "colorspace": node.image.colorspace_settings.name, "feeds": feeds})
        materials.append(entry)
    colour_space_issues = []
    for m in materials:
        for t in m["textures"]:
            data = [f for f in t["feeds"] if f in DATA_SOCKETS]
            colour = [f for f in t["feeds"] if f in COLOUR_SOCKETS]
            if data and t["colorspace"] == "sRGB":
                colour_space_issues.append(f"{m['name']}:{t['image']} is sRGB but feeds data input {data}; set Non-Color")
            if colour and t["colorspace"] in ("Non-Color", "Raw", "Linear Rec.709") and not data:
                colour_space_issues.append(f"{m['name']}:{t['image']} is {t['colorspace']} but feeds colour input {colour}; set sRGB")

    return {
        "object": obj.name,
        "vertices": len(me.vertices), "faces": len(me.polygons), "triangles": tris, "ngons": ngons,
        "boundary_edges": len(boundary), "boundary_edges_welded": boundary_welded, "non_manifold_edges": len(non_manifold),
        "inconsistent_normal_edges": len(inconsistent), "degenerate_faces": len(degenerate),
        "zero_length_edges": len(zero_edges), "loose_vertices": len(loose),
        "scale": [round(s, 6) for s in obj.scale],
        "bbox_m": {"min": [round(x, 5) for x in lo], "max": [round(x, 5) for x in hi], "size": [round(hi[i] - lo[i], 5) for i in range(3)]},
        "uv": uv, "materials": materials, "colour_space_issues": colour_space_issues,
    }


def rig_checks(obj):
    arm = obj.find_armature()
    if not arm:
        return None
    deform = {b.name for b in arm.data.bones if b.use_deform}
    names = {g.index: g.name for g in obj.vertex_groups}
    unweighted, over, not_normalised = 0, 0, 0
    for v in obj.data.vertices:
        ws = [g.weight for g in v.groups if names.get(g.group) in deform and g.weight > 1e-6]
        if not ws:
            unweighted += 1
            continue
        if len(ws) > MAX_INFLUENCES:
            over += 1
        if abs(sum(ws) - 1) > 1e-3:
            not_normalised += 1
    roots = [b.name for b in arm.data.bones if b.parent is None]
    return {
        "armature": arm.name, "bones": len(arm.data.bones), "deform_bones": len(deform), "roots": roots,
        "hierarchy": {b.name: (b.parent.name if b.parent else None) for b in arm.data.bones},
        "unweighted_vertices": unweighted, "vertices_over_4_influences": over, "non_normalised_vertices": not_normalised,
    }


def main():
    if asset:
        load(asset)
    # Importers add bone display shapes (the glTF importer adds an Icosphere). They are not part of the asset.
    helpers = {pb.custom_shape for o in bpy.context.scene.objects if o.type == "ARMATURE" for pb in o.pose.bones if pb.custom_shape}
    meshes = [o for o in bpy.context.scene.objects if o.type == "MESH" and o not in helpers]
    actions = [{"name": a.name, "frames": [int(a.frame_range[0]), int(a.frame_range[1])]} for a in bpy.data.actions]
    report = {"asset": asset, "blender": bpy.app.version_string, "ignored_helpers": sorted(h.name for h in helpers), "meshes": [mesh_checks(o) for o in meshes],
              "rigs": [r for r in (rig_checks(o) for o in meshes) if r], "animations": actions}

    floor = {
        "has_geometry": bool(meshes),
        "no_non_manifold_edges": all(m["non_manifold_edges"] == 0 for m in report["meshes"]),
        "no_degenerate_faces": all(m["degenerate_faces"] == 0 for m in report["meshes"]),
        "consistent_normals": all(m["inconsistent_normal_edges"] == 0 for m in report["meshes"]),
        "no_loose_vertices": all(m["loose_vertices"] == 0 for m in report["meshes"]),
        "has_uvs": all(m["uv"]["layers"] for m in report["meshes"]),
        "colour_spaces_valid": all(not m["colour_space_issues"] for m in report["meshes"]),
        "rig_weights_normalised": all(r["non_normalised_vertices"] == 0 and r["unweighted_vertices"] == 0 for r in report["rigs"]),
    }
    reflex = {
        "unit_scale": all(all(abs(s - 1) < 1e-4 for s in m["scale"]) for m in report["meshes"]),
        "max_4_influences": all(r["vertices_over_4_influences"] == 0 for r in report["rigs"]),
        "watertight": all(m["boundary_edges_welded"] == 0 for m in report["meshes"]),
        "no_ngons": all(m["ngons"] == 0 for m in report["meshes"]),
    }
    report["floor"], report["reflex"] = floor, reflex
    report["pass"] = all(floor.values())
    text = json.dumps(report, indent=2)
    if report_path:
        with open(report_path, "w", encoding="utf-8", newline="\n") as f:
            f.write(text + "\n")
    print(text)
    print(("PASS" if report["pass"] else "FAIL") + " floor checks: " + ", ".join(k for k, v in floor.items() if not v))
    sys.exit(0 if report["pass"] else 1)


if __name__ == "__main__":
    main()
