// Babylon.js in headless Chrome: load the Blender fixture's GLB and check the handoff contract.
import { existsSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';
import { evaluate, launch, open, screenshot, serve } from '../../lib/cdp.mjs';
import { ROOT } from './versions.mjs';

const FIXTURES = join(ROOT, '..');
const GLB = '/blender-glb/out/toy_limb.glb';

export default async function run() {
  if (!existsSync(join(FIXTURES, GLB))) return { pass: false, details: { error: `missing ${GLB}; run the blender-glb fixture first` } };
  const server = await serve(FIXTURES);
  const cdp = await launch(undefined, { width: 480, height: 480 });
  try {
    await open(cdp, `http://127.0.0.1:${server.address().port}/game-dev/web/babylon.html?file=${encodeURIComponent(GLB)}`);
    const r = await evaluate(cdp, 'window.__report');
    if (r.error) return { pass: false, details: r };
    writeFileSync(join(ROOT, 'out', 'babylon-glb.png'), await screenshot(cdp));
    const moved = Math.hypot(...r.tipRest.map((v, i) => v - r.tipBent[i]));
    const checks = {
      oneSkinnedMesh: r.skinnedMeshes === 1 && r.skeletons === 1,
      threeBones: r.bones.length === 3,
      bendGroup: r.animationGroups.some((g) => g.name === 'bend' && g.targets > 0),
      heightPoint3m: Math.abs(r.heightMeters - 0.3) <= 0.003,
      bendMovesTip: moved > 0.01,
    };
    return { pass: Object.values(checks).every(Boolean), details: { ...r, chrome: cdp.version, tipMovedMeters: moved, checks, screenshot: 'out/babylon-glb.png' } };
  } finally {
    await cdp.close();
    server.close();
  }
}
