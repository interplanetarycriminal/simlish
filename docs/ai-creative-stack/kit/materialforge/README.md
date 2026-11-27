# materialforge

Makes procedural, tileable PBR texture sets: base color, roughness, metallic, normal, height and ambient occlusion, plus a `material.json` that lists each map, its color space and suggested Principled BSDF values. Same seed, same output.

**Stands in for:** the Seamless (tiling texture) option of [Dream Textures](../../docs/repositories/dream-textures.md). Dream Textures makes a tiling color image with Stable Diffusion. materialforge makes the whole PBR set from math instead, with no model and no GPU.

## How it works

- **Every field is periodic by construction.** Noise is white noise filtered in the frequency domain (FFT). Only whole-number frequencies exist on the FFT grid, so the result repeats exactly. Frequencies are set in cycles per tile, so the look does not depend on resolution.
- **Shapes are built from periodic parts:** stretched spectra for grain and brushing, domain warping with periodic offset fields (`scipy.ndimage.map_coordinates` with `grid-wrap`), a jittered-grid Voronoi on a torus for stones, integer ring and thread counts for wood and fabric, and scratches measured with wrapped distances.
- **Normals come from the height field** with wrapped central differences. Height 0 to 1 maps to `height_depth_m` metres, and one texel is `tile_size_m / size` metres, so the slope is in real units. The map is tangent space, OpenGL convention (+Y up the image), as Blender and glTF expect.
- **AO is a cheap cavity term:** how far each texel sits below wrapped Gaussian blurs of the height at five radii.
- **Seeds:** each preset seeds NumPy's generator from `(seed, crc32(preset))`.

| Preset | Look | Metallic |
| --- | --- | --- |
| `wood` | Plain-sawn grain along +X, 14 rings per tile, pores | 0 |
| `brushed-metal` | Long brush streaks along +X, a few scratches | 1 |
| `painted-plastic` | Blue paint, orange peel, light scuffs | 0 |
| `fabric` | Plain weave, 32 threads each way, dark warp and light weft | 0 |
| `stone` | Irregular flagstones (5 x 5 cells) with mortar | 0 |
| `rust` | Steel with rust patches (about 45 percent) | 1 on steel, 0 on rust |

## Output

| File | Color space | Format |
| --- | --- | --- |
| `base_color.png` | sRGB | 8-bit RGB |
| `roughness.png` | Non-Color | 8-bit gray |
| `metallic.png` | Non-Color | 8-bit gray |
| `normal.png` | Non-Color | 8-bit RGB, OpenGL tangent space |
| `height.png` | Non-Color | 16-bit gray, 0 to `height_depth_m` |
| `ao.png` | Non-Color | 8-bit gray |
| `material.json` | | maps, color spaces, glTF slots, BSDF values, tile size, displacement scale |

In Blender: set every image node except base color to Non-Color. Wire `normal.png` through a Normal Map node (Tangent Space). For displacement, use a Displacement node with Midlevel 0 and Scale `height_depth_m` on a mesh at real scale.

## Use

```sh
python materialforge.py stone --size 1024 --seed 7 --out out/stone/
```

Presets: `wood`, `brushed-metal`, `painted-plastic`, `fabric`, `stone`, `rust`. A 1024 px set takes about 5 to 7 seconds on one CPU core.

## Test

```sh
python test.py
```

The test runs the CLI for every preset at 256 px and checks the files it wrote. Result on 2026-11-26: **pass, 0 failures, 14 s.**

- **Tiling:** for all 6 maps of all 6 presets, in both directions, the mean difference across the wrap seam is no larger than the interior neighbour differences (bound: mean + 3 std of the column-pair or row-pair differences). Seam to interior ratios are 0.4 to 1.6. A control proves the check works: a 200 px crop (not periodic) of the stone tile fails in both directions (seam 22.6 and 20.5 against a bound of 13.5), and a rolled tile passes.
- **Normals:** decoded length within 0.0063 of 1 (8-bit limit). Wherever the height slope is above quantisation, the normal's X leans against dh/dx and its Y (OpenGL, up) leans with the slope down the rows on 100 percent of those pixels. The stored normals match normals recomputed from `height.png` and the scales in `material.json` to a mean error of 0.002. Mean tilt runs from 0.7 degrees (plastic) to 20.6 degrees (fabric).
- **Values:** metallic is exactly 0 for the four dielectrics and 1 for brushed metal; rust is 98.5 percent near 0 or 1, with 55 percent steel and 45 percent rust. Roughness means sit in each preset's band. Base color stays between 2 and 97 percent luminance. Height uses the full 16-bit range.
- **Color spaces in `material.json`:** base color sRGB, all others Non-Color.
- **Determinism:** two runs with the same seed are identical, the CLI files equal the in-process result, and seed + 1 differs.
- **Preview:** `out/preview_sheet.png` shows each preset tiled 2 x 2: base color, a lit view (normal and AO), and the normal map.

To stay under the size budget, the test keeps the full 256 px map sets for `wood` and `rust` only. The other presets keep their `material.json`; the test regenerates all of them on every run.

## What it does not do

- No prompts and no learned images. Each preset is a hand-written recipe, so the variety is limited to what the recipe and seed can make.
- No projection onto a mesh, no depth-guided texturing and no upscaling, which Dream Textures offers.
- AO is a height-field cavity estimate, not a ray-traced bake. It is subtle on the low-relief presets (mean 0.95 to 1.0). Height is a single layer, so there are no overhangs.
- Physical scales (`tile_size_m`, `height_depth_m`) are chosen to read well, not measured from real samples. Fine detail above a size's Nyquist limit is dropped, so a 1024 px set has steeper normals than a 256 px set of the same preset.
- No packed ORM image and no texture compression (KTX2). `material.json` names the glTF slots so a packer can do that step.
