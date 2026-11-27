#!/usr/bin/env node
// Expressive-motion fixture: which upstream motion libraries can be seeked deterministically from
// ONE authoritative frame clock for offline rendering?
//
//   node run.mjs [--only motion,theatre,r3f,ownership,pixelfx] [--pixelfx <path to a pixelfx clone>]
//
// --pixelfx regenerates the optional pixelfx sprite sheets from a clone kept OUTSIDE the catalogue and
// copies the small ones into out/pixelfx/. Without it, the copies already in out/pixelfx/ are re-verified.
//
// Each check runs in headless Chrome (--disable-threaded-animation) through ../lib/cdp.mjs.
// Libraries load from esm.sh at the exact versions in pages/shared.js.
// Writes out/result.json (and out/r3f-sheet.png). Exits 0 only when every check passes.
import { execFileSync } from 'node:child_process';
import { copyFileSync, existsSync, mkdirSync, mkdtempSync, readdirSync, readFileSync, rmSync, statSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { inflateSync } from 'node:zlib';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { evaluate, launch, open, serve } from '../lib/cdp.mjs';
import { VERSIONS, bezier } from './pages/shared.js';

const HERE = dirname(fileURLToPath(import.meta.url));
const OUT = join(HERE, 'out');
mkdirSync(OUT, { recursive: true });
const FPS = 24;
const onlyArg = process.argv.indexOf('--only');
const ONLY = onlyArg > 0 ? process.argv[onlyArg + 1].split(',') : null;
const pfxArg = process.argv.indexOf('--pixelfx');
const PIXELFX_CLONE = pfxArg > 0 ? process.argv[pfxArg + 1] : null;

const server = await serve(join(HERE, '..')); // serve fixtures/ so the r3f page can reach ../blender-glb/out
const base = `http://127.0.0.1:${server.address().port}/expressive-motion/pages`;
let chrome = null;

/** Fresh browser + page load per call, so "repeatable" means a new process, not a reload. */
async function withPage(page, fn, size = { width: 480, height: 360 }) {
  const cdp = await launch(undefined, { ...size, args: ['--disable-threaded-animation'] });
  chrome = cdp.version;
  try {
    await open(cdp, `${base}/${page}`);
    const err = await evaluate(cdp, 'window.__error || null');
    if (err) throw new Error(`${page}: ${err}`);
    return await fn((expr) => evaluate(cdp, expr));
  } finally { await cdp.close(); }
}

const frameTimes = (seconds) => Array.from({ length: seconds * FPS + 1 }, (_, i) => i / FPS);
const r = (v, d = 3) => Math.round(v * 10 ** d) / 10 ** d;
const maxAbs = (a, b) => Math.max(...a.map((v, i) => Math.abs(v - b[i])));
const same = (a, b) => JSON.stringify(a) === JSON.stringify(b);

// ---------------------------------------------------------------------------------------------
async function motionSeek() {
  const T = frameTimes(1);
  const seekAll = (ev, which, times) => ev(`(async () => { const o = []; for (const t of ${JSON.stringify(times)}) o.push(await window.__probe.seek('${which}', t)); return o; })()`);
  const load1 = await withPage('motion.html', async (ev) => {
    const info = await ev('window.__probe.info()');
    const out = { info };
    for (const which of ['ease', 'spring']) {
      out[which] = {
        inOrder: await seekAll(ev, which, T),
        twice: await seekAll(ev, which, T.flatMap((t) => [t, t])),
        reversed: (await seekAll(ev, which, [...T].reverse())).reverse(),
      };
    }
    out.springLong = await seekAll(ev, 'spring', frameTimes(2));
    out.springTail = await seekAll(ev, 'spring', [3, 4]);
    return out;
  });
  const load2 = await withPage('motion.html', async (ev) => ({ ease: await seekAll(ev, 'ease', T), spring: await seekAll(ev, 'spring', T) }));

  const settled = (arr) => arr.map((s) => s.settled);
  const res = {};
  for (const which of ['ease', 'spring']) {
    const a = settled(load1[which].inOrder);
    const tw = settled(load1[which].twice);
    res[which] = {
      values: a.map((v) => r(v, 2)),
      seekTwiceIdentical: T.every((_, i) => tw[2 * i] === tw[2 * i + 1]),
      outOfOrderMatches: same(settled(load1[which].reversed), a),
      repeatableAcrossLoads: same(settled(load2[which]), a),
      // Does the DOM show the seeked value right after "controls.time = t", or only after the next animation frame?
      syncReadMatchesSettled: load1[which].inOrder.every((s) => Math.abs(s.sync - s.settled) < 1e-6),
      exampleAtHalf: { sync: r(load1[which].inOrder[12].sync, 2), settled: r(load1[which].inOrder[12].settled, 2) },
    };
  }
  // Ease: monotonic, ends at 0 and 200, and equals cubic-bezier(0.42, 0, 0.58, 1) computed here independently.
  const e = settled(load1.ease.inOrder);
  const expected = T.map((t) => 200 * bezier(0.42, 0, 0.58, 1, t));
  Object.assign(res.ease, {
    monotonic: e.every((v, i) => i === 0 || v >= e[i - 1] - 1e-9),
    endpoints: Math.abs(e[0]) < 0.01 && Math.abs(e.at(-1) - 200) < 0.01,
    maxErrorVsBezierPx: r(maxAbs(e, expected), 4),
  });
  res.ease.matchesBezier = res.ease.maxErrorVsBezierPx < 0.5;
  // Spring: compare with the closed-form underdamped spring (k = 180, c = 9, m = 1, from rest). Informational.
  const k = 180, c = 9, m = 1, w0 = Math.sqrt(k / m), z = c / (2 * Math.sqrt(k * m)), wd = w0 * Math.sqrt(1 - z * z);
  const spring = (t) => 200 * (1 - Math.exp(-z * w0 * t) * (Math.cos(wd * t) + (z * w0 / wd) * Math.sin(wd * t)));
  const s = settled(load1.spring.inOrder);
  const T2 = frameTimes(2);
  const s2 = settled(load1.springLong);
  const dur = load1.info.springDuration;
  Object.assign(res.spring, {
    durationReported: dur,
    overshootPx: r(Math.max(...s) - 200, 2),
    maxErrorVsClosedFormPx: r(maxAbs(s2.filter((_, i) => T2[i] < dur), T2.filter((t) => t < dur).map(spring)), 4),
    // At its reported duration Motion holds the target value; the residual it drops is the snap size.
    snapAtDurationPx: r(Math.max(...T2.map((t, i) => (t >= dur ? Math.abs(s2[i] - spring(t)) : 0))), 4),
    valuesTo2s: s2.map((v) => r(v, 2)),
    tailValues: settled(load1.springTail).map((v) => r(v, 3)),
  });
  delete res.spring.values;
  res.spring.seekable = res.spring.seekTwiceIdentical && res.spring.outOfOrderMatches && res.spring.repeatableAcrossLoads && Math.max(...s) > 150;
  const pass = ['seekTwiceIdentical', 'outOfOrderMatches', 'repeatableAcrossLoads', 'monotonic', 'endpoints', 'matchesBezier'].every((k2) => res.ease[k2]);
  return { pass, library: `motion@${VERSIONS.motion}`, samples: T.length, fps: FPS, ...res, modules: load1.info.modules };
}

// ---------------------------------------------------------------------------------------------
async function theatreSeek() {
  const T = frameTimes(2);
  const seekAll = (ev, times) => ev(`(async () => { const o = []; for (const t of ${JSON.stringify(times)}) o.push(await window.__probe.seek(t)); return o; })()`);
  const load1 = await withPage('theatre.html', async (ev) => ({
    info: await ev('window.__probe.info()'),
    inOrder: await seekAll(ev, T),
    twice: await seekAll(ev, T.flatMap((t) => [t, t])),
    reversed: (await seekAll(ev, [...T].reverse())).reverse(),
  }));
  const load2 = await withPage('theatre.html', async (ev) => seekAll(ev, T));
  const v = load1.inOrder.map((s) => s.value);
  // Expected from the keyframes in theatre.html: straight 0 -> 120 over [0, 1], ease-in-out 120 -> 40 over [1, 2].
  const expected = T.map((t) => (t <= 1 ? 120 * t : 120 + (40 - 120) * bezier(0.42, 0, 0.58, 1, t - 1)));
  const tw = load1.twice.map((s) => s.value);
  const res = {
    values: v.map((x) => r(x, 3)),
    maxErrorVsKeyframes: r(maxAbs(v, expected), 4),
    domFollowsValue: load1.inOrder.every((s) => Math.abs(s.dom - s.value) < 0.01),
    seekTwiceIdentical: T.every((_, i) => tw[2 * i] === tw[2 * i + 1]),
    outOfOrderMatches: same(load1.reversed.map((s) => s.value), v),
    repeatableAcrossLoads: same(load2.map((s) => s.value), v),
    sequenceLength: load1.info.length,
  };
  res.matchesKeyframes = res.maxErrorVsKeyframes < 0.5;
  const pass = ['matchesKeyframes', 'domFollowsValue', 'seekTwiceIdentical', 'outOfOrderMatches', 'repeatableAcrossLoads'].every((k) => res[k]);
  return { pass, library: `@theatre/core@${VERSIONS['@theatre/core']} (no studio)`, samples: T.length, fps: FPS, ...res, modules: load1.info.modules };
}

// ---------------------------------------------------------------------------------------------
async function r3fFrameloop() {
  const probeTimes = [0, 0.5, 1.0];
  const load1 = await withPage('r3f.html', async (ev) => {
    const stats = await ev('window.__scene.stats');
    const info = await ev('window.__scene.info()');
    const before = await ev('window.__scene.frameCount()');
    await new Promise((ok) => setTimeout(ok, 600));
    const idle = await ev('window.__scene.frameCount()');
    const shots = {};
    const seq = [];
    for (const t of probeTimes) {
      seq.push({ t, ...(await ev(`window.__scene.seek(${t})`)) });
      shots[t] = await ev('window.__scene.png()');
    }
    const again = await ev('window.__scene.seek(0.5)');
    const again2 = await ev('window.__scene.seek(0.5)');
    const backFrom = await ev('window.__scene.seek(1.0)').then(() => ev('window.__scene.seek(0.5)'));
    return { stats, info, before, idle, seq, again, again2, backFrom, shots };
  }, { width: 480, height: 400 });
  const load2 = await withPage('r3f.html', (ev) => ev('window.__scene.seek(0.5)'), { width: 480, height: 400 });

  const h = Object.fromEntries(load1.seq.map((s) => [s.t, s.hash]));
  const bend = load1.stats.clips.find((c) => c.name === 'bend');
  const res = {
    glbLoads: load1.stats.skinnedMeshes === 1,
    threeBones: load1.stats.bones.length === 3,
    bendClip: Boolean(bend),
    noAutonomousFrames: load1.idle === load1.before,
    sameTimeIdenticalPixels: load1.again.hash === h[0.5] && load1.again2.hash === h[0.5],
    outOfOrderIdenticalPixels: load1.backFrom.hash === h[0.5],
    animationChangesPixels: new Set(Object.values(h)).size === probeTimes.length,
    repeatableAcrossLoads: load2.hash === h[0.5],
    meshVisible: load1.seq.every((s) => s.nonBackgroundPixels > 500),
  };
  const pass = Object.values(res).every(Boolean);
  // Contact sheet of the three probe frames.
  const tmp = probeTimes.map((t) => { const p = join(OUT, `r3f-tmp-${t}.png`); writeFileSync(p, Buffer.from(load1.shots[t].split(',')[1], 'base64')); return p; });
  try {
    execFileSync('ffmpeg', ['-hide_banner', '-loglevel', 'error', '-y', ...tmp.flatMap((p) => ['-i', p]), '-filter_complex', 'hstack=3', join(OUT, 'r3f-sheet.png')]);
  } catch (e) { res.sheetError = String(e.message).slice(0, 200); }
  for (const p of tmp) rmSync(p, { force: true });
  return {
    pass, ...res,
    versions: load1.info.versions,
    stats: load1.stats,
    hashes: Object.fromEntries(Object.entries(h).map(([t, x]) => [t, x.slice(0, 16)])),
    framesRendered: load1.seq.map((s) => s.frame),
    modules: load1.info.modules,
  };
}

// ---------------------------------------------------------------------------------------------
async function ownership() {
  const T = frameTimes(1);
  const out = await withPage('ownership.html', async (ev) => {
    const info = await ev('window.__probe.info()');
    const disjoint = await ev(`(async () => { const o = []; for (const t of ${JSON.stringify(T)}) o.push(await window.__probe.disjoint(t)); return o; })()`);
    const conflict = {};
    for (const order of ['gsap-then-motion', 'motion-then-gsap']) {
      conflict[order] = await ev(`(async () => { const o = []; for (const t of ${JSON.stringify(T)}) o.push(await window.__probe.conflict(t, '${order}')); return o; })()`);
    }
    const live = await ev('window.__probe.live(40)');
    return { info, disjoint, conflict, live };
  });

  const disjoint = {
    xMaxErrorPx: r(maxAbs(out.disjoint.map((s) => s.x), T.map((t) => 200 * t)), 4),
    opacityMaxError: r(maxAbs(out.disjoint.map((s) => s.opacity), T), 4),
  };
  disjoint.pass = disjoint.xMaxErrorPx < 0.5 && disjoint.opacityMaxError < 0.01;

  const winner = (x, t) => (Math.abs(x - 200 * t) < 0.5 ? 'gsap' : Math.abs(x + 100 * t) < 0.5 ? 'motion' : 'neither');
  const conflict = {};
  for (const [order, samples] of Object.entries(out.conflict)) {
    const moving = samples.map((s, i) => ({ ...s, t: T[i] })).filter((s) => s.t > 0);
    const tally = (key) => moving.reduce((acc, s) => { const w = winner(s[key], s.t); acc[w] = (acc[w] || 0) + 1; return acc; }, {});
    conflict[order] = {
      winnerImmediately: tally('sync'),
      winnerAfterTwoFrames: tally('settled'),
      // GSAP keeps its own cache of x; it does not see Motion's write.
      gsapCacheDisagreesWithDom: moving.filter((s) => Math.abs(s.gsapBelieves - s.settled) > 0.5).length,
      exampleAtHalf: { t: 0.5, sync: r(samples[12].sync, 2), settled: r(samples[12].settled, 2), gsapBelieves: r(samples[12].gsapBelieves, 2), inlineTransform: samples[12].inline },
    };
    conflict[order].someOwnerIgnored = moving.some((s) => Math.abs(s.settled - 200 * s.t) > 1) || moving.some((s) => Math.abs(s.settled + 100 * s.t) > 1);
  }
  const orders = Object.values(conflict);
  const w = (o) => Object.entries(o.winnerAfterTwoFrames).sort((a, b) => b[1] - a[1])[0][0];
  const flips = out.live.slice(1).filter((v, i) => Math.sign(v) !== Math.sign(out.live[i]) && v !== 0 && out.live[i] !== 0).length;
  const conflictSummary = {
    detected: orders.every((o) => o.someOwnerIgnored),
    dominantWinnerByOrder: Object.fromEntries(Object.entries(conflict).map(([k, o]) => [k, w(o)])),
    orderDependent: w(orders[0]) !== w(orders[1]),
    liveSamples: out.live,
    liveSignFlips: flips,
  };
  return {
    pass: disjoint.pass && conflictSummary.detected,
    versions: out.info.versions,
    disjoint,
    conflict: { ...conflictSummary, byOrder: conflict },
    modules: out.info.modules,
  };
}

// ---------------------------------------------------------------------------------------------
// pixelfx sprite sheets: decode the PNG here (8-bit RGBA, non-interlaced) and check it against its JSON.
function decodeRGBA(buf) {
  if (buf.readUInt32BE(0) !== 0x89504e47) throw new Error('not a PNG');
  let off = 8, w = 0, h = 0, depth = 0, colorType = 0, interlace = 0;
  const idat = [];
  while (off < buf.length) {
    const len = buf.readUInt32BE(off), type = buf.toString('ascii', off + 4, off + 8), data = buf.subarray(off + 8, off + 8 + len);
    if (type === 'IHDR') { w = data.readUInt32BE(0); h = data.readUInt32BE(4); depth = data[8]; colorType = data[9]; interlace = data[12]; }
    else if (type === 'IDAT') idat.push(data);
    else if (type === 'IEND') break;
    off += 12 + len;
  }
  if (depth !== 8 || colorType !== 6 || interlace !== 0) return { w, h, colorType, depth, pixels: null };
  const raw = inflateSync(Buffer.concat(idat)), stride = w * 4, px = Buffer.alloc(stride * h);
  for (let y = 0; y < h; y++) {
    const f = raw[y * (stride + 1)], src = raw.subarray(y * (stride + 1) + 1, (y + 1) * (stride + 1)), row = y * stride;
    for (let x = 0; x < stride; x++) {
      const a = x >= 4 ? px[row + x - 4] : 0, b = y > 0 ? px[row - stride + x] : 0, c = x >= 4 && y > 0 ? px[row - stride + x - 4] : 0;
      let pred = 0;
      if (f === 1) pred = a; else if (f === 2) pred = b; else if (f === 3) pred = (a + b) >> 1;
      else if (f === 4) { const p = a + b - c, pa = Math.abs(p - a), pb = Math.abs(p - b), pc = Math.abs(p - c); pred = pa <= pb && pa <= pc ? a : pb <= pc ? b : c; }
      px[row + x] = (src[x] + pred) & 255;
    }
  }
  return { w, h, colorType, depth, pixels: px };
}

function verifySheet(pngPath, jsonPath) {
  const img = decodeRGBA(readFileSync(pngPath));
  const json = JSON.parse(readFileSync(jsonPath, 'utf8'));
  const res = { png: `${img.w}x${img.h}`, colorType: img.colorType, frames: json.frames.length, bytes: statSync(pngPath).size + statSync(jsonPath).size };
  res.hasAlphaChannel = img.colorType === 6;
  if (!img.pixels) return { ...res, pass: false, error: 'not 8-bit non-interlaced RGBA' };
  let transparent = 0, partial = 0, opaque = 0;
  for (let i = 3; i < img.pixels.length; i += 4) { const a = img.pixels[i]; if (a === 0) transparent++; else if (a === 255) opaque++; else partial++; }
  res.alpha = { transparent, partial, opaque };
  res.alphaUsed = transparent > 0 && partial + opaque > 0;
  res.metaSizeMatchesPng = json.meta.size.w === img.w && json.meta.size.h === img.h;
  res.rectsInsidePng = json.frames.every(({ frame: f }) => f.x >= 0 && f.y >= 0 && f.x + f.w <= img.w && f.y + f.h <= img.h);
  res.rectsDistinct = new Set(json.frames.map(({ frame: f }) => `${f.x},${f.y}`)).size === json.frames.length;
  res.rectsMatchFrameSize = json.frames.every(({ frame: f }) => f.w === json.meta.pixelfx.frameSize[0] && f.h === json.meta.pixelfx.frameSize[1]);
  res.frameCountMatchesMeta = json.frames.length === json.meta.pixelfx.frames;
  res.framesWithContent = json.frames.filter(({ frame: f }) => {
    for (let y = f.y; y < f.y + f.h; y++) for (let x = f.x; x < f.x + f.w; x++) if (img.pixels[(y * img.w + x) * 4 + 3]) return true;
    return false;
  }).length;
  res.pass = res.hasAlphaChannel && res.alphaUsed && res.metaSizeMatchesPng && res.rectsInsidePng && res.rectsDistinct
    && res.rectsMatchFrameSize && res.frameCountMatchesMeta && res.framesWithContent > 0;
  return res;
}

const PIXELFX_IDS = ['ice/frost-nova', 'ice/ice-lance'];
const COPY_LIMIT = 300 * 1024;
async function pixelfxSheet(previous) {
  const dest = join(OUT, 'pixelfx');
  const out = { upstream: 'https://github.com/patch-gg/pixelfx', license: 'MIT', command: 'node tools/render.mjs <id> --sheet --out <dir>' };
  if (PIXELFX_CLONE) {
    out.commit = execFileSync('git', ['-C', PIXELFX_CLONE, 'rev-parse', 'HEAD']).toString().trim();
    const work = mkdtempSync(join(tmpdir(), 'pixelfx-sheets-'));
    out.regenerated = {};
    try {
      for (const id of PIXELFX_IDS) {
        execFileSync(process.execPath, [join(PIXELFX_CLONE, 'tools', 'render.mjs'), id, '--sheet', '--out', work], { cwd: work, stdio: ['ignore', 'pipe', 'pipe'] });
        const name = id.split('/')[1], d = join(work, ...id.split('/'));
        const v = verifySheet(join(d, `${name}.png`), join(d, `${name}.json`));
        v.copied = v.bytes <= COPY_LIMIT;
        if (v.copied) { mkdirSync(dest, { recursive: true }); for (const ext of ['png', 'json']) copyFileSync(join(d, `${name}.${ext}`), join(dest, `${name}.${ext}`)); }
        out.regenerated[id] = v;
      }
    } finally { rmSync(work, { recursive: true, force: true }); }
  } else if (previous) {
    Object.assign(out, { commit: previous.commit, regenerated: previous.regenerated });
  }
  if (!existsSync(dest)) return { ...out, status: 'not run', pass: null, reason: 'No pixelfx clone given (--pixelfx) and no sheets in out/pixelfx/.' };
  out.committedCopies = {};
  for (const f of readdirSync(dest).filter((n) => n.endsWith('.png'))) {
    const name = f.slice(0, -4);
    out.committedCopies[name] = verifySheet(join(dest, f), join(dest, `${name}.json`));
  }
  const all = [...Object.values(out.regenerated || {}), ...Object.values(out.committedCopies)];
  out.pass = all.length > 0 && all.every((v) => v.pass);
  out.status = out.pass ? 'pass' : 'fail';
  return out;
}

// ---------------------------------------------------------------------------------------------
const CHECKS = { 'motion-seek': motionSeek, 'theatre-seek': theatreSeek, 'r3f-frameloop': r3fFrameloop, 'gsap-vs-motion-ownership': ownership };
const result = { fixture: 'expressive-motion', date: new Date().toISOString().slice(0, 10), fps: FPS, versions: VERSIONS, checks: {} };
const resultPath = join(OUT, 'result.json');
const previous = existsSync(resultPath) ? JSON.parse(readFileSync(resultPath, 'utf8')) : null;
try {
  for (const [name, fn] of Object.entries(CHECKS)) {
    if (ONLY && !ONLY.some((o) => name.includes(o))) { if (previous?.checks?.[name]) result.checks[name] = previous.checks[name]; continue; }
    try { result.checks[name] = await fn(); } catch (e) { result.checks[name] = { pass: false, error: String(e.stack || e).slice(0, 800) }; }
    console.log(`${result.checks[name].pass ? 'PASS' : 'FAIL'}  ${name}`);
  }
} finally { server.close(); }
// Optional: pixelfx sprite sheets. It counts toward the overall result only when it ran.
if (!ONLY || ONLY.includes('pixelfx')) {
  try { result.checks['pixelfx-sheet'] = await pixelfxSheet(previous?.checks?.['pixelfx-sheet']); } catch (e) { result.checks['pixelfx-sheet'] = { pass: false, status: 'fail', error: String(e.stack || e).slice(0, 800) }; }
  const st = result.checks['pixelfx-sheet'].status;
  console.log(`${st === 'pass' ? 'PASS' : st === 'fail' ? 'FAIL' : 'SKIP'}  pixelfx-sheet (optional)`);
} else if (previous?.checks?.['pixelfx-sheet']) result.checks['pixelfx-sheet'] = previous.checks['pixelfx-sheet'];
result.chrome = chrome ?? previous?.chrome ?? null;
const required = Object.keys(CHECKS);
result.pass = required.every((k) => result.checks[k]?.pass === true) && result.checks['pixelfx-sheet']?.pass !== false;
writeFileSync(resultPath, JSON.stringify(result, null, 2) + '\n');
console.log(result.pass ? 'ALL REQUIRED CHECKS PASS' : 'SOME CHECKS FAILED', '->', 'out/result.json');
process.exit(result.pass ? 0 : 1);
