#!/usr/bin/env node
// Load the Blender-exported GLB in Three.js (headless Chrome) and check the handoff contract.
//   node check.mjs [--file out/toy_limb.glb]
// Writes out/three-check.json and out/three-sheet.png. Exit 0 when every check passes.
import { execFileSync } from 'node:child_process';
import { writeFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { evaluate, launch, open, screenshot, serve } from '../lib/cdp.mjs';

const HERE = dirname(fileURLToPath(import.meta.url));
const i = process.argv.indexOf('--file');
const FILE = i > 0 ? process.argv[i + 1] : 'out/toy_limb.glb';
const OUT = join(HERE, 'out');

const server = await serve(HERE);
const cdp = await launch(undefined, { width: 640, height: 640 });
await open(cdp, `http://127.0.0.1:${server.address().port}/viewer.html?file=${encodeURIComponent(FILE)}`);
const stats = await evaluate(cdp, 'window.__asset.stats');

const poses = [[0, 0], [0.5, 0.9], [1.5, -0.9]];
const tips = [];
const shots = [];
for (const [t, angle] of poses) {
  tips.push(await evaluate(cdp, `window.__asset.seek(${t}, ${angle})`));
  const png = await screenshot(cdp);
  const path = join(OUT, `three-t${t}.png`);
  writeFileSync(path, png); shots.push(path);
}
const again = await evaluate(cdp, 'window.__asset.seek(0.5, 0.9)');
const version = cdp.version;
await cdp.close();
server.close();

const dist = (a, b) => Math.hypot(a[0] - b[0], a[1] - b[1], a[2] - b[2]);
const bend = stats.animations.find((a) => /bend/.test(a.name));
const checks = {
  loads: stats.meshes >= 1,
  skinned: stats.skinnedMeshes === 1 && stats.bones.length === 3,
  clip: Boolean(bend) && Math.abs(bend.duration - 47 / 24) < 0.05,
  metersAndYUp: Math.abs(stats.sizeMeters[1] - 0.3) < 0.003 && stats.upAxis === 'Y',
  animationDeforms: tips[0] && tips[1] && dist(tips[0], tips[1]) > 0.01,
  seekRepeatable: JSON.stringify(again) === JSON.stringify(tips[1]),
};
const result = { file: FILE, chrome: version, three: 'r187', stats, tipPositions: tips, checks, pass: Object.values(checks).every(Boolean) };
writeFileSync(join(OUT, 'three-check.json'), JSON.stringify(result, null, 2) + '\n');
execFileSync('ffmpeg', ['-hide_banner', '-loglevel', 'error', '-y', ...shots.flatMap((s) => ['-i', s]),
  '-filter_complex', 'hstack=3', join(OUT, 'three-sheet.png')]);
for (const [k, v] of Object.entries(checks)) console.log(`${v ? 'PASS' : 'FAIL'}  ${k}`);
process.exit(result.pass ? 0 : 1);
