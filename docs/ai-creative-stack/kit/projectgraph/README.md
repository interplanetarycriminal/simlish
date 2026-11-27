# projectgraph

A local knowledge graph of a project, with a ranked search sized for an agent's context. It is our own code, written from first principles. Python standard library only. No model, no network, no telemetry, no hooks.

Stands in for: [Graphify](../../docs/repositories/graphify.md), in its local, code-only mode. See [persistent project intelligence](../../docs/workflows/persistent-intelligence.md) for where it fits.

## What it builds

Walking the project (skipping `.git`, `node_modules`, `out`, `__pycache__`, virtual environments, binary files, and patterns from `.gitignore`, `.projectgraphignore` and `--ignore`):

| Node kind | Source |
| --- | --- |
| `file` | Every text file. Id `file:<path>`. |
| `heading` | Markdown ATX headings, with GitHub-style anchors (`-1`, `-2` for repeats). Id `<path>#<slug>`. Fenced code is skipped. |
| `symbol` | Python functions, classes and methods (via `ast`). JavaScript exported functions, classes and arrow-function constants (regex over source with comments, strings and regex literals blanked). Id `<path>::<name>`. |
| `json_key` | Top-level keys of a JSON object, or the `id`/`name` of each item in a JSON array of objects (registry-like files). Id `<path>$<key>`. |
| `module` | External imports: `py:json`, `node:fs`, `npm:three`. |
| `asset`, `dir` | Binary files and folders that something links to. |

| Edge type | Confidence | Source |
| --- | --- | --- |
| `contains` | EXTRACTED | File to heading, heading to sub-heading, file to symbol or key. |
| `links_to`, `embeds` | EXTRACTED | Markdown inline links, images and reference definitions. Anchors resolve to the heading node. |
| `imports` | EXTRACTED | Python `import` / `from` (local files resolved first). JS `import`, `export ... from`, `import()`, `require()`. |
| `mentions` | INFERRED | A file names another file's path, a unique file name, or a distinctive symbol (snake_case or camelCase, 5+ characters). Skipped when a link or import already connects them. |

Links that point at a missing file or heading, and relative JS imports that resolve to nothing, go into the graph's `broken` list.

## Usage

```sh
python projectgraph.py build <root> [--out out/graph.json] [--ignore PATTERN ...]
python projectgraph.py query out/graph.json "gaussian splat viewer licence" [--hops 1] [--top 8] [--budget 4000] [--json]
python projectgraph.py stats [out/graph.json]
python projectgraph.py broken [out/graph.json]     # exits 1 when anything is broken
```

`query` ranks every node with BM25 over its label, path and text (names weigh three times the body). Words are split on camelCase and snake_case, lightly stemmed, and a few British spellings map to US ones (license to license). Each hit prints a `path:line` citation, the best-matching line, and its neighbors: syntax edges first, inferred ones marked `(inferred)`. `--budget` caps the text output in characters. `--hops 2` adds neighbors of neighbors.

## What it does not do, compared with Graphify

- No tree-sitter. Only Python (full `ast`), JavaScript/TypeScript (regex) and Markdown/JSON are parsed. Other languages are file nodes only.
- No model calls. Documents, PDFs and images are never sent anywhere, and are not understood either: PDFs and images are asset nodes.
- No community detection, no graph report, no editor hooks, no MCP server.
- JS parsing is a careful regex, not a parser. Template-literal nesting and unusual regex literals can fool it. CommonJS `module.exports = {...}` is not read as exports.
- Setext headings (underlined with `===`) and HTML anchors are not read. `.gitignore` negation (`!`) is not supported.
- `mentions` is a name match. It can be wrong; that is why it is marked INFERRED.

## Test

```sh
python test.py                     # catalogue root defaults to two folders up
python test.py --catalogue <path>  # or pass it
```

The test builds a synthetic project (links, anchors, repeated headings, a fenced fake link, ignored folders, a binary file, Python and JS imports, a commented-out and a string-embedded import, exported and private JS functions, a syntax error, JSON registries) and asserts each node and edge. Then it builds the catalogue into a temporary folder (read-only; `kit/` is excluded because sibling tools are written there) and asserts:

- `README.md` links to `TOOL_SELECTION.md`; `scripts/validate-registry.py` imports `json`; `fixtures/lib/cdp.mjs` exports `findChrome`.
- Zero broken links.
- "gaussian splat viewer license" puts a gaussian-splatting guide file in the top 3.
- Text output stays within `--budget`.

Result on 26 Nov 2026: **32/32 checks passed**. Catalogue: 1,068 nodes, 2,040 edges (799 `links_to`, 68 `imports`, 276 `mentions`), 0 broken links, build in about 0.6 s. Gaussian query top 3: `docs/3d-pipeline/gaussian-splatting.md#gaussian-splatting`, `file:docs/repositories/gaussian-splatting.md`, `file:docs/3d-pipeline/gaussian-splatting.md`. See `out/result.json`, `out/catalogue-stats.json` and `out/catalogue-query.txt`.
