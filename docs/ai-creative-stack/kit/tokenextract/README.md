# tokenextract

Reads a rendered page's design language from computed styles and writes design tokens and a draft `DESIGN.md`.

It stands in for **[Designlang (design-extract)](../../docs/repositories/designlang.md)**. This is original code written from the idea of extracting tokens from computed styles. No upstream code was read or copied.

Use it on your own pages, or on sites whose owners allow it. Extract principles, not a brand: the catalogue's [DESIGN.md](../../DESIGN.md) prohibits copying any brand's design language.

## What it does

It opens the page in headless Chrome (through [fixtures/lib/cdp.mjs](../../fixtures/lib/cdp.mjs)) at one width (1280 px by default) and walks every rendered element.

| Token group | How it is found |
| --- | --- |
| Colors | Text, background, border and SVG fill and stroke colors, counted. Near-duplicates merge by CIEDE2000 color difference in CIE Lab (default threshold 1.5). The most frequent color in a cluster names it. Clusters with Lab chroma under 20 are neutrals; the rest are brand colors. Both groups are ranked by frequency. |
| Typography | Font family stacks, sizes, weights and line-height ratios of text-bearing elements, plus the 8 most used family + size + weight + line-height combinations as DTCG `typography` composites. |
| Spacing | Non-zero margins, paddings and flex or grid gaps, merged within 0.5 px. The base unit is the largest of 8, 6, 5, 4, 3 or 2 px that divides at least 90% of the values. |
| Radii | Corner radii; percentage radii become one `radius-round` token. |
| Shadows | Distinct `box-shadow` values, parsed into DTCG `shadow` layers. |
| Breakpoints | `min-width`, `max-width` and range-syntax `width` conditions in `@media` rules of same-origin stylesheets. `em` and `rem` count as 16 px. |
| Motion | Transition and animation durations and timing functions. Keywords map to cubic Bézier curves; the top transitions become DTCG `transition` composites. It also notes `@keyframes` names and whether a reduced-motion rule exists. |

## Usage

```sh
node kit/tokenextract/tokenextract.mjs <url-or-html-file> [--out out/] [--width 1280] [--de 1.5] [--neutral-chroma 20]
```

Outputs in `--out`:

- `tokens.json`: W3C Design Tokens Community Group (DTCG) format. Colors use the object form (`colorSpace`, `components`, `hex`, `alpha`), dimensions and durations use `{ "value", "unit" }`. Counts, roles and merged members sit under `$extensions["kit.tokenextract"]`.
- `tokens.css`: the same tokens as custom properties on `:root`, such as `--color-brand-1`, `--space-3`, `--easing-1`.
- `DESIGN.md`: a draft with the section structure of [templates/design-system.md](../../templates/design-system.md), marked "draft, extracted — review before adopting; extract principles only from your own or permitted sites". It fills in typography, color, spacing, motion and contrast pairs, and leaves identity, composition and the other judgment sections for a person.
- `raw.json`: the raw counts the tokens came from.

## What it does not do, compared with Designlang

- One viewport width and one color scheme per run. No dark-mode pass, no responsive sweep, no hover or focus states (colors that appear only on interaction are missed).
- No component detection, voice or copy analysis, or Tailwind, shadcn and Figma exports. DTCG JSON and CSS only.
- No AI classification. Token names are positional (`brand-1`, `space-3`), not semantic.
- Cross-origin stylesheets cannot be read, so their breakpoints are missed.
- Equal left and right margins are skipped, because computed styles cannot tell `margin: auto` from a set value.
- The brand and neutral split is a chroma threshold. A muted brand color can land in neutrals; adjust `--neutral-chroma`.
- The dark column of the color table is left empty.

## Test

```sh
node kit/tokenextract/test.mjs
```

The test writes a page with known tokens into `out/fixtures/`: 3 brand colors (`#2363cf`, `#bf315c`, `#198047`) and a near-duplicate `#2464cf`, a 4/8/12/16/24/32 px spacing scale, Georgia and Verdana, 4, 8 and 16 px radii, one `200ms ease-out` transition, and one `@media (min-width: 768px)`. It also checks the CIEDE2000 code against the published test pair (expected 2.0425), and that the `DESIGN.md` headings match the template's in order. It writes `out/result.json`.

Result on 2026-11-26 (Chrome 158, Node 24): **pass, 31/31 checks.**

- CIEDE2000 test pair: 2.0425.
- Exactly 3 brand colors, each recovered at ΔE00 0.000; `#2464cf` merged into `#2363cf`.
- Families Verdana and Georgia; sizes 12, 16, 20, 32 px; spacing 4, 8, 12, 16, 24, 32 px with base 4 px (100% of values); radii 4, 8, 16 px; breakpoint 768 px; duration 200 ms; easing `[0, 0, 0.58, 1]`.
- `out/` is about 32 KB.
