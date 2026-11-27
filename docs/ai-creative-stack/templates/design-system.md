# DESIGN.md template

Copy this file to the project root as `DESIGN.md`. One file, one authority. Agents read it before any visual change and propose edits instead of making them.

## Identity

- **Name and purpose**
- **Personality** Three adjectives it is, and three it must never be.
- **Signature** The one element people should remember.

## Typography

| Role | Family | Weight | Size / line height | License |
| --- | --- | --- | --- | --- |
| Display | | | | |
| Body | | | | |
| Mono | | | | |

## Color tokens

| Token | Light | Dark | Use | Contrast checked against |
| --- | --- | --- | --- | --- |
| `--bg` | | | Page | — |
| `--fg` | | | Text | `--bg`, at least 4.5:1 |
| `--accent` | | | The one primary action | `--bg` |

## Spacing and layout

Spacing scale (for example 4, 8, 12, 16, 24, 32, 48, 64), grid, maximum widths and breakpoints.

## Composition

How a screen is built: focal point, alignment, density and how much empty space.

## Illustration language

Line weight, fill style, palette subset, and what illustrations may and may not depict.

## Material language (3D)

Base materials and their PBR ranges (roughness, metallic), texture resolution budget and allowed stylization.

## Lighting direction (3D and renders)

Key, fill and rim directions, color temperature, HDRI if any, and shadow softness.

## Motion rules

Durations, easing curves, what may move and why. The reduced-motion behavior for every animation.

## Accessibility

Contrast targets, focus style, minimum touch target, captions, and text alternatives for 3D and video.

## Approved references

| Reference | Rights status | What we take from it |
| --- | --- | --- |

## Prohibited visual patterns

The lazy defaults and lookalikes to avoid, each with the reason.

## Change log

| Date | Change | Approved by |
| --- | --- | --- |
