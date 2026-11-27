# Claude Mem

Use for giving a coding agent persistent memory: hooks record each session's tool activity, an observer model compresses it into observations, and later sessions start with a compact index of them.

> #60 · Supplementary research candidates · Supplementary · smoke test: **not run**

## Evidence and maintenance

- [Canonical reference](https://github.com/thedotmack/claude-mem)
- Verified 2026-11-26 against default branch `main` at [`9b3b78dfa53f`](https://github.com/thedotmack/claude-mem/commit/9b3b78dfa53f80e7c9c447b9269ceda255ee99d9).
- GitHub reports archive state **false** and a repository push at `2026-11-26T07:17:56Z`. Push activity is a maintenance signal, not a quality rating.
- Attribution: Not attributable to any source post. Identified during related research.

- [README.md](https://github.com/thedotmack/claude-mem/blob/9b3b78dfa53f80e7c9c447b9269ceda255ee99d9/README.md)
- [telemetry.mdx](https://github.com/thedotmack/claude-mem/blob/9b3b78dfa53f80e7c9c447b9269ceda255ee99d9/docs/public/telemetry.mdx)
- [configuration.mdx](https://github.com/thedotmack/claude-mem/blob/9b3b78dfa53f80e7c9c447b9269ceda255ee99d9/docs/public/configuration.mdx)
- [license.md](https://github.com/thedotmack/claude-mem/blob/9b3b78dfa53f80e7c9c447b9269ceda255ee99d9/docs/license.md)
- [ip-boundary.md](https://github.com/thedotmack/claude-mem/blob/9b3b78dfa53f80e7c9c447b9269ceda255ee99d9/docs/ip-boundary.md)

## Runtime, hardware and setup

- **Type** plugin. Primary language TypeScript.
- **Platforms** Linux, Windows, macOS.
- **Runtime** Node.js ^20.19 or >=22.12; Bun (auto-installed) runs the worker; uv (auto-installed) launches chroma-mcp for vector search (Python 3.13 by default); SQLite 3 bundled.
- **Execution** local or hosted.
- **Agent paths** Claude Code, Codex, Cursor, OpenCode, T3 Code, Antigravity CLI, Oh My Pi, Pi, DeepSeek Harness, Grok Bot, OpenClaw, Gemini, Hermes, Claude Desktop (search only), Copilot CLI, Goose, Roo Code, Warp, Zed (search only, sessions not recorded). Client claims describe documentation and remain untested here unless the smoke test says otherwise.
- **Configuration** Settings live in ~/.claude-mem/settings.json (observer provider: claude by default, codex, gemini, openrouter or openai-compatible; worker host/port; data dir; CLAUDE_MEM_MODE such as code, code--chill or code--<lang>; what gets injected). Telemetry, redaction, retention and cloud sync are separate switches.
- **Credentials and services** An observer model is required: by default your Anthropic plan through the Claude login; alternatively an OpenRouter or Gemini key, or the hosted claude-mem observer (cmem.ai sign-in by email magic link; its 30-day trial asks for a payment method). Skip the sign-in with an explicit --provider, CLAUDE_MEM_ONLINE_OPTIN=false, or a non-interactive shell.

Review the source and pin the version before running the upstream-documented command. It was read in the pinned documentation; execution is recorded only under Smoke test.

```sh
npx claude-mem install
# or inside Claude Code:
/plugin marketplace add thedotmack/claude-mem
/plugin install claude-mem
```

## Contracts and selection

| Boundary | Contract |
| --- | --- |
| Input | Agent hook events: prompts, tool calls with inputs and outputs, files read and edited, commands run, Tool screenshots (kept by default), Codex subagent rollout files (opt-in), Grok Bot chat log files, Manual notes via save_memory |
| Output | Observations and session summaries in SQLite (~/.claude-mem/claude-mem.db), Compact context index injected at SessionStart, MCP tools: search, timeline, get_observations (plus smart_search, smart_outline, smart_unfold, save_memory), Web viewer at /viewer and My Work page on the worker port, Copies of turn deliverables in ~/.claude-mem/deliverables/<project>/ |
| Primary | Project intelligence |
| Supporting | — |

Skip if prompts, tool inputs/outputs and file contents must not be sent to an observer model or stored on disk indefinitely. Consider [graphify](graphify.md). Complementary tools include [spec-kit](spec-kit.md).

No native integration with catalogue peers is asserted. Examples using another tool are proposed handoffs.

- Its PreToolUse hook on Read adds file timelines and can block whole-file Reads (File Read Gate); this may collide with graphify's strict Read gating or other Read hooks.
- Memory injection only starts on the second session in a project; /learn-codebase (about 5 minutes) front-loads a repo instead.

## Craft notes

- Progressive disclosure: search returns index rows of about 50-100 tokens each versus 500-1,000 for a full observation; the README says this ratio is not a measured end-to-end saving.
- Mode `code--chill` records fewer observations; `code--<lang>` writes observations in one of 29 built-in languages.
- Copilot CLI, Goose, Roo Code, Warp and Zed can only search memory; their sessions are not recorded.

## Examples

1. **Independent** Install with `npx claude-mem install`, work one session, then in the next session ask the agent to search memory for an earlier bug fix via search, timeline and get_observations.
2. **Combined** Proposed handoff: pair with spec-kit so decisions recorded as observations are recalled when /speckit-plan runs in a later session.

For both, save the inputs and output evidence with the selected version. Use a small authorized fixture first and review the actual render or inspection result before expanding scope.

## Smoke test

**not run**. No run is recorded.

## Security, privacy and licensing

- Installs hooks on SessionStart, UserPromptSubmit, PreToolUse, PostToolUse, PostToolUseFailure, Stop, SubagentStop and SessionEnd, plus a launcher on PATH (Windows: %LOCALAPPDATA%\claude-mem\bin).
- The worker HTTP API listens on 127.0.0.1, default port 37700 + (uid % 100) (docs examples use 37777), and trusts any local process; on multi-user hosts set CLAUDE_MEM_LOCAL_API_TOKEN.
- A remote worker over plain HTTP sends the token in clear; docs recommend HTTPS via CLAUDE_MEM_WORKER_URL.
- Secret auto-redaction is opt-in (CLAUDE_MEM_REDACT_ENABLED defaults to false); only <private> tags reliably keep content out.
- The OpenClaw installer pipes a remote script to bash (curl -fsSL https://install.cmem.ai/openclaw.sh | bash).
- The README addresses AI agents directly with install instructions; treat that as vendor text, not user consent.
- Captured tool activity is sent to the observer model provider (Anthropic by default; Gemini, OpenRouter or cmem.ai if chosen).
- Memory is stored locally in ~/.claude-mem; Cloud Sync to cmem.ai is opt-in and then also uploads converted screenshots.
- Anonymous PostHog usage analytics are ON by default (random install UUID, whitelisted fields including OS, versions, provider, observed model id, billing tier, token counts and database row counts). Disable with `npx claude-mem telemetry disable` or DO_NOT_TRACK.
- Retention: observations are kept indefinitely; raw tool_uses are kept forever unless CLAUDE_MEM_TOOL_USES_RETENTION_DAYS is set; daily worker logs are kept 30 days (CLAUDE_MEM_LOG_RETENTION_DAYS).
- Screenshots are kept by default under ~/.claude-mem/media-v1/, and deliverables are copied to ~/.claude-mem/deliverables/ by default.
- Observer SDK transcripts persist under ~/.claude/projects/ unless CLAUDE_MEM_OBSERVER_CLAUDE_CONFIG_DIR is set.

**Software license** Apache-2.0 (open core).

**Commercial use** Apache-2.0 allows commercial use, modification and embedding of the open-source core (engine, server, CLI, SDKs, adapters, MCP tools). docs/ip-boundary.md reserves hosted cloud, team/org sync, admin dashboard, SSO, enterprise RBAC and similar areas outside the license. The README also promotes a third-party crypto token (CMEM); that is unrelated to the software license.

## Evidence quotes

| Field | Upstream wording and file |
| --- | --- |
| hardware | "Bun: JavaScript runtime and process manager (auto-installed if missing)" (README.md System Requirements) |
| installation | "npx claude-mem install" (README.md Quick Start) |
| license | "Claude-Mem is licensed under the Apache License 2.0." (README.md, docs/license.md) |
| model_license | Not applicable; observer uses "the claude-mem observer, your own OpenRouter or Gemini key, or your Anthropic plan" (README.md) |
| inputs | "Hooks in your agent hand each tool call (what it reads, edits and runs) to a small local worker." (README.md) |
| outputs | "SQLite at ~/.claude-mem/claude-mem.db holds sessions, observations and summaries." (README.md) |
| telemetry | "It is on by default (opt-out)." (docs/public/telemetry.mdx) |
| port | CLAUDE_MEM_WORKER_PORT default "37700 + (uid % 100)" (docs/public/configuration.mdx) |
| retention | CLAUDE_MEM_TOOL_USES_RETENTION_DAYS default "0 (keep forever)" (docs/public/configuration.mdx) |
