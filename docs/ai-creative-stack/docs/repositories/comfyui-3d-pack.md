# ComfyUI-3D-Pack (Comfy3D)

Use for running image-to-3D, multi-view diffusion, 3D Gaussian splatting and mesh texture-baking pipelines as ComfyUI node graphs.

> AI-assisted 3D asset production · Source C · smoke test: **not feasible here**

## Evidence and maintenance

- [Canonical reference](https://github.com/MrForExample/ComfyUI-3D-Pack)
- Verified 2026-11-26 against default branch `main` at [`9e8096e50c5b`](https://github.com/MrForExample/ComfyUI-3D-Pack/commit/9e8096e50c5bcf35e1f3e34c6ae06216101f8a11).
- GitHub reports archive state **false** and a repository push at `2025-12-29T08:06:02Z`. Push activity is a maintenance signal, not a quality rating.
- Attribution: Confirmed. Named in the user-supplied transcript of source C.

- [README.md](https://github.com/MrForExample/ComfyUI-3D-Pack/blob/9e8096e50c5bcf35e1f3e34c6ae06216101f8a11/README.md)
- [install.py](https://github.com/MrForExample/ComfyUI-3D-Pack/blob/9e8096e50c5bcf35e1f3e34c6ae06216101f8a11/install.py)
- [requirements.txt](https://github.com/MrForExample/ComfyUI-3D-Pack/blob/9e8096e50c5bcf35e1f3e34c6ae06216101f8a11/requirements.txt)
- [build_config.yaml](https://github.com/MrForExample/ComfyUI-3D-Pack/blob/9e8096e50c5bcf35e1f3e34c6ae06216101f8a11/_Pre_Builds/_Build_Scripts/build_config.yaml)
- [build_utils.py](https://github.com/MrForExample/ComfyUI-3D-Pack/blob/9e8096e50c5bcf35e1f3e34c6ae06216101f8a11/_Pre_Builds/_Build_Scripts/build_utils.py)
- [README.md](https://github.com/MrForExample/ComfyUI-3D-Pack/blob/9e8096e50c5bcf35e1f3e34c6ae06216101f8a11/_Pre_Builds/README.md)
- [system.conf](https://github.com/MrForExample/ComfyUI-3D-Pack/blob/9e8096e50c5bcf35e1f3e34c6ae06216101f8a11/Configs/system.conf)
- [server.py](https://github.com/MrForExample/ComfyUI-3D-Pack/blob/9e8096e50c5bcf35e1f3e34c6ae06216101f8a11/webserver/server.py)
- [pyproject.toml](https://github.com/MrForExample/ComfyUI-3D-Pack/blob/9e8096e50c5bcf35e1f3e34c6ae06216101f8a11/pyproject.toml)
- [LICENSE](https://github.com/MrForExample/ComfyUI-3D-Pack/blob/9e8096e50c5bcf35e1f3e34c6ae06216101f8a11/LICENSE)
- [DOCKER_INSTRUCTIONS.md](https://github.com/MrForExample/ComfyUI-3D-Pack/blob/9e8096e50c5bcf35e1f3e34c6ae06216101f8a11/DOCKER_INSTRUCTIONS.md)
- [README.md](https://github.com/MrForExample/ComfyUI-3D-Pack/blob/9e8096e50c5bcf35e1f3e34c6ae06216101f8a11/Checkpoints/Diffusers/JeffreyXiang/TRELLIS-image-large/README.md)
- [Hunyuan3D-2.1](https://huggingface.co/api/models/tencent/Hunyuan3D-2.1)
- [stable-fast-3d](https://huggingface.co/api/models/stabilityai/stable-fast-3d)

## Runtime, hardware and setup

- **Type** ComfyUI custom nodes. Primary language Python.
- **Platforms** Windows, Linux.
- **Runtime** Inside a ComfyUI install. README pre-builds: Windows 10/11, Python 3.12, CUDA 12.4, torch 2.5.1+cu124. build_config.yaml at the same commit pins torch 2.7.0 / torchvision 0.22.0 / xformers 0.0.30 with default CUDA 12.8 (supported 12.8, 12.6, 12.4, 12.1, 11.8); requirements.txt pins spconv-cu126 and cumm 0.7.11. Visual Studio Build Tools (Windows) or gcc/g++ (Linux) needed for JIT CUDA extensions.
- **Execution** local.
- **Agent paths** Generic coding agent via project files. Client claims describe documentation and remain untested here unless the smoke test says otherwise.
- **Configuration** Configs/system.conf holds an allow-list of client IPs for the 3D preview server and an optional Hugging Face token for gated weights; per-model YAML configs live in Configs/. Example workflows need the example inputs copied into ComfyUI/input.
- **Credentials and services** None for most nodes; a Hugging Face user token (in Configs/system.conf) is needed to auto-download gated weights such as Stable Fast 3D.

| Hardware | Documented value |
| --- | --- |
| GPU | NVIDIA CUDA GPU |
| Minimum VRAM | Not documented |
| Recommended VRAM | Not documented |
| System RAM | Not documented |
| Storage | Each model downloads its own weights into Checkpoints/ or ComfyUI models folders; total size not documented. |
| CPU fallback | not documented |
| Training versus inference | Mostly inference; 3DGS, Instant-NGP, FlexiCubes and mesh fitting nodes run per-scene optimization. |
| Weights | Many Hugging Face repos auto-downloaded per node, e.g. tencent/Hunyuan3D-2.1, tencent/Hunyuan3D-2, jetx/TRELLIS-image-large, stabilityai/stable-fast-3d (gated), VAST-AI/TripoSG, wgsxm/PartCrafter, TencentARC/InstantMesh, stabilityai/TripoSR, huanngzh/mv-adapter, Stable-X/trellis-normal-v0-1, ashawkey/LGM. (public) |
| Weights size | Not documented |
| Notes | VRAM is per model: Era3D 'needs at least 16GB vram'; CRM can be split into separate workflows for low VRAM; LGM image-to-3DGS under 30 s and TriplaneGaussian under 10 s on an RTX 3080 (README). |

Review the source and pin the version before running the upstream-documented command. It was read in the pinned documentation; execution is recorded only under Smoke test.

```sh
Install from ComfyUI-Manager, or manually:
cd Your ComfyUI Root Directory\ComfyUI\custom_nodes\
git clone https://github.com/MrForExample/ComfyUI-3D-Pack.git
cd ComfyUI-3D-Pack
Your ComfyUI Root Directory\python_embeded\python.exe -s -m pip install -r requirements.txt
Your ComfyUI Root Directory\python_embeded\python.exe install.py
```

## Contracts and selection

| Boundary | Contract |
| --- | --- |
| Input | Single image (object or scene), Scribble image (TripoSG), Multi-view images, Text prompt plus mesh (MV-Adapter TG2MV), Multi-view depth/mask/normal maps (FlexiCubes), Mesh files .obj/.ply/.glb, 3DGS .ply, Orbit camera poses |
| Output | Mesh .obj/.ply/.glb (with RGB/UV texture for several models), Part-segmented meshes plus ZIP of parts (PartCrafter), 3D Gaussians as standard 3DGS .ply, Multi-view images and normal maps, Orbit render image sequences or video |
| Primary | Image-to-3D, Spatial reconstruction, Texturing |
| Supporting | 3D rendering, 3D orchestration, Media processing |

Skip if you need TRELLIS.2, SAM 3D Objects, UniRig or MeshAnything: none are in the node pack at the pinned commit (it has TRELLIS v1 image-large, Stable Fast 3D and its own 3DGS nodes only). Consider [stable-fast-3d](stable-fast-3d.md), [trellis-2](trellis-2.md), [sam-3d-objects](sam-3d-objects.md), [gaussian-splatting](gaussian-splatting.md), [dream-textures](dream-textures.md). Complementary tools include [blender-mcp](blender-mcp.md), [blender-skills](blender-skills.md), [unirig](unirig.md), [meshanything-v2](meshanything-v2.md), [real-esrgan](real-esrgan.md), [dream-loop](dream-loop.md).

The pinned README documents native nodes for Stable Fast 3D and TRELLIS v1 (not TRELLIS.2), Hunyuan3D, TripoSG, InstantMesh and its own 3D Gaussian Splatting nodes. SAM 3D Objects, UniRig and MeshAnything V2 have no native nodes at the pinned commit.

- Install pins torch 2.7.0 and xformers into the ComfyUI Python, which can replace the torch version other custom nodes expect.
- README pre-build versions (Python 3.12, CUDA 12.4, torch 2.5.1) contradict build_config.yaml (torch 2.7.0, CUDA 12.8 default), so the documented environment is ambiguous.
- No macOS or CPU path is documented.

## Craft notes

- Broadest single node suite for 3D in ComfyUI: PartCrafter, Hunyuan3D 2.1/2.0/1.0, MV-Adapter, Stable3DGen, TripoSG, TRELLIS, StableFast3D, CharacterGen, Unique3D, Era3D, InstantMesh, Zero123++, CRM, TripoSR, Wonder3D, LGM, TriplaneGaussian, plus FlexiCubes, Instant-NGP and 3DGS optimizers.
- Distinctive glue nodes: Stack Orbit Camera Poses, 3DGS/mesh orbit renderers, nvdiffrast multi-view texture baking, and axis switching between algorithms' coordinate systems; preview uses gsplat.js and three.js.
- Install is the main failure point: README last updated June 2025, pre-builds target fixed Python/CUDA/torch combos, and Instant-NGP plus 3DGS-to-mesh nodes still need a C++ compiler at runtime.

## Examples

1. **Independent** Run the Hunyuan3D 2.1 Full example workflow to turn one product photo into a textured .glb.
2. **Combined** Proposed handoff: generate a mesh with the TripoSG workflow, then rig it with unirig before animation.

For both, save the inputs and output evidence with the selected version. Use a small authorized fixture first and review the actual render or inspection result before expanding scope.

## Smoke test

**not feasible here**. Needs gated or multi-gigabyte weights or a large GPU; not downloaded for documentation.

## Security, privacy and licensing

- install.py downloads prebuilt binary wheels from the third-party GitHub repo DenisKochetov/Comfy3D_Pre_Builds (not the author's MrForExample repo named in README) at its default branch, with no hash check, and installs them with pip --no-deps --force-reinstall.
- install.py also downloads Python C++ source files from that repo into the Python install's root folder, and auto-installs PyGithub, triton/triton-windows and diso from an unpinned git URL with --no-build-isolation.
- requirements.txt pulls unpinned git dependencies (EasternJournalist/utils3d, ashawkey/kiuikit); if wheels fail, a build script compiles from source; some nodes JIT-compile CUDA extensions at runtime.
- webserver/server.py adds a /viewfile route that returns any existing local file path with extensions .png/.jpg/.obj/.glb/.ply/.mtl/.splat to clients whose IP is in the allow-list (127.0.0.1 and Docker bridge IPs); behind a local reverse proxy this exposes arbitrary file reads of those types.
- Hugging Face token is stored in plain text in Configs/system.conf; Unique3D needs .ckpt/.pth pickle weights (SD 1.5 .ckpt, RealESRGAN .pth).
- Generation runs locally; input images are not sent to a service by the nodes.
- Install and first runs contact GitHub, PyPI, download.pytorch.org and Hugging Face.

**Software license** MIT License.

**Model license** Per model and often more restrictive than the MIT node code: Tencent Hunyuan Community License (Hunyuan3D 2/2.1), Stability AI Community License (Stable Fast 3D), MIT/Apache-2.0 for TripoSG, PartCrafter, TripoSR, InstantMesh, MV-Adapter..

**Commercial use** Node code is MIT and allows commercial use. Commercial use of outputs depends on each model's license: Hunyuan3D community license and Stability AI Community License carry their own conditions; MIT/Apache models are permissive. Check per workflow.

## Evidence quotes

| Field | Upstream wording and file |
| --- | --- |
| hardware | Era3D: 'you need at least 16GB vram to run this model' (README.md) |
| installation | 'python.exe -s -m pip install -r requirements.txt' then 'python.exe install.py' (README.md) |
| license | 'MIT License Copyright (c) 2024 MrForExample' (LICENSE) |
| model_license | HF API cardData license_name 'tencent-hunyuan-community' (tencent/Hunyuan3D-2.1); 'stabilityai-ai-community' (stabilityai/stable-fast-3d) |
| inputs | 'Single image to 3D Mesh with RGB texture'; 'Multi-View images as inputs' (README.md) |
| outputs | '.obj, .ply, .glb for 3D Mesh'; '.ply for 3DGS' (README.md) |
| runtime_requirements | 'Python 3.12 ... CUDA 12.4 ... torch 2.5.1+cu124' (README.md) vs 'version: "2.7.0"', 'cuda_version: "12.8"' (build_config.yaml) |
| security_notes | 'repo_id: "DenisKochetov/Comfy3D_Pre_Builds"' (build_config.yaml); '"--no-deps", "--force-reinstall"' (install.py) |
