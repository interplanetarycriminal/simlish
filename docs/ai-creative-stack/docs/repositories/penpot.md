# Penpot

Use for explicit design ownership and collaborative prototyping.

> #10 · Design and prototyping · Source A · smoke test: **not run**

## Evidence and maintenance

- [Canonical reference](https://github.com/penpot/penpot)
- Verified 2026-11-26 against default branch `develop` at [`e6f3d21dce2a`](https://github.com/penpot/penpot/commit/e6f3d21dce2a094ce14c4576279f4b50219b80e1).
- GitHub reports archive state **false** and a repository push at `2026-11-26T06:19:33Z`. Push activity is a maintenance signal, not a quality rating.
- Attribution: Provisional. Sources A and B were recovered from likely matching mirrored posts; the posts themselves were not readable here. The A/B split follows the order of the seed list (simlish README) and catalogue v1.

- [README.md](https://github.com/penpot/penpot/blob/e6f3d21dce2a094ce14c4576279f4b50219b80e1/README.md)
- [LICENSE](https://github.com/penpot/penpot/blob/e6f3d21dce2a094ce14c4576279f4b50219b80e1/LICENSE)
- [package.json](https://github.com/penpot/penpot/blob/e6f3d21dce2a094ce14c4576279f4b50219b80e1/package.json)

## Runtime, hardware and setup

- **Type** design application. Primary language Clojure.
- **Platforms** Browser, Self-hosted Docker/Kubernetes.
- **Runtime** Browser. Cloud or self-hosted infrastructure documented for Docker and Kubernetes.
- **Execution** local or hosted.
- **Agent paths** Generic coding agent via exported artifacts. Client claims describe documentation and remain untested here unless the smoke test says otherwise.
- **Configuration** Choose cloud or self-hosted access and configure team, project and export permissions.
- **Credentials and services** Cloud account or self-host access, depending on deployment.

| Hardware | Documented value |
| --- | --- |
| GPU | unverified |
| Minimum VRAM | Not documented |
| Recommended VRAM | Not documented |
| System RAM | Not documented |
| Storage | Not documented |
| CPU fallback | not applicable |
| Training versus inference | Not documented |

Review the source and pin the version before running the upstream-documented command. It was read in the pinned documentation; execution is recorded only under Smoke test.

```sh
Use a hosted Penpot account or follow the linked self-hosting guide for the selected Docker or Kubernetes deployment.
```

## Contracts and selection

| Boundary | Contract |
| --- | --- |
| Input | Wireframes, vectors, typography and design tokens |
| Output | Prototypes, SVG assets and design specs |
| Primary | Prototyping |
| Supporting | Creative direction |

Skip operating a server if the brief only needs one local sketch. Consider [stitch-skills](stitch-skills.md), [open-design](open-design.md), [figma-context](figma-context.md). Complementary tools include [astryx](astryx.md), [ui-ux-pro-max](ui-ux-pro-max.md).

No native integration with catalogue peers is asserted. Examples using another tool are proposed handoffs.

## Craft notes

- An open-source, self-hostable design platform that stores design as SVG, CSS and HTML, with native design tokens, an MCP server and a plugin API.
- A local source of truth for tokens and layouts that agents can read and write.

## Examples

1. **Independent** Prototype error, loading and empty states for a settings panel.
2. **Combined** Export an SVG icon and map Penpot token values to application variables.

For both, save the inputs and output evidence with the selected version. Use a small authorized fixture first and review the actual render or inspection result before expanding scope.

## Smoke test

**not run**. No run is recorded.

## Security, privacy and licensing

- Self-hosting needs access controls, protected storage and backups. Audit connector access separately.
- Design files live on the chosen Penpot instance: self-hosted keeps them local.

**Software license** MPL-2.0.

**Commercial use** Review MPL file-level source and notice obligations for distributed modifications.
