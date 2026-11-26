# Sources and provenance

Where every reference came from, how sure that attribution is, and how each URL was checked. Attribution and verification are tracked separately: a repository can be fully verified while its source attribution stays provisional.

![Collection provenance from three posts and a separate research list](docs/diagrams/collection-provenance.svg)

## Counts

| Group | References | Attribution status |
| --- | --- | --- |
| Source A only | 10 | Provisional |
| Source B only | 10 | Provisional |
| Shared by A and B | 5 | Provisional |
| **First two collections** | **25** | 15 + 15 − 5 shared |
| Source C | 7 | Confirmed from the user-supplied transcript |
| **Post-associated** | **32** | |
| Supplementary candidates | 12 | Not attributable to any post |
| **Working registry** | **44** | |

The validator recomputes these counts from [the registry](registry/repositories.json) and fails if they change without this page.

## The three posts

| Source | Post | How the list was obtained |
| --- | --- | --- |
| A | https://x.com/0xnicc0/status/2125567907522379841 | Recovered from a likely matching mirrored post. 15 references. |
| B | https://x.com/flxrnc/status/2125681086722097551 | Recovered from a likely matching mirrored post. 15 references. |
| C | https://x.com/thegreatest_sv/status/2125614738943934706 | A transcript supplied by the user, naming exactly seven repositories. |

The posts themselves were not readable from this environment. The A/B split below follows the order of the seed list in the `simlish` README and catalogue v1, where the first 15 entries form one set. Treat which set belongs to which post as provisional until someone checks the posts.

## Source A (15, provisional)

| Reference | Original URL | Verification |
| --- | --- | --- |
| [Taste Skill](docs/repositories/taste-skill.md) | https://github.com/Leonxlnx/taste-skill | verified |
| [Impeccable](docs/repositories/impeccable.md) | https://github.com/pbakaus/impeccable | verified |
| [Hallmark](docs/repositories/hallmark.md) | https://github.com/Nutlope/hallmark | verified |
| [Anthropic Frontend Design](docs/repositories/anthropic-frontend.md) | https://github.com/anthropics/skills/tree/main/skills/frontend-design | verified |
| [UI/UX Pro Max](docs/repositories/ui-ux-pro-max.md) | https://github.com/nextlevelbuilder/ui-ux-pro-max-skill | verified |
| [Stitch Skills](docs/repositories/stitch-skills.md) | https://github.com/google-labs-code/stitch-skills | verified |
| [Open Design](docs/repositories/open-design.md) | https://github.com/nexu-io/open-design | verified |
| [Penpot](docs/repositories/penpot.md) | https://github.com/penpot/penpot | verified |
| [Figma Context MCP](docs/repositories/figma-context.md) | https://github.com/GLips/Figma-Context-MCP | verified |
| [Astryx](docs/repositories/astryx.md) | https://github.com/meta/astryx | verified |
| [Magic MCP](docs/repositories/magic-mcp.md) | https://github.com/21st-dev/magic-mcp | verified |
| [Magic UI](docs/repositories/magic-ui.md) | https://github.com/magicuidesign/magicui | verified |
| [Three.js](docs/repositories/three-js.md) | https://github.com/mrdoob/three.js | verified |
| [Blender MCP](docs/repositories/blender-mcp.md) | https://github.com/ahujasid/mcp-for-blender | verified |
| [HyperFrames](docs/repositories/hyperframes.md) | https://github.com/heygen-com/hyperframes | verified |

## Source B (15, provisional)

| Reference | Original URL | Verification |
| --- | --- | --- |
| [Impeccable](docs/repositories/impeccable.md) | https://github.com/pbakaus/impeccable | verified |
| [Hallmark](docs/repositories/hallmark.md) | https://github.com/Nutlope/hallmark | verified |
| [Meng To Skills](docs/repositories/mengto-skills.md) | https://github.com/MengTo/Skills | verified |
| [Rough.js](docs/repositories/rough-js.md) | https://github.com/rough-stuff/rough | verified |
| [Sakuga VFX](docs/repositories/sakuga-vfx.md) | https://github.com/finktheartist/sakuga-vfx | verified |
| [Line Art Animation](docs/repositories/line-art-animation.md) | https://github.com/JDhruv14/line-art-animation | verified |
| [Motion Canvas](docs/repositories/motion-canvas.md) | https://github.com/motion-canvas/motion-canvas | verified |
| [Three.js](docs/repositories/three-js.md) | https://github.com/mrdoob/three.js | verified |
| [Blender MCP](docs/repositories/blender-mcp.md) | https://github.com/ahujasid/mcp-for-blender | verified |
| [HyperFrames](docs/repositories/hyperframes.md) | https://github.com/heygen-com/hyperframes | verified |
| [Remotion](docs/repositories/remotion.md) | https://github.com/remotion-dev/remotion | verified |
| [Scarlet](docs/repositories/scarlet.md) | https://github.com/Forward-Future/scarlet | verified |
| [Video Use](docs/repositories/video-use.md) | https://github.com/browser-use/video-use | verified |
| [Real-ESRGAN](docs/repositories/real-esrgan.md) | https://github.com/xinntao/Real-ESRGAN | verified |
| [FFmpeg](docs/repositories/ffmpeg.md) | https://github.com/FFmpeg/FFmpeg | verified |

## Source C (7, confirmed)

None of these duplicates a URL from sources A or B.

| Reference | Original URL | Verification |
| --- | --- | --- |
| [SAM 3D Objects](docs/repositories/sam-3d-objects.md) | https://github.com/facebookresearch/sam-3d-objects | verified |
| [Stable Fast 3D (SF3D)](docs/repositories/stable-fast-3d.md) | https://github.com/Stability-AI/stable-fast-3d | verified |
| [MeshAnything V2](docs/repositories/meshanything-v2.md) | https://github.com/buaacyw/MeshAnythingV2 | verified |
| [UniRig](docs/repositories/unirig.md) | https://github.com/VAST-AI-Research/UniRig | verified |
| [Dream Textures](docs/repositories/dream-textures.md) | https://github.com/carson-katri/dream-textures | verified |
| [ComfyUI-3D-Pack (Comfy3D)](docs/repositories/comfyui-3d-pack.md) | https://github.com/MrForExample/ComfyUI-3D-Pack | verified |
| [Gaussian Splatting](docs/repositories/gaussian-splatting.md) | https://github.com/graphdeco-inria/gaussian-splatting | verified |

## Supplementary candidates (12, not from any post)

Identified during related research. Kept as a separate collection: they are evaluated on their merits and never presented as part of the posts.

| Reference | Original URL | Verification |
| --- | --- | --- |
| [Graphify](docs/repositories/graphify.md) | https://github.com/Graphify-Labs/graphify | verified |
| [Spec Kit](docs/repositories/spec-kit.md) | https://github.com/github/spec-kit | verified |
| [Claude Mem](docs/repositories/claude-mem.md) | https://github.com/thedotmack/claude-mem | verified |
| [Awesome DESIGN.md](docs/repositories/awesome-design-md.md) | https://github.com/VoltAgent/awesome-design-md | verified |
| [Designlang (design-extract)](docs/repositories/designlang.md) | https://github.com/Manavarya09/designlang | redirected |
| [Anatomy](docs/repositories/anatomy.md) | https://github.com/wheresryan22/anatomy | verified |
| [Video Shotcraft](docs/repositories/video-shotcraft.md) | https://github.com/Vincentwei1021/video-shotcraft | verified |
| [Dream Loop](docs/repositories/dream-loop.md) | https://github.com/achimala/dream-loop | verified |
| [Blender Skills](docs/repositories/blender-skills.md) | https://github.com/EL4CTEO/blender-skills | verified |
| [TRELLIS.2](docs/repositories/trellis-2.md) | https://github.com/microsoft/TRELLIS.2 | verified |
| [React Bits](docs/repositories/react-bits.md) | https://github.com/DavidHDev/react-bits | verified |
| [Awesome Claude Skills](docs/repositories/awesome-claude-skills.md) | https://github.com/ComposioHQ/awesome-claude-skills | verified |

## Verification method

On 2026-11-26, for every reference:

1. Resolved the original URL through the GitHub API, recording the canonical owner and repository and the default branch.
2. Recorded the head commit of the default branch as the inspected commit. Every documentation link in a guide is pinned to that commit.
3. Read the README, license and the manifests, requirements or setup files needed for runtime and hardware facts, at that commit. Hugging Face API metadata was used for model sizes, gating and model licenses.
4. Recorded archive state and last push as maintenance signals.
5. Ran a smoke test where it needed no gated or multi-gigabyte download. See [smoke tests](docs/examples/smoke-tests.md).

`python scripts/check-repositories.py` repeats steps 1 and 4 and reports drift.

## Corrections

| Original URL | Finding | Recorded as | Evidence |
| --- | --- | --- | --- |
| https://github.com/Manavarya09/designlang | 404 on 2026-11-26. The owner account exists. | https://github.com/Manavarya09/design-extract (status `redirected`) | The npm package `designlang` 13.4.1 lists `git+https://github.com/Manavarya09/design-extract.git` as its repository. No other project was substituted. |
| https://github.com/ahujasid/mcp-for-blender | Resolves. Catalogue v1 noted the Python package is now published as `mcp-for-blender`. | Unchanged | Pinned README |
| https://github.com/21st-dev/magic-mcp | Resolves. Upstream points new setups to the 21st MCP. | Unchanged | Pinned README |

All other URLs resolved to themselves. 43 references are `verified` and 1 is `redirected`; none is unavailable.
