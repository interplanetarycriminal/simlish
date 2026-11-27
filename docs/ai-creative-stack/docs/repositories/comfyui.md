# ComfyUI

Use for running open image, video, audio and 3D generation models locally as node-graph workflows, and for driving those workflows from code over its HTTP API.

> #40 · Motion films, explainers and engines · Source D (cinema) · smoke test: **passed**

## Evidence and maintenance

- [Canonical reference](https://github.com/Comfy-Org/ComfyUI)
- Verified 2026-11-26 against default branch `master` at [`4a4b3409792d`](https://github.com/Comfy-Org/ComfyUI/commit/4a4b3409792d499cc36626d76a24fe425f40b5e7).
- GitHub reports archive state **false** and a repository push at `2026-11-26T09:11:37Z`. Push activity is a maintenance signal, not a quality rating.
- Attribution: Listed in the cinematic post (source D, transcript supplied by the user on 2026-11-26); first added to this catalogue on 2026-11-26.

- [README.md](https://github.com/Comfy-Org/ComfyUI/blob/4a4b3409792d499cc36626d76a24fe425f40b5e7/README.md)
- [installation.md](https://github.com/Comfy-Org/ComfyUI/blob/4a4b3409792d499cc36626d76a24fe425f40b5e7/docs/installation.md)
- [pyproject.toml](https://github.com/Comfy-Org/ComfyUI/blob/4a4b3409792d499cc36626d76a24fe425f40b5e7/pyproject.toml)
- [requirements.txt](https://github.com/Comfy-Org/ComfyUI/blob/4a4b3409792d499cc36626d76a24fe425f40b5e7/requirements.txt)
- [server.py](https://github.com/Comfy-Org/ComfyUI/blob/4a4b3409792d499cc36626d76a24fe425f40b5e7/server.py)
- [cli_args.py](https://github.com/Comfy-Org/ComfyUI/blob/4a4b3409792d499cc36626d76a24fe425f40b5e7/comfy/cli_args.py)
- [LICENSE](https://github.com/Comfy-Org/ComfyUI/blob/4a4b3409792d499cc36626d76a24fe425f40b5e7/LICENSE)

## Runtime, hardware and setup

- **Type** application. Primary language Python.
- **Platforms** Windows, Linux, macOS.
- **Runtime** Python >=3.10 (pyproject); 3.13 very well supported, 3.14 works with some custom-node issues. torch 2.7 minimally supported; PyTorch cu130 or above required on NVIDIA 20 series and newer. ROCm 7.2 wheels on Linux; ROCm 10.0 with torch 2.13 and Python 3.13 on Windows AMD; Intel Arc via torch xpu; Apple Silicon via PyTorch nightly; Huawei Ascend, Cambricon MLU, Iluvatar Corex.
- **Execution** local or hosted.
- **Agent paths** Generic coding agent via HTTP API (POST /prompt, GET /history, GET /view, WebSocket), MCP clients via the separate Comfy MCP product. Client claims describe documentation and remain untested here unless the smoke test says otherwise.
- **Configuration** Install PyTorch for your GPU first; put checkpoints in models/checkpoints and VAEs in models/vae, or map other folders with extra_model_paths.yaml. Server listens on 127.0.0.1:8188 by default (--listen, --port, --tls-keyfile/--tls-certfile, --offline).
- **Credentials and services** None for local use. Optional paid partner/API nodes (e.g. Nano Banana, Seedance) need a Comfy account; --offline or --disable-partner-nodes turns them off.

| Hardware | Documented value |
| --- | --- |
| GPU | NVIDIA CUDA, AMD ROCm, Intel Arc (xpu), Apple Silicon (MPS) supported; also Ascend, Cambricon, Iluvatar |
| Minimum VRAM | 4 GB |
| Recommended VRAM | Not documented |
| System RAM | 8 GB |
| Storage | Model checkpoints are user-supplied (models/checkpoints, models/vae); size depends on models |
| CPU fallback | documented |
| Training versus inference | Inference |
| Notes | README claims the biggest open models run on as little as 4 GB VRAM + 8 GB RAM using asynchronous weight streaming. --cpu runs everything on the CPU (slow); GTX 10 series and older need the legacy cu126 portable build. |

Review the source and pin the version before running the upstream-documented command. It was read in the pinned documentation; execution is recorded only under Smoke test.

```sh
git clone https://github.com/Comfy-Org/ComfyUI.git
cd ComfyUI
pip install -r requirements.txt
python main.py
```

## Contracts and selection

| Boundary | Contract |
| --- | --- |
| Input | Workflow graphs as JSON (UI or API format), Text prompts, Images, video, audio and 3D files, Model weights (checkpoints, diffusion models, VAEs, text encoders, LoRAs, ControlNets, upscalers), Media made by ComfyUI (dropped onto the canvas to recover its workflow) |
| Output | Images (incl. 16-bit PNG, 32-bit EXR, 10-bit AVIF, HDR), Video, Audio, 3D models, Text, Workflow metadata embedded in outputs |
| Primary | Media processing, Illustration |
| Supporting | Upscaling, Image-to-3D, Animation, Spatial reconstruction |

Skip if you cannot accept GPL-3.0 obligations when redistributing a modified ComfyUI inside your product. Consider [dream-textures](dream-textures.md). Complementary tools include [comfyui-3d-pack](comfyui-3d-pack.md), [real-esrgan](real-esrgan.md), [trellis-2](trellis-2.md), [stable-fast-3d](stable-fast-3d.md), [blender-mcp](blender-mcp.md).

ComfyUI hosts custom node packs such as ComfyUI-3D-Pack. Its HTTP API takes workflow JSON on POST /prompt.

- Skip on GPUs whose drivers cannot run PyTorch cu130 or newer, unless you use the legacy cu126 portable build.

## Craft notes

- The README recommends ComfyUI-native quantised formats (convrot int8, w6a8) over GGUF, claiming more than 2x speed, and removing extra launch flags because most hurt performance.
- Partial graph re-execution and smart VRAM/RAM offloading let you change one node and re-run only what changed.
- It is the host for custom node packs such as ComfyUI-3D-Pack; --disable-all-custom-nodes is the first troubleshooting step when a node breaks startup.

## Examples

1. **Independent** POST an API-format workflow JSON to http://127.0.0.1:8188/prompt, then poll /history/{prompt_id} and download the image from /view.
2. **Combined** Install comfyui-3d-pack as custom nodes so an image generated in ComfyUI flows straight into an image-to-3D node in the same graph.

For both, save the inputs and output evidence with the selected version. Use a small authorized fixture first and review the actual render or inspection result before expanding scope.

## Smoke test

**passed**. Read-only query of a running local ComfyUI 0.42.5: GET /system_stats answered with Python 3.13, PyTorch 2.14.1+cu130 and one 24 GB CUDA GPU. No workflow was run.

## Security, privacy and licensing

- Custom nodes are arbitrary Python code installed from third parties (often via ComfyUI-Manager); vet them before installing.
- The server binds to 127.0.0.1 by default; --listen exposes it to the network, so add TLS and access control before doing that.
- Core runs fully offline and downloads nothing unless asked; partner/API nodes send inputs to paid third-party services.
- Outputs embed the full workflow and seeds in their metadata, which reveals your prompts when shared.

**Software license** GPL-3.0.

**Model license** Not applicable to ComfyUI itself; each model you load keeps its own license.

**Commercial use** GPL-3.0 allows commercial use; distributing ComfyUI or modified versions requires releasing source under GPL-3.0. Output rights depend on the license of the model used. Comfy Enterprise offers separate commercial licensing.

## Evidence quotes

| Field | Upstream wording and file |
| --- | --- |
| hardware | 'Can run even the biggest open source models on as low as 4GB vram + 8GB ram' (README.md) |
| cpu_fallback | '--cpu', 'To use the CPU for everything (slow).' (comfy/cli_args.py) |
| installation | 'pip install -r requirements.txt' then 'python main.py' (README.md) |
| runtime_requirements | 'torch 2.7 is minimally supported and cu130 or above is required on Nvidia 20 series and above' (README.md) |
| license | 'GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007' (LICENSE) |
| model_license | No weights shipped; 'Put your checkpoints in models/checkpoints' (README.md) |
| inputs | 'Save and load workflows as JSON.' (README.md) |
| outputs | '16 bit PNG images, 32 bit EXR, 10 bit AVIF are supported' (README.md) |
| api | @routes.post("/prompt") and @routes.get("/history") in server.py; default port 8188 (comfy/cli_args.py) |
