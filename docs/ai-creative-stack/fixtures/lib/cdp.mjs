// Minimal shared helpers for fixture checks: a static server and a headless Chrome DevTools client.
// No npm dependencies. Node 22+ (global WebSocket and fetch).
import { spawn } from 'node:child_process';
import { createServer } from 'node:http';
import { existsSync, readFileSync, rmSync } from 'node:fs';
import { extname, join, resolve } from 'node:path';
import { tmpdir } from 'node:os';

export function findChrome(given = process.env.CHROME) {
  const candidates = [given,
    'C:/Program Files/Google/Chrome/Application/chrome.exe',
    'C:/Program Files (x86)/Google/Chrome/Application/chrome.exe',
    '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
    '/usr/bin/google-chrome', '/usr/bin/chromium', '/usr/bin/chromium-browser', '/opt/pw-browsers/chromium'].filter(Boolean);
  const hit = candidates.find((p) => existsSync(p));
  if (!hit) throw new Error('No Chrome found. Set CHROME to its path.');
  return hit;
}

const TYPES = { '.svg': 'image/svg+xml', '.css': 'text/css', '.html': 'text/html', '.js': 'text/javascript', '.mjs': 'text/javascript', '.json': 'application/json', '.glb': 'model/gltf-binary', '.gltf': 'model/gltf+json', '.bin': 'application/octet-stream', '.png': 'image/png' };

export function serve(root) {
  const base = resolve(root);
  const server = createServer((req, res) => {
    const path = resolve(base, '.' + decodeURIComponent(new URL(req.url, 'http://x').pathname));
    if (!path.startsWith(base) || !existsSync(path)) { res.writeHead(404); return res.end(); }
    res.writeHead(200, { 'content-type': TYPES[extname(path)] || 'application/octet-stream' });
    res.end(readFileSync(path));
  });
  return new Promise((ok) => server.listen(0, '127.0.0.1', () => ok(server)));
}

let launches = 0;
export async function launch(chrome = findChrome(), { width = 1280, height = 720, args = [] } = {}) {
  const profile = join(tmpdir(), `fixture-chrome-${process.pid}-${++launches}`);
  const proc = spawn(chrome, ['--headless=new', '--remote-debugging-port=0', `--user-data-dir=${profile}`,
    '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--hide-scrollbars', '--mute-audio',
    '--no-first-run', '--no-default-browser-check', `--window-size=${width},${height}`, ...args, 'about:blank'], { stdio: ['ignore', 'ignore', 'pipe'] });
  const wsUrl = await new Promise((ok, fail) => {
    let buf = '';
    proc.stderr.on('data', (d) => { buf += d; const m = buf.match(/DevTools listening on (ws:\/\/\S+)/); if (m) ok(m[1]); });
    proc.on('exit', (c) => fail(new Error(`Chrome exited (${c}): ${buf.slice(-400)}`)));
  });
  const port = new URL(wsUrl).port;
  const page = (await (await fetch(`http://127.0.0.1:${port}/json/list`)).json()).find((t) => t.type === 'page');
  const ws = new WebSocket(page.webSocketDebuggerUrl);
  await new Promise((ok) => ws.addEventListener('open', ok, { once: true }));
  let id = 0; const pending = new Map();
  ws.addEventListener('message', (e) => {
    const msg = JSON.parse(e.data);
    if (msg.id && pending.has(msg.id)) { const { ok, fail } = pending.get(msg.id); pending.delete(msg.id); msg.error ? fail(new Error(msg.error.message)) : ok(msg.result); }
  });
  const send = (method, params = {}) => new Promise((ok, fail) => { pending.set(++id, { ok, fail }); ws.send(JSON.stringify({ id, method, params })); });
  const version = (await (await fetch(`http://127.0.0.1:${port}/json/version`)).json()).Browser;
  const close = () => new Promise((ok) => {
    ws.close();
    proc.once('exit', () => { try { rmSync(profile, { recursive: true, force: true, maxRetries: 5, retryDelay: 200 }); } catch { /* temp folder */ } ok(); });
    proc.kill();
  });
  await send('Emulation.setDeviceMetricsOverride', { width, height, deviceScaleFactor: 1, mobile: false });
  return { send, close, version };
}

export async function evaluate(cdp, expression) {
  const r = await cdp.send('Runtime.evaluate', { expression, awaitPromise: true, returnByValue: true });
  if (r.exceptionDetails) throw new Error(r.exceptionDetails.exception?.description || r.exceptionDetails.text);
  return r.result.value;
}

export async function open(cdp, url, ready = 'window.__ready === true') {
  await evaluate(cdp, 'window.__ready = false').catch(() => {});
  await cdp.send('Page.navigate', { url });
  for (let i = 0; i < 300; i++) {
    if (await evaluate(cdp, ready).catch(() => false)) return;
    await new Promise((r) => setTimeout(r, 100));
  }
  throw new Error(`Page never became ready: ${url}`);
}

export async function screenshot(cdp) {
  await evaluate(cdp, 'new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r)))');
  const { data } = await cdp.send('Page.captureScreenshot', { format: 'png', fromSurface: true });
  return Buffer.from(data, 'base64');
}
