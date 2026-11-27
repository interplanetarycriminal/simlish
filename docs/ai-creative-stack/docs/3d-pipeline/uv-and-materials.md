# UVs and materials

This stage turns a clean mesh into a surface the renderer can shade: a UV layout, a set of texture maps in the right color spaces, and a material that looks right under more than one light. It runs after [retopology](retopology.md), because retopology discards UVs.

## UV inspection and unwrapping in Blender

Generated meshes arrive in three states. Stable Fast 3D writes a UV-unwrapped texture atlas. TRELLIS.2 writes a PBR GLB with textures. MeshAnything V2 writes no UVs at all. Inspect whatever arrives before keeping it.

1. **Look at the layout.** UV Editor with the mesh selected in Edit Mode. Turn on the stretch overlay (Display Stretch, angle or area).
2. **Apply a checker.** Assign a UV grid or checker image. Squares should stay square and roughly the same size across the model. Stretching and size jumps show at once.
3. **Decide: keep or re-unwrap.** Keep an atlas only if it has no visible stretching on surfaces the camera sees, and seams sit where the texture can hide them. A generator atlas with hundreds of small islands is hard to paint and wastes texture space.
4. **Unwrap.** Mark seams, then UV > Unwrap for hand-quality layouts. Smart UV Project is the quick route for hard-surface props: the fixture used it with a 66 degree angle limit and 0.02 island margin ([make_asset.py](../../fixtures/blender-glb/make_asset.py)). Lightmap Pack suits non-overlapping bake targets.
5. **Pack.** Pack islands with a margin (padding) of several pixels at the delivery texture size, more if the texture will be mipmapped (general practice). Overlapping islands are fine for mirrored or tiled parts, but not for baked ambient occlusion or lightmaps.

[`validate_asset.py`](../../scripts/blender/validate_asset.py) checks that each mesh has a UV layer (`has_uvs`, Floor) and reports the share of UV coordinates outside 0 to 1 (`uv.outside_0_1`). That number is reported, not gated: tiling textures use coordinates outside 0 to 1 on purpose. glTF has one texture per map slot per material and no UDIM tiles (general practice), so a UDIM layout must be baked down to a single atlas before a GLB delivery.

## Seams

- Hide seams in creases, under overlaps, along hard edges and on sides the camera rarely sees.
- Every seam splits vertices in the delivered GLB. The fixture's closed, smooth-shaded limb gained 116 vertices (314 in FBX, 430 in GLB) from these splits ([reports](../../fixtures/blender-glb/out/report-glb.json)). Seams that coincide with hard edges cost nothing extra, because the normals split there anyway.
- Fewer, longer seams paint and bake more cleanly than many short ones.
- Check seams on the shaded model with the normal map applied. A seam that shows only after baking usually means mismatched tangent space or too little padding.

## Texel density

Texel density is texture pixels per meter of surface. Keep it consistent across one asset and across assets that appear together, or some parts look sharp and others blurry next to each other (general practice).

- Measure: texture width in pixels × the square root of (UV island area ÷ the island's surface area in square meters).
- Set a target in the brief per asset class, for example the hero object versus background props, and record it in the [mesh quality report](../../templates/mesh-quality-report.md).
- Give extra density only to areas the camera sees close up, and say so in the report.

## What Dream Textures can and cannot do

[Dream Textures](../repositories/dream-textures.md) is a Blender add-on that runs Stable Diffusion through diffusers. It is useful for:

- Prompted images and **tiling textures** through its Seamless option (512 × 512 by default; the 4x upscaler needs a separate model).
- **Depth-guided projection**: select faces, pick a depth model, and the image projects onto them. "Depth and Color" also uses the viewport color. Use Local View so other objects do not leak into the depth, and subdivide large faces before projecting, because large unbroken faces warp.

It produces **color images**. It is not a full PBR set: no roughness, metallic, normal or ambient-occlusion maps come out of it. Generated color often contains baked lighting that has to be removed or painted out before it can serve as base color. Assemble the remaining maps with Blender nodes, bakes from a dense source, or a generator that outputs them (TRELLIS.2 documents base color, roughness, metallic and opacity). The Dream Textures plus Blender nodes pairing is *proposed* in `registry/compatibility.json`.

Limits recorded in the registry: GPL-3.0; the pinned stack is torch 2.3.1 and diffusers 0.27.2 with a Blender 3.1+ target, so Blender 5.x support is not established; the recommended Stable Diffusion 2.x repositories were not reachable anonymously on 2026-11-26; each model carries its own license. Not run here. [Real-ESRGAN](../repositories/real-esrgan.md) is an alternative for upscaling finished textures (not run here).

## PBR maps and color spaces

Set each image node's color space in Blender. A wrong setting changes how the value is read and produces shading that looks wrong under every light.

| Map | Blender color space | glTF slot (general practice) | Notes |
| --- | --- | --- | --- |
| Base color (albedo) | **sRGB** | `baseColorTexture` (RGB) | No baked shadows or highlights |
| Emission | **sRGB** | `emissiveTexture` | |
| Roughness | **Non-Color** | `metallicRoughnessTexture`, green channel | |
| Metallic | **Non-Color** | `metallicRoughnessTexture`, blue channel | Mostly 0 or 1 for real materials |
| Normal | **Non-Color** | `normalTexture` | Tangent space, OpenGL (Y+) convention in Blender and glTF |
| Ambient occlusion | **Non-Color** | `occlusionTexture`, red channel | Often packed with roughness and metallic as one ORM image |
| Displacement or height | **Non-Color** | none in core glTF | Bake into geometry or a normal map for GLB delivery |
| Opacity (alpha) | **Non-Color** | alpha channel of `baseColorTexture` | Set the material's blend or clip mode; TRELLIS.2 exports OPAQUE, so wire alpha by hand |

**What the validator checks.** `validate_asset.py` traces each image's Color output through Normal Map, Bump, Separate Color and math nodes to the input it drives. It flags an sRGB image that reaches a data input and a Non-Color image that reaches only color inputs (`colour_space_issues`, Floor check `colour_spaces_valid`). A negative test with six materials proves it flags exactly the four wrong wirings; see [how the check works](asset-validation.md#how-the-color-space-check-works).

## Check under several lights

A material that looks right under one light can be wrong. Review every textured asset under at least three setups, in Blender and in the target renderer (general practice):

1. **Neutral studio:** even light and a gray background. Base color should read flat, with no painted-in shadows.
2. **Hard directional light (sun):** reveals normal map direction, seams and roughness variation.
3. **Low-key or rim light:** reveals metallic and roughness errors and over-bright emission.
4. **The delivery environment:** the actual HDRI or lights, tone mapping and output color space of the consumer, such as a Three.js scene. Match these settings to the consumer before judging color.

Render the same camera views under each setup and keep the contact sheet with the [mesh quality report](../../templates/mesh-quality-report.md). The [interactive 3D gate](../../QUALITY_GATES.md) requires materials to match the source on target hardware.

## Evidence to keep

UV layout screenshot with checker, texel density target and measured value, the list of maps with color spaces, the lighting contact sheet, and the validator report. Record the texture sizes in the [asset manifest](../../templates/asset-manifest.json).
