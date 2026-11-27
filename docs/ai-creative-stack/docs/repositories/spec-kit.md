# Spec Kit

Use for running spec-driven development with a coding agent: write a constitution and spec, then turn it into a plan, tasks and code, with optional bug-fix and idea-assessment processes.

> #59 · Supplementary research candidates · Supplementary · smoke test: **passed**

## Evidence and maintenance

- [Canonical reference](https://github.com/github/spec-kit)
- Verified 2026-11-26 against default branch `main` at [`f2010547121b`](https://github.com/github/spec-kit/commit/f2010547121b3351e4923fe467205079e4593a32).
- GitHub reports archive state **false** and a repository push at `2026-11-25T19:16:59Z`. Push activity is a maintenance signal, not a quality rating.
- Attribution: Not attributable to any source post. Identified during related research.

- [README.md](https://github.com/github/spec-kit/blob/f2010547121b3351e4923fe467205079e4593a32/README.md)
- [index.md](https://github.com/github/spec-kit/blob/f2010547121b3351e4923fe467205079e4593a32/docs/integrations/index.md)
- [agentic-sdd.md](https://github.com/github/spec-kit/blob/f2010547121b3351e4923fe467205079e4593a32/docs/reference/agentic-sdd.md)
- [pyproject.toml](https://github.com/github/spec-kit/blob/f2010547121b3351e4923fe467205079e4593a32/pyproject.toml)

## Runtime, hardware and setup

- **Type** framework. Primary language Python.
- **Platforms** Linux, Windows, macOS.
- **Runtime** Python 3.11+ and uv (Specify CLI, pyproject requires-python >=3.11), plus a supported AI coding agent; CLI-based integrations need that agent's CLI installed.
- **Execution** local.
- **Agent paths** Alquimia AI, Amp, Antigravity, Auggie CLI, Claude Code, Cline, CodeBuddy CLI, Codex CLI, Command Code, Cursor, DeepSeek Harness, Devin for Terminal, Docker Agent, Factory Droid, Firebender, Forge, Gemini CLI, GitHub Copilot, Goose, Grok Build, Hermes, IBM Bob, Junie, Kilo Code, Kimi Code, Kiro CLI, Lingma, MiniMax Code, Mistral Vibe, Muse Code, Oh My Pi, opencode, Pi Coding Agent, Qoder CLI, Qwen Code, RovoDev, SHAI (OVHcloud), Tabnine CLI, Trae, ZCode, Zed, Generic coding agent via project files. Client claims describe documentation and remain untested here unless the smoke test says otherwise.
- **Configuration** `specify init <project> --integration <key>` scaffolds templates and agent commands/skills; `specify integration install|use|switch|uninstall <key>` manages agents. Customize with presets, extensions (`specify extension add bug`, `specify extension add assess`), workflows, bundles and project-local overrides; `--integration none` gives agent-neutral scaffolding for mixed teams.
- **Credentials and services** None for Spec Kit itself; the chosen coding agent needs its own account. Private catalogs and component downloads can require authentication.

Review the source and pin the version before running the upstream-documented command. It was read in the pinned documentation; execution is recorded only under Smoke test.

```sh
uv tool install specify-cli
specify init my-project --integration copilot
cd my-project
```

## Contracts and selection

| Boundary | Contract |
| --- | --- |
| Input | Natural-language project principles and feature descriptions, Tech-stack and architecture choices for /speckit.plan, Bug symptom descriptions (bug extension), Idea statements (assess extension), Existing codebases |
| Output | Constitution and spec.md, Plan and design artifacts, Task list, checklists/requirements.md and custom checklists, Implemented code and convergence reports, .specify/bugs/<slug>/ reports with verdict verified/partial/failed, .specify/assessments/<slug>/ artifacts and decision.md (go/needs-clarification/kill), Generated agent commands or SKILL.md files |
| Primary | Specification |
| Supporting | Project intelligence |

Skip when a change is small enough that a constitution, spec, plan and task list would cost more than the change itself. Consider the existing project toolchain. Complementary tools include [graphify](graphify.md), [claude-mem](claude-mem.md).

No native integration with catalogue peers is asserted. Examples using another tool are proposed handoffs.

- Docs say not to hand-edit generated agent commands or skills; customizations belong in presets or project-local overrides, or they are lost on regeneration.
- In mixed-agent teams, switch back to `--integration none` before committing, or agent-specific files enter the repository.

## Craft notes

- Core order: /speckit.constitution, specify, clarify, plan, checklist, tasks, analyze, implement, converge; only specify is strictly required before plan, and implement/converge repeat until convergence reports Converged.
- /speckit.clarify asks up to five targeted questions and writes the answers back into spec.md; /speckit.analyze checks artifact consistency after tasks and before implementation.
- Invocation differs by agent: /speckit-* (Copilot skills mode), $speckit-* (Codex, ZCode), /skill:speckit-* (Kimi); the docs use /speckit.* notation.

## Examples

1. **Independent** Run /speckit-specify for a photo organizer, then /speckit-plan, /speckit-tasks and /speckit-implement until /speckit-converge reports Converged.
2. **Combined** Proposed handoff: build a graphify graph of the existing repo before /speckit-plan so the plan step can query real dependencies instead of grepping.

For both, save the inputs and output evidence with the selected version. Use a small authorized fixture first and review the actual render or inspection result before expanding scope.

## Smoke test

**passed**. specify-cli 1.4.5 via uvx: `specify init demo --integration claude --script sh --non-interactive --ignore-agent-tools` created .specify/ with constitution, spec, plan, tasks and checklist templates.

## Security, privacy and licensing

- README: catalog listings are not audits or endorsements; review community source before installing or running it.
- External integration adapters execute code; docs say to review adapter code before authorizing it, and the default community catalog is discovery-only.
- Core templates are bundled in the wheel so `specify init` works offline or air-gapped.
- Spec Kit writes local Markdown artifacts; whatever the agent reads is sent to that agent's model provider.
- No telemetry is documented in the files reviewed.

**Software license** MIT.

**Commercial use** MIT allows commercial use, modification and redistribution with the copyright notice. Community extensions, presets and adapters from catalogs carry their own licenses and are not covered.

## Evidence quotes

| Field | Upstream wording and file |
| --- | --- |
| hardware | No hardware section; "You need Python 3.11+, uv, and a supported AI coding agent" (README.md) |
| installation | "uv tool install specify-cli" / "specify init my-project --integration copilot" (README.md) |
| license | "Spec Kit is MIT licensed." (README.md) |
| model_license | Not applicable; no model weights (README.md) |
| inputs | "/speckit-specify Build a photo organizer with albums grouped by date" (README.md) |
| outputs | "turn the specification into a plan, tasks, and working code" (README.md) |
| supported_agents | Integration table lists 41 agent keys plus `none` and `generic` (docs/integrations/index.md) |
| security | "Catalog listings are not audits or endorsements, so review community source code" (README.md) |
