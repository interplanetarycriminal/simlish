# designlint report

- Target: out/fixtures/bad.html
- Widths: 390, 768, 1024, 1440 px
- Chrome: Chrome/158.0.8127.37
- Result: **FAIL** (Floor 8, Reflex 10, Finish 4)

| Width | Page width | Spacing on 4px grid | Distinct colors | Contrast checks |
| --- | --- | --- | --- | --- |
| 390 | 605 | 31.6% of 38 | 22 | 14 (0 on images/gradients skipped) |
| 768 | 768 | 31.6% of 38 | 22 | 14 (0 on images/gradients skipped) |
| 1024 | 1024 | 31.6% of 38 | 22 | 14 (0 on images/gradients skipped) |
| 1440 | 1440 | 31.6% of 38 | 22 | 14 (0 on images/gradients skipped) |

## Floor (8)

| Rule | Widths | Selector | Message |
| --- | --- | --- | --- |
| accessible-name | all | `body > a` | Link has no accessible name |
| contrast | 390, 768, 1024, 1440 | `body > p.faint:nth-of-type(1)` | Text contrast 1.92:1 is below 4.5:1 (normal text, #bbbbbb on #ffffff) |
| contrast | 390, 768, 1024, 1440 | `body > p.c4:nth-of-type(6)` | Text contrast 3.03:1 is below 4.5:1 (normal text, #00aa66 on #ffffff) |
| focus-outline | all | `button.icon-btn:nth-of-type(1)` | Keyboard focus is invisible: outline-style is none and no other style changes on focus |
| focus-outline | all | `a` | Keyboard focus is invisible: outline-style is none and no other style changes on focus |
| focus-outline | all | `#go` | Keyboard focus is invisible: outline-style is none and no other style changes on focus |
| img-alt | all | `body > img` | Image has no alt attribute (use alt="" if decorative): data:image/svg+xml,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.o |
| overflow-x | 390 | `body > div.wide:nth-of-type(1)` | Element spans 5..605px in a 390px viewport; page scrolls sideways to 605px |

## Reflex (10)

| Rule | Widths | Selector | Message |
| --- | --- | --- | --- |
| font-families | all | `page` | 5 font families in use (more than 3): georgia, impact, arial, courier new, verdana |
| font-size-min | 390, 768, 1024, 1440 | `body > p.tiny:nth-of-type(2)` | 1 text element(s) at 10.0px, below the 12px minimum |
| heading-skip | all | `body > h4` | Heading level jumps from h1 to h4 |
| multiple-h1 | all | `body > h1.grad:nth-of-type(2)` | 2 h1 elements on the page; use one |
| reduced-motion | all | `page` | 1 element(s) animate or transition, but no @media (prefers-reduced-motion) rule was found |
| text-clipped | 390, 768, 1024, 1440 | `body > div.box:nth-of-type(3)` | Text is cut off vertically: content 96px in a 28px box |
| text-overlap | 390, 768, 1024, 1440 | `body > div.stack:nth-of-type(2) > p:nth-of-type(1)` | Text overlaps text of body > div.stack:nth-of-type(2) > p.over:nth-of-type(2) (221x17px) |
| touch-target | 390 | `body > button.icon-btn:nth-of-type(1)` | Touch target is 16x16px, under 24x24px |
| touch-target | 390 | `body > a` | Touch target is 30x17px, under 24x24px |
| touch-target | 390 | `#go` | Touch target is 34x21px, under 24x24px |

## Finish (4)

| Rule | Widths | Selector | Message |
| --- | --- | --- | --- |
| color-count | 390, 768, 1024, 1440 | `page` | 22 distinct colors in use (limit 12); consolidate into tokens |
| emoji-heading | all | `body > h1:nth-of-type(1)` | Emoji in heading (a common lazy default): "Launch day 🚀" |
| gradient-text | all | `body > h1.grad:nth-of-type(2)` | Gradient-filled text (a common lazy default) |
| spacing-grid | 390, 768, 1024, 1440 | `page` | Only 31.6% of 38 spacing values sit on a 4px grid (off-grid: 13px x6, 3px x6, 5px x4, 21.28px x2, 7px x2, 11px x2) |
