#!/usr/bin/env node
// Render the seekable scene to MP4 and prove the time contract.
// No npm dependencies: Node 22+ (global WebSocket and fetch), a local Chrome or Chromium, FFmpeg.
//
//   node render.mjs [--fps 30] [--out out] [--chrome PATH]
//
// Checks written to out/evidence.json:
//   repeatable   same frame, two separate page loads, identical PNG bytes
//   seekable     frames rendered out of order match frames rendered in order
//   pauseToPlay  the live page opened at #t=T reports the same state digest as film frame T
//   stream       ffprobe reports the declared size, frame rate, frame count and duration
import { spawn, execFileSync } from 'node:child_process';
import { createServer } from 'node:http';
import { createHash } from 'node:crypto';
import { existsSync, mkdirSync, readdirSync, readFileSync, rmSync, writeFileSync } from 'node:fs';
import { dirname, extname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { tmpdir } from 'node:os';

const HERE = dirname(fileURLToPath(import.meta.url));
const arg = (name, fallback) => { const i = process.argv.indexOf(`--${name}`); return i > 0 ? process.argv[i + 1] : fallback; };
const FPS = Number(arg('fps', 30));
const OUT = resolve(HERE, arg('out', 'out'));
const W = 1280, H = 720;

function findChrome() {
  const given = arg('chrome', process.env.CHROME);
  const candidates = [given,
    'C:/Program Files/Google/Chrome/Application/chrome.exe',
    'C:/Program Files (x86)/Google/Chrome/Application/chrome.exe',
    '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
    '/usr/bin/google-chrome', '/usr/bin/chromium', '/usr/bin/chromium-browser', '/opt/pw-browsers/chromium'].filter(Boolean);
  const hit = candidates.find((p) => existsSync(p));
  if (!hit) throw new Error('No Chrome found. Pass --chrome PATH or set CHROME.');
  return hit;
}

// Static server for this folder only.
const TYPES = { '.html': 'text/html', '.js': 'text/javascript', '.mjs': 'text/javascript', '.json': 'application/json' };
function serve() {
  const server = createServer((req, res) => {
    const path = resolve(HERE, '.' + decodeURIComponent(new URL(req.url, 'http://x').pathname));
    if (!path.startsWith(HERE) || !existsSync(path) || path.includes(`${OUT}`)) { res.writeHead(404); return res.end(); }
    res.writeHead(200, { 'content-type': TYPES[extname(path)] || 'application/octet-stream' });
    res.end(readFileSync(path === HERE ? join(HERE, 'index.html') : path));
  });
  return new Promise((ok) => server.listen(0, '127.0.0.1', () => ok(server)));
}

// Minimal DevTools protocol client over one page target.
let launches = 0;
async function launch(chrome) {
  const profile = join(tmpdir(), `seekable-scene-${process.pid}-${++launches}`);
  const proc = spawn(chrome, ['--headless=new', '--remote-debugging-port=0', `--user-data-dir=${profile}`,
    '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--hide-scrollbars', '--mute-audio',
    '--no-first-run', '--no-default-browser-check', `--window-size=${W},${H}`, 'about:blank'], { stdio: ['ignore', 'ignore', 'pipe'] });
  const wsUrl = await new Promise((ok, fail) => {
    let buf = '';
    proc.stderr.on('data', (d) => { buf += d; const m = buf.match(/DevTools listening on (ws:\/\/\S+)/); if (m) ok(m[1]); });
    proc.on('exit', (c) => fail(new Error(`Chrome exited (${c}): ${buf.slice(-400)}`)));
  });
  const port = new URL(wsUrl).port;
  const page = (await (await fetch(`http://127.0.0.1:${port}/json/list`)).json()).find((t) => t.type === 'page');
  const ws = new WebSocket(page.webSocketDebuggerUrl);
  await new Promise((ok) => ws.addEventListener('open', ok, { once: true }));
  let id = 0; const pending = new Map(); const waiters = [];
  ws.addEventListener('message', (e) => {
    const msg = JSON.parse(e.data);
    if (msg.id && pending.has(msg.id)) { const { ok, fail } = pending.get(msg.id); pending.delete(msg.id); msg.error ? fail(new Error(msg.error.message)) : ok(msg.result); }
    else if (msg.method) waiters.filter((w) => w.method === msg.method).forEach((w) => w.ok(msg.params));
  });
  const send = (method, params = {}) => new Promise((ok, fail) => { pending.set(++id, { ok, fail }); ws.send(JSON.stringify({ id, method, params })); });
  const close = () => new Promise((ok) => {
    ws.close();
    proc.once('exit', () => { try { rmSync(profile, { recursive: true, force: true, maxRetries: 5, retryDelay: 200 }); } catch { /* Windows may hold the profile briefly; it is in the temp folder */ } ok(); });
    proc.kill();
  });
  const version = (await (await fetch(`http://127.0.0.1:${port}/json/version`)).json()).Browser;
  return { send, close, version };
}

async function evaluate(cdp, expression) {
  const r = await cdp.send('Runtime.evaluate', { expression, awaitPromise: true, returnByValue: true });
  if (r.exceptionDetails) throw new Error(r.exceptionDetails.exception?.description || r.exceptionDetails.text);
  return r.result.value;
}

async function open(cdp, url) {
  await cdp.send('Emulation.setDeviceMetricsOverride', { width: W, height: H, deviceScaleFactor: 1, mobile: false });
  await evaluate(cdp, 'window.__ready = false').catch(() => {});
  await cdp.send('Page.navigate', { url });
  for (let i = 0; i < 300; i++) {
    if (await evaluate(cdp, 'window.__ready === true').catch(() => false)) return;
    await new Promise((r) => setTimeout(r, 100));
  }
  throw new Error(`Page never became ready: ${url}`);
}

async function frameAt(cdp, t) {
  const digest = await evaluate(cdp, `(window.__scene.seek(${t}), window.__scene.digest())`);
  // Wait two animation frames so the compositor presents the seeked state, then capture.
  await evaluate(cdp, 'new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r)))');
  const { data } = await cdp.send('Page.captureScreenshot', { format: 'png', fromSurface: true });
  const png = Buffer.from(data, 'base64');
  return { png, digest, sha: createHash('sha256').update(png).digest('hex') };
}

const pad = (n) => String(n).padStart(4, '0');

async function main() {
  const chrome = findChrome();
  // Clear previous output file by file (the folder itself may be open in a shell or viewer).
  if (existsSync(OUT)) for (const f of readdirSync(OUT)) rmSync(join(OUT, f), { recursive: true, force: true });
  mkdirSync(join(OUT, 'frames'), { recursive: true });
  const server = await serve();
  const base = `http://127.0.0.1:${server.address().port}/index.html`;
  const evidence = { fixture: 'seekable-scene', date: new Date().toISOString(), fps: FPS, size: [W, H], checks: {} };

  // Pass 1: the film, in order.
  let cdp = await launch(chrome);
  evidence.chrome = cdp.version;
  await open(cdp, `${base}?render`);
  const meta = await evaluate(cdp, '({ duration: window.__scene.duration, three: window.__scene.three, beats: window.__scene.beats.map(b => b.t) })');
  Object.assign(evidence, { three: `r${meta.three}`, duration: meta.duration, beats: meta.beats });
  const total = Math.round(meta.duration * FPS);
  const film = [];
  const started = Date.now();
  for (let i = 0; i < total; i++) {
    const f = await frameAt(cdp, i / FPS);
    writeFileSync(join(OUT, 'frames', `f${pad(i)}.png`), f.png);
    film.push({ sha: f.sha, digest: f.digest });
    if (i % FPS === 0) process.stdout.write(`\rframe ${i}/${total}`);
  }
  evidence.renderSeconds = (Date.now() - started) / 1000;
  process.stdout.write(`\rframe ${total}/${total}\n`);

  // Seekable: jump around out of order in the same page and compare with the in-order pass.
  const probes = [Math.floor(total * 0.8), 3, Math.floor(total / 2), total - 1, 0, ...meta.beats.map((b) => Math.round(b * FPS))].filter((i) => i < total);
  const seek = [];
  for (const i of probes) { const f = await frameAt(cdp, i / FPS); seek.push({ frame: i, match: f.sha === film[i].sha }); }
  evidence.checks.seekable = { pass: seek.every((s) => s.match), probes: seek };
  await cdp.close();

  // Repeatable: a fresh browser and page load renders the same bytes.
  cdp = await launch(chrome);
  await open(cdp, `${base}?render`);
  const repeat = [];
  for (const i of probes) { const f = await frameAt(cdp, i / FPS); repeat.push({ frame: i, match: f.sha === film[i].sha }); }
  evidence.checks.repeatable = { pass: repeat.every((s) => s.match), probes: repeat };

  // Pause-to-play: open the live page at each beat's deep link and compare scene state with the film.
  const live = [];
  for (const b of meta.beats) {
    const i = Math.round(b * FPS);
    const tt = (i / FPS).toFixed(2);
    await open(cdp, `${base}?live=${i}#t=${tt}`);
    const d = await evaluate(cdp, 'window.__scene.digest()');
    // Camera aspect differs only if the viewport does; both run at 1280x720 here.
    live.push({ t: Number(tt), match: d === film[i].digest });
  }
  evidence.checks.pauseToPlay = { pass: live.every((s) => s.match), probes: live };
  await open(cdp, `${base}?shot#beat=5`);
  await evaluate(cdp, 'new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r)))');
  writeFileSync(join(OUT, 'live-beat5.png'), Buffer.from((await cdp.send('Page.captureScreenshot', { format: 'png' })).data, 'base64'));
  await cdp.close();
  server.close();

  // Encode and inspect.
  const mp4 = join(OUT, 'seekable-scene.mp4');
  execFileSync('ffmpeg', ['-hide_banner', '-loglevel', 'error', '-y', '-framerate', String(FPS), '-i', join(OUT, 'frames', 'f%04d.png'),
    '-c:v', 'libx264', '-preset', 'slow', '-crf', '18', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', '-tune', 'animation', mp4]);
  const probe = JSON.parse(execFileSync('ffprobe', ['-v', 'error', '-count_frames', '-select_streams', 'v:0', '-show_entries',
    'stream=codec_name,width,height,r_frame_rate,nb_read_frames:format=duration', '-of', 'json', mp4]).toString());
  const st = probe.streams[0];
  const okStream = st.width === W && st.height === H && st.r_frame_rate === `${FPS}/1` && Number(st.nb_read_frames) === total
    && Math.abs(Number(probe.format.duration) - meta.duration) < 1 / FPS + 1e-6;
  evidence.checks.stream = { pass: okStream, codec: st.codec_name, width: st.width, height: st.height, fps: st.r_frame_rate, frames: Number(st.nb_read_frames), duration: Number(probe.format.duration) };
  // Keep one still per beat: late in the beat, but before the camera starts moving to the next one
  // (moves take 1.4 s and finish as the next beat starts). The last beat's still is its final frame.
  meta.beats.forEach((b, k) => {
    const t = k + 1 < meta.beats.length ? meta.beats[k + 1] - 1.5 : meta.duration - 1 / FPS;
    const i = Math.min(total - 1, Math.round(t * FPS));
    writeFileSync(join(OUT, `beat-${k + 1}.png`), readFileSync(join(OUT, 'frames', `f${pad(i)}.png`)));
  });
  rmSync(join(OUT, 'frames'), { recursive: true, force: true });
  const stills = meta.beats.map((_, k) => ['-i', join(OUT, `beat-${k + 1}.png`)]).flat();
  if (meta.beats.length === 6) {
    execFileSync('ffmpeg', ['-hide_banner', '-loglevel', 'error', '-y', ...stills, '-filter_complex',
      '[0][1][2]hstack=3[a];[3][4][5]hstack=3[b];[a][b]vstack,scale=1920:-1', join(HERE, 'contact-sheet.png')]);
  }

  evidence.pass = Object.values(evidence.checks).every((c) => c.pass);
  writeFileSync(join(OUT, 'evidence.json'), JSON.stringify(evidence, null, 2) + '\n');
  for (const [k, c] of Object.entries(evidence.checks)) console.log(`${c.pass ? 'PASS' : 'FAIL'}  ${k}`);
  console.log(`${evidence.pass ? 'All checks passed' : 'Some checks failed'}: ${join(OUT, 'evidence.json')}`);
  process.exit(evidence.pass ? 0 : 1);
}

main().catch((e) => { console.error(e); process.exit(2); });
