---
name: design-critique
description: Critique and refine a rendered page or screen against its DESIGN.md with tiered gates and named moves. Use after any UI change, before calling frontend work done, or when the user asks to review, polish, audit or improve a design.
---

# Design critique

Our own stand-in for Impeccable's commands and detector and Hallmark's tiered gates and fresh reviewer. It judges rendered output, never source alone.

## 1. Measure

```sh
node kit/designlint/designlint.mjs <url-or-file> --out out/critique/
```

Read `report.md`. Findings come in three tiers:

- **Floor:** blocks delivery. Fix every one.
- **Reflex:** a lazy default. Fix it, or write a one-line reason to keep it.
- **Finish:** polish. Do it if time allows.

## 2. Look

Open the four screenshots. For each width, write three lines: the focal point, the weakest area, and what breaks the `DESIGN.md` rules.

## 3. Choose moves

Steer each change with one named move. One move per pass, so each change can be judged on its own.

| Move | Does |
| --- | --- |
| `bolder` | Raise contrast and scale on the focal element only |
| `quieter` | Remove or soften everything competing with the focal element |
| `distill` | Delete a section, element or effect that does not serve the primary action |
| `typeset` | Fix the type scale, measure (45–75 characters), line height and hierarchy |
| `space` | Snap spacing to the scale; group related items; separate unrelated ones |
| `colour` | Reduce to the token palette; one accent; fix contrast |
| `animate` | Add motion only where it explains or responds; include a reduced-motion version |
| `harden` | Empty, loading, error, long-content and narrow-width states |
| `polish` | The Finish findings |

## 4. Re-render and compare

Render again, run designlint again, and compare the tier counts. A pass is zero Floor findings, and every Reflex finding either fixed or justified in writing.

## 5. Fresh review

When the change is large, review it as someone who has not seen the work. Start a new session or a subagent, give it only `DESIGN.md` and the screenshots, and ask it for the three weakest points. Fix what it finds that you missed.

## Rules

- Never redesign while critiquing: moves refine the existing direction. A new direction needs the [creative-direction](../creative-direction/SKILL.md) skill and the owner's approval.
- Report the before and after tier counts and the screenshots.
