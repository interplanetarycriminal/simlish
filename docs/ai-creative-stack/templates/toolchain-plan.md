# Toolchain plan

Write this before installing anything. The strongest plan uses the fewest tools that meet the acceptance criteria.

## Capability gaps

| Need from the brief | Can the existing stack do it? | Evidence |
| --- | --- | --- |

## Selected tools

| Tool (registry id) | Role: guidance, execution, orchestration or storage | Version or commit pinned | License and commercial terms | Hardware it needs | Owner of its output |
| --- | --- | --- | --- | --- | --- |

## Rejected alternatives

| Tool | Why not |
| --- | --- |

## Ownership

One authority per asset, timeline and specification.

| Artifact | Sole owner | Who may propose changes |
| --- | --- | --- |

## Environments

| Environment | Isolation (venv, conda, container) | Python / Node / CUDA / PyTorch | Why it is separate |
| --- | --- | --- | --- |

## Permissions and data

- External services, and what each receives:
- Credentials needed, and where they are stored (never in the repository):
- Installer scripts reviewed (file, reviewer, date):

## Handoffs

| Producer | Consumer | Format | Contract check |
| --- | --- | --- | --- |

## First fixture

The smallest test that proves the chain works end to end, and its pass condition.
