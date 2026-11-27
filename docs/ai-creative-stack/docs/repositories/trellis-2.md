# TRELLIS.2

Use for high-fidelity single-image to PBR-textured GLB generation, and for PBR texturing of an existing mesh from a reference image.

> #67 · Supplementary research candidates · Supplementary · smoke test: **not feasible here**

## Evidence and maintenance

- [Canonical reference](https://github.com/microsoft/TRELLIS.2)
- Verified 2026-11-26 against default branch `main` at [`75fbf0183001`](https://github.com/microsoft/TRELLIS.2/commit/75fbf0183001ed9876c8dbb35de6b68552ee08bd).
- GitHub reports archive state **false** and a repository push at `2026-07-10T12:34:32Z`. Push activity is a maintenance signal, not a quality rating.
- Attribution: Not attributable to any source post. Identified during related research.

- [README.md](https://github.com/microsoft/TRELLIS.2/blob/75fbf0183001ed9876c8dbb35de6b68552ee08bd/README.md)
- [LICENSE](https://github.com/microsoft/TRELLIS.2/blob/75fbf0183001ed9876c8dbb35de6b68552ee08bd/LICENSE)
- [setup.sh](https://github.com/microsoft/TRELLIS.2/blob/75fbf0183001ed9876c8dbb35de6b68552ee08bd/setup.sh)
- [example_texturing.py](https://github.com/microsoft/TRELLIS.2/blob/75fbf0183001ed9876c8dbb35de6b68552ee08bd/example_texturing.py)
- [app.py](https://github.com/microsoft/TRELLIS.2/blob/75fbf0183001ed9876c8dbb35de6b68552ee08bd/app.py)
- [trellis2_image_to_3d.py](https://github.com/microsoft/TRELLIS.2/blob/75fbf0183001ed9876c8dbb35de6b68552ee08bd/trellis2/pipelines/trellis2_image_to_3d.py)
- [TRELLIS.2-4B](https://huggingface.co/api/models/microsoft/TRELLIS.2-4B)
- [pipeline.json](https://huggingface.co/microsoft/TRELLIS.2-4B/raw/main/pipeline.json)
- [README.md](https://huggingface.co/microsoft/TRELLIS.2-4B/raw/main/README.md)

## Runtime, hardware and setup

- **Type** model and inference code. Primary language Python.
- **Platforms** Linux.
- **Runtime** Linux only (tested); CUDA Toolkit 12.4 recommended; Python >= 3.8 (setup.sh creates Python 3.10); torch 2.6.0 + torchvision 0.21.0 (cu124); flash-attn 2.7.3 (or xformers via ATTN_BACKEND); nvdiffrast v0.4.0, nvdiffrec, CuMesh, FlexGEMM, o-voxel built from source. setup.sh also has a ROCm 6.2.4 branch, not mentioned in the README.
- **Execution** local or hosted.
- **Agent paths** Generic coding agent via project files. Client claims describe documentation and remain untested here unless the smoke test says otherwise.
- **Configuration** Pick resolution 512, 1024 or 1536 (cascade) in the app; GLB export takes decimation_target (example 1,000,000), texture_size (example 4096) and remesh options. Set ATTN_BACKEND=xformers on GPUs without flash-attn.
- **Credentials and services** Hugging Face login with approved access to the gated DINOv3 and RMBG-2.0 repos referenced by pipeline.json; TRELLIS.2-4B itself is public.

| Hardware | Documented value |
| --- | --- |
| GPU | NVIDIA CUDA GPU |
| Minimum VRAM | 24 GB |
| Recommended VRAM | Not documented |
| System RAM | Not documented |
| Storage | About 16.2 GB in microsoft/TRELLIS.2-4B (HF API), plus the sparse-structure decoder from microsoft/TRELLIS-image-large, DINOv3 and RMBG-2.0 pulled by pipeline.json. |
| CPU fallback | not documented |
| Training versus inference | Inference on H100: about 3 s at 512^3, 17 s at 1024^3, 60 s at 1536^3. Full training code (SC-VAEs and three flow models) is included, multi-node capable. |
| Weights | Hugging Face microsoft/TRELLIS.2-4B (public); pipeline.json also loads facebook/dinov3-vitl16-pretrain-lvd1689m (gated, manual) and briaai/RMBG-2.0 (gated) (public) |
| Weights size | About 16.2 GB (4B parameters) per HF API |
| Notes | Verified on A100 and H100. PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True is set in the examples to save memory. Mesh is simplified to 16,777,216 faces (nvdiffrast limit) before rendering. |

Review the source and pin the version before running the upstream-documented command. It was read in the pinned documentation; execution is recorded only under Smoke test.

```sh
git clone -b main https://github.com/microsoft/TRELLIS.2.git --recursive
cd TRELLIS.2
. ./setup.sh --new-env --basic --flash-attn --nvdiffrast --nvdiffrec --cumesh --o-voxel --flexgemm
```

## Contracts and selection

| Boundary | Contract |
| --- | --- |
| Input | Single image (background removed by the RMBG-2.0 BiRefNet model), For texturing: an existing mesh (e.g. .ply via trimesh) plus a reference image |
| Output | GLB with PBR materials (base color, roughness, metallic, opacity in texture alpha; exported OPAQUE by default), MP4 turntable render, O-Voxel sparse voxel data (o_voxel io supports .vxz, .npz, .ply) |
| Primary | Image-to-3D, Texturing |
| Supporting | Retopology, 3D rendering |

Skip when you have under 24 GB of VRAM or no Linux box; TRELLIS.2 is only tested on Linux with A100/H100. Consider [stable-fast-3d](stable-fast-3d.md), [sam-3d-objects](sam-3d-objects.md), [dream-textures](dream-textures.md), [comfyui-3d-pack](comfyui-3d-pack.md). Complementary tools include [unirig](unirig.md), [meshanything-v2](meshanything-v2.md), [blender-mcp](blender-mcp.md), [three-js](three-js.md), [real-esrgan](real-esrgan.md), [dream-loop](dream-loop.md), [blender-skills](blender-skills.md), [comfyui](comfyui.md), [babylonjs](babylonjs.md).

The default pipeline downloads DINOv3 and RMBG-2.0, which have their own licenses and need a Hugging Face login. ComfyUI-3D-Pack supports TRELLIS v1, not TRELLIS.2.

- Skip if you need clear commercial rights for every component without checking the nvdiffrast, nvdiffrec, DINOv3 and RMBG-2.0 licenses.

## Craft notes

- 4B-parameter flow model on a 'field-free' O-Voxel representation, so it keeps open surfaces, non-manifold parts and internal structures that SDF methods lose.
- Generates full PBR (base color, roughness, metallic, opacity) up to 1536^3; GLB is exported OPAQUE, so you must wire the alpha channel by hand for transparency.
- Needs 24 GB+ VRAM and a heavy CUDA build chain; H100 timings are about 3 s, 17 s and 60 s for 512, 1024 and 1536.

## Examples

1. **Independent** Generate a 1024^3 PBR GLB of a lantern from one photo with TRELLIS.2 example.py.
2. **Combined** Proposed handoff: create a character with TRELLIS.2, then auto-rig the GLB with unirig.

For both, save the inputs and output evidence with the selected version. Use a small authorized fixture first and review the actual render or inspection result before expanding scope.

## Smoke test

**not feasible here**. Needs gated or multi-gigabyte weights or a large GPU; not downloaded for documentation.

## Security, privacy and licensing

- setup.sh runs 'sudo apt install' and clones and builds several CUDA extensions from GitHub into /tmp/extensions.
- Weights are safetensors; the rembg and DINOv3 models come from third-party gated repos.
- Runs locally after downloads; the Gradio app saves outputs to a per-user directory.
- Gated access to DINOv3 and RMBG-2.0 shares your Hugging Face identity with their owners.

**Software license** MIT (code and TRELLIS.2-4B model).

**Model license** MIT (TRELLIS.2-4B); separate terms for DINOv3 and RMBG-2.0 dependencies.

**Commercial use** MIT for TRELLIS.2 code and weights allows commercial use. The README warns that nvdiffrast and nvdiffrec have their own licenses (texts not inspected here). The default pipeline also pulls gated DINOv3 and RMBG-2.0 weights under their own custom licenses, so commercial rights for the full default pipeline are not established.

## Evidence quotes

| Field | Upstream wording and file |
| --- | --- |
| hardware | 'An NVIDIA GPU with at least 24GB of memory is necessary. ... verified on NVIDIA A100 and H100' (README.md) |
| supported_platforms | 'The code is currently tested only on Linux.' (README.md) |
| runtime_requirements | 'pip install torch==2.6.0 torchvision==0.21.0 --index-url .../cu124' (setup.sh) |
| installation | '. ./setup.sh --new-env --basic --flash-attn --nvdiffrast --nvdiffrec --cumesh --o-voxel --flexgemm' (README.md) |
| license | 'This model and code are released under the MIT License.' (README.md) |
| model_license | HF API 'license:mit' for TRELLIS.2-4B; pipeline.json names 'facebook/dinov3-vitl16-pretrain-lvd1689m' and 'briaai/RMBG-2.0' |
| dependency_licences | 'nvdiffrast: Utilized for rendering ... governed by its own License' (README.md) |
| inputs | 'Input: Single Image' (HF model card); 'pipeline.run(mesh, image)' (example_texturing.py) |
| outputs | 'sample.glb: The extracted PBR-ready 3D asset in GLB format.' (README.md) |
| speed | '512³ ~3s; 1024³ ~17s; 1536³ ~60s ... Tested on NVIDIA H100 GPU.' (README.md) |
