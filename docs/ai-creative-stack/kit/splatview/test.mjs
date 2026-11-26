// Test for splatview: node kit/splatview/test.mjs
// Builds a synthetic splat scene and a textured test box, converts the box with mesh2splat,
// checks both PLY files directly, renders each in headless Chrome from 3 views and checks
// colours, background, counts and determinism. Writes out/result.json and out/contact_sheet.png.
import { spawnSync } from 'node:child_process';
import { createHash } from 'node:crypto';
import { existsSync, mkdirSync, readFileSync, rmSync, statSync, writeFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { deflateSync } from 'node:zlib';
import { evaluate, launch, open, serve } from '../../fixtures/lib/cdp.mjs';
import { parsePly, sortBackToFront } from './splatview.mjs';

const HERE = dirname(fileURLToPath(import.meta.url));
const OUT = join(HERE, 'out');
const PY = process.env.PYTHON || 'python';
const W = 640, H = 480;
const BG = [0x12, 0x12, 0x17];
const BOX_COUNT = 30000;
const failures = [];
const result = { pass: false, checks: {} };
const check = (ok, msg) => { if (!ok) failures.push(msg); return ok; };

mkdirSync(OUT, { recursive: true });

function py(args) {
  const r = spawnSync(PY, args, { cwd: HERE, encoding: 'utf8' });
  check(r.status === 0, `python ${args.join(' ')} exited ${r.status}: ${(r.stderr || '').slice(-400)}`);
  return r;
}

// ---- independent PLY reader (header + float body), not shared with the viewer ----
function readPly(path) {
  const buf = readFileSync(path);
  const end = buf.indexOf('end_header\n') + 'end_header\n'.length;
  const header = buf.subarray(0, end).toString('ascii').split('\n');
  let count = 0; const fields = []; let format = '';
  for (const line of header) {
    const p = line.split(' ');
    if (p[0] === 'format') format = p[1];
    if (p[0] === 'element' && p[1] === 'vertex') count = Number(p[2]);
    if (p[0] === 'property') fields.push({ type: p[1], name: p[2] });
  }
  const stride = fields.length * 4;
  const body = new Float32Array(buf.buffer.slice(buf.byteOffset + end, buf.byteOffset + end + count * stride));
  const col = (name) => { const k = fields.findIndex((f) => f.name === name); const a = new Float32Array(count); for (let i = 0; i < count; i++) a[i] = body[i * fields.length + k]; return a; };
  return { count, format, fields, stride, headerBytes: end, fileBytes: buf.length, col };
}

const EXPECT_FIELDS = 'x y z nx ny nz f_dc_0 f_dc_1 f_dc_2 opacity scale_0 scale_1 scale_2 rot_0 rot_1 rot_2 rot_3';
const C0 = 0.28209479177387814;

function checkPlyFormat(tag, ply, expectedCount) {
  const names = ply.fields.map((f) => f.name).join(' ');
  check(ply.format === 'binary_little_endian', `${tag}: format ${ply.format}`);
  check(names === EXPECT_FIELDS, `${tag}: fields "${names}"`);
  check(ply.fields.every((f) => f.type === 'float'), `${tag}: non-float property`);
  check(ply.fileBytes === ply.headerBytes + ply.count * 68, `${tag}: file size ${ply.fileBytes} != header + ${ply.count} * 68`);
  if (expectedCount !== undefined) check(ply.count === expectedCount, `${tag}: count ${ply.count} != ${expectedCount}`);
  const op = ply.col('opacity'), q = [0, 1, 2, 3].map((i) => ply.col(`rot_${i}`)), s = [0, 1, 2].map((i) => ply.col(`scale_${i}`));
  let qErr = 0, thinOk = 0, opMin = 1, opMax = 0;
  for (let i = 0; i < ply.count; i++) {
    qErr = Math.max(qErr, Math.abs(Math.hypot(q[0][i], q[1][i], q[2][i], q[3][i]) - 1));
    if (s[2][i] < Math.min(s[0][i], s[1][i])) thinOk++;
    const o = 1 / (1 + Math.exp(-op[i])); opMin = Math.min(opMin, o); opMax = Math.max(opMax, o);
  }
  check(qErr < 1e-4, `${tag}: quaternion norm error ${qErr}`);
  check(thinOk === ply.count, `${tag}: ${ply.count - thinOk} splats whose third axis is not the thinnest`);
  return { count: ply.count, quatNormErr: qErr, opacity: [opMin, opMax] };
}

// rotate local axis 3 (column 2 of R) and compare with stored normal
function normalAlignment(ply) {
  const q = [0, 1, 2, 3].map((i) => ply.col(`rot_${i}`)), n = ['nx', 'ny', 'nz'].map((k) => ply.col(k));
  let worst = 1;
  for (let i = 0; i < ply.count; i++) {
    const [w, x, y, z] = [q[0][i], q[1][i], q[2][i], q[3][i]];
    const ax = [2 * (x * z + w * y), 2 * (y * z - w * x), 1 - 2 * (x * x + y * y)];
    worst = Math.min(worst, Math.abs(ax[0] * n[0][i] + ax[1] * n[1][i] + ax[2] * n[2][i]));
  }
  return worst;
}

// ---- pixel helpers ----
function classify(r, g, b) {
  if (r > 150 && g > 150 && b < 90) return 'yellow';
  if (r > 150 && g < 90 && b < 90) return 'red';
  if (g > 140 && r < 90 && b < 110) return 'green';
  if (b > 150 && r < 90 && g < 110) return 'blue';
  return null;
}
const isBg = (r, g, b) => Math.abs(r - BG[0]) <= 2 && Math.abs(g - BG[1]) <= 2 && Math.abs(b - BG[2]) <= 2;

async function grab(cdp) {
  const p = await evaluate(cdp, 'window.__splat.pixelsBase64()');
  return { width: p.width, height: p.height, data: Buffer.from(p.data, 'base64') };
}
const px = (img, x, y) => { const i = (y * img.width + x) * 4; return [img.data[i], img.data[i + 1], img.data[i + 2]]; };

function diskFraction(img, cx, cy, r, pred) {
  let n = 0, hit = 0;
  for (let y = Math.floor(cy - r); y <= Math.ceil(cy + r); y++) {
    for (let x = Math.floor(cx - r); x <= Math.ceil(cx + r); x++) {
      if (x < 0 || y < 0 || x >= img.width || y >= img.height || (x - cx) ** 2 + (y - cy) ** 2 > r * r) continue;
      n++; if (pred(...px(img, x, y))) hit++;
    }
  }
  return n ? hit / n : 0;
}

async function screenBox(cdp, bounds, pad) {
  const { min, max } = bounds;
  let x0 = Infinity, y0 = Infinity, x1 = -Infinity, y1 = -Infinity;
  for (const cx of [min[0], max[0]]) for (const cy of [min[1], max[1]]) for (const cz of [min[2], max[2]]) {
    const p = await evaluate(cdp, `window.__splat.project(${cx}, ${cy}, ${cz})`);
    x0 = Math.min(x0, p.x); y0 = Math.min(y0, p.y); x1 = Math.max(x1, p.x); y1 = Math.max(y1, p.y);
  }
  return [x0 - pad, y0 - pad, x1 + pad, y1 + pad];
}

function outsideBackground(img, box) {
  let n = 0, bg = 0;
  for (let y = 0; y < img.height; y++) for (let x = 0; x < img.width; x++) {
    if (x >= box[0] && x <= box[2] && y >= box[1] && y <= box[3]) continue;
    n++; if (isBg(...px(img, x, y))) bg++;
  }
  return { pixels: n, fraction: n ? bg / n : 1 };
}

function colourCounts(img) {
  const c = { red: 0, green: 0, blue: 0, yellow: 0 };
  for (let i = 0; i < img.width * img.height; i++) { const k = classify(img.data[i * 4], img.data[i * 4 + 1], img.data[i * 4 + 2]); if (k) c[k]++; }
  return c;
}
const hash = (img) => createHash('sha256').update(img.data).digest('hex').slice(0, 16);

// ---- minimal PNG encoder for the contact sheet ----
function crc32(buf) {
  let c, crc = 0xffffffff;
  for (let n = 0; n < buf.length; n++) { c = (crc ^ buf[n]) & 0xff; for (let k = 0; k < 8; k++) c = c & 1 ? 0xedb88320 ^ (c >>> 1) : c >>> 1; crc = (crc >>> 8) ^ c; }
  return (crc ^ 0xffffffff) >>> 0;
}
function chunk(type, data) {
  const len = Buffer.alloc(4); len.writeUInt32BE(data.length);
  const td = Buffer.concat([Buffer.from(type, 'ascii'), data]);
  const crc = Buffer.alloc(4); crc.writeUInt32BE(crc32(td));
  return Buffer.concat([len, td, crc]);
}
function encodePng(width, height, rgb) {
  const raw = Buffer.alloc((width * 3 + 1) * height);
  for (let y = 0; y < height; y++) { raw[y * (width * 3 + 1)] = 0; rgb.copy(raw, y * (width * 3 + 1) + 1, y * width * 3, (y + 1) * width * 3); }
  const ihdr = Buffer.alloc(13); ihdr.writeUInt32BE(width, 0); ihdr.writeUInt32BE(height, 4); ihdr[8] = 8; ihdr[9] = 2;
  return Buffer.concat([Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]), chunk('IHDR', ihdr), chunk('IDAT', deflateSync(raw, { level: 9 })), chunk('IEND', Buffer.alloc(0))]);
}
function contactSheet(rows, scale = 2) {
  const cw = W / scale, ch = H / scale, gap = 4;
  const cols = Math.max(...rows.map((r) => r.length));
  const width = cols * cw + (cols + 1) * gap, height = rows.length * ch + (rows.length + 1) * gap;
  const rgb = Buffer.alloc(width * height * 3, 40);
  rows.forEach((row, ri) => row.forEach((img, ci) => {
    for (let y = 0; y < ch; y++) for (let x = 0; x < cw; x++) {
      const acc = [0, 0, 0];
      for (let dy = 0; dy < scale; dy++) for (let dx = 0; dx < scale; dx++) { const p = px(img, x * scale + dx, y * scale + dy); acc[0] += p[0]; acc[1] += p[1]; acc[2] += p[2]; }
      const o = ((gap + ri * (ch + gap) + y) * width + gap + ci * (cw + gap) + x) * 3;
      for (let k = 0; k < 3; k++) rgb[o + k] = Math.round(acc[k] / (scale * scale));
    }
  }));
  return encodePng(width, height, rgb);
}

// ================= run =================
const t0 = Date.now();

// unit check of the depth sort: a permutation, back to front, and repeatable with reused scratch
{
  let seed = 12345; const rnd = () => ((seed = (seed * 1103515245 + 12345) >>> 0) / 4294967296);
  const n = 20000, center = new Float32Array(n * 3);
  for (let i = 0; i < n * 3; i++) center[i] = rnd() * 10 - 5;
  const scratch = {}, order = new Uint32Array(n);
  const rows = [[0.3, -0.2, -0.93, 1.5], [-0.8, 0.1, 0.59, -2], [0.3, -0.2, -0.93, 1.5]];
  const runs = rows.map((r) => Array.from(sortBackToFront(center, n, r, order, scratch)));
  const r0 = rows[0];
  const depth = (i) => -(r0[0] * center[i * 3] + r0[1] * center[i * 3 + 1] + r0[2] * center[i * 3 + 2] + r0[3]);
  const perm = new Set(runs[0]).size === n;
  let maxInversion = 0;
  for (let i = 1; i < n; i++) maxInversion = Math.max(maxInversion, depth(runs[0][i]) - depth(runs[0][i - 1]));
  const repeat = runs[0].every((v, i) => v === runs[2][i]);
  result.checks.sort_unit = { n, permutation: perm, max_inversion: maxInversion, repeatable: repeat };
  check(perm, 'sort: output is not a permutation');
  check(maxInversion < 20 / 65535 * 2, `sort: depth inversion ${maxInversion}`);
  check(repeat, 'sort: same view gave a different order after another view');
}
py(['synth.py', join('out', 'synth.ply')]);
py(['make_test_box.py', join('out', 'box.glb')]);
const m2s = py(['mesh2splat.py', join('out', 'box.glb'), join('out', 'box.ply'), '--count', String(BOX_COUNT), '--seed', '1']);
py(['mesh2splat.py', join('out', 'box.glb'), join('out', 'box_again.ply'), '--count', String(BOX_COUNT), '--seed', '1']);

const synthMeta = JSON.parse(readFileSync(join(OUT, 'synth.json'), 'utf8'));
const boxMeta = JSON.parse(readFileSync(join(OUT, 'box.json'), 'utf8'));
const synthPly = readPly(join(OUT, 'synth.ply'));
{ const b = readFileSync(join(OUT, 'synth.ply')); const p = parsePly(b.buffer.slice(b.byteOffset, b.byteOffset + b.length)); check(p.count === synthPly.count && p.fields.length === 17, 'parsePly disagrees with the header'); }
const boxPly = readPly(join(OUT, 'box.ply'));
result.checks.synth_ply = checkPlyFormat('synth.ply', synthPly, synthMeta.count);
result.checks.box_ply = checkPlyFormat('box.ply', boxPly, BOX_COUNT);
result.checks.box_ply.mesh2splat_stdout = JSON.parse(m2s.stdout.trim().split('\n').pop() || '{}');
check(readFileSync(join(OUT, 'box.ply')).equals(readFileSync(join(OUT, 'box_again.ply'))), 'mesh2splat: same seed gave different files');
rmSync(join(OUT, 'box_again.ply'), { force: true });

// vertex-coloured input: red upper half, blue lower half
py(['make_test_box.py', '--vertex-sphere', join('out', 'vc_sphere.glb')]);
py(['mesh2splat.py', join('out', 'vc_sphere.glb'), join('out', 'vc_sphere.ply'), '--count', '5000']);
{
  const vc = readPly(join(OUT, 'vc_sphere.ply'));
  result.checks.vertex_colour_ply = checkPlyFormat('vc_sphere.ply', vc, 5000);
  const y = vc.col('y'), dc = [0, 1, 2].map((i) => vc.col(`f_dc_${i}`));
  let ok = 0, n = 0;
  for (let i = 0; i < vc.count; i++) {
    if (Math.abs(y[i]) < 0.12) continue;
    const k = classify(...dc.map((d) => Math.round((0.5 + C0 * d[i]) * 255)));
    n++; if (k === (y[i] > 0 ? 'red' : 'blue')) ok++;
  }
  result.checks.vertex_colour_ply.share_correct = ok / n;
  check(ok / n > 0.98, `vertex colours: only ${(ok / n).toFixed(3)} of samples match`);
  rmSync(join(OUT, 'vc_sphere.ply'), { force: true });
}

// box PLY content: texture colours by quadrant on the +Z face, normals, opacity
{
  const x = boxPly.col('x'), y = boxPly.col('y'), z = boxPly.col('z');
  const dc = [0, 1, 2].map((i) => boxPly.col(`f_dc_${i}`));
  const hz = boxMeta.half_extents[2];
  const quads = { 'x<0,y>0': (a, b) => a < -0.1 && b > 0.1, 'x>0,y>0': (a, b) => a > 0.1 && b > 0.1, 'x<0,y<0': (a, b) => a < -0.1 && b < -0.1, 'x>0,y<0': (a, b) => a > 0.1 && b < -0.1 };
  const q = {};
  for (const [name, f] of Object.entries(quads)) {
    const tally = {}; let n = 0;
    for (let i = 0; i < boxPly.count; i++) {
      if (Math.abs(z[i] - hz) > 1e-4 || !f(x[i], y[i])) continue;
      const rgb = dc.map((d) => Math.round((0.5 + C0 * d[i]) * 255));
      const k = classify(...rgb) || 'other'; tally[k] = (tally[k] || 0) + 1; n++;
    }
    const want = boxMeta.plus_z_quadrants[name];
    q[name] = { want, n, share: n ? (tally[want] || 0) / n : 0 };
    check(n > 50 && q[name].share > 0.97, `box.ply +Z quadrant ${name}: ${want} share ${q[name].share.toFixed(3)} of ${n}`);
  }
  result.checks.box_ply.plus_z_quadrants = q;
  const align = normalAlignment(boxPly);
  result.checks.box_ply.min_thin_axis_dot_normal = align;
  check(align > 0.999, `box.ply: thin axis not along the normal (min |dot| ${align})`);
  const op = result.checks.box_ply.opacity;
  check(Math.abs(op[0] - 0.9) < 1e-3 && Math.abs(op[1] - 0.9) < 1e-3, `box.ply: opacity range ${op}`);
}

// ---- render ----
const server = await serve(HERE);
const base = `http://127.0.0.1:${server.address().port}`;
const cdp = await launch(undefined, { width: W, height: H });
result.chrome = cdp.version;
const sheetRows = [];
try {
  // synthetic scene
  await open(cdp, `${base}/viewer.html?file=out/synth.ply&hud=0&dpr=1`);
  const err = await evaluate(cdp, 'window.__error || null');
  check(!err, `viewer error: ${err}`);
  const st = await evaluate(cdp, 'window.__splat.stats()');
  check(st.count === synthPly.count, `viewer count ${st.count} != file ${synthPly.count}`);
  check(st.width === W && st.height === H, `canvas ${st.width}x${st.height}`);
  result.checks.synth_viewer = { count: st.count, bounds: st.bounds, views: [] };
  const views = [[0, 18, 7], [40, 32, 7.5], [-35, 12, 6.5]];
  const synthImgs = [];
  for (const [az, el, dist] of views) {
    await evaluate(cdp, `window.__splat.setView(${az}, ${el}, ${dist})`);
    const img = await grab(cdp);
    synthImgs.push(img);
    const v = { az, el, dist, spheres: {} };
    for (const sp of synthMeta.spheres) {
      const p = await evaluate(cdp, `window.__splat.project(${sp.center.join(',')})`);
      const r = sp.radius * p.pxPerUnit;
      const share = diskFraction(img, p.x, p.y, 0.5 * r, (a, b, c) => classify(a, b, c) === sp.name);
      const holes = diskFraction(img, p.x, p.y, 0.5 * r, isBg);
      v.spheres[sp.name] = { x: Math.round(p.x), y: Math.round(p.y), radius_px: +r.toFixed(1), share: +share.toFixed(3), holes: +holes.toFixed(4) };
      check(share > 0.85, `synth view ${az}/${el}: ${sp.name} sphere share ${share.toFixed(3)} at (${p.x.toFixed(0)}, ${p.y.toFixed(0)})`);
      check(holes < 0.01, `synth view ${az}/${el}: ${sp.name} sphere has background showing through (${holes.toFixed(3)})`);
    }
    const sb = await screenBox(cdp, st.bounds, 6);
    const ob = outsideBackground(img, sb);
    v.outside = { box: sb.map(Math.round), pixels: ob.pixels, background_fraction: +ob.fraction.toFixed(5) };
    check(ob.pixels > 0.2 * W * H, `synth view ${az}/${el}: too little area outside the scene to test`);
    check(ob.fraction > 0.999, `synth view ${az}/${el}: background outside the scene is ${ob.fraction}`);
    const counts = colourCounts(img);
    v.colour_pixels = counts;
    let torusPx = 0;
    for (let i = 0; i < W * H; i++) { const r = img.data[i * 4], g = img.data[i * 4 + 1], b = img.data[i * 4 + 2]; if (!isBg(r, g, b) && !['red', 'green', 'blue'].includes(classify(r, g, b))) torusPx++; }
    v.torus_pixels = torusPx;
    check(torusPx > 0.01 * W * H, `synth view ${az}/${el}: torus covers only ${torusPx} pixels`);
    result.checks.synth_viewer.views.push(v);
  }
  // determinism: back to view 0 after other views
  await evaluate(cdp, `window.__splat.setView(${views[0].join(',')})`);
  const again = await grab(cdp);
  const det = hash(again) === hash(synthImgs[0]);
  result.checks.synth_viewer.deterministic = det;
  result.checks.synth_viewer.hashes = synthImgs.map(hash);
  check(det, 'synth: re-rendering view 0 gave different pixels');
  check(new Set(synthImgs.map(hash)).size === 3, 'synth: different views gave identical images');
  sheetRows.push(synthImgs);

  // mesh2splat box
  await open(cdp, `${base}/viewer.html?file=out/box.ply&hud=0&dpr=1`);
  const bst = await evaluate(cdp, 'window.__splat.stats()');
  check(bst.count === boxPly.count, `box viewer count ${bst.count} != file ${boxPly.count}`);
  result.checks.box_viewer = { count: bst.count, views: [] };
  const bviews = [[25, 20, 4.2], [140, 35, 4.2], [-110, -25, 4.2]];
  const boxImgs = [];
  for (const [az, el, dist] of bviews) {
    await evaluate(cdp, `window.__splat.setView(${az}, ${el}, ${dist})`);
    const img = await grab(cdp);
    boxImgs.push(img);
    const counts = colourCounts(img);
    const sb = await screenBox(cdp, bst.bounds, 6);
    const ob = outsideBackground(img, sb);
    const v = { az, el, dist, colour_pixels: counts, outside_background_fraction: +ob.fraction.toFixed(5) };
    for (const k of ['red', 'green', 'blue', 'yellow']) check(counts[k] > 0.005 * W * H, `box view ${az}/${el}: too few ${k} pixels (${counts[k]})`);
    check(ob.fraction > 0.999, `box view ${az}/${el}: background outside the box is ${ob.fraction}`);
    if (az === 25) {
      // the +Z face faces this camera: each quadrant centre must show its texture colour
      v.plus_z = {};
      const hx = boxMeta.half_extents[0] / 2, hy = boxMeta.half_extents[1] / 2, hz = boxMeta.half_extents[2];
      const pts = { 'x<0,y>0': [-hx, hy], 'x>0,y>0': [hx, hy], 'x<0,y<0': [-hx, -hy], 'x>0,y<0': [hx, -hy] };
      for (const [name, [qx, qy]] of Object.entries(pts)) {
        const p = await evaluate(cdp, `window.__splat.project(${qx}, ${qy}, ${hz})`);
        const share = diskFraction(img, p.x, p.y, 0.08 * p.pxPerUnit, (a, b, c) => classify(a, b, c) === boxMeta.plus_z_quadrants[name]);
        v.plus_z[name] = { want: boxMeta.plus_z_quadrants[name], share: +share.toFixed(3) };
        check(share > 0.95, `box +Z quadrant ${name} on screen: ${boxMeta.plus_z_quadrants[name]} share ${share.toFixed(3)}`);
      }
    }
    result.checks.box_viewer.views.push(v);
  }
  await evaluate(cdp, `window.__splat.setView(${bviews[0].join(',')})`);
  const bagain = await grab(cdp);
  { let d = 0, mx = 0; for (let i = 0; i < bagain.data.length; i++) { const e = Math.abs(bagain.data[i] - boxImgs[0].data[i]); if (e) { d++; mx = Math.max(mx, e); } } result.checks.box_viewer.rerender_diff = { bytes: d, max: mx }; }
  result.checks.box_viewer.deterministic = hash(bagain) === hash(boxImgs[0]);
  check(result.checks.box_viewer.deterministic, 'box: re-rendering view 0 gave different pixels');
  result.checks.box_viewer.sort_ms = (await evaluate(cdp, 'window.__splat.stats()')).lastSortMs;
  sheetRows.push(boxImgs);

  writeFileSync(join(OUT, 'contact_sheet.png'), contactSheet(sheetRows));
} catch (e) {
  failures.push(`exception: ${e.stack || e}`);
} finally {
  await cdp.close();
  server.close();
}

// keep out/ small: PLY files are regenerated by the test
for (const f of ['synth.ply', 'box.ply']) if (existsSync(join(OUT, f))) { result[`${f}_bytes`] = statSync(join(OUT, f)).size; rmSync(join(OUT, f)); }

result.pass = failures.length === 0;
result.failures = failures;
result.seconds = (Date.now() - t0) / 1000;
writeFileSync(join(OUT, 'result.json'), JSON.stringify(result, null, 2));
console.log(JSON.stringify({ pass: result.pass, failures, seconds: result.seconds }, null, 2));
process.exit(result.pass ? 0 : 1);
