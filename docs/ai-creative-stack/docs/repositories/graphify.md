# Graphify

Use for turning a codebase, plus its docs, PDFs, images and media, into a local knowledge graph that coding agents query instead of grepping files.

> Supplementary research candidates · Supplementary · smoke test: **not run**

## Evidence and maintenance

- [Canonical reference](https://github.com/Graphify-Labs/graphify)
- Verified 2026-11-26 against default branch `v8` at [`02c27dc246cd`](https://github.com/Graphify-Labs/graphify/commit/02c27dc246cd7bc359d0f4acaf53a3fce595bc1e).
- GitHub reports archive state **false** and a repository push at `2026-11-25T13:52:46Z`. Push activity is a maintenance signal, not a quality rating.
- Attribution: Not attributable to any source post. Identified during related research.

- [README.md](https://github.com/Graphify-Labs/graphify/blob/02c27dc246cd7bc359d0f4acaf53a3fce595bc1e/README.md)

## Runtime, hardware and setup

- **Type** CLI. Primary language Python.
- **Platforms** Linux, Windows, macOS.
- **Runtime** Python 3.11.5-3.14 with uv (recommended) or pipx. Optional extras add PDF, Office, video/audio (faster-whisper + yt-dlp), MCP server, Leiden clustering, Ollama/OpenAI/Gemini/Anthropic/Bedrock backends, SQL/Postgres, Neo4j/FalkorDB push.
- **Execution** local or hosted.
- **Agent paths** Claude Code, Cursor, Codex, Gemini CLI, GitHub Copilot CLI, VS Code Copilot Chat, OpenCode, Kilo Code, Aider, OpenClaw, Factory Droid, Trae, Hermes, Kimi Code, Amp, Kiro, Pi, Devin CLI, Google Antigravity, CodeBuddy, Any MCP client (graphify-mcp or hosted Graphify Cloud MCP). Client claims describe documentation and remain untested here unless the smoke test says otherwise.
- **Configuration** `graphify install` (or `graphify <platform> install`, `--project`, `--strict`) registers the skill and hooks or instruction files for the chosen assistant. A `.graphifyrc` in the scan root sets per-project options (language for ambiguous extensions, query_budget, query_depth, viz_node_limit); backends and logging are set with environment variables such as GRAPHIFY_BACKEND.
- **Credentials and services** None for code-only graphs. The semantic pass over docs, PDFs and images uses the assistant's own model inside /graphify; headless `graphify extract` needs one of GEMINI_API_KEY/GOOGLE_API_KEY, MOONSHOT_API_KEY, ANTHROPIC_API_KEY, OPENAI_API_KEY, DEEPSEEK_API_KEY, Azure OpenAI key+endpoint, AWS IAM (Bedrock), a local Ollama, or the `claude` CLI. The hosted Graphify Cloud MCP needs a Graphify account.

Review the source and pin the version before running the upstream-documented command. It was read in the pinned documentation; execution is recorded only under Smoke test.

```sh
uv tool install graphifyy
graphify install
# alternatives: pipx install graphifyy | pip install graphifyy
```

## Contracts and selection

| Boundary | Contract |
| --- | --- |
| Input | Source code in about 40 languages (tree-sitter AST), Markdown docs, PDF (pdf extra), .docx/.xlsx (office extra), Images, Video/audio (video extra), SQL schemas and live PostgreSQL via --postgres DSN, URLs added with `graphify add` (papers, YouTube) |
| Output | graphify-out/graph.html (interactive graph), graphify-out/GRAPH_REPORT.md, graphify-out/graph.json, Markdown wiki (--wiki), Mermaid call-flow HTML (export callflow-html), SVG export (svg extra), Neo4j/FalkorDB push, MCP stdio server over graph.json (graphify-mcp) |
| Primary | Project intelligence |
| Supporting | — |

Skip when a small repo is easier to grep, or when docs must not reach any cloud model and you cannot use Ollama or --code-only. Consider [claude-mem](claude-mem.md). Complementary tools include [spec-kit](spec-kit.md).

No native integration with catalogue peers is asserted. Examples using another tool are proposed handoffs.

- Its Claude Code hooks fire before Read/Grep/Glob and Bash readers; with --strict they deny Read/Grep once per session until a graph query. This can clash with other PreToolUse Read hooks, such as claude-mem's file-read gate.
- Without the `leiden` extra, clustering silently falls back to networkx Louvain; switching later reshuffles every community and needs a full relabel.

## Craft notes

- Best at structural code questions: tree-sitter resolves calls/imports/inherits across about 40 languages and every edge is tagged EXTRACTED or INFERRED, so `graphify path` reports a path's confidence as that of its weakest hop.
- graph.html renders up to 5,000 nodes before switching to an aggregated community view; community labeling sends 100 communities per call, sized for about a 16k-token context.
- Ambiguous extensions (.inc, .h, .m) can parse as the wrong language and yield a sparse but plausible-looking graph unless declared in .graphifyrc.

## Examples

1. **Independent** Run `/graphify .` in a repo, then `graphify path "UserService" "DatabasePool"` to trace how two components connect.
2. **Combined** Proposed handoff: build a graphify graph of an existing repo, then give GRAPH_REPORT.md to spec-kit's /speckit-plan so the plan names real components and dependencies.

For both, save the inputs and output evidence with the selected version. Use a small authorized fixture first and review the actual render or inspection result before expanding scope.

## Smoke test

**not run**. No run is recorded.

## Security, privacy and licensing

- The official PyPI package is `graphifyy` (double y); the README warns other graphify* packages are not affiliated (typosquat risk).
- Install writes hooks or always-on instruction files (AGENTS.md, .cursor/rules, CODEBUDDY.md) into assistant config; `graphify uninstall` removes them.
- `graphify add <url>` fetches remote papers and videos (yt-dlp) into the graph.
- The Pi guard hook fails open and needs graphify on an absolute PATH entry outside the project.
- Code is parsed locally; README: nothing leaves the machine for code, and `graphify extract` runs offline for code-only corpora.
- Docs, PDFs and images go to the assistant's model or to the configured API provider; auto-detection order is Gemini, Kimi, Claude, OpenAI, DeepSeek, Azure, Bedrock, Ollama. Kimi routes to Moonshot AI servers in China. GRAPHIFY_BACKEND=none or ollama keeps everything local.
- No telemetry or analytics per README.
- Every query/path/explain call (including the question text) is logged to ~/.cache/graphify-queries.log by default; set GRAPHIFY_QUERY_LOG_DISABLE=1 to opt out.
- Connecting to the hosted MCP at api.graphify.com means the graph is served from Graphify Cloud, not your machine.

**Software license** Apache-2.0.

**Commercial use** Apache-2.0 allows commercial use, modification and redistribution with notice and patent terms. The 'graphify' name and logo are marks of Graphify Labs; community projects using the name must say they are not affiliated. Graphify Cloud is a separate hosted commercial service.

## Evidence quotes

| Field | Upstream wording and file |
| --- | --- |
| hardware | "Code is parsed with tree-sitter AST: deterministic, no LLM, nothing leaves your machine." (README.md) |
| installation | "uv tool install graphifyy      # install the CLI" then "graphify install" (README.md) |
| license | Badge "License: Apache-2.0" and LICENSE link (README.md) |
| model_license | No weights; semantic pass uses "your assistant's model, or a configured API key" (README.md) |
| inputs | "maps your entire project (code, docs, PDFs, images, videos) into a knowledge graph" (README.md) |
| outputs | "You get three files": graph.html, GRAPH_REPORT.md, graph.json (README.md) |
| privacy | "No telemetry, no usage tracking, no analytics." and query log at ~/.cache/graphify-queries.log (README.md) |
| runtime_requirements | "Needs Python 3.11.5–3.14 and uv (or pipx)" (README.md) |
