# Designlang (design-extract)

Use for reading a live website's design system (tokens, type, spacing, motion, components, voice) into DTCG, Tailwind, shadcn, Figma and DESIGN.md files, and for checking your own UI for drift against a brand.

> #62 · Supplementary research candidates · Supplementary · smoke test: **not run**

## Evidence and maintenance

- [Canonical reference](https://github.com/Manavarya09/design-extract)
- Original reference: https://github.com/Manavarya09/designlang (status: redirected; see security notes for the evidence)
- Verified 2026-11-26 against default branch `main` at [`25fa810ba893`](https://github.com/Manavarya09/design-extract/commit/25fa810ba893142b21b1a9b93122403be19574f6).
- GitHub reports archive state **false** and a repository push at `2026-11-25T07:52:15Z`. Push activity is a maintenance signal, not a quality rating.
- Attribution: Not attributable to any source post. Identified during related research.

- [README.md](https://github.com/Manavarya09/design-extract/blob/25fa810ba893142b21b1a9b93122403be19574f6/README.md)
- [package.json](https://github.com/Manavarya09/design-extract/blob/25fa810ba893142b21b1a9b93122403be19574f6/package.json)
- [SECURITY.md](https://github.com/Manavarya09/design-extract/blob/25fa810ba893142b21b1a9b93122403be19574f6/SECURITY.md)
- [PRIVACY.md](https://github.com/Manavarya09/design-extract/blob/25fa810ba893142b21b1a9b93122403be19574f6/chrome-extension/PRIVACY.md)

## Runtime, hardware and setup

- **Type** CLI. Primary language HTML.
- **Platforms** Unverified.
- **Runtime** Node.js 20 or later (package.json engines >=20); Playwright ^1.61 driving its matching Chromium (`designlang install-browser`, add --with-deps on bare Linux) or an installed Google Chrome.
- **Execution** local or hosted.
- **Agent paths** Claude Code (plugin and MCP), Cursor, Windsurf, Codex, Other agents via the skills CLI (README: 40+). Client claims describe documentation and remain untested here unless the smoke test says otherwise.
- **Configuration** Per-run flags (viewport, --dark, --depth, --responsive, --interactions, --motion-runtime, --full, --platforms, --emit-agent-rules, --cookie/--header for authenticated pages). Optional --smart classification reads ATLASCLOUD_API_KEY/ATLASCLOUD_MODEL, OPENAI_API_KEY or ANTHROPIC_API_KEY.
- **Credentials and services** None for core use (README: no account, no API key). Optional --smart needs an Atlas Cloud, OpenAI or Anthropic key. Extracting protected pages uses your own session cookies.

Review the source and pin the version before running the upstream-documented command. It was read in the pinned documentation; execution is recorded only under Smoke test.

```sh
npm i -g designlang
designlang install-browser
npx skills add Manavarya09/design-extract
# Claude Code plugin:
/plugin marketplace add Manavarya09/design-extract
/plugin install designlang@designlang
# MCP:
claude mcp add designlang -- npx -y designlang mcp
```

## Contracts and selection

| Boundary | Contract |
| --- | --- |
| Input | Public URLs, localhost dev servers, Authenticated pages via cookies, cookie files or headers, Local token files (.json/.css) for lint/drift, DESIGN.md or token files as the brand for verify-ui and slop |
| Output | *-design-language.md (19 sections), *-design-tokens.json (W3C DTCG), *-tailwind.config.js, *-shadcn-theme.css, *-figma-variables.json, *-variables.css, *-anatomy.tsx (typed React stubs), *-motion-tokens.json, *-voice.json, *-prompts/ for v0, Lovable, Cursor, Claude Artifacts, Grade/battle/remix HTML and SVG badges, 13-chapter brand book, Next.js starter (clone), iOS, Android, Flutter, WordPress emitters, Cursor/Claude Code agent rule files, Component screenshots |
| Primary | Design-system extraction |
| Supporting | Design critique, Prototyping, Frontend implementation |

Skip when the target site's terms forbid automated access, or when the result would ship as a near-copy of another brand. Consider [awesome-design-md](awesome-design-md.md). Complementary tools include [figma-context](figma-context.md), [react-bits](react-bits.md), [stitch-skills](stitch-skills.md).

Ships an MCP server for Claude Code, Cursor and Windsurf and emits DTCG tokens and Tailwind config for implementation.

- Closed shadow roots cannot be read (SECURITY.md), so design inside them is missed.
- The default `dna` reference corpus holds only 8 systems, so its percentiles are coarse unless you build your own corpus.

## Craft notes

- Reads computed styles off the live DOM (25+ properties per element) rather than parsing CSS, and with --interactions and --motion-runtime it captures hover/focus deltas and real animations via document.getAnimations().
- `site` elects tokens by page coverage and merges near-identical colors in OKLab; `fidelity` blends a pixel diff and a motion comparison into a 0-100 score with a ranked correction plan.
- `verify-ui` checks a page at 390, 768 and 1280 px plus dark mode and exits 1 on drift, so it can gate CI.

## Examples

1. **Independent** Run `npx designlang verify-ui localhost:3000 --brand DESIGN.md` to check your own app against your brand file at phone, tablet and desktop widths.
2. **Combined** Proposed handoff: extract tokens from your own production site with designlang, then theme react-bits components with the emitted shadcn CSS for new sections.

For both, save the inputs and output evidence with the selected version. Use a small authorized fixture first and review the actual render or inspection result before expanding scope.

## Smoke test

**not run**. No run is recorded.

## Security, privacy and licensing

- Headless Chromium loads and runs arbitrary third-party JavaScript from the target pages.
- --cookie/--cookie-file pass your session cookies into the browser; keep cookie files out of repositories. --insecure ignores TLS errors.
- SECURITY.md lists supported versions 11.x and 10.x while package.json is 13.4.1, so the support table looks out of date.
- The README sponsor block promotes discounted third-party LLM API resellers; treat that as advertising.
- The original URL github.com/Manavarya09/designlang returned 404 on 2026-11-26. The npm package `designlang` 13.4.1 lists github.com/Manavarya09/design-extract as its repository, so that is recorded as canonical.
- Core extraction runs locally; --smart sends classification data to the chosen LLM provider.
- Hosted surfaces (designlang.app/watch, gallery, badge endpoint, hosted extractor) run extraction on the author's servers; a README badge fetches from designlang.app.
- Extraction history is saved by default (--no-history to skip).
- The Chrome extension uses activeTab only and states no analytics or tracking (chrome-extension/PRIVACY.md).

**Software license** MIT.

**Commercial use** The tool's code is MIT and free for commercial use. The README says nothing about rights in what it extracts: colors, fonts and @font-face sources, icons, screenshots, brand voice, component anatomy and Next.js clones come from third-party sites whose trademarks, copyrighted assets, font licenses and terms of service still apply. Commands such as clone, pair, theme-swap and brand make imitating another brand easy. Use on sites you own or have permission to analyze; commercial reuse of another site's identity is Not established.

## Evidence quotes

| Field | Upstream wording and file |
| --- | --- |
| hardware | "Use the system Chrome install instead of the bundled Chromium (skips 150MB download)" (README.md CLI reference) |
| installation | "npm i -g designlang" / "designlang install-browser" (README.md Install) |
| license | "MIT - Manav Arya Singh" (README.md) and "license": "MIT" (package.json) |
| model_license | Not applicable; optional --smart uses external LLM APIs (README.md) |
| inputs | "points a headless browser at any URL and reads the design system off the live DOM" (README.md) |
| outputs | "One command emits 17+ files — DTCG tokens, Tailwind config, shadcn theme, Figma variables" (README.md) |
| runtime_requirements | "Needs Node.js 20 or later. No account, no API key." (README.md) |
| repo_identity | package name "designlang", repository "git+https://github.com/Manavarya09/design-extract.git" (package.json) |
