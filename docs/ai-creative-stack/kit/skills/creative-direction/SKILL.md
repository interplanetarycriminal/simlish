---
name: creative-direction
description: Set one distinctive, project-specific visual direction and write it down as DESIGN.md before any UI, illustration, 3D or motion work. Use when a project has no design authority yet, when output looks generic, or when the user asks for a look, a style, a brand feel or a redesign.
---

# Creative direction

Our own stand-in for Taste Skill, Anthropic Frontend Design, UI/UX Pro Max and Meng To's direction skills. One skill, one authority: never run another direction skill on the same project.

## 1. Ground it in the subject

Before choosing anything, write five nouns from the subject's own world: its materials, tools, places, era and vernacular. A bakery has flour sacks, enamel trays and chalkboard prices. A machine-learning tool has graph paper, terminals and lab notebooks. Distinctive choices come from these nouns, not from a trend.

## 2. Deal the system

Choose one option in each row, and write the reason in one line.

| Decision | Options to choose from |
| --- | --- |
| Type pairing | Grotesque display + humanist body; serif display + grotesque body; mono-led technical; slab display + neutral sans; one variable family across widths |
| Color model | Ink on paper (one accent); dark instrument (two signals); duotone print; full-color illustrative (fixed palette of six); material-led (taken from the subject's materials) |
| Density | Airy editorial; balanced product; dense instrument panel |
| Shape | Hard corners; 4–8 px radius; pill and capsule; hand-drawn (use [sketchy](../../sketchy/README.md)) |
| Motion | Still (motion only for feedback); measured (200–300 ms, ease-out); expressive (springs, overshoot), always with a reduced-motion version |
| Signature | The one element people remember. Spend boldness here and nowhere else. |

## 3. Write DESIGN.md

Fill the catalogue's [DESIGN.md template](../../../templates/design-system.md). Every token needs a value and a reason. List at least five prohibited patterns: lazy defaults such as purple gradients, glassmorphism cards, emoji headings, three-column feature grids with icons, and centered everything.

If the user supplies a reference site they own or have permission to use, extract its tokens first with [tokenextract](../../tokenextract/README.md). Keep principles; never copy a brand.

## 4. Prove it on one screen

Build one representative screen or frame. Render it at 390, 768, 1024 and 1440 px. Run [designlint](../../designlint/README.md) and fix every Floor finding. Then look at the screenshots and answer in writing:

- What is the focal point at each width?
- Does the signature read in under three seconds?
- Which element is generic, and what from the subject's world could replace it?

Revise DESIGN.md with what you learned. Only then build the rest.

## Rules

- One accent color does more than five.
- Never ship a tool's default theme unchanged.
- Contrast is at least 4.5:1 for body text, in both themes.
- Every animation has a reduced-motion equivalent.
- Record every approved direction change in the project's decision log ([decisionlog](../../decisionlog/README.md)).
