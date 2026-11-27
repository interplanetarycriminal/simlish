# DESIGN.md: the catalogue's own design system

Every project gets exactly one `DESIGN.md`, and it is the only design authority. This file is the catalogue's own: it governs its diagrams, fixtures and pages, and it is a filled-in example of the [template](templates/design-system.md). Copy the template, not this file, into a project.

## Identity

- **Purpose** Technical documentation that an agent and a technical artist act on.
- **Personality** Exact, calm, legible. Never decorative, salesy or crowded.
- **Signature** Rounded cards with a color bar for meaning, and every arrow labelled with what it carries.

## Typography

| Role | Family | Weight | Size | Notes |
| --- | --- | --- | --- | --- |
| Diagram title | `system-ui, -apple-system, sans-serif` | 750 | 29 px | No web fonts in SVGs: GitHub renders them as images. |
| Card title | same | 720 | 16.5–17 px | |
| Card detail and arrow labels | same | 450–560 | 12.5–13 px | Minimum size that stays legible at GitHub's content width. |
| Fixture pages | `system-ui, "Segoe UI", sans-serif` | 650 captions | `clamp(1.1rem, 2.4vw, 1.9rem)` | |

## Color tokens

Semantic colors mark meaning, not decoration. Each appears as a 7 px bar on a neutral card, so text contrast never depends on it.

| Token | Bar color | Meaning |
| --- | --- | --- |
| slate | `#596b84` | Requirements, specifications, infrastructure |
| purple | `#733ed0` | Intelligence and creative direction |
| blue | `#2363cf` | UI, UX and frontend |
| amber | `#a05212` | Geometry, illustration and 3D |
| teal | `#087d73` | Motion, time and spatial reconstruction |
| rose | `#bf315c` | Post-production, external adapters, lossy steps |
| green | `#198047` | Quality assurance and delivery |

| Surface | Light | Dark |
| --- | --- | --- |
| Background | `#fbfcff` | `#101829` |
| Card | `#ffffff`, stroke `#d0d9e7` | `#182439`, stroke `#435570` |
| Text | `#152137` | `#f2f5fb` |
| Secondary text | `#465773` | `#c2cee1` |
| Connectors | `#62738d` | `#a4b7d1` |

Every SVG switches with `prefers-color-scheme`. Fixture pages use `--bg #F2F4F1`, `--fg #17201E`, `--accent #1D6A84` and `--signal #B57900`.

## Spacing and layout

Cards are 300 px wide with 76 px between columns and 64 px between rows. Diagrams flow top to bottom. Captions keep the left third of a landscape fixture frame, and the subject sits right of center.

## Composition

One claim per diagram. Show the mechanism, not a list of names. Alternatives share a card ("one generator: A, B or C") instead of competing boxes.

## Illustration language

Flat, hand-authored SVG. No gradients, shadows, stock icons or decorative imagery.

## Material language (3D fixtures)

Matte plastics with roughness 0.4–0.5 and metallic below 0.3, and brushed steel with metallic about 0.7. Colors come from the fixture tokens.

## Lighting direction (3D fixtures)

A hemisphere fill and one warm-neutral key light from the upper front right. No HDRI, so headless renders stay repeatable.

## Motion rules

Motion explains a mechanism or it is removed. Camera moves settle before a beat starts (see the [time contract](docs/contracts/time-contract.md)). Reduced motion opens fixtures paused.

## Arrow semantics

| Mark | Meaning |
| --- | --- |
| Solid arrow | Required step, or an integration tested by a fixture here |
| Dashed arrow | Optional step, or an integration documented upstream or proposed |
| Dashed card outline | A decision |
| Dashed boundary | A group with a stated limit, such as "ComfyUI-3D-Pack native" |
| Label on an arrow | The artifact or format that crosses |

## Accessibility

Every SVG has `role="img"`, a `<title>` and a `<desc>` that states its claim. Text stays at least 12.5 px. Body text meets at least 4.5:1 contrast on its card in both themes. Color is never the only signal: card text names the role too.

## Approved references

The catalogue's own v1 diagrams, whose palette this extends.

## Prohibited visual patterns

- Unlabelled arrows.
- Boxes that only restate a list.
- Numerical ratings of tools.
- Badges, logos and brand marks of the catalogued projects.
- Copying any brand's design language, including through Awesome DESIGN.md or Designlang output.

## Change log

| Date | Change | Approved by |
| --- | --- | --- |
| 2026-11-26 | Diagrams generated from `.mmd` sources; decision and boundary marks added for V3 | Catalogue maintainer |
