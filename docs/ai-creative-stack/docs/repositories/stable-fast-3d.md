# Stable Fast 3D (SF3D)

Use for fast single-image to game-ready GLB meshes with UV-unwrapped textures, delit color and material parameters.

> AI-assisted 3D asset production · Source C · smoke test: **not feasible here**

## Evidence and maintenance

- [Canonical reference](https://github.com/Stability-AI/stable-fast-3d)
- Verified 2026-11-26 against default branch `main` at [`ff21fc491b4d`](https://github.com/Stability-AI/stable-fast-3d/commit/ff21fc491b4dc5314bf6734c7c0dabd86b5f5bb2).
- GitHub reports archive state **false** and a repository push at `2025-01-22T14:55:42Z`. Push activity is a maintenance signal, not a quality rating.
- Attribution: Confirmed. Named in the user-supplied transcript of source C.

- [README.md](https://github.com/Stability-AI/stable-fast-3d/blob/ff21fc491b4dc5314bf6734c7c0dabd86b5f5bb2/README.md)
- [LICENSE.md](https://github.com/Stability-AI/stable-fast-3d/blob/ff21fc491b4dc5314bf6734c7c0dabd86b5f5bb2/LICENSE.md)
- [requirements.txt](https://github.com/Stability-AI/stable-fast-3d/blob/ff21fc491b4dc5314bf6734c7c0dabd86b5f5bb2/requirements.txt)
- [run.py](https://github.com/Stability-AI/stable-fast-3d/blob/ff21fc491b4dc5314bf6734c7c0dabd86b5f5bb2/run.py)
- [gradio_app.py](https://github.com/Stability-AI/stable-fast-3d/blob/ff21fc491b4dc5314bf6734c7c0dabd86b5f5bb2/gradio_app.py)
- [stable-fast-3d](https://huggingface.co/api/models/stabilityai/stable-fast-3d)

## Runtime, hardware and setup

- **Type** model and inference code. Primary language Python.
- **Platforms** Linux, Windows, macOS.
- **Runtime** Python >= 3.8; PyTorch installed per platform with a matching CUDA version; setuptools==69.5.1 and wheel; Windows (experimental) needs Visual Studio 2022; macOS MPS (experimental) needs an OpenMP runtime, PYTORCH_ENABLE_MPS_FALLBACK=1 and recent PyTorch (2.4.0 or nightly).
- **Execution** local or hosted.
- **Agent paths** Generic coding agent via project files. Client claims describe documentation and remain untested here unless the smoke test says otherwise.
- **Configuration** run.py takes --texture-resolution (default 1024), --remesh_option none|triangle|quad (default none), --target_vertex_count (default -1) and --foreground-ratio (default 0.85). Background removal uses rembg unless disabled.
- **Credentials and services** A Hugging Face account that has accepted the gated license form, plus a read token via huggingface-cli login.

| Hardware | Documented value |
| --- | --- |
| GPU | NVIDIA CUDA GPU; Apple Silicon supported (experimental, MPS) |
| Minimum VRAM | Not documented |
| Recommended VRAM | 6 GB |
| System RAM | Not documented |
| Storage | About 4.0 GB (model.safetensors) per HF API metadata. |
| CPU fallback | documented |
| Training versus inference | Inference only; no training code in the repo. |
| Weights | Hugging Face stabilityai/stable-fast-3d (gated, auto-approval after a form) (gated) |
| Weights size | About 4.0 GB (model.safetensors) per HF API |
| Notes | README: default options take about 6 GB VRAM for one image. MPS was tested on an M1 Max 64 GB and uses more memory than CUDA; CPU is advised under 32 GB unified memory. Set SF3D_USE_CPU=1 to force CPU. No inference-time figure is stated in the pinned files. |

Review the source and pin the version before running the upstream-documented command. It was read in the pinned documentation; execution is recorded only under Smoke test.

```sh
pip install -U setuptools==69.5.1
pip install wheel
pip install -r requirements.txt
pip install -r requirements-demo.txt  # for the gradio demo
huggingface-cli login
```

## Contracts and selection

| Boundary | Contract |
| --- | --- |
| Input | Single RGB or RGBA image (background removed automatically with rembg if no alpha) |
| Output | GLB mesh with UV-unwrapped texture atlas, normals and predicted material parameters |
| Primary | Image-to-3D |
| Supporting | Texturing, Retopology |

Skip if you need high-detail or scene-level reconstruction; SF3D is a fast single-object feed-forward model. Consider [trellis-2](trellis-2.md), [sam-3d-objects](sam-3d-objects.md), [comfyui-3d-pack](comfyui-3d-pack.md). Complementary tools include [unirig](unirig.md), [meshanything-v2](meshanything-v2.md), [blender-mcp](blender-mcp.md), [three-js](three-js.md), [real-esrgan](real-esrgan.md), [blender-skills](blender-skills.md).

ComfyUI-3D-Pack documents a native Stable Fast 3D node. The GLB output is a proposed handoff to Blender and Three.js.

- Skip if your organization earns over US $1M a year and has no Stability enterprise license.

## Craft notes

- Built on TripoSR but tuned for artifact-free meshes with UV unwrapping, delit albedo and predicted material parameters, so assets drop into a game engine.
- Default run takes about 6 GB VRAM per image; remeshing to triangle (Botsch-Kobbelt) or quad (Instant Meshes) costs CPU time and can add artifacts on thin surfaces.
- Speed is the selling point, but the pinned README gives no seconds figure; windows and MPS backends are labelled experimental.

## Examples

1. **Independent** Turn a product photo of a chair into a textured GLB with 2048 px texture using SF3D's run.py.
2. **Combined** Proposed handoff: generate a quick character GLB with SF3D, then rig it with unirig.

For both, save the inputs and output evidence with the selected version. Use a small authorized fixture first and review the actual render or inspection result before expanding scope.

## Smoke test

**not feasible here**. Needs gated or multi-gigabyte weights or a large GPU; not downloaded for documentation.

## Security, privacy and licensing

- Builds two local C++/CUDA extensions (texture_baker, uv_unwrapper) from source.
- Weights are safetensors, which avoids pickle loading.
- Inference runs locally after the weights download.
- The gated form asks for name, email, country, organization and intended use.

**Software license** Stability AI Community License Agreement (LICENSE.md, July 5, 2024).

**Model license** Stability AI Community License.

**Commercial use** Free for research, non-commercial and commercial use if you and your affiliates make under US $1,000,000 a year; commercial users must register with Stability AI. Above that the license ends and an enterprise license is needed. Redistribution needs the license, a Notice file and 'Powered by Stability AI'. Outputs may not train other foundation models.

## Evidence quotes

| Field | Upstream wording and file |
| --- | --- |
| hardware | 'The default options takes about 6GB VRAM for a single image input.' (README.md) |
| supported_platforms | 'For Windows (experimental): Visual Studio 2022'; 'MPS backend support was tested on M1 max 64GB' (README.md) |
| runtime_requirements | 'Python >= 3.8'; 'Update setuptools by pip install -U setuptools==69.5.1' (README.md) |
| installation | 'install the remaining requirements with pip install -r requirements.txt' (README.md) |
| license | 'STABILITY AI COMMUNITY LICENSE AGREEMENT Last Updated: July 5, 2024' (LICENSE.md) |
| model_license | HF API cardData license_name 'stabilityai-ai-community', gated 'auto' |
| model | 'Our model is gated at Hugging Face' (README.md) |
| inputs | 'If the image already has an alpha channel, you can skip the background removal step.' (gradio_app.py) |
| outputs | 'This will save the reconstructed 3D model as a GLB file to output/.' (README.md) |
| commercial_use_notes | 'preserves free access ... for people or organizations generating annual revenue of less than US $1,000,000' (LICENSE.md) |
| cpu_fallback | 'CPU backend will automatically be used if no GPU is detected in your system.' (README.md) |
