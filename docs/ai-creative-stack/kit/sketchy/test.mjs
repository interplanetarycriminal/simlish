#!/usr/bin/env node
// Test for sketchy.mjs. Builds a demo sheet, checks determinism, fill containment and stroke
// bounds, then rasterizes the SVG in headless Chrome and checks that ink landed on the page.
//
//   node test.mjs        -> out/sheet.svg, out/sheet.png, out/result.json; exit 0 only on pass
import { mkdirSync, writeFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { createGenerator, toSvg, parsePath, strayBounds } from './sketchy.mjs';
import { serve, launch, open, evaluate, screenshot } from '../../fixtures/lib/cdp.mjs';

const HERE = dirname(fileURLToPath(import.meta.url));
const OUT = join(HERE, 'out');
mkdirSync(OUT, { recursive: true });

const W = 900, H = 560;
const STAR = Array.from({ length: 10 }, (_, k) => {
  const a = -Math.PI / 2 + (k * Math.PI) / 5, r = k % 2 ? 48 : 110;
  return [600 + r * Math.cos(a), 150 + r * Math.sin(a)];
});
const L_SHAPE = [[40, 330], [200, 330], [200, 400], [110, 400], [110, 520], [40, 520]];
const BLOB = 'M260 340 L400 330 Q470 420 400 520 C350 545 290 540 255 500 Z';
const REL = 'm560 340 l80 0 l0 60 h60 v80 h-140 z';

function sheet(seed) {
  const g = createGenerator(seed);
  return [
    g.line(40, 40, 360, 70, { roughness: 1.5 }),
    g.rectangle(40, 100, 300, 180, { fill: '#e0457b', fillStyle: 'hachure', hachureGap: 9 }),
    g.ellipse(430, 190, 120, 160, { fill: '#2a7de1', fillStyle: 'zigzag', hachureGap: 10 }),
    g.polygon(STAR, { fill: '#f2a516', fillStyle: 'hachure', hachureAngle: 30, hachureGap: 7 }),
    g.polygon(L_SHAPE, { fill: '#18a058', fillStyle: 'zigzag', hachureGap: 9, roughness: 2 }),
    g.path(BLOB, { fill: '#8a4fd8', fillStyle: 'hachure', hachureAngle: -20, hachureGap: 6 }),
    g.path(REL, { fill: '#d24d2c', fillStyle: 'hachure', hachureAngle: 75, hachureGap: 8 }),
    g.ellipse(800, 450, 130, 90, { roughness: 2.5 }),
  ];
}

// Independent reader for the generator's output: chunks of "M x y C x y x y x y".
function cubics(d) {
  const nums = (s) => s.trim().split(/[\s,]+/).map(Number);
  const out = [];
  for (const chunk of d.split('M').slice(1)) {
    const [head, ...cs] = chunk.split('C');
    let cur = nums(head);
    for (const c of cs) {
      const v = nums(c);
      out.push([cur, [v[0], v[1]], [v[2], v[3]], [v[4], v[5]]]);
      cur = [v[4], v[5]];
    }
  }
  return out;
}
const bez = (p0, c1, c2, p3, t) => {
  const u = 1 - t;
  return [0, 1].map((i) => u * u * u * p0[i] + 3 * u * u * t * c1[i] + 3 * u * t * t * c2[i] + t * t * t * p3[i]);
};
function inside(p, rings) {
  let c = false;
  for (const r of rings) for (let i = 0, j = r.length - 1; i < r.length; j = i++) {
    if ((r[i][1] > p[1]) !== (r[j][1] > p[1]) && p[0] < ((r[j][0] - r[i][0]) * (p[1] - r[i][1])) / (r[j][1] - r[i][1]) + r[i][0]) c = !c;
  }
  return c;
}
function segDist(p, a, b) {
  const dx = b[0] - a[0], dy = b[1] - a[1], L2 = dx * dx + dy * dy;
  const t = L2 ? Math.max(0, Math.min(1, ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / L2)) : 0;
  return Math.hypot(p[0] - a[0] - t * dx, p[1] - a[1] - t * dy);
}
// True regions, sampled finely and independently of the generator's own flattening.
function pathRings(d, steps = 64) {
  const rings = []; let ring = null, cur = [0, 0];
  for (const c of parsePath(d)) {
    if (c.cmd === 'M') { if (ring) rings.push(ring); ring = [c.pts[0]]; cur = c.pts[0]; }
    else if (c.cmd === 'L') { ring.push(c.pts[0]); cur = c.pts[0]; }
    else if (c.cmd === 'C') { for (let k = 1; k <= steps; k++) ring.push(bez(cur, ...c.pts, k / steps)); cur = c.pts[2]; }
    else if (c.cmd === 'Z') { rings.push(ring); ring = null; cur = c.pts[0]; }
  }
  if (ring) rings.push(ring);
  return rings;
}
const ellipseRing = (cx, cy, w, h) => Array.from({ length: 720 }, (_, k) => [cx + (w / 2) * Math.cos(k * Math.PI / 360), cy + (h / 2) * Math.sin(k * Math.PI / 360)]);

const result = { tool: 'sketchy', date: new Date().toISOString(), checks: {} };

// 1. Determinism.
const svgA = toSvg(sheet(42), { width: W, height: H });
const svgB = toSvg(sheet(42), { width: W, height: H });
const svgC = toSvg(sheet(43), { width: W, height: H });
result.checks.determinism = { pass: svgA === svgB && svgA !== svgC, sameSeedIdentical: svgA === svgB, otherSeedDiffers: svgA !== svgC, bytes: svgA.length };
writeFileSync(join(OUT, 'sheet.svg'), svgA);

// 2. Fill lines stay inside their shapes.
const shapes = sheet(42);
const regions = [null,
  [[[40, 100], [340, 100], [340, 280], [40, 280]]],
  [ellipseRing(430, 190, 120, 160)],
  [STAR], [L_SHAPE], pathRings(BLOB), pathRings(REL), null];
const fillReport = [];
let fillOk = true;
shapes.forEach((s, k) => {
  const fill = s.sets.find((x) => x.type === 'fill');
  if (!regions[k]) return;
  if (!fill) { fillOk = false; fillReport.push({ shape: k, error: 'no fill set' }); return; }
  const cs = cubics(fill.d);
  let samples = 0, outside = 0;
  for (const c of cs) for (let t = 0; t <= 1.0001; t += 1 / 32) { samples++; if (!inside(bez(...c, t), regions[k])) outside++; }
  fillReport.push({ shape: k, kind: s.shape, style: s.options.fillStyle, lines: cs.length, samples, outside });
  if (outside > 0 || cs.length < 5) fillOk = false;
});
result.checks.fillInside = { pass: fillOk, shapes: fillReport };

// 3. Strokes: two passes per segment, ends within the jitter bound, every point within the curve bound.
const g = createGenerator(9);
let worstEnd = 0, worstCurve = 0, strokeOk = true, cases = 0;
const segChecks = [];
for (const roughness of [0.5, 1, 2, 3]) {
  for (const [a, b] of [[[10, 10], [410, 30]], [[50, 300], [60, 40]], [[0, 0], [35, 20]], [[200, 200], [700, 520]]]) {
    const ln = g.line(a[0], a[1], b[0], b[1], { roughness, bowing: 1.5 });
    const cs = cubics(ln.sets.find((x) => x.type === 'stroke').d);
    const len = Math.hypot(b[0] - a[0], b[1] - a[1]);
    const bound = strayBounds(len, roughness, 1.5);
    if (cs.length !== 2) strokeOk = false;
    if (cs.length === 2 && JSON.stringify(cs[0]) === JSON.stringify(cs[1])) strokeOk = false;
    for (const c of cs) {
      const e = Math.max(Math.hypot(c[0][0] - a[0], c[0][1] - a[1]), Math.hypot(c[3][0] - b[0], c[3][1] - b[1]));
      let m = 0; for (let t = 0; t <= 1.0001; t += 1 / 64) m = Math.max(m, segDist(bez(...c, t), a, b));
      worstEnd = Math.max(worstEnd, e / bound.endpoint); worstCurve = Math.max(worstCurve, m / bound.curve);
      if (e > bound.endpoint + 0.01 || m > bound.curve + 0.01) strokeOk = false;
      cases++;
    }
  }
}
// Rectangle: 4 edges x 2 passes, each chunk near its own edge.
const rect = g.rectangle(100, 100, 240, 120, { roughness: 2 });
const rc = cubics(rect.sets.find((x) => x.type === 'stroke').d);
const corners = [[100, 100], [340, 100], [340, 220], [100, 220]];
rc.forEach((c, i) => {
  const a = corners[i % 4], b = corners[(i + 1) % 4];
  const bound = strayBounds(Math.hypot(b[0] - a[0], b[1] - a[1]), 2, 1);
  const e = Math.max(Math.hypot(c[0][0] - a[0], c[0][1] - a[1]), Math.hypot(c[3][0] - b[0], c[3][1] - b[1]));
  if (e > bound.endpoint + 0.01) strokeOk = false;
  segChecks.push(Number((e / bound.endpoint).toFixed(3)));
});
if (rc.length !== 8) strokeOk = false;
// Roughness 0 must reproduce the true geometry exactly.
const clean = cubics(g.line(5, 5, 105, 55, { roughness: 0 }).sets[0].d);
const cleanOk = clean.every((c) => c[0][0] === 5 && c[0][1] === 5 && c[3][0] === 105 && c[3][1] === 55);
result.checks.strokeBounds = { pass: strokeOk && cleanOk, strokes: cases, worstEndpointRatio: Number(worstEnd.toFixed(3)), worstCurveRatio: Number(worstCurve.toFixed(3)), rectangleChunks: rc.length, rectangleEndpointRatios: segChecks, roughnessZeroExact: cleanOk };

// 4. Path parser: relative commands and Q conversion.
const p = parsePath('m10 10 l20 0 h5 v5 q10 10 20 0 z');
const parseOk = p.length === 6 && p[1].pts[0][0] === 30 && p[2].pts[0][0] === 35 && p[3].pts[0][1] === 15 && p[4].cmd === 'C' && p[4].pts[2][0] === 55 && p[5].cmd === 'Z';
result.checks.pathParser = { pass: parseOk, commands: p.map((c) => c.cmd).join('') };

// 5. Rasterize in headless Chrome. The SVG is inlined as a data URL because the shared static
// server does not label .svg files as image/svg+xml.
writeFileSync(join(OUT, 'raster.html'), `<!doctype html><html><head><style>html,body{margin:0;background:#fff}</style></head><body>
<img id="s" src="data:image/svg+xml;base64,${Buffer.from(svgA).toString('base64')}" width="${W}" height="${H}" style="display:block">
<script>
const img = document.getElementById('s');
img.onload = () => {
  const c = document.createElement('canvas'); c.width = ${W}; c.height = ${H};
  const x = c.getContext('2d'); x.fillStyle = '#fff'; x.fillRect(0, 0, ${W}, ${H}); x.drawImage(img, 0, 0);
  const d = x.getImageData(0, 0, ${W}, ${H}).data;
  let ink = 0, pink = 0, blue = 0;
  for (let i = 0; i < d.length; i += 4) {
    const r = d[i], g = d[i + 1], b = d[i + 2];
    if (r + g + b < 700) ink++;
    if (r > 150 && g < 140 && b > 70 && b < 170) pink++;
    if (b > 150 && r < 120) blue++;
  }
  window.__ink = { ink: ink / (${W} * ${H}), pink, blue };
  window.__ready = true;
};
img.onerror = () => { window.__ink = { error: 'svg failed to load' }; window.__ready = true; };
</script></body></html>`);
const server = await serve(OUT);
const cdp = await launch(undefined, { width: W, height: H });
try {
  await open(cdp, `http://127.0.0.1:${server.address().port}/raster.html`);
  const ink = await evaluate(cdp, 'window.__ink');
  const png = await screenshot(cdp);
  writeFileSync(join(OUT, 'sheet.png'), png);
  result.checks.rasterize = { pass: !ink.error && ink.ink > 0.01 && ink.ink < 0.5 && ink.pink > 200 && ink.blue > 200, chrome: cdp.version, inkFraction: Number((ink.ink || 0).toFixed(4)), pinkPixels: ink.pink, bluePixels: ink.blue, pngBytes: png.length, error: ink.error };
} finally {
  await cdp.close();
  server.close();
}

result.pass = Object.values(result.checks).every((c) => c.pass);
writeFileSync(join(OUT, 'result.json'), JSON.stringify(result, null, 2) + '\n');
for (const [k, c] of Object.entries(result.checks)) console.log(`${c.pass ? 'PASS' : 'FAIL'}  ${k}`);
console.log(result.pass ? 'All checks passed' : 'Some checks failed');
process.exit(result.pass ? 0 : 1);
