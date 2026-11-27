# Real-ESRGAN

Use when a reference A/B test confirms a valuable restoration improvement.

> #22 · Video composition and post-production · Source B · smoke test: **not run**

## Evidence and maintenance

- [Canonical reference](https://github.com/xinntao/Real-ESRGAN)
- Verified 2026-11-26 against default branch `master` at [`a4abfb2979a7`](https://github.com/xinntao/Real-ESRGAN/commit/a4abfb2979a7bbff3f69f58f58ae324608821e27).
- GitHub reports archive state **false** and a repository push at `2024-08-06T13:15:18Z`. Push activity is a maintenance signal, not a quality rating.
- Attribution: Provisional. Sources A and B were recovered from likely matching mirrored posts; the posts themselves were not readable here. The A/B split follows the order of the seed list (simlish README) and catalogue v1.

- [README.md](https://github.com/xinntao/Real-ESRGAN/blob/a4abfb2979a7bbff3f69f58f58ae324608821e27/README.md)
- [LICENSE](https://github.com/xinntao/Real-ESRGAN/blob/a4abfb2979a7bbff3f69f58f58ae324608821e27/LICENSE)
- [requirements.txt](https://github.com/xinntao/Real-ESRGAN/blob/a4abfb2979a7bbff3f69f58f58ae324608821e27/requirements.txt)

## Runtime, hardware and setup

- **Type** restoration model and CLI scripts. Primary language Python.
- **Platforms** Python environment, Vulkan binaries by upstream platform.
- **Runtime** Python 3.7+ documented, compatible PyTorch environment. Vulkan alternative described upstream.
- **Execution** local.
- **Agent paths** Generic coding agent via shell. Client claims describe documentation and remain untested here unless the smoke test says otherwise.
- **Configuration** Select compatible weights and check output scale, tile size and device before batching.
- **Credentials and services** No separate API key established for local inference.

| Hardware | Documented value |
| --- | --- |
| GPU | NVIDIA CUDA GPU recommended (unverified) |
| Minimum VRAM | Not documented |
| Recommended VRAM | Not documented |
| System RAM | Not documented |
| Storage | Not documented |
| CPU fallback | not applicable |
| Training versus inference | Not documented |
| Weights | GitHub release assets of the repository (public) |
| Weights size | Not documented |

Review the source and pin the version before running the upstream-documented command. It was read in the pinned documentation; execution is recorded only under Smoke test.

```sh
pip install -r requirements.txt
```

## Contracts and selection

| Boundary | Contract |
| --- | --- |
| Input | Images or video frames and optional model selection |
| Output | Restored/upscaled images or processed video via supported script |
| Primary | Upscaling |
| Supporting | — |

Skip native-resolution media or footage where hallucinated details are unacceptable. Consider the existing project toolchain. Complementary tools include [ffmpeg](ffmpeg.md), [stable-fast-3d](stable-fast-3d.md), [dream-textures](dream-textures.md), [comfyui-3d-pack](comfyui-3d-pack.md), [trellis-2](trellis-2.md), [effectcraft](effectcraft.md), [comfyui](comfyui.md).

No native integration with catalogue peers is asserted. Examples using another tool are proposed handoffs.

## Craft notes

- General restoration and upscaling models with CLI scripts, including RealESRGAN_x4plus_anime_6B and the AnimeVideo-v3 model.
- Upscaling invents detail. A/B test at delivery size, and keep it off text, UI captures and faces that must stay accurate. Repository activity stopped in 2024.

## Examples

1. **Independent** Compare small crops of an image at native size and upscaled size before batching.
2. **Combined** Restore numbered video frames and use FFmpeg to reassemble with original audio and cadence.

For both, save the inputs and output evidence with the selected version. Use a small authorized fixture first and review the actual render or inspection result before expanding scope.

## Smoke test

**not run**. No run is recorded.

## Security, privacy and licensing

- Verify model provenance and weight terms separately. Inspect for hallucinations and temporal instability.
- No external service in the documented base workflow.

**Software license** BSD-3-Clause.

**Model license** Not established separately from the BSD-3-Clause code license.

**Commercial use** Preserve BSD notices and confirm the terms of separately downloaded weights.
