# designlint

Deterministic design-quality checks on a rendered page, sorted into the catalogue's three tiers (Floor, Reflex, Finish; see [QUALITY_GATES.md](../../QUALITY_GATES.md)).

It stands in for two catalogue tools:

- **[Impeccable](../../docs/repositories/impeccable.md)**: its deterministic detector of design problems and lazy defaults.
- **[Hallmark](../../docs/repositories/hallmark.md)**: its tiered gates, where Floor failures block release.

This is original code written from the rule descriptions below. No upstream code was read or copied.

## What it does

It opens the page in headless Chrome (through [fixtures/lib/cdp.mjs](../../fixtures/lib/cdp.mjs)), sets each viewport width in turn, and reads computed styles and layout boxes.

| Rule | Tier | Where | What it measures |
| --- | --- | --- | --- |
| `contrast` | Floor | each width | WCAG contrast of text against its effective background. Fails under 4.5:1, or 3:1 for large text (24 px, or 18.66 px bold). Background is the ancestor chain of background colors, composited for alpha. Text opacity is included. |
| `overflow-x` | Floor | each width | Page wider than the viewport. Names the outermost elements that stick out. |
| `img-alt` | Floor | once | `img` with no `alt` attribute (`alt=""` passes as decorative). |
| `accessible-name` | Floor | once | Links and buttons with no name from `aria-labelledby`, `aria-label`, text, image `alt`, SVG `<title>` or `title`. |
| `focus-outline` | Floor | once | Presses Tab through the page with real key events. Fails when the focused element has `outline-style: none` and no change in box-shadow, border, background, color, underline or transform. |
| `text-overlap` | Reflex | each width | Text line boxes from different elements that overlap by at least a quarter of the smaller box, after clipping by `overflow` ancestors. |
| `text-clipped` | Reflex | each width | Text in an `overflow: hidden` or `clip` box whose content is larger than the box. |
| `font-families` | Reflex | once | More than 3 primary font families on text. |
| `font-size-min` | Reflex | each width | Text below 12 px. |
| `touch-target` | Reflex | 390 px | Interactive elements smaller than 24 x 24 CSS px. Inline links inside sentences are exempt, as in WCAG 2.5.8. |
| `heading-skip` | Reflex | once | A heading level jumps by more than one (h1 to h4). |
| `multiple-h1` | Reflex | once | More than one visible `h1`. |
| `reduced-motion` | Reflex | once | Elements animate or transition, and no `@media (prefers-reduced-motion)` rule exists in readable stylesheets. |
| `spacing-grid` | Finish | each width | Share of non-zero margins, paddings and gaps that are multiples of 4 px. Reported for every width; a finding under 80%. |
| `color-count` | Finish | each width | More than 12 distinct text, background, border and SVG colors. |
| `gradient-text` | Finish | once | Text filled with a gradient through `background-clip: text`. |
| `emoji-heading` | Finish | once | Emoji in a heading. |

## Usage

```sh
node kit/designlint/designlint.mjs <url-or-html-file> [--widths 390,768,1024,1440] [--out out/] [--height 800]
```

A local file is served from its own folder on 127.0.0.1, so its stylesheets are same-origin and readable. Set `CHROME` if Chrome is not in a standard place.

Outputs in `--out`:

- `report.json`: target, widths, tier counts, per-width metrics (spacing share, distinct colors, families, motion), and findings. Each finding has `rule`, `tier`, `width` (first width seen, or `null` for page-wide rules), `widths` (every width where it occurred), `selector`, `message` and `value` (the measured number).
- `report.md`: the same as a short summary.
- `shot-<width>.png`: one viewport screenshot per width.

Exit code: 1 when any Floor finding exists, 0 otherwise, 2 on a usage or load error.

## What it does not do, compared with the upstream tools

- No design critique or taste judgment. Impeccable's skill side (critique, rewriting, project context) is not here; only deterministic rules.
- No hooks or editor integration, as Hallmark has. You run it by hand or in CI.
- Contrast ignores text over images, gradients, video and canvas; those are counted as skipped in the metrics. It only follows ancestors, so text placed over a sibling by absolute positioning is judged against its own ancestors.
- Equal left and right margins are left out of the spacing share, because computed styles cannot tell `margin: auto` from a set value.
- Focus checks follow the Tab order only; elements outside it, and focus styles drawn on a parent through `:focus-within`, are not judged.
- Cross-origin stylesheets cannot be read, so a reduced-motion rule there is not seen. The report says how many were unreadable.
- The thresholds (12 colors, 80% grid share, 3 families) are starting defaults, not standards.

## Test

```sh
node kit/designlint/test.mjs
```

The test writes two pages into `out/fixtures/`. The bad page plants low contrast, overflow at 390 px only, an image without alt, an emoji heading, `outline: none`, and 5 font families. It also plants a nameless link, gradient text, 10 px text, a 16 x 16 button, an h1 to h4 skip, two h1s, overlapping text, clipped text, a transition without a reduced-motion rule, off-grid spacing and 21 colors. The clean page uses one family, a 4 px scale, visible focus, and a reduced-motion rule. It writes `out/result.json`.

Result on 2026-11-26 (Chrome 158, Node 24): **pass, 24/24 checks.**

- Bad page: Floor 8, Reflex 12, Finish 4, exit code 1. Contrast 1.92:1 for `#bbb` on white; overflow 605 px at 390 px and none at 768 px and wider; 31.6% of spacing on the 4 px grid.
- Clean page: Floor 0, Reflex 0, Finish 0, exit code 0. 100% of spacing on the grid at every width; 3 of 3 tab stops show focus.
- `out/` is about 210 KB.

A smoke run on [fixtures/seekable-scene/index.html](../../fixtures/seekable-scene/index.html) gave Floor 0, Reflex 1 (the range slider is 16 px tall) and Finish 4 (rem-based spacing is off the 4 px grid).
