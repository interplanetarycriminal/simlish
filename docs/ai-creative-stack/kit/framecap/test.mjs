#!/usr/bin/env node
// Test for framecap. Builds its own pages and audio, runs the CLI, and checks the decoded output.
//
//   node test.mjs   -> out/*.mp4, out/*.mov, out/result.json; exit 0 only on pass
//
// (a) CSS-only animation: a box slides left to right over 2 s; the decoded box position in every
//     frame must match the linear path within 2 px.
// (b) --alpha: ProRes 4444 .mov and a PNG sequence; alpha present, corners transparent, subject opaque.
// (c) --audio: a generated 2 s sine is muxed; the audio stream exists with the right duration.
// (d) Time contract: a canvas page with window.__scene.seek(t) is driven frame by frame.
import { execFileSync, spawnSync } from 'node:child_process';
import { existsSync, mkdirSync, readdirSync, readFileSync, rmSync, statSync, writeFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const HERE = dirname(fileURLToPath(import.meta.url));
const OUT = join(HERE, 'out');
const PAGES = join(OUT, 'pages');
if (existsSync(OUT)) for (const f of readdirSync(OUT)) rmSync(join(OUT, f), { recursive: true, force: true });
mkdirSync(PAGES, { recursive: true });

const result = { tool: 'framecap', date: new Date().toISOString(), checks: {} };

function framecap(args) {
  const r = spawnSync(process.execPath, [join(HERE, 'framecap.mjs'), ...args], { cwd: HERE, encoding: 'utf8' });
  if (r.status !== 0) throw new Error(`framecap failed (${r.status}): ${r.stdout}\n${r.stderr}`);
  return JSON.parse(readFileSync(`${args[args.indexOf('--out') + 1]}.report.json`, 'utf8'));
}
// Decode a video (or image pattern) to raw pixels with FFmpeg.
function decode(file, pixFmt, extra = []) {
  return execFileSync('ffmpeg', ['-hide_banner', '-loglevel', 'error', ...extra, '-i', file, '-f', 'rawvideo', '-pix_fmt', pixFmt, '-'], { maxBuffer: 1 << 30 });
}
async function check(name, fn) {
  try { result.checks[name] = await fn(); } catch (e) { result.checks[name] = { pass: false, error: String(e.stack || e) }; }
  console.log(`${result.checks[name].pass ? 'PASS' : 'FAIL'}  ${name}`);
}

// ---------- (a) CSS animation, position accuracy ----------
writeFileSync(join(PAGES, 'css-box.html'), `<!doctype html><html><head><style>
html, body { margin: 0; width: 1280px; height: 720px; background: #fff; overflow: hidden; }
.box { position: absolute; left: 0; top: 310px; width: 100px; height: 100px; background: rgb(230, 20, 20);
       animation: slide 2s linear forwards; }
@keyframes slide { from { transform: translateX(0px); } to { transform: translateX(1180px); } }
</style></head><body><div class="box"></div></body></html>`);

await check('cssPosition', async () => {
  const out = join(OUT, 'css-box.mp4');
  const rep = framecap([join(PAGES, 'css-box.html'), '--duration', '2', '--fps', '30', '--size', '1280x720', '--out', out]);
  const W = 1280, H = 720, fps = 30;
  const raw = decode(out, 'rgb24');
  const n = raw.length / (W * H * 3);
  let worst = 0; const samples = [];
  for (let i = 0; i < n; i++) {
    // Redness-weighted centroid along three rows through the box. Robust to anti-aliasing and chroma blur.
    let sw = 0, sx = 0;
    for (const y of [330, 360, 390]) {
      for (let x = 0; x < W; x++) {
        const o = ((i * H + y) * W + x) * 3;
        const red = Math.max(0, raw[o] - (raw[o + 1] + raw[o + 2]) / 2) / 255;
        if (red > 0.2) { sw += red; sx += red * x; }
      }
    }
    const measured = sx / sw + 0.5; // pixel centers are at x + 0.5
    const expected = 50 + 1180 * Math.min(1, i / fps / 2);
    const err = Math.abs(measured - expected);
    worst = Math.max(worst, err);
    if (i % 10 === 0 || i === n - 1) samples.push({ frame: i, expected: Number(expected.toFixed(2)), measured: Number(measured.toFixed(2)) });
  }
  return { pass: rep.pass && rep.mode === 'animations' && n === 60 && worst <= 2, framecapChecks: rep.checks, mode: rep.mode, animations: rep.animations, frames: n, worstErrorPx: Number(worst.toFixed(3)), samples, mp4Bytes: statSync(out).size, captureSeconds: rep.captureSeconds };
});

// ---------- (b) alpha ----------
writeFileSync(join(PAGES, 'alpha.html'), `<!doctype html><html><head><style>
html, body { margin: 0; background: transparent; overflow: hidden; }
.dot { position: absolute; left: 110px; top: 70px; width: 100px; height: 100px; border-radius: 50%;
       background: rgb(30, 200, 90); animation: pulse 1s ease-in-out infinite alternate; }
@keyframes pulse { from { transform: scale(0.6); opacity: 1; } to { transform: scale(1); opacity: 0.5; } }
</style></head><body><div class="dot"></div></body></html>`);

function alphaStats(rgba, W, H, frames) {
  const corner = [], center = [];
  for (let i = 0; i < frames; i++) {
    const a = (x, y) => rgba[((i * H + y) * W + x) * 4 + 3];
    corner.push(Math.max(a(0, 0), a(W - 1, 0), a(0, H - 1), a(W - 1, H - 1), a(5, 5), a(W - 6, H - 6)));
    center.push(a(160, 120));
  }
  return { maxCornerAlpha: Math.max(...corner), centerAlphaFirst: center[0], centerAlphaLast: center[frames - 1] };
}

await check('alphaMov', async () => {
  const out = join(OUT, 'alpha.mov');
  const rep = framecap([join(PAGES, 'alpha.html'), '--duration', '1', '--fps', '12', '--size', '320x240', '--alpha', '--out', out]);
  const st = alphaStats(decode(out, 'rgba'), 320, 240, 12);
  const ok = rep.pass && /yuva/.test(rep.probe.pix_fmt) && st.maxCornerAlpha === 0 && st.centerAlphaFirst > 240 && st.centerAlphaLast > 100 && st.centerAlphaLast < 160;
  const bytes = statSync(out).size;
  const res = { pass: ok, framecapChecks: rep.checks, codec: rep.probe.codec, pix_fmt: rep.probe.pix_fmt, ...st, movBytes: bytes };
  if (bytes > 1.2e6) { rmSync(out); res.note = 'mov deleted after checking to keep out/ small'; }
  return res;
});

await check('alphaPng', async () => {
  const out = join(OUT, 'alpha-png');
  const rep = framecap([join(PAGES, 'alpha.html'), '--duration', '0.5', '--fps', '12', '--size', '320x240', '--alpha', '--format', 'png', '--out', out]);
  const files = readdirSync(out).filter((f) => f.endsWith('.png'));
  const st = alphaStats(decode(join(out, 'f%05d.png'), 'rgba', ['-framerate', '12']), 320, 240, files.length);
  // Keep one frame as a sample.
  for (const f of files.slice(1)) rmSync(join(out, f));
  return { pass: rep.pass && files.length === 6 && rep.probe.colorType === 6 && st.maxCornerAlpha === 0 && st.centerAlphaFirst > 240, framecapChecks: rep.checks, frames: files.length, pngColorType: rep.probe.colorType, ...st };
});

// ---------- (c) audio mux ----------
await check('audioMux', async () => {
  const wav = join(OUT, 'sine-2s.wav');
  execFileSync('ffmpeg', ['-hide_banner', '-loglevel', 'error', '-y', '-f', 'lavfi', '-i', 'sine=frequency=440:sample_rate=48000:duration=2', '-c:a', 'pcm_s16le', wav]);
  const out = join(OUT, 'css-box-audio.mp4');
  const rep = framecap([join(PAGES, 'css-box.html'), '--duration', '2', '--fps', '30', '--size', '640x360', '--audio', wav, '--out', out]);
  const pcm = execFileSync('ffmpeg', ['-hide_banner', '-loglevel', 'error', '-i', out, '-map', '0:a', '-f', 'f32le', '-ac', '1', '-ar', '48000', '-'], { maxBuffer: 1 << 28 });
  const s = new Float32Array(pcm.buffer, pcm.byteOffset, pcm.length / 4);
  let sum = 0; for (const x of s) sum += x * x;
  const rms = Math.sqrt(sum / s.length);
  rmSync(wav);
  const a = rep.probe.audio;
  return { pass: rep.pass && !!a && Math.abs(a.duration - 2) <= 1 / 30 && rms > 0.05, framecapChecks: rep.checks, audio: a, decodedSeconds: s.length / 48000, rms: Number(rms.toFixed(4)) };
});

// ---------- (d) time contract page ----------
writeFileSync(join(PAGES, 'scene.html'), `<!doctype html><html><head><style>html,body{margin:0;background:#000}</style></head><body>
<canvas id="c" width="640" height="360"></canvas>
<script>
window.__ready = false;
const ctx = document.getElementById('c').getContext('2d');
// State is a pure function of t: a white bar at x = 100 + 300 t.
window.__scene = { duration: 1, seek(t) { ctx.fillStyle = '#000'; ctx.fillRect(0, 0, 640, 360); ctx.fillStyle = '#fff'; ctx.fillRect(Math.round(100 + 300 * t) - 5, 0, 10, 360); }, digest() { return '' } };
setTimeout(() => { window.__ready = true; }, 300); // pretend to load something
</script></body></html>`);

await check('timeContract', async () => {
  const out = join(OUT, 'scene.mp4');
  const rep = framecap([join(PAGES, 'scene.html'), '--duration', '1', '--fps', '24', '--size', '640x360', '--out', out]);
  const raw = decode(out, 'gray');
  const W = 640, H = 360, n = raw.length / (W * H);
  let worst = 0;
  for (let i = 0; i < n; i++) {
    let sw = 0, sx = 0;
    for (let x = 0; x < W; x++) { const v = raw[(i * H + 180) * W + x] / 255; if (v > 0.3) { sw += v; sx += v * x; } }
    worst = Math.max(worst, Math.abs(sx / sw + 0.5 - Math.round(100 + 300 * i / 24)));
  }
  return { pass: rep.pass && rep.mode === 'scene' && n === 24 && worst <= 1, mode: rep.mode, frames: n, worstErrorPx: Number(worst.toFixed(3)), framecapChecks: rep.checks };
});

// ---------- (e) GSAP timeline ----------
writeFileSync(join(PAGES, 'gsap.html'), `<!doctype html><html><head><style>
html, body { margin: 0; background: #000; overflow: hidden; }
.bar { position: absolute; left: 0; top: 160px; width: 40px; height: 40px; background: #fff; }
</style><script src="https://cdn.jsdelivr.net/npm/gsap@3.13.0/dist/gsap.min.js"></script></head>
<body><div class="bar"></div><script>
gsap.fromTo('.bar', { x: 80 }, { x: 380, duration: 1, ease: 'none' });
</script></body></html>`);

await check('gsapTimeline', async () => {
  const out = join(OUT, 'gsap.mp4');
  const rep = framecap([join(PAGES, 'gsap.html'), '--duration', '1', '--fps', '24', '--size', '640x360', '--out', out]);
  const raw = decode(out, 'gray');
  const W = 640, H = 360, n = raw.length / (W * H);
  let worst = 0;
  for (let i = 0; i < n; i++) {
    let sw = 0, sx = 0;
    for (let x = 0; x < W; x++) { const v = raw[(i * H + 180) * W + x] / 255; if (v > 0.3) { sw += v; sx += v * x; } }
    // Bar centre = x offset + 20 px half width.
    worst = Math.max(worst, Math.abs(sx / sw + 0.5 - (80 + 300 * i / 24 + 20)));
  }
  return { pass: rep.pass && rep.mode === 'gsap' && n === 24 && worst <= 1.5, mode: rep.mode, frames: n, worstErrorPx: Number(worst.toFixed(3)), framecapChecks: rep.checks };
});

let bytes = 0;
const walk = (d) => { for (const f of readdirSync(d)) { const p = join(d, f); const s = statSync(p); s.isDirectory() ? walk(p) : (bytes += s.size); } };
walk(OUT);
result.outBytes = bytes;
result.pass = Object.values(result.checks).every((c) => c.pass);
writeFileSync(join(OUT, 'result.json'), JSON.stringify(result, null, 2) + '\n');
console.log(result.pass ? 'All checks passed' : 'Some checks failed');
process.exit(result.pass ? 0 : 1);
