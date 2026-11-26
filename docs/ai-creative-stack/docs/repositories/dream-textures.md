# Dream Textures

Use for generating Stable Diffusion images, seamless tiling textures and depth-guided projected textures directly inside Blender.

> AI-assisted 3D asset production · Source C · smoke test: **not feasible here**

## Evidence and maintenance

- [Canonical reference](https://github.com/carson-katri/dream-textures)
- Verified 2026-11-26 against default branch `main` at [`5895fcb5cb20`](https://github.com/carson-katri/dream-textures/commit/5895fcb5cb20eab1885276145b4d6ecec3d5a191).
- GitHub reports archive state **false** and a repository push at `2026-09-17T11:34:23Z`. Push activity is a maintenance signal, not a quality rating.
- Attribution: Confirmed. Named in the user-supplied transcript of source C.

- [README.md](https://github.com/carson-katri/dream-textures/blob/5895fcb5cb20eab1885276145b4d6ecec3d5a191/README.md)
- [__init__.py](https://github.com/carson-katri/dream-textures/blob/5895fcb5cb20eab1885276145b4d6ecec3d5a191/__init__.py)
- [SETUP.md](https://github.com/carson-katri/dream-textures/blob/5895fcb5cb20eab1885276145b4d6ecec3d5a191/docs/SETUP.md)
- [TEXTURE_PROJECTION.md](https://github.com/carson-katri/dream-textures/blob/5895fcb5cb20eab1885276145b4d6ecec3d5a191/docs/TEXTURE_PROJECTION.md)
- [win-linux-cuda.txt](https://github.com/carson-katri/dream-textures/blob/5895fcb5cb20eab1885276145b4d6ecec3d5a191/requirements/win-linux-cuda.txt)
- [mac-mps-cpu.txt](https://github.com/carson-katri/dream-textures/blob/5895fcb5cb20eab1885276145b4d6ecec3d5a191/requirements/mac-mps-cpu.txt)
- [linux-rocm.txt](https://github.com/carson-katri/dream-textures/blob/5895fcb5cb20eab1885276145b4d6ecec3d5a191/requirements/linux-rocm.txt)
- [win-dml.txt](https://github.com/carson-katri/dream-textures/blob/5895fcb5cb20eab1885276145b4d6ecec3d5a191/requirements/win-dml.txt)
- [choose_device.py](https://github.com/carson-katri/dream-textures/blob/5895fcb5cb20eab1885276145b4d6ecec3d5a191/generator_process/actions/choose_device.py)
- [package-release.yml](https://github.com/carson-katri/dream-textures/blob/5895fcb5cb20eab1885276145b4d6ecec3d5a191/.github/workflows/package-release.yml)
- [diffusers_backend.py](https://github.com/carson-katri/dream-textures/blob/5895fcb5cb20eab1885276145b4d6ecec3d5a191/diffusers_backend.py)
- [preferences.py](https://github.com/carson-katri/dream-textures/blob/5895fcb5cb20eab1885276145b4d6ecec3d5a191/preferences.py)

## Runtime, hardware and setup

- **Type** Blender add-on. Primary language Python.
- **Platforms** Windows, macOS, Linux.
- **Runtime** Blender 3.1.0 or newer per bl_info (add-on v0.4.1). Prebuilt releases bundle dependencies for Python 3.10 and Python 3.11 (Blender 4.1+ suffix '-4-1'). Pinned stack: torch 2.3.1, diffusers 0.27.2, controlnet-aux 0.0.7; CUDA build uses the PyTorch cu118 index; ROCm 6.1 and DirectML requirement files also exist.
- **Execution** local or hosted.
- **Agent paths** Generic coding agent via project files. Client claims describe documentation and remain untested here unless the smoke test says otherwise.
- **Configuration** Enable the add-on, then search and download a model in add-on preferences; paste a Hugging Face token for gated models or a DreamStudio API key for cloud processing. The Dream panel lives in the Image Editor and 3D Viewport sidebars.
- **Credentials and services** None for local generation with public models; a Hugging Face token for gated/private models; a DreamStudio API key for cloud processing.

| Hardware | Documented value |
| --- | --- |
| GPU | NVIDIA CUDA GPU or Apple Silicon (tested); DirectML (Windows) and ROCm (Linux) requirement files exist but are not listed as tested |
| Minimum VRAM | Not documented |
| Recommended VRAM | 4 GB |
| System RAM | Not documented |
| Storage | Several GB free for add-on dependencies and model weights (docs/SETUP.md). |
| CPU fallback | documented |
| Training versus inference | Inference only (Stable Diffusion via diffusers). |
| Weights | User downloads Stable Diffusion models from Hugging Face inside add-on preferences (recommended stabilityai/stable-diffusion-2-1-base, -2-inpainting, -2-depth, -x4-upscaler); .ckpt import is also supported. (unknown) |
| Weights size | Not documented |
| Notes | README says 'Over 4GB of VRAM is recommended', so 4 GB is a floor, not a comfortable target. choose_device.py falls back cuda > mps > dml > cpu, and a cpu_only option exists. Cloud processing via DreamStudio is offered for unsupported hardware. |

Review the source and pin the version before running the upstream-documented command. It was read in the pinned documentation; execution is recorded only under Smoke test.

```sh
Download the latest release from https://github.com/carson-katri/dream-textures/releases/latest and install the zip in Blender preferences (Windows archive is 7-Zip compressed). macOS quarantine fix: xattr -r -d com.apple.quarantine ~/Library/Application\ Support/Blender/3.3/scripts/addons/dream_textures/.python_dependencies
```

## Contracts and selection

| Boundary | Contract |
| --- | --- |
| Input | Text prompt, Existing image or texture (img2img, inpaint, outpaint), Blender mesh plus viewport depth (and optionally color) for texture projection, Cycles render passes for the Dream Textures render engine, .ckpt Stable Diffusion checkpoint files (import) |
| Output | Generated images in Blender image editor (512x512 default), Seamless tiling textures, Projected texture plus material on selected faces, 4x upscaled images, Re-styled animation frames via render pass, History entries (export/import) |
| Primary | Texturing, Illustration |
| Supporting | Upscaling, 3D rendering, Visual effects |

Skip when you need current-generation diffusion models (SDXL, FLUX) or recent Blender 5.x support; the pinned stack is diffusers 0.27.2 / torch 2.3.1 with bl_info targeting Blender 3.1+. Consider [comfyui-3d-pack](comfyui-3d-pack.md), [trellis-2](trellis-2.md). Complementary tools include [blender-mcp](blender-mcp.md), [blender-skills](blender-skills.md), [real-esrgan](real-esrgan.md).

Dream Textures runs inside Blender as an add-on, so its textures land directly in Blender materials.

- The DreamStudio backend is documented (docs/SETUP.md, __init__.py references requirements/dreamstudio.txt) but no DreamStudio backend file or requirements/dreamstudio.txt exists in the tree at the pinned commit.
- The recommended stabilityai SD 2.x repos were not reachable anonymously via the Hugging Face API on 2026-11-26, so the documented first-run model path may fail.

## Craft notes

- Strongest at depth-to-image texture projection: select faces in edit mode, pick a depth model, and the result projects onto the mesh; 'Depth and Color' also factors in viewport color.
- Projection depth uses every visible object unless you enter Local View, and large unbroken faces warp, so subdivide before projecting; depth map aspect follows the 3D Viewport window.
- Seamless option and inpaint-based seamless conversion make tiling textures; outputs default to 512x512 and the 4x upscaler needs the separate stabilityai/stable-diffusion-x4-upscaler model.

## Examples

1. **Independent** Generate a seamless 512x512 mossy-stone texture from a prompt and apply it to a ground plane inside Blender.
2. **Combined** Proposed handoff: retopologize and UV a prop with blender-skills, then project a depth-guided Dream Texture onto its selected faces.

For both, save the inputs and output evidence with the selected version. Use a small authorized fixture first and review the actual render or inspection result before expanding scope.

## Smoke test

**not feasible here**. Needs gated or multi-gigabyte weights or a large GPU; not downloaded for documentation.

## Security, privacy and licensing

- Importing .ckpt checkpoints converts pickle-based files, which can execute code on load; import only trusted checkpoints.
- Prebuilt release zips ship a bundled .python_dependencies folder of compiled binaries; the macOS instructions remove Gatekeeper quarantine on that whole folder.
- SETUP.md warns: do not install dependencies yourself, always use a prebuilt release.
- Local generation keeps prompts and images on the machine.
- DreamStudio mode sends prompts and images to Stability AI's cloud service under that account's terms.

**Software license** GPL-3.0.

**Model license** Not stated in the add-on; each downloaded Stable Diffusion model carries its own license (not verified: the Hugging Face API returned 401 for stabilityai/stable-diffusion-2-1-base and stable-diffusion-2-depth on 2026-11-26)..

**Commercial use** GPL-3.0 allows commercial use of the add-on, but redistributing modified versions requires releasing source under GPL-3.0. Generated images fall under the chosen model's license and DreamStudio terms; Not established for outputs.

## Evidence quotes

| Field | Upstream wording and file |
| --- | --- |
| hardware | 'tested with CUDA and Apple Silicon GPUs. Over 4GB of VRAM is recommended.' (README.md) |
| installation | 'Download the latest release and follow the instructions there' (README.md); 'DO NOT try to install dependencies' (docs/SETUP.md) |
| license | 'GNU General Public License ... either version 3' (__init__.py header); GitHub SPDX GPL-3.0 |
| model_license | No model licence stated; 'A good model to start with is stabilityai/stable-diffusion-2-1-base' (docs/SETUP.md) |
| inputs | 'select the objects you want to project onto ... select all of the faces to target' (docs/TEXTURE_PROJECTION.md) |
| outputs | 'Use the Seamless option to create textures that tile perfectly'; 'Upscale your low-res generations 4x' (README.md) |
| runtime_requirements | '"blender": (3, 1, 0)' (__init__.py); 'torch==2.3.1', 'diffusers==0.27.2' (requirements/win-linux-cuda.txt) |
| supported_platforms | release matrix: windows-cuda, windows-directml, macos-arm (package-release.yml); linux-rocm.txt exists |
