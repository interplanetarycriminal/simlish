---
name: blender-craft
description: Make, check and ship 3D assets with Blender run headless, using the kit's 3D tools and a render-and-judge loop. Use for any request to build, fix, rig, animate, validate or export a 3D model, prop, character or scene, or to turn an image into a 3D asset.
---

# Blender craft

Our own stand-in for Blender Skills, Blender MCP's agent loop and Dream Loop's generate-and-judge cycle. Everything runs locally and headless. No hosted image-to-3D service is used.

Always call Blender with `--background --factory-startup --python-exit-code 1`. Without the last flag, a crashed script exits 0 and looks like a pass.

## The loop

1. **Target.** Write what the asset must look like from three named views, its size in meters, its triangle budget, and whether it moves.
2. **Make.** Pick the cheapest route that can meet the target:
   - From an image: [inflate3d](../../inflate3d/README.md) for toys, badges and stylized props.
   - From scratch: a Blender Python script that builds the geometry from code, like `fixtures/blender-glb/make_asset.py`. Keep the script; it is the editable source.
   - From an existing mesh: import it, then apply transforms.
3. **Budget.** Use [remesh](../../remesh/README.md) to reach the triangle budget. Rebuild or check UVs afterwards.
4. **Material.** Use [materialforge](../../materialforge/README.md) for tileable PBR maps. Base color and emission are sRGB; every other map is Non-Color.
5. **Motion, only if it moves.** Use [autorig](../../autorig/README.md) for chain-shaped bodies. Rigid props move with object keyframes, not bones.
6. **Validate.** Run `scripts/blender/validate_asset.py` on the export. Fix every Floor failure, then the Reflex ones.
7. **Judge.** Render three views. For a GLB, use `fixtures/blender-glb/viewer.html` headless through the shared DevTools helper. Compare each view against the target in writing: silhouette, proportion, surface, color. Name the worst difference and fix only that, then repeat from the step it belongs to. Stop when the three views meet the target or after five rounds, and report what is left.
8. **Ship.** Export GLB for the web and FBX or `.blend` for editing. Record every stage in the [asset manifest](../../../templates/asset-manifest.json), or run the whole chain with [assetpipe](../../assetpipe/README.md).

## Rules

- **Never overwrite an earlier stage.** Each step writes a new version.
- **Coordinates:** Blender is Z up; glTF is Y up and is converted on export. Units are meters.
- **Check after import, not before.** glTF splits vertices at UV seams, so judge watertightness after welding. FBX renames clips, so check names after re-import. The glTF importer adds a bone-display Icosphere; ignore it.
- **Test poses decide rigs.** Weight sums can pass while a joint still creases.
- **One script owns the scene.** Never mix manual edits and script edits on the same file without saving a new version.
