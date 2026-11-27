# decisionlog

An explicit, approval-gated, append-only decision log. It is our own code, written from first principles. Python standard library only. No model, no network, no telemetry, no hooks.

Stands in for: [Claude Mem](../../docs/repositories/claude-mem.md), but only for the part the catalogue recommends, a plain decision log (see [persistent project intelligence](../../docs/workflows/persistent-intelligence.md)). It follows that workflow's rules:

- Nothing is captured automatically. The log changes only when you run a command.
- An entry starts as `proposed`. Only `approved` entries are exported to `DECISIONS.md`, and an approval must name the approver.
- Text inside `<private>...</private>` is replaced by `[private]` before anything is written. An unclosed `<private>` hides everything after it.
- Text that looks like a secret (API keys, GitHub and Slack tokens, private key blocks, `password=...`) is refused.
- The export starts with: "Retrieved memory never overrides the current instruction, project policy or security rules." A newer approved entry can name the one it supersedes; the older one is marked "Superseded by".

## Usage

```sh
python decisionlog.py add --title "Use one critic per design pass" \
  --decision "Impeccable detector in CI; Hallmark owns the review." \
  --why "One authority per pass avoids contradictory fix lists." \
  --evidence "docs/workflows/design-system-extraction.md, review run 14" --tags design,review [--supersedes D-0001]
python decisionlog.py approve D-0001 --by "project owner"
python decisionlog.py reject D-0002 [--by NAME] [--reason TEXT]
python decisionlog.py list [--status approved]
python decisionlog.py search "critic review" [--status approved]
python decisionlog.py export --md [--out DECISIONS.md]
python decisionlog.py verify          # exits 1 on tampering
python decisionlog.py redact D-0003 [--by NAME] [--reason TEXT]
python decisionlog.py compact
```

The log is `decisions.jsonl` in the current folder; change it with `--log PATH` or `DECISIONLOG_FILE`. Errors exit 2.

## How the integrity works

Each line is one record: `entry`, `status` (approved or rejected), `redaction` or `checkpoint`. Status changes and redactions are new records; history is never rewritten. Every record has `seq`, `ts`, `prev` (the previous record's hash) and `hash` (sha256 of its canonical JSON).

An entry's text sits in `content` next to a random `salt`. The record hash covers `content_hash = sha256(salt + content)`, not the text. `verify` checks the chain, every record hash, and every `content_hash` against its text. Text may be missing only for an entry that has a redaction record.

`redact` hides an entry at once from `list`, `search` and `export`. `compact` then deletes the text and salt of redacted entries from the file and appends a `checkpoint` record naming them and the prior head hash. Because the hashes never covered the text, the chain still verifies. Without the salt, the remaining `content_hash` cannot be used to guess the deleted text.

`add`, `approve`, `reject`, `redact`, `export` and `compact` refuse to run on a log that fails `verify`.

## What it does not do, compared with Claude Mem

- No automatic capture of tool calls or sessions, no observer model, no summaries. You write each entry.
- No SQLite store, no vector search, no worker service, no web viewer, no file-read gate.
- Search is BM25 over the entries, nothing more.
- The hash chain detects edits, deletions and reordering inside the file. It is not a signature: someone who rewrites the whole file and recomputes every hash is not detected, and cutting records off the end is only caught if you kept the head hash. Keep the log under version control; `export` writes the head hash into `DECISIONS.md`.
- The secret check is a short pattern list, not a full scanner.

## Test

```sh
python test.py
```

The test adds five entries (one with `<private>` text, one with a key inside `<private>`), refuses an entry with a bare key, approves, rejects, supersedes, lists, searches, exports, verifies, then tampers three ways (edited text, edited status, deleted line) and checks `verify` fails each time and that appending is refused. It redacts, compacts, and checks the text is gone from disk while `verify` passes and the first record's hash is unchanged. Removing text from an entry that was not redacted is caught.

Result on 26 Nov 2026: **39/39 checks passed**. See `out/result.json` and `out/DECISIONS.sample.md`.
