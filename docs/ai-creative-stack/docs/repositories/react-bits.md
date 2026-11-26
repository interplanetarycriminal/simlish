# React Bits

Use for adding animated React components, text effects and shader backgrounds to an app or website by copying their source in via the shadcn or jsrepo CLI.

> Supplementary research candidates · Supplementary · smoke test: **not run**

## Evidence and maintenance

- [Canonical reference](https://github.com/DavidHDev/react-bits)
- Verified 2026-11-26 against default branch `main` at [`37f53df7efb6`](https://github.com/DavidHDev/react-bits/commit/37f53df7efb61238b0fea9ea8be74e3cce62b959).
- GitHub reports archive state **false** and a repository push at `2026-11-24T10:47:33Z`. Push activity is a maintenance signal, not a quality rating.
- Attribution: Not attributable to any source post. Identified during related research.

- [README.md](https://github.com/DavidHDev/react-bits/blob/37f53df7efb61238b0fea9ea8be74e3cce62b959/README.md)
- [LICENSE.md](https://github.com/DavidHDev/react-bits/blob/37f53df7efb61238b0fea9ea8be74e3cce62b959/LICENSE.md)

## Runtime, hardware and setup

- **Type** library. Primary language JavaScript.
- **Platforms** Unverified.
- **Runtime** React (Next.js supported); npx with the shadcn CLI or jsrepo to install. Per-component dependencies and versions are not stated in the README.
- **Execution** local or hosted.
- **Agent paths** Claude Code, Cursor, Codex, VS Code, Antigravity. Client claims describe documentation and remain untested here unless the smoke test says otherwise.
- **Configuration** Add the registry `"@react-bits": "https://reactbits.dev/r/{name}.json"` to components.json; for agents run `npx shadcn@latest mcp init --client claude`. The name suffix picks JS or TS and CSS or Tailwind.
- **Credentials and services** None for the free components and tools.

Review the source and pin the version before running the upstream-documented command. It was read in the pinned documentation; execution is recorded only under Smoke test.

```sh
npx shadcn@latest add @react-bits/SplitText-TS-TW
# or: npx jsrepo@latest add https://reactbits.dev/r/SplitText-TS-TW
```

## Contracts and selection

| Boundary | Contract |
| --- | --- |
| Input | Component name plus flavor suffix (JS/TS, CSS/TW), Component props, For the web tools: screenshots, recordings, photos, camera, SVGs |
| Output | React component source files copied into your project, From the hosted tools: code, high-resolution images, MP4/WebM loops, GIFs, SVG/PNG, favicons, WAV/MP3/OGG sounds |
| Primary | Component generation, Animation |
| Supporting | Frontend implementation, Visual effects |

Skip if you are building something to distribute as components themselves (a UI kit, template marketplace item, design-tool clone or port to another framework); the license forbids redistributing the components or tools. Consider [magic-ui](magic-ui.md), [magic-mcp](magic-mcp.md). Complementary tools include [awesome-design-md](awesome-design-md.md), [designlang](designlang.md), [three-js](three-js.md), [anatomy](anatomy.md).

No native integration with catalogue peers is asserted. Examples using another tool are proposed handoffs.

- Official Vue, Svelte and Solid ports exist on separate sites; porting React Bits yourself for redistribution is forbidden.

## Craft notes

- 215+ components: 33 text animations, 38 animations, 48 components, 34 micro-interactions and 63 backgrounds, each in four flavors (JS/TS x CSS/Tailwind) with a live demo and controls.
- Strongest for hero and section backgrounds and text reveals (Liquid Chrome, Light Tunnel, Split Text); performance cost of heavy WebGL backgrounds is not documented.
- Background Studio can export a looping MP4 or WebM of a background, which helps where a live shader is too heavy.

## Examples

1. **Independent** Run `npx shadcn@latest add @react-bits/SplitText-TS-TW` to add an animated headline to a landing page.
2. **Combined** Proposed handoff: take color and type tokens from your own site via designlang, then theme React Bits backgrounds and text effects with them.

For both, save the inputs and output evidence with the selected version. Use a small authorized fixture first and review the actual render or inspection result before expanding scope.

## Smoke test

**not run**. No run is recorded.

## Security, privacy and licensing

- Components arrive as source from the reactbits.dev registry at install time; review the code and any dependencies it pulls in.
- Some components draw on public code examples; Texture Lab and Shape Magic include code adapted from Paper Shaders (Apache-2.0) and Shaders.com (MIT) with third-party notices.
- Installed components run in your app with no documented network calls. The browser tools (Center Stage, Texture Lab) take your screenshots, videos or camera; whether processing stays in the browser is not stated.

**Software license** MIT + Commons Clause License Condition v1.0 (custom wording).

**Commercial use** Allowed: use, copy, modify, merge, publish and distribute the components as part of an application, website or product, including commercial and paid ones, with the copyright and permission notice kept. Forbidden: selling, sublicensing or redistributing the components themselves, whether alone, in a bundle or as a ported version (so no UI kits, component libraries, template packs or framework ports built from them). The same applies to the tools (Background Studio, Texture Lab, Shape Magic, Center Stage, Sound Lab and later tools) and the sound library, and you may not offer the tools or a substantially similar copy as a hosted service. Tool exports may be used in any personal or commercial product but may not be sold or redistributed on their own, such as sound, texture, background or template packs. The grant omits MIT's 'sublicense' and 'sell' rights, so this is not an OSI open-source license.

## Evidence quotes

| Field | Upstream wording and file |
| --- | --- |
| hardware | No hardware section; components are copied into your React project (README.md Installation) |
| installation | "npx shadcn@latest add @react-bits/SplitText-TS-TW" (README.md) |
| license | "you do not sell, sublicense, or redistribute the components themselves-whether alone, in a bundle, or as a ported version" (LICENSE.md) |
| model_license | Not applicable; no model (README.md) |
| inputs | "The suffix picks the flavor: JS or TS, then CSS or TW." (README.md) |
| outputs | "Export the code, a high-resolution image or a looping MP4 or WebM video." (README.md, Background Studio) |
| hosted_service_ban | "or offer the tools or a substantially similar copy of them as a hosted service" (LICENSE.md) |
