# splatview

Our own Gaussian splat tools: a mesh-to-splat converter, a synthetic scene writer and a WebGL2 splat viewer. Files are the standard 3D Gaussian Splatting PLY layout.

**Stands in for:** the viewing side of [Gaussian Splatting](../../docs/repositories/gaussian-splatting.md) (its SIBR real-time viewer) and, for meshes, a way to produce a splat PLY without training. It is our own code; it does not train from photos.

## Tools

| File | What it does |
| --- | --- |
| `mesh2splat.py` | Mesh (GLB, glTF, OBJ, PLY mesh) to splat PLY |
| `synth.py` | Writes a test scene: a gold-to-violet torus and red, green and blue spheres, plus a `.json` sidecar with their positions |
| `viewer.html` + `splatview.mjs` | WebGL2 renderer with orbit controls |
| `splatply.py` | Shared Python helpers: flat Gaussians on a surface, PLY writer and reader |
| `make_test_box.py` | Test fixtures: a box with a 2 x 2 color texture, and a vertex-colored sphere |
| `serve.mjs` | Small static server for the viewer |

### mesh2splat

```sh
python mesh2splat.py in.glb out.ply --count 50000 [--seed 1] [--opacity 0.9] [--size-factor 1.0] [--smooth-normals]
```

- Samples `count` points over the surface, weighted by triangle area (uniform barycentric sampling). All meshes in the scene are used, with their node transforms.
- Color: the base-color texture through the UVs (bilinear, wrapped, times `baseColorFactor`), else vertex colors, else face colors, else the material color.
- Each sample becomes a flat Gaussian. The k = 8 nearest neighbours are projected into the tangent plane; their 2 x 2 covariance gives the two in-plane axes and the shape. The size is set from the local sample spacing (k-th neighbour radius x sqrt(pi / k)) times `--size-factor`. Anisotropy is capped at 3:1. The third axis lies along the face normal and is 8 percent of the smaller in-plane scale. The rotation quaternion comes from that tangent frame.
- Written as binary little endian with `x y z nx ny nz f_dc_0 f_dc_1 f_dc_2 opacity scale_0 scale_1 scale_2 rot_0 rot_1 rot_2 rot_3` (all float32). `f_dc = (rgb - 0.5) / 0.28209479`, opacity is a logit, scales are logs, the quaternion is (w, x, y, z). Normals are filled in (the trainer writes zeros there).
- Exits 0 and prints a JSON summary. 50,000 splats from a small GLB take about 2 seconds.

### Viewer

Open `viewer.html?file=<path to .ply, relative to viewer.html>` over HTTP (ES modules do not load from `file://`):

```sh
node serve.mjs            # serves the catalogue root on 127.0.0.1:8765 and prints the viewer URL
```

URL options: `bg=121217` (hex background), `fov=50`, `az`, `el`, `dist` (start view), `hud=0`, `dpr=1`. Drag to orbit, shift or right drag to pan, wheel to zoom. You can also drop a PLY on the page.

How it renders:

- Parses the binary PLY in the browser (any numeric property types; `f_dc_*` or `red/green/blue`; missing scale or rotation get defaults so plain point clouds still show).
- Builds each 3D covariance as R S S Rᵀ on the CPU and stores centres, covariances and colors in float textures.
- The vertex shader projects each covariance to 2D with the Jacobian of the perspective projection at the splat center (an EWA-style local linear approximation), adds 0.3 px² for antialiasing, takes the eigenvectors, and expands an instanced quad to 3 standard deviations along them. The fragment shader applies the Gaussian falloff and outputs premultiplied color.
- Splats are sorted back to front by view depth on the CPU with a single-pass counting sort on 16-bit depth keys (stable, so it is deterministic), on every camera change. Blending is `ONE, ONE_MINUS_SRC_ALPHA`, with no depth test.

Headless hooks: `window.__ready`, `window.__error`, and `window.__splat` with `setView(azimuthDeg, elevationDeg, distance)` (renders at once), `stats()` (count, bounds, fields, view, sort time), `project(x, y, z)` (pixel position and pixels per unit at that depth) and `pixelsBase64()` (RGBA, top row first). Azimuth turns around +Y starting from +Z toward +X; elevation is up from the XZ plane. Y is up.

## Test

```sh
node test.mjs
```

Result on 2026-11-26 (Chrome 158 headless, SwiftShader): **pass, 0 failures, 21 s.**

- **Sort unit check:** 20,000 random points give a full permutation in back-to-front order (largest inversion 0.0002, inside one 16-bit bucket), and the same view gives the same order after a different view. This check found a real bug during development (float32 keys against a float64 minimum made a key overflow, which left stale entries in the order).
- **PLY files:** synth (48,000 splats) and the mesh2splat box (30,000) have exactly the required fields in order, all float32, size = header + count x 68 bytes, unit quaternions (error under 1e-7), the third axis the thinnest on every splat and aligned with the normal (min |dot| 0.9999998), and opacity 0.95 or 0.9 as written. Same seed gives a byte-identical file.
- **Texture colors via UVs:** on the box's +Z face, 98.7 to 98.9 percent of samples in each quarter carry that quarter's texture color (the rest are bilinear blends at block borders). This also confirms the UV convention through a GLB round trip. A vertex-colored sphere gives 100 percent correct colors.
- **Rendering, synthetic scene, 3 views:** each sphere's projected center disk (half its projected radius) is 100 percent its primary color with no background showing through, in all 3 views. Outside the projected scene bounds, 100 percent of pixels are the background color (189,000 to 221,000 pixels per view). The torus covers 12,000 to 15,000 pixels. The viewer reports 48,000 splats, matching the file.
- **Rendering, mesh2splat box, 3 views** (including one from below): all 4 texture colors appear in every view, each +Z quarter shows its color on 100 percent of a disk at its center, and 99.98 percent or more of pixels outside the box are background.
- **Determinism:** returning to the first view after the others gives byte-identical pixels for both scenes.
- **Evidence:** `out/contact_sheet.png` (top row synthetic scene, bottom row box, 3 views each) and `out/result.json`. The PLY files (3.3 MB and 2.0 MB) are deleted after the test to keep `out/` small; the test regenerates them.

## What it does not do

- No training from photos and no camera solving. mesh2splat only re-expresses an existing mesh; it cannot capture anything the mesh does not have.
- Color is SH degree 0 only. mesh2splat writes no `f_rest_*`, and the viewer ignores `f_rest_*` if present, so there is no view-dependent shine.
- Splats from mesh2splat carry the texture color with no lighting. They will not match a lit render of the mesh.
- The 2D projection is the usual local linear approximation; very large splats near the camera are distorted. Splats whose centres are far outside the view are culled.
- The sort runs on the main thread. It took 0.6 ms for 30,000 splats here; millions of splats will stutter while orbiting. There is no level of detail, no compressed format (`.splat`, `.ksplat`, SPZ) and no editing.
- Headless tests use SwiftShader (software WebGL2). Speed on a real GPU was not measured.
