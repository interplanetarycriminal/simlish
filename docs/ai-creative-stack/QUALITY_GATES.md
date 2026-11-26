# Quality gates

Record the artifact, exact build or render command, tool versions, fixture, owner and outcome for each applicable gate. Mark blocked checks explicitly and retain evidence.

Check actual outputs. A source review can uncover issues and should be paired with a rendered preview. Apply corrections and repeat the affected checks before release.

## Three tiers

Every check below belongs to one tier, a structure borrowed from [Hallmark](docs/repositories/hallmark.md):

| Tier | Meaning | Who can waive it |
| --- | --- | --- |
| **Floor** | A failure blocks release | Nobody. Fix it or cut the feature. |
| **Reflex** | Catches lazy defaults. A failure needs a fix or a written reason. | The creative owner, on the record |
| **Finish** | Polish. Never blocks. | Anyone, by leaving it for the next pass |

The numbers are starting defaults. Set your own in the brief and record which ones you changed.

## Gates

| Gate | Floor | Reflex | Finish |
| --- | --- | --- | --- |
| Visual design | Screenshots exist at every target size. Nothing overlaps, clips or overflows. Text contrast is at least 4.5:1, or 3:1 for large text. | One focal point per view. Decoration does not compete with the primary action. No tool's default theme left unchanged. | Spacing on one scale. Type, color and motion read as one system across sizes. |
| Engineering | Clean rebuild from the lockfile. No console errors on the primary path. Error and empty states exist. | Largest Contentful Paint under 2.5 s and layout shift under 0.1 on a mid-range phone profile. Components reused, not copied. | Bundle and image sizes recorded per route. |
| Accessibility | Keyboard reaches every control in a sensible order with a visible focus. Controls have names. Reduced motion is honored. | Status changes are announced. Every motion has a static or paused equivalent. | Tested with a screen reader as well as automated tools. |
| Interactive 3D | Scene loads on target hardware with a poster or static fallback. Controls work outside the canvas. Asset scale and materials match the source. | Hero GLB under 10 MB, or under 3 MB for mobile-first work. p95 frame time under 20 ms on target hardware. Under 150 draw calls. | Load progress shown. Level of detail tuned per device class. |
| Time contract | For a scene that plays live and renders: seekable, repeatable and pause-to-play checks pass on the fixture. See the [time contract](docs/contracts/time-contract.md). | `digest()` values match across machines. No `Math.random()` or wall-clock reads inside the scene. | Chapters in the film link to the live scene at the same `#t=`. |
| Motion and video | ffprobe reports the declared codec, size, frame rate, frame count and duration. Audio and captions are present when the contract requires them. | Cuts land on beats or words. No audio pops at cuts. Captions stay inside safe areas. | Loudness normalized for the target platform. Representative frames reviewed at full size. |
| Geometry | `validate_asset.py` Floor checks pass: geometry present, no non-manifold edges, no degenerate faces, consistent normals, no loose vertices. Transforms applied; units in meters. | Triangle count within the brief's budget. Watertight after welding where the use needs it. No n-gons in deforming areas. Silhouette matches the reference from three angles. | Edge flow follows the forms that deform. Level-of-detail variants exist. |
| UVs and materials | UVs exist. Roughness, metallic, normal and opacity maps are Non-Color; base color and emission are sRGB. Every face has a material. | Seams sit in hidden or natural breaks. Texel density is consistent across the asset. Texture resolution fits the budget. | The material reads plausibly under two lighting set-ups and an HDRI. |
| Rigging | A single root and a valid hierarchy. Bind pose matches the mesh. Every vertex is weighted, weights are normalized, and there are at most 4 influences for glTF. | Test poses at each joint's limits show no candy-wrapping, collapse or penetration. Clip names survive export and re-import. | Bone roll is consistent. Deform bones are limited to what moves. |
| Physics and animation | Caches are baked and versioned. The final frame range plays without a solver failure. | No unintended clipping or popping. Timing matches the shot list. Playback reproduces from the baked cache. | Secondary motion (settling, wobble) is present where the brief wants it. |
| Gaussian reconstruction | Capture covers every side the brief needs. Camera poses converge. The scene opens in the target viewer. | Held-out views show no large floaters or holes. File size and frame rate meet the target device. Moving objects are removed or masked. | View-dependent shine looks plausible. Any mesh conversion records its losses. |
| Learning | Each beat's caption is true and legible at delivery size, clear of the subject. The prediction can be answered from what was shown. | One idea per beat. A prediction comes before the main reveal. Every beat is reachable by keyboard and by `#t=` link. | Tested with one learner who matches the brief: their prediction, their explanation afterwards and where they got stuck are recorded. |
| Delivery | Every declared artifact opens and matches its format. Rights recorded for fonts, images, audio, weights and code. | A reproducible source or export command for each artifact. | Release manifest lists versions and evidence for each gate. |

## Evidence format

For a rendered fixture, keep a machine-readable record like the one `render.mjs` writes, so a later run can be compared:

```json
{ "fixture": "seekable-scene", "chrome": "Chrome/158.0.8127.37", "three": "r187", "fps": 30,
  "checks": { "seekable": { "pass": true }, "repeatable": { "pass": true },
              "pauseToPlay": { "pass": true }, "stream": { "pass": true, "frames": 600 } } }
```

The validator fails the catalogue if a committed `fixtures/*/out/evidence.json` records a failed check.
