# Awesome Claude Skills

Use for discovering candidate Claude skills and plugins by category, as a starting point for reviewing each skill before installing it.

> #69 · Supplementary research candidates · Supplementary · smoke test: **not run**

## Evidence and maintenance

- [Canonical reference](https://github.com/ComposioHQ/awesome-claude-skills)
- Verified 2026-11-26 against default branch `master` at [`be2a406907db`](https://github.com/ComposioHQ/awesome-claude-skills/commit/be2a406907dbc61b73e6827ded415c96139d13a2).
- GitHub reports archive state **false** and a repository push at `2026-09-18T07:16:11Z`. Push activity is a maintenance signal, not a quality rating.
- Attribution: Not attributable to any source post. Identified during related research.

- [README.md](https://github.com/ComposioHQ/awesome-claude-skills/blob/be2a406907dbc61b73e6827ded415c96139d13a2/README.md)
- [LICENSE.txt](https://github.com/ComposioHQ/awesome-claude-skills/blob/be2a406907dbc61b73e6827ded415c96139d13a2/document-skills/docx/LICENSE.txt)
- [LICENSE.txt](https://github.com/ComposioHQ/awesome-claude-skills/blob/be2a406907dbc61b73e6827ded415c96139d13a2/canvas-design/LICENSE.txt)

## Runtime, hardware and setup

- **Type** curated list. Primary language Python.
- **Platforms** Unverified.
- **Runtime** Unverified; varies per listed or vendored skill.
- **Execution** local or hosted.
- **Agent paths** Claude.ai, Claude Code, Claude API, Codex, Cursor, Gemini CLI, Antigravity. Client claims describe documentation and remain untested here unless the smoke test says otherwise.
- **Configuration** Per skill. The connect-apps plugin runs `/connect-apps:setup` and asks for a Composio API key.
- **Credentials and services** None to browse. Composio-based skills (connect-apps and the composio-skills folders) need a Composio API key and route actions through Composio's hosted service; other skills may need their own keys (for example imagen uses the Google Gemini API).

| Hardware | Documented value |
| --- | --- |
| GPU | unverified |
| Minimum VRAM | Not documented |
| Recommended VRAM | Not documented |
| System RAM | Not documented |
| Storage | Not documented |
| CPU fallback | not documented |
| Training versus inference | Not documented |
| Notes | Depends on each skill; the list itself needs nothing. |

Review the source and pin the version before running the upstream-documented command. It was read in the pinned documentation; execution is recorded only under Smoke test.

```sh
mkdir -p ~/.config/claude-code/skills/
cp -r skill-name ~/.config/claude-code/skills/
# connect-apps plugin:
claude --plugin-dir ./connect-apps-plugin
```

## Contracts and selection

| Boundary | Contract |
| --- | --- |
| Input | Varies per skill |
| Output | Varies per skill |
| Primary | Discovery |
| Supporting | — |

Skip if you need vetted, license-clear skills; this is an unaudited discovery list and each linked or vendored skill must be reviewed on its own. Consider the existing project toolchain.

No native integration with catalogue peers is asserted. Examples using another tool are proposed handoffs.

- The README's Claude Code path ~/.config/claude-code/skills/ differs from ~/.claude/skills/ used by other catalogue entries (for example anatomy); confirm the path for your Claude Code version.
- The list is maintained by Composio and steers users to its MCP gateway; expect promotional placement.

## Craft notes

- More than a link list: the pinned tree vendors about 864 SKILL.md files, 832 of them Composio app-automation skills for Rube MCP, plus copies of Anthropic example skills and links to external repositories.
- The README describes the Composio section as skills for 78 SaaS apps, while the tree holds 832 composio-skills folders, so counts in the text and the repo differ.
- Useful for breadth across document processing, dev tools, data, marketing, writing, creative media and security; quality and maintenance vary per entry.

## Examples

1. **Independent** Browse the Creative & Media section to shortlist candidate skills, then read each SKILL.md and its license before installing one.
2. **Combined** Proposed handoff: shortlist a design skill from the list and test it beside an awesome-design-md reference file on the same page brief before adopting it.

For both, save the inputs and output evidence with the selected version. Use a small authorized fixture first and review the actual render or inspection result before expanding scope.

## Smoke test

**not run**. No run is recorded.

## Security, privacy and licensing

- Vendored and linked skills include scripts that run on your machine; review SKILL.md and scripts before installing any of them.
- connect-apps gives Claude real actions across 1000+ apps (send email, create issues, post to Slack), a large blast radius if a skill or prompt misbehaves.
- Some listed skills download media from third-party platforms (Video Downloader) or drive your logged-in Chrome session (Chrome Relay); weigh platform terms and session exposure.
- Composio-routed skills send app data and actions through Composio's hosted service.
- Third-party skills may call external APIs; check each one's data flow before use.

**Software license** No LICENSE file at the repository root (GitHub reports no license); the README states Apache-2.0; vendored skill folders carry their own LICENSE.txt files..

**Commercial use** With no license file, default copyright applies to the repository: beyond GitHub's terms (viewing and forking on GitHub), no reuse right is clearly granted. The README's 'licensed under the Apache License 2.0' line is the owner's only stated grant and is weaker evidence than a LICENSE file, so copying or redistributing the list text or Composio-authored skills is Not established until confirmed. The README itself says individual skills may have different licenses: vendored Anthropic document skills (docx, pdf, pptx, xlsx) read '© 2025 Anthropic, PBC. All rights reserved' and fall under Anthropic's terms, while others such as canvas-design carry Apache-2.0. Every externally linked skill has its own license that must be checked.

## Evidence quotes

| Field | Upstream wording and file |
| --- | --- |
| hardware | No requirements section; skills vary (README.md) |
| installation | "mkdir -p ~/.config/claude-code/skills/" then "cp -r skill-name ~/.config/claude-code/skills/" (README.md) |
| license | "This repository is licensed under the Apache License 2.0." but no root LICENSE in tree (README.md; git tree) |
| model_license | Not applicable; no model (README.md) |
| inputs | "Individual skills may have different licenses - please check each skill's folder" (README.md) |
| outputs | Varies; e.g. "Creates beautiful visual art in PNG and PDF documents" for Canvas Design (README.md) |
| vendored_anthropic_licence | "© 2025 Anthropic, PBC. All rights reserved." (document-skills/docx/LICENSE.txt) |
