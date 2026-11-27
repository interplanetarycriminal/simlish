# UniRig

Use for automatically adding a skeleton and per-vertex skinning weights to humans, animals and objects.

> #29 · AI-assisted 3D asset production · Source C (3D) · smoke test: **not feasible here**

## Evidence and maintenance

- [Canonical reference](https://github.com/VAST-AI-Research/UniRig)
- Verified 2026-11-26 against default branch `main` at [`6793c6640ff0`](https://github.com/VAST-AI-Research/UniRig/commit/6793c6640ff01c8fb389f3993434124bb43d2933).
- GitHub reports archive state **false** and a repository push at `2026-06-04T07:15:34Z`. Push activity is a maintenance signal, not a quality rating.
- Attribution: Confirmed. Named in the user-supplied transcript of source C.

- [README.md](https://github.com/VAST-AI-Research/UniRig/blob/6793c6640ff01c8fb389f3993434124bb43d2933/README.md)
- [LICENSE](https://github.com/VAST-AI-Research/UniRig/blob/6793c6640ff01c8fb389f3993434124bb43d2933/LICENSE)
- [requirements.txt](https://github.com/VAST-AI-Research/UniRig/blob/6793c6640ff01c8fb389f3993434124bb43d2933/requirements.txt)
- [generate_skeleton.sh](https://github.com/VAST-AI-Research/UniRig/blob/6793c6640ff01c8fb389f3993434124bb43d2933/launch/inference/generate_skeleton.sh)
- [merge.sh](https://github.com/VAST-AI-Research/UniRig/blob/6793c6640ff01c8fb389f3993434124bb43d2933/launch/inference/merge.sh)
- [merge.py](https://github.com/VAST-AI-Research/UniRig/blob/6793c6640ff01c8fb389f3993434124bb43d2933/src/inference/merge.py)
- [LICENSE](https://github.com/VAST-AI-Research/UniRig/blob/6793c6640ff01c8fb389f3993434124bb43d2933/src/model/michelangelo/LICENSE)
- [LICENSE](https://github.com/VAST-AI-Research/UniRig/blob/6793c6640ff01c8fb389f3993434124bb43d2933/src/model/pointcept/LICENSE)
- [UniRig](https://huggingface.co/api/models/VAST-AI/UniRig)

## Runtime, hardware and setup

- **Type** model and inference code. Primary language Python.
- **Platforms** Unverified.
- **Runtime** Python 3.11; PyTorch >= 2.3.1 (tested); spconv matched to your CUDA; torch_scatter and torch_cluster from the PyG wheel index; numpy 1.26.4; bpy==4.2 (Blender as a Python module); flash_attn; transformers 4.51.3. Launch scripts are bash.
- **Execution** local.
- **Agent paths** Generic coding agent via project files. Client claims describe documentation and remain untested here unless the smoke test says otherwise.
- **Configuration** Three bash steps: generate_skeleton.sh (--seed for variations), generate_skin.sh, then merge.sh to transfer the result onto the original model. Optional modified VRM add-on enables .vrm import/export.
- **Credentials and services** None; checkpoints are public on Hugging Face.

| Hardware | Documented value |
| --- | --- |
| GPU | NVIDIA CUDA GPU |
| Minimum VRAM | 8 GB |
| Recommended VRAM | Not documented |
| System RAM | Not documented |
| Storage | About 11.5 GB in the HF repo including datasets; inference checkpoints: skeleton articulation-xl 1.4 GB, skin articulation-xl 4.4 GB (HF API). |
| CPU fallback | not documented |
| Training versus inference | Inference: CUDA GPU with at least 8 GB VRAM. Skeleton training: best around epoch 120, about 18 h on 4x RTX 4090. Skin training: at least 60 GB on one GPU even at batch size 2. |
| Weights | Hugging Face VAST-AI/UniRig (public, auto-downloaded by scripts) (public) |
| Weights size | About 11.5 GB repo total incl. datasets; skeleton 1.4 GB + skin 4.4 GB checkpoints for inference |
| Notes | Skeleton preprocessing simplifies input to 50,000 faces by default (faces_target_count). Bone-attribute (physics stiffness) prediction is still 'Coming Soon'. |

Review the source and pin the version before running the upstream-documented command. It was read in the pinned documentation; execution is recorded only under Smoke test.

```sh
git clone https://github.com/VAST-AI-Research/UniRig
cd UniRig
conda create -n UniRig python=3.11
conda activate UniRig
python -m pip install torch torchvision
python -m pip install -r requirements.txt
python -m pip install spconv-{you-cuda-version}
python -m pip install torch_scatter torch_cluster -f https://data.pyg.org/whl/torch-{your-torch-version}+{your-cuda-version}.html --no-cache-dir
python -m pip install numpy==1.26.4
```

## Contracts and selection

| Boundary | Contract |
| --- | --- |
| Input | 3D model in .obj, .fbx, .glb or .vrm (README); launch scripts also accept .dae and .gltf, For skinning: an FBX with a predicted or edited skeleton |
| Output | Skeleton FBX, Skinned FBX, Rigged model after merge in .glb/.gltf, .fbx, .vrm or .dae (Blender exporters in merge.py), NPZ of predicted skeleton/skin |
| Primary | Rigging |
| Supporting | Animation |

Skip if you need physics bone attributes or the paper's Rig-XL/VRoid model; only the Articulation-XL2.0 checkpoint is released. Consider the existing project toolchain. Complementary tools include [trellis-2](trellis-2.md), [stable-fast-3d](stable-fast-3d.md), [sam-3d-objects](sam-3d-objects.md), [meshanything-v2](meshanything-v2.md), [blender-mcp](blender-mcp.md), [blender-skills](blender-skills.md), [three-js](three-js.md), [comfyui-3d-pack](comfyui-3d-pack.md).

UniRig's merge step uses Blender's Python module (bpy 4.2) to write FBX, GLB, VRM or DAE. Import into Blender is a documented file handoff.

- Skinning quality drops sharply when the skeleton misses bones (tails, wings); edit the skeleton before skinning.
- For new work, check the successor SkinTokens, which the README says improves skinning accuracy 98%-133%.

## Craft notes

- Two-stage: a GPT-like transformer predicts the skeleton with Skeleton Tree Tokenization, then Bone-Point Cross Attention predicts skin weights; both are in the current release.
- Merging a skeleton-only FBX gives no skinning; merge the skin FBX instead. Different --seed values give skeleton variations.
- The README now points to SkinTokens, a successor that unifies skeleton and skinning in one autoregressive sequence.

## Examples

1. **Independent** Rig the example giraffe.glb with generate_skeleton.sh, generate_skin.sh and merge.sh into giraffe_rigged.glb.
2. **Combined** Proposed handoff: create a creature GLB with trellis-2, rig it with UniRig, then pose it in Blender through blender-mcp.

For both, save the inputs and output evidence with the selected version. Use a small authorized fixture first and review the actual render or inspection result before expanding scope.

## Smoke test

**not feasible here**. Needs gated or multi-gigabyte weights or a large GPU; not downloaded for documentation.

## Security, privacy and licensing

- Merge step runs Blender (bpy 4.2) on your files and installs a modified VRM add-on zip from the repo.
- Checkpoints are .ckpt pickle files fetched automatically from Hugging Face.
- Runs locally; training configs include optional Weights & Biases logging, which you can comment out.

**Software license** MIT (repository); vendored src/model/michelangelo is GPL-3.0; src/model/pointcept is MIT.

**Model license** MIT (HF metadata).

**Commercial use** MIT for the main code and weights allows commercial use. The vendored Michelangelo shape encoder carries GPL-3.0, so redistributing a product that includes it brings GPL obligations. Released checkpoint is trained on Articulation-XL2.0; dataset terms not inspected.

## Evidence quotes

| Field | Upstream wording and file |
| --- | --- |
| hardware | 'For generation: CUDA-enabled GPU with at least 8GB VRAM' (README.md) |
| runtime_requirements | 'Python 3.11'; 'PyTorch (tested with version >=2.3.1)' (README.md); 'bpy==4.2' (requirements.txt) |
| installation | 'python -m pip install -r requirements.txt' and 'python -m pip install spconv-{you-cuda-version}' (README.md) |
| license | 'MIT License ... Copyright (c) 2025 VAST-AI-Research' (LICENSE); 'GNU GENERAL PUBLIC LICENSE Version 3' (src/model/michelangelo/LICENSE) |
| model_license | HF API tags 'license:mit', gated False (VAST-AI/UniRig) |
| inputs | 'Supported input formats: .obj, .fbx, .glb, and .vrm' (README.md); 'require_suffix="obj,fbx,FBX,dae,glb,gltf,vrm"' (generate_skeleton.sh) |
| outputs | merge.py exports via export_scene.vrm, export_scene.fbx, export_scene.gltf and collada_export |
| skinning | 'Automated Skinning Prediction: Predicts per-vertex skinning weights. (Available in current release)' (README.md) |
| successor | 'Introducing SkinTokens! ... the powerful successor to UniRig' (README.md) |
