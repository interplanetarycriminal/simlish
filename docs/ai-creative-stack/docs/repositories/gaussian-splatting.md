# Gaussian Splatting

Use for training a radiance-field scene of 3D Gaussians from posed photos (COLMAP) and viewing it in real time.

> AI-assisted 3D asset production · Source C · smoke test: **not feasible here**

## Evidence and maintenance

- [Canonical reference](https://github.com/graphdeco-inria/gaussian-splatting)
- Verified 2026-11-26 against default branch `main` at [`54c035f7834b`](https://github.com/graphdeco-inria/gaussian-splatting/commit/54c035f7834b564019656c3e3fcc3646292f727d).
- GitHub reports archive state **false** and a repository push at `2025-10-17T14:28:15Z`. Push activity is a maintenance signal, not a quality rating.
- Attribution: Confirmed. Named in the user-supplied transcript of source C.

- [README.md](https://github.com/graphdeco-inria/gaussian-splatting/blob/54c035f7834b564019656c3e3fcc3646292f727d/README.md)
- [LICENSE.md](https://github.com/graphdeco-inria/gaussian-splatting/blob/54c035f7834b564019656c3e3fcc3646292f727d/LICENSE.md)
- [environment.yml](https://github.com/graphdeco-inria/gaussian-splatting/blob/54c035f7834b564019656c3e3fcc3646292f727d/environment.yml)
- [__init__.py](https://github.com/graphdeco-inria/gaussian-splatting/blob/54c035f7834b564019656c3e3fcc3646292f727d/scene/__init__.py)

## Runtime, hardware and setup

- **Type** model and inference code. Primary language Python.
- **Platforms** Windows, Linux.
- **Runtime** Conda; environment.yml pins Python 3.7.13, PyTorch 1.12.1, cudatoolkit 11.6. README asks for CUDA SDK 11 (used 11.8, 'known issues with 11.6'), a compatible C++ compiler (Visual Studio 2019 on Windows); a newer env (Python 3.8, PyTorch 2.0.0, CUDA 12) reportedly works. Viewers: OpenGL 4.5, CMake build of SIBR, Visual Studio or g++ (not Clang).
- **Execution** local.
- **Agent paths** Generic coding agent via project files. Client claims describe documentation and remain untested here unless the smoke test says otherwise.
- **Configuration** Train with python train.py -s <COLMAP or NeRF Synthetic dataset>; flags control resolution (-r), --data_device, iterations (30_000 default), --antialiasing, depth regularization, exposure compensation and --optimizer_type sparse_adam with the accelerated rasterizer. The network GUI server binds 127.0.0.1:6009 by default.
- **Credentials and services** None.

| Hardware | Documented value |
| --- | --- |
| GPU | NVIDIA CUDA GPU (Compute Capability 7.0+) |
| Minimum VRAM | Not documented |
| Recommended VRAM | 24 GB |
| System RAM | Not documented |
| Storage | Conda env needs significant disk; sample datasets 650 MB, pre-trained models 14 GB, evaluation images 7 GB, Windows viewers 60 MB. |
| CPU fallback | not documented |
| Training versus inference | Training: 24 GB VRAM for paper-quality 30k iterations; viewers: OpenGL 4.5 GPU with 4 GB VRAM recommended, CUDA CC 7.0+ for the real-time viewer. |
| Weights | No pretrained network; each scene is optimized from its own photos. Optional pre-trained scene models (14 GB) hosted at repo-sam.inria.fr. (public) |
| Weights size | 14 GB (pre-trained evaluation scenes, optional) |
| Notes | FAQ: VRAM grows with Gaussian count; 7k-iteration runs need significantly less; raise --densify_grad_threshold or lower --densify_until_iter, use --data_device cpu, and set --test_iterations -1 to fit smaller GPUs. |

Review the source and pin the version before running the upstream-documented command. It was read in the pinned documentation; execution is recorded only under Smoke test.

```sh
git clone https://github.com/graphdeco-inria/gaussian-splatting --recursive
SET DISTUTILS_USE_SDK=1 # Windows only
conda env create --file environment.yml
conda activate gaussian_splatting
```

## Contracts and selection

| Boundary | Contract |
| --- | --- |
| Input | COLMAP dataset: images/ plus sparse/0/cameras.bin, images.bin, points3D.bin (SIMPLE_PINHOLE or PINHOLE), Synthetic NeRF (Blender) dataset, Raw photos in <location>/input processed by convert.py (needs COLMAP; ImageMagick for resize), Optional monocular depth maps (Depth-Anything-V2) for depth regularization |
| Output | point_cloud/iteration_<N>/point_cloud.ply (Gaussian model), input.ply copy of SfM points, Checkpoints, Rendered test/train images and PSNR/SSIM/LPIPS metrics |
| Primary | Spatial reconstruction, 3D rendering |
| Supporting | Media processing |

Skip if the work is commercial and you have no Inria license; the code is research and evaluation only. Consider [comfyui-3d-pack](comfyui-3d-pack.md). Complementary tools include [blender-skills](blender-skills.md), [three-js](three-js.md), [sam-3d-objects](sam-3d-objects.md).

Input comes from COLMAP; output is a Gaussian PLY for splat viewers. ComfyUI-3D-Pack has its own separate 3DGS nodes.

- Skip if you only have a single image; it needs many posed photos and COLMAP reconstruction.
- No macOS support: the FAQ says platforms outside Windows and Ubuntu are unsupported.
- environment.yml pins cudatoolkit 11.6 while the README warns of known issues with CUDA 11.6.

## Craft notes

- Reference-quality radiance fields: default 30k iterations with SH degree 3, saves Gaussians at 7k and 30k; inputs wider than 1.6K px are auto-downscaled.
- October 2024 update adds Taming-3DGS rasterizer (1.6x faster, 2.7x with sparse_adam), Mip-Splatting anti-aliasing, depth regularization and exposure compensation.
- Struggles with multi-scale scenes (close-ups mixed with far shots, e.g. driving data); lower position and scaling learning rates for large scenes.

## Examples

1. **Independent** Convert 200 phone photos of a room with convert.py, train for 30k iterations and open the result in SIBR_gaussianViewer_app.
2. **Combined** Proposed handoff: train a scene here, then load point_cloud.ply into comfyui-3d-pack's Gaussian Splatting Orbit Renderer for turntable video.

For both, save the inputs and output evidence with the selected version. Use a small authorized fixture first and review the actual render or inspection result before expanding scope.

## Smoke test

**not feasible here**. Needs gated or multi-gigabyte weights or a large GPU; not downloaded for documentation.

## Security, privacy and licensing

- Clone is recursive and builds CUDA submodules (diff-gaussian-rasterization, simple-knn, fused-ssim) and SIBR from source.
- Training opens a GUI socket on 127.0.0.1:6009 by default; changing --ip exposes it on the network.
- Windows viewer binaries are a prebuilt zip from repo-sam.inria.fr.
- All processing is local; captured photos of people or places stay on disk but end up baked into the .ply.

**Software license** Gaussian-Splatting License (Inria and MPII; research and evaluation only, non-commercial).

**Model license** Not separately stated. The optional pre-trained evaluation scenes are distributed by Inria alongside the research-only Gaussian-Splatting License; treat them under the same terms until confirmed..

**Commercial use** License grants use for research purposes only, non-commercially, without right to sublicense; commercial use, exploitation or distribution needs prior explicit consent from Inria (contact stip-sophia.transfert@inria.fr). Not usable in a commercial product as is.

## Evidence quotes

| Field | Upstream wording and file |
| --- | --- |
| hardware | 'CUDA-ready GPU with Compute Capability 7.0+'; '24 GB VRAM (to train to paper evaluation quality)' (README.md) |
| installation | 'conda env create --file environment.yml' (README.md) |
| license | 'may be used "non-commercially", i.e., for research and/or evaluation purposes only' (LICENSE.md) |
| model_license | No separate model weights; pre-trained scenes linked without licence statement (README.md) |
| inputs | 'Path to the source directory containing a COLMAP or Synthetic NeRF data set' (README.md) |
| outputs | 'self.gaussians.save_ply(os.path.join(point_cloud_path, "point_cloud.ply"))' (scene/__init__.py) |
| commercial_use_notes | 'YOU MUST CONTACT INRIA FOR ANY UNAUTHORIZED USE: stip-sophia.transfert@inria.fr' (LICENSE.md) |
| viewer | 'OpenGL 4.5-ready GPU and drivers'; '4 GB VRAM recommended' (README.md) |
