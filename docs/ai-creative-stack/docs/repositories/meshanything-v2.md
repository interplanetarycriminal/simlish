# MeshAnything V2

Use for converting a dense scanned or generated mesh (or point cloud with normals) into a low-poly, artist-style triangle mesh.

> AI-assisted 3D asset production · Source C · smoke test: **not feasible here**

## Evidence and maintenance

- [Canonical reference](https://github.com/buaacyw/MeshAnythingV2)
- Verified 2026-11-26 against default branch `main` at [`461d3b6ed750`](https://github.com/buaacyw/MeshAnythingV2/commit/461d3b6ed750ab3443281b2e4a0e30e8ee98097e).
- GitHub reports archive state **false** and a repository push at `2025-04-28T16:36:51Z`. Push activity is a maintenance signal, not a quality rating.
- Attribution: Confirmed. Named in the user-supplied transcript of source C.

- [README.md](https://github.com/buaacyw/MeshAnythingV2/blob/461d3b6ed750ab3443281b2e4a0e30e8ee98097e/README.md)
- [LICENSE.txt](https://github.com/buaacyw/MeshAnythingV2/blob/461d3b6ed750ab3443281b2e4a0e30e8ee98097e/LICENSE.txt)
- [requirements.txt](https://github.com/buaacyw/MeshAnythingV2/blob/461d3b6ed750ab3443281b2e4a0e30e8ee98097e/requirements.txt)
- [main.py](https://github.com/buaacyw/MeshAnythingV2/blob/461d3b6ed750ab3443281b2e4a0e30e8ee98097e/main.py)
- [MeshAnythingV2](https://huggingface.co/api/models/Yiwen-ntu/MeshAnythingV2)

## Runtime, hardware and setup

- **Type** model and inference code. Primary language Python.
- **Platforms** Linux.
- **Runtime** Tested on Ubuntu 22 with CUDA 11.8; Python 3.10.13 (conda); torch 2.1.1, torchvision 0.16.1, torchaudio 2.1.1 (cu118); transformers 4.39.3; flash-attn.
- **Execution** local or hosted.
- **Agent paths** Generic coding agent via project files. Client claims describe documentation and remain untested here unless the smoke test says otherwise.
- **Configuration** main.py takes --input_type mesh|pc_normal, --input_dir or --input_path, --out_dir, --mc and --mc_level (default 7 = 128^3). Inputs are normalized to a unit box; +Y up gives better results.
- **Credentials and services** None; weights download from a public Hugging Face repo.

| Hardware | Documented value |
| --- | --- |
| GPU | NVIDIA CUDA GPU |
| Minimum VRAM | Not documented |
| Recommended VRAM | 8 GB |
| System RAM | Not documented |
| Storage | About 4.0 GB in the HF weights repo (350m.pth and model.safetensors, 2.0 GB each) per HF API. |
| CPU fallback | not documented |
| Training versus inference | Inference about 8 GB and 45 s per mesh on an A6000. Training example uses 8 GPUs (accelerate, batch 2 per GPU); env tested on A800. |
| Weights | Hugging Face Yiwen-ntu/MeshAnythingV2 (public) (public) |
| Weights size | About 4.0 GB total per HF API |
| Notes | Generation time depends on the output face count. Marching Cubes preprocessing (--mc) takes several minutes; --mc_level 8 (256^3) is slower but keeps fine detail. |

Review the source and pin the version before running the upstream-documented command. It was read in the pinned documentation; execution is recorded only under Smoke test.

```sh
git clone https://github.com/buaacyw/MeshAnythingV2.git && cd MeshAnythingV2
conda create -n MeshAnythingV2 python==3.10.13 -y
conda activate MeshAnythingV2
pip install torch==2.1.1 torchvision==0.16.1 torchaudio==2.1.1 --index-url https://download.pytorch.org/whl/cu118
pip install -r requirements.txt
pip install flash-attn --no-build-isolation
pip install -U gradio
```

## Contracts and selection

| Boundary | Contract |
| --- | --- |
| Input | Mesh (.obj or .ply) with --input_type mesh, Point cloud .npy of shape (N, 6) with xyz and unit normals, at least 8192 points, with --input_type pc_normal |
| Output | Untextured triangle mesh .obj (at most 1600 faces), flat orange face colors |
| Primary | Retopology |
| Supporting | 3D authoring |

Skip if you need more than 1600 faces, a textured result or commercial rights; MeshAnything V2 gives none of these. Consider the existing project toolchain. Complementary tools include [sam-3d-objects](sam-3d-objects.md), [trellis-2](trellis-2.md), [stable-fast-3d](stable-fast-3d.md), [unirig](unirig.md), [blender-mcp](blender-mcp.md), [comfyui-3d-pack](comfyui-3d-pack.md), [blender-skills](blender-skills.md).

No native integration with catalogue peers is asserted. Examples using another tool are proposed handoffs.

- Soft or blobby inputs from feed-forward generators often give poor results; the authors suggest scans, SDS methods or Rodin output.

## Craft notes

- Uses Adjacent Mesh Tokenization to write meshes face by face like an artist; trained only on meshes under 1600 faces and cannot exceed that.
- Mesh input is turned into a point cloud internally; run --mc (Marching Cubes) first on non-MC meshes and raise --mc_level to 8 for delicate shapes.
- About 8 GB VRAM and 45 s per mesh on an A6000; output is a bare .obj with no UVs or texture.

## Examples

1. **Independent** Convert a dense photogrammetry .obj of a sword into a sub-1600-face artist mesh with main.py --input_type mesh --mc.
2. **Combined** Proposed handoff: generate a dense GLB with trellis-2, then run MeshAnything V2 to get a low-poly stand-in for a mobile game.

For both, save the inputs and output evidence with the selected version. Use a small authorized fixture first and review the actual render or inspection result before expanding scope.

## Smoke test

**not feasible here**. Needs gated or multi-gigabyte weights or a large GPU; not downloaded for documentation.

## Security, privacy and licensing

- main.py loads 350m.pth / safetensors from Hugging Face; prefer the safetensors file.
- flash-attn is built from source with --no-build-isolation.
- Runs fully locally after the weight download; no telemetry is mentioned.

**Software license** S-Lab License 1.0 (non-commercial).

**Model license** MIT (Hugging Face metadata for Yiwen-ntu/MeshAnythingV2).

**Commercial use** The code license allows redistribution and use for non-commercial purposes only; commercial use requires contacting the authors. The HF weights are tagged MIT, but running them needs the S-Lab-licensed code, so treat commercial use as not allowed without permission.

## Evidence quotes

| Field | Upstream wording and file |
| --- | --- |
| hardware | 'It takes about 8GB and 45s to generate a mesh on an A6000 GPU' (README.md) |
| runtime_requirements | 'Our environment has been tested on Ubuntu 22, CUDA 11.8 with A800.' (README.md) |
| installation | 'pip install torch==2.1.1 torchvision==0.16.1 torchaudio==2.1.1 --index-url .../cu118' (README.md) |
| license | 'Redistribution and use for non-commercial purpose in source and binary forms ... are permitted' (S-Lab License 1.0) |
| model_license | HF API tags 'license:mit', gated False (Yiwen-ntu/MeshAnythingV2) |
| inputs | 'The file format should be a .npy file with shape (N, 6)' (README.md); 'assert cur_data.shape[0] >= 8192' (main.py) |
| outputs | 'cannot generate meshes with more than 1600 faces' (README.md); save_path ends '_gen.obj' (main.py) |
| face_limit | 'MeshAnything is trained on meshes with fewer than 1600 faces' (README.md) |
