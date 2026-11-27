#!/usr/bin/env node
// Run every game-development handoff check and write out/result.json.
//   node run.mjs [check-name ...]
// Exit 0 only when every selected check passes.
import { mkdirSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';
import { ROOT } from './checks/versions.mjs';

const CHECKS = ['phaser-slice', 'matter-determinism', 'rapier-determinism', 'ink-branches', 'jsfxr-sfx', 'colyseus-room', 'babylon-glb'];
const TIMEOUT_MS = 180_000;

const wanted = process.argv.slice(2);
const selected = wanted.length ? CHECKS.filter((c) => wanted.includes(c)) : CHECKS;
mkdirSync(join(ROOT, 'out'), { recursive: true });

const results = {};
for (const name of selected) {
  const t0 = performance.now();
  let timer;
  try {
    const { default: check } = await import(`./checks/${name}.mjs`);
    const timeout = new Promise((_, fail) => { timer = setTimeout(() => fail(new Error(`timed out after ${TIMEOUT_MS / 1000} s`)), TIMEOUT_MS); });
    const r = await Promise.race([check(), timeout]);
    results[name] = { pass: Boolean(r.pass), seconds: +((performance.now() - t0) / 1000).toFixed(2), details: r.details };
  } catch (e) {
    results[name] = { pass: false, seconds: +((performance.now() - t0) / 1000).toFixed(2), error: String(e?.stack || e) };
  } finally { clearTimeout(timer); }
  console.log(`${results[name].pass ? 'PASS' : 'FAIL'}  ${name}  (${results[name].seconds} s)${results[name].error ? '\n      ' + results[name].error.split('\n')[0] : ''}`);
}

const result = {
  date: new Date().toISOString().slice(0, 10),
  node: process.version,
  platform: `${process.platform}-${process.arch}`,
  checks: results,
  pass: selected.length > 0 && Object.values(results).every((r) => r.pass),
};
writeFileSync(join(ROOT, 'out', 'result.json'), JSON.stringify(result, null, 2) + '\n');
console.log(result.pass ? 'ALL PASS' : 'SOME CHECKS FAILED');
process.exit(result.pass ? 0 : 1);
