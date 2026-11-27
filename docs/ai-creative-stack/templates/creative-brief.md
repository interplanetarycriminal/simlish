# Creative brief

Fill every line or write "not applicable". An agent should be able to act on this file alone.

## Outcome

- **Deliverables** What ships: site, app screen, GLB, splat scene, film, explorable.
- **Audience** Who uses it, on which devices, with what prior knowledge.
- **The one thing** What the audience should feel, do or understand afterwards.
- **Primary action** For pages and apps, the single action that matters most.

## Acceptance criteria

Write each one as something a person or a script can check.

| Criterion | How it is checked | Owner |
| --- | --- | --- |
| Example: hero GLB under 3 MB | `ls -l` on the delivery file | Technical artist |
| Example: LCP under 2.5 s on a mid-range phone profile | Lighthouse run, report attached | Frontend |

## Creative direction

- **Design authority** The single skill, system or person that owns the look. Link `DESIGN.md`.
- **References** Authorized references only, with their rights status. What to take from each and what to avoid.
- **Prohibited** Patterns, styles or brands this work must not resemble.

## Constraints

- **Existing stack** Framework, design system, render engine, delivery platform.
- **Hardware** Machines and GPUs actually available. Do not assume.
- **Budget and time** Hosted-service spend, render time, review rounds.
- **Data** What may leave the machine, and to which services. Faces, locations, client assets.
- **Licenses** Is commercial use required? Revenue thresholds? Attribution?

## Handoffs

List each producer → consumer boundary with its format. Use the [asset manifest](asset-manifest.json) for 3D assets and the [shot list](shot-list.md) for video.

## Sign-off

| Gate | Who signs | Evidence required |
| --- | --- | --- |
| Direction | | `DESIGN.md` approved |
| Delivery | | [Execution report](execution-report.md) with every gate result |
