# SAM 3D Objects

Use for turning masked objects in a real, cluttered photo into textured 3D objects with pose and scene layout.

> #26 · AI-assisted 3D asset production · Source C (3D) · smoke test: **not feasible here**

## Evidence and maintenance

- [Canonical reference](https://github.com/facebookresearch/sam-3d-objects)
- Verified 2026-11-26 against default branch `main` at [`f91db411c50e`](https://github.com/facebookresearch/sam-3d-objects/commit/f91db411c50efee93d8db7aeb323885650f6f722).
- GitHub reports archive state **false** and a repository push at `2026-06-02T21:16:44Z`. Push activity is a maintenance signal, not a quality rating.
- Attribution: Confirmed. Named in the user-supplied transcript of source C.

- [README.md](https://github.com/facebookresearch/sam-3d-objects/blob/f91db411c50efee93d8db7aeb323885650f6f722/README.md)
- [setup.md](https://github.com/facebookresearch/sam-3d-objects/blob/f91db411c50efee93d8db7aeb323885650f6f722/doc/setup.md)
- [LICENSE](https://github.com/facebookresearch/sam-3d-objects/blob/f91db411c50efee93d8db7aeb323885650f6f722/LICENSE)
- [default.yml](https://github.com/facebookresearch/sam-3d-objects/blob/f91db411c50efee93d8db7aeb323885650f6f722/environments/default.yml)
- [requirements.txt](https://github.com/facebookresearch/sam-3d-objects/blob/f91db411c50efee93d8db7aeb323885650f6f722/requirements.txt)
- [demo.py](https://github.com/facebookresearch/sam-3d-objects/blob/f91db411c50efee93d8db7aeb323885650f6f722/demo.py)
- [inference.py](https://github.com/facebookresearch/sam-3d-objects/blob/f91db411c50efee93d8db7aeb323885650f6f722/notebook/inference.py)
- [inference_pipeline.py](https://github.com/facebookresearch/sam-3d-objects/blob/f91db411c50efee93d8db7aeb323885650f6f722/sam3d_objects/pipeline/inference_pipeline.py)
- [sam-3d-objects](https://huggingface.co/api/models/facebook/sam-3d-objects)

## Runtime, hardware and setup

- **Type** model and inference code. Primary language Python.
- **Platforms** Linux.
- **Runtime** Linux 64-bit; conda/mamba env from environments/default.yml (Python 3.11.0, CUDA 12.1 toolchain); PyTorch 2.5.1 cu121 wheels; pytorch3d and Kaolin (torch-2.5.1_cu121) installed in separate pip steps; a Hydra patch script.
- **Execution** local or hosted.
- **Agent paths** Generic coding agent via project files. Client claims describe documentation and remain untested here unless the smoke test says otherwise.
- **Configuration** Load checkpoints/hf/pipeline.yaml through notebook/inference.py's Inference class. The pipeline decodes both 'gaussian' and 'mesh' formats by default; a seed and an optional pointmap can be passed.
- **Credentials and services** A Hugging Face account with approved access to facebook/sam-3d-objects and a read token (hf auth login) to download checkpoints.

| Hardware | Documented value |
| --- | --- |
| GPU | NVIDIA CUDA GPU |
| Minimum VRAM | 32 GB |
| Recommended VRAM | Not documented |
| System RAM | Not documented |
| Storage | About 13.2 GB of checkpoints in the Hugging Face repo (largest files: ss_generator 6.7 GB, slat_generator 4.9 GB), per HF API metadata. |
| CPU fallback | not documented |
| Training versus inference | Inference code and checkpoints only; encoder weights added 06/01/2026. No training recipe in the README. |
| Weights | Hugging Face facebook/sam-3d-objects (gated, manual approval; rejected in comprehensively sanctioned jurisdictions) (gated) |
| Weights size | About 13.2 GB total (31 files) per HF API |
| Notes | setup.md says the env may need to be built on a GPU compute node, or Pytorch3D raises 'Not compiled with GPU support'. No specific test GPU is named. |

Review the source and pin the version before running the upstream-documented command. It was read in the pinned documentation; execution is recorded only under Smoke test.

```sh
mamba env create -f environments/default.yml
mamba activate sam3d-objects
export PIP_EXTRA_INDEX_URL="https://pypi.ngc.nvidia.com https://download.pytorch.org/whl/cu121"
pip install -e '.[dev]'
pip install -e '.[p3d]'
export PIP_FIND_LINKS="https://nvidia-kaolin.s3.us-east-2.amazonaws.com/torch-2.5.1_cu121.html"
pip install -e '.[inference]'
./patching/hydra
pip install 'huggingface-hub[cli]<1.0'
hf download --repo-type model --local-dir checkpoints/hf-download --max-workers 1 facebook/sam-3d-objects
```

## Contracts and selection

| Boundary | Contract |
| --- | --- |
| Input | RGB image, Binary object mask per object (PNG), merged into the image alpha channel, Optional pointmap (otherwise estimated by a bundled MoGe depth model) |
| Output | Gaussian splat (.ply via output['gs'].save_ply), Textured mesh (GLB, output['glb'] when the mesh decoder runs), Object pose and layout for multi-object scenes |
| Primary | Image-to-3D, Spatial reconstruction |
| Supporting | Texturing |

Skip when you have less than 32 GB of VRAM, no Linux box, or no object mask; SAM 3D Objects needs all three. Consider [stable-fast-3d](stable-fast-3d.md), [trellis-2](trellis-2.md), [comfyui-3d-pack](comfyui-3d-pack.md). Complementary tools include [gaussian-splatting](gaussian-splatting.md), [three-js](three-js.md), [blender-mcp](blender-mcp.md), [meshanything-v2](meshanything-v2.md), [unirig](unirig.md).

No native integration with catalogue peers is asserted. Examples using another tool are proposed handoffs.

- Its scene-aware layout output is aimed at real photos; for a clean single product shot a lighter image-to-3D model may be enough.

## Craft notes

- Built for occluded, cluttered real-world scenes: it takes one image plus a mask per object and returns shape, texture, pose and layout, including multi-object scenes.
- The quick-start path exports a Gaussian splat (.ply); the pipeline also decodes a mesh and builds a GLB, but the demo runs it with mesh post-processing and texture baking off (vertex colors).
- Masks are mandatory, so pair it with a segmenter. The 32 GB VRAM floor rules out 24 GB consumer cards.

## Examples

1. **Independent** Mask the chair in a living-room photo and export it as a Gaussian splat .ply with SAM 3D Objects.
2. **Combined** Proposed handoff: reconstruct a toy from a photo with SAM 3D Objects, then pass the GLB mesh to unirig to add a skeleton and skinning.

For both, save the inputs and output evidence with the selected version. Use a small authorized fixture first and review the actual render or inspection result before expanding scope.

## Smoke test

**not feasible here**. Needs gated or multi-gigabyte weights or a large GPU; not downloaded for documentation.

## Security, privacy and licensing

- Install pulls packages from extra indexes (pypi.ngc.nvidia.com, download.pytorch.org, an NVIDIA Kaolin S3 bucket) and runs a repo patch script for Hydra.
- Checkpoints are .ckpt/.pt pickle files; load only from the official gated repo.
- Runs locally after the download; images are not sent anywhere by the inference code.
- Getting gated access shares your Hugging Face identity with Meta.

**Software license** SAM License (custom Meta license, covers code and checkpoints).

**Model license** SAM License.

**Commercial use** The SAM License grants a royalty-free right to use, modify and distribute, with no non-commercial clause. It requires shipping the license with redistributions, crediting SAM in publications, and bans ITAR, military, nuclear, espionage and weapons uses and sanctioned users. Meta may change the terms at any time.

## Evidence quotes

| Field | Upstream wording and file |
| --- | --- |
| hardware | 'A NVIDIA GPU with at least 32 Gb of VRAM.' (doc/setup.md) |
| supported_platforms | 'A linux 64-bits architecture (i.e. linux-64 platform in mamba info).' (doc/setup.md) |
| runtime_requirements | 'python=3.11.0' and cuda 12.1 packages (environments/default.yml); 'torchaudio==2.5.1+cu121' (requirements.txt) |
| installation | 'mamba env create -f environments/default.yml' then 'pip install -e .[dev]' (doc/setup.md) |
| license | 'The SAM 3D Objects model checkpoints and code are licensed under SAM License' (README.md) |
| model_license | 'SAM License ... Last Updated: November 19, 2025' (LICENSE) |
| model | 'please request access to the checkpoints on the SAM 3D Objects Hugging Face repo' (doc/setup.md); HF API gated=manual |
| inputs | 'load image (RGBA only, mask is embedded in the alpha channel)' (demo.py) |
| outputs | 'output["gs"].save_ply(f"splat.ply")' (README.md); 'decode_formats=["gaussian", "mesh"]' and 'outputs["glb"] = glb' (inference_pipeline.py) |
| commercial_use_notes | 'not use ... for any activities subject to the International Traffic in Arms Regulations' (LICENSE) |
