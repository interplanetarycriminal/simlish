#!/usr/bin/env node
// framecap: render a web page to a frame-exact video.
// No npm dependencies. Node 22+, a local Chrome or Chromium, FFmpeg and ffprobe on PATH.
//
//   node framecap.mjs <page-url | page.html | "<html>..."> --duration 4 --fps 30 --size 1280x720
//        [--audio file.wav] [--alpha] [--format mov|png] [--out out/film.mp4]
//        [--ready "<js expression>"] [--chrome PATH] [--crf 18] [--keep-frames]
//
// Clock: GSAP pages are seeked through gsap.globalTimeline. If the page defines window.__scene with seek(t) or setTime(t) (the catalogue's time
// contract), framecap calls it for every frame. Otherwise it pauses every animation in
// document.getAnimations() and sets its currentTime, which makes CSS animations, CSS transitions
// and Web Animations seekable.
//
// Writes the video and <out>.report.json. Exits 0 only when the ffprobe checks pass.
import { execFileSync } from 'node:child_process';
import { existsSync, mkdirSync, readdirSync, readFileSync, rmSync, statSync, writeFileSync } from 'node:fs';
import { basename, dirname, join, relative, resolve } from 'node:path';
import { pathToFileURL } from 'node:url';
import { findChrome, serve, launch, evaluate } from '../../fixtures/lib/cdp.mjs';

export const DEFAULT_READY = "document.readyState === 'complete' && window.__ready !== false";

function parseArgs(argv) {
  const opts = { duration: 4, fps: 30, size: '1280x720', audio: null, alpha: false, format: null, out: null, ready: DEFAULT_READY, chrome: undefined, crf: 18, keepFrames: false, input: null };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    const next = () => { if (i + 1 >= argv.length) throw new Error(`${a} needs a value`); return argv[++i]; };
    if (a === '--duration') opts.duration = Number(next());
    else if (a === '--fps') opts.fps = Number(next());
    else if (a === '--size') opts.size = next();
    else if (a === '--audio') opts.audio = next();
    else if (a === '--alpha') opts.alpha = true;
    else if (a === '--format') opts.format = next();
    else if (a === '--out') opts.out = next();
    else if (a === '--ready') opts.ready = next();
    else if (a === '--chrome') opts.chrome = next();
    else if (a === '--crf') opts.crf = Number(next());
    else if (a === '--keep-frames') opts.keepFrames = true;
    else if (a === '-h' || a === '--help') opts.help = true;
    else if (!opts.input) opts.input = a;
    else throw new Error(`Unexpected argument ${a}`);
  }
  return opts;
}

const run = (cmd, args) => execFileSync(cmd, args, { stdio: ['ignore', 'pipe', 'pipe'], maxBuffer: 1 << 28 }).toString();

/** Probe a rendered file (or PNG folder) and compare it with what was asked for. */
export function verify(file, { width, height, fps, frames, duration, audio }) {
  const tol = 1 / fps + 1e-6;
  if (statSync(file).isDirectory()) {
    const pngs = readdirSync(file).filter((f) => f.endsWith('.png')).sort();
    const head = readFileSync(join(file, pngs[0]));
    // PNG IHDR: width and height are big-endian at bytes 16 and 20; color type at byte 25 (6 = RGBA).
    const w = head.readUInt32BE(16), h = head.readUInt32BE(20), colorType = head[25];
    const checks = { frames: pngs.length === frames, size: w === width && h === height, alpha: colorType === 6 || colorType === 4 };
    return { pass: Object.values(checks).every(Boolean), checks, probe: { kind: 'png-sequence', frames: pngs.length, width: w, height: h, colorType } };
  }
  const p = JSON.parse(run('ffprobe', ['-v', 'error', '-count_frames', '-show_entries',
    'stream=index,codec_type,codec_name,width,height,r_frame_rate,nb_read_frames,pix_fmt,duration,sample_rate,channels:format=duration', '-of', 'json', file]));
  const v = p.streams.find((s) => s.codec_type === 'video');
  const a = p.streams.find((s) => s.codec_type === 'audio');
  const [num, den] = v.r_frame_rate.split('/').map(Number);
  const vdur = Number(v.duration ?? p.format.duration);
  const checks = {
    frames: Number(v.nb_read_frames) === frames,
    size: v.width === width && v.height === height,
    fps: Math.abs(num / den - fps) < 1e-6,
    duration: Math.abs(vdur - duration) <= tol,
  };
  if (audio) {
    checks.audioStream = !!a;
    checks.audioDuration = !!a && Math.abs(Number(a.duration ?? p.format.duration) - duration) <= tol;
  }
  return {
    pass: Object.values(checks).every(Boolean), checks,
    probe: { codec: v.codec_name, pix_fmt: v.pix_fmt, width: v.width, height: v.height, fps: v.r_frame_rate, frames: Number(v.nb_read_frames), videoDuration: vdur, containerDuration: Number(p.format.duration), audio: a ? { codec: a.codec_name, duration: Number(a.duration ?? NaN), sampleRate: Number(a.sample_rate), channels: a.channels } : null },
  };
}

// Installed in the page once: a seek function that works for both clock kinds.
const INSTALL = `(() => {
  const s = window.__scene;
  const seekFn = s && (typeof s.seek === 'function' ? 'seek' : typeof s.setTime === 'function' ? 'setTime' : null);
  // GSAP runs its own clock: pause the global timeline and seek it. Tweens start where the global
  // timeline was when they were created (slightly after load), so t = 0 is the earliest start.
  const g = window.gsap && window.gsap.globalTimeline;
  let gsapOffset = 0;
  if (g) {
    g.pause();
    const kids = g.getChildren(false, true, true);
    gsapOffset = kids.length ? Math.min(...kids.map((c) => c.startTime())) : 0;
  }
  window.__framecap = {
    mode: seekFn ? 'scene' : g ? 'gsap' : 'animations',
    seek(t) {
      if (seekFn) return window.__scene[seekFn](t);
      if (g) g.time(gsapOffset + t, false);
      // Ask again every frame: animations can be created after load.
      const anims = document.getAnimations();
      for (const a of anims) { a.pause(); a.currentTime = t * 1000; }
      // Force a style recalc on every animated element so the seeked values are committed to the
      // compositor before the next frame; paused compositor animations can otherwise lag one capture.
      for (const a of anims) { const el = a.effect && a.effect.target; if (el) getComputedStyle(el).opacity; }
    },
    count: () => document.getAnimations().length,
  };
  return { mode: window.__framecap.mode, animations: document.getAnimations().length };
})()`;

export async function render(opts) {
  const t0 = Date.now();
  const m = /^(\d+)x(\d+)$/.exec(opts.size);
  if (!m) throw new Error(`--size must look like 1280x720, got ${opts.size}`);
  const width = Number(m[1]), height = Number(m[2]);
  const { fps, duration } = opts;
  if (!(fps > 0) || !(duration > 0)) throw new Error('--fps and --duration must be positive');
  const frames = Math.round(duration * fps);
  const format = opts.format || (opts.alpha ? 'mov' : 'mp4');
  if (!['mp4', 'mov', 'png'].includes(format)) throw new Error('--format must be mp4, mov or png');
  if (format === 'mp4' && opts.alpha) throw new Error('H.264 MP4 has no alpha channel; use --format mov or png with --alpha');
  if (format === 'mp4' && (width % 2 || height % 2)) throw new Error('yuv420p needs an even width and height');
  if (opts.audio && !existsSync(opts.audio)) throw new Error(`Audio file not found: ${opts.audio}`);

  const defaultOut = join('out', format === 'png' ? 'frames' : `film.${format}`);
  const out = resolve(opts.out || defaultOut);
  mkdirSync(dirname(out), { recursive: true });
  const work = format === 'png' ? out : `${out}.frames`;
  if (existsSync(work)) for (const f of readdirSync(work)) rmSync(join(work, f), { force: true });
  mkdirSync(work, { recursive: true });

  // Resolve the input to a URL. Local files are served over HTTP so ES modules and fetch work.
  let server = null, url = opts.input, tempHtml = null;
  if (!url) throw new Error('Give a page URL, an .html file or an HTML string');
  if (url.trimStart().startsWith('<')) {
    tempHtml = `${out}.input.html`;
    writeFileSync(tempHtml, url);
    url = tempHtml;
  }
  if (!/^(https?|file|data):/i.test(url)) {
    const file = resolve(url);
    if (!existsSync(file)) throw new Error(`Input not found: ${url}`);
    server = await serve(dirname(file));
    url = `http://127.0.0.1:${server.address().port}/${encodeURIComponent(basename(file))}`;
  }

  // Run CSS and Web Animations on the main thread: compositor-thread animations do not reliably show a
  // JavaScript pause and seek in the next captured frame (seen as frames from the wrong time).
  const cdp = await launch(findChrome(opts.chrome), { width, height, args: ['--disable-threaded-animation'] });
  // Paths in the report are relative to the working directory so reports can be shared.
  const rel = (p) => relative(process.cwd(), resolve(p)).split('\\').join('/');
  const input = opts.input.trimStart().startsWith('<') ? '(inline html)' : /^(https?|file|data):/i.test(opts.input) ? opts.input : rel(opts.input);
  const report = { tool: 'framecap', input, url, chrome: cdp.version, width, height, fps, duration, frames, format, alpha: !!opts.alpha, audio: opts.audio ? rel(opts.audio) : null, output: rel(out) };
  try {
    if (opts.alpha) await cdp.send('Emulation.setDefaultBackgroundColorOverride', { color: { r: 0, g: 0, b: 0, a: 0 } });
    await cdp.send('Page.navigate', { url });
    let ready = false;
    for (let i = 0; i < 300 && !ready; i++) {
      ready = await evaluate(cdp, `(${opts.ready}) === true`).catch(() => false);
      if (!ready) await new Promise((r) => setTimeout(r, 100));
    }
    if (!ready) throw new Error(`Page never became ready (${opts.ready})`);
    await evaluate(cdp, 'document.fonts ? document.fonts.ready.then(() => true) : true');
    Object.assign(report, await evaluate(cdp, INSTALL));
    // Warm-up: freeze at t = 0, let the compositor present it, and discard one capture. Without this the
    // first capture can show a compositor frame from before the pause (seen under load: frame 0 at ~0.07 s).
    for (let k = 0; k < 2; k++) {
      await evaluate(cdp, 'Promise.resolve(window.__framecap.seek(0)).then(() => new Promise(r => setTimeout(r, 120))).then(() => new Promise(r => requestAnimationFrame(() => requestAnimationFrame(() => requestAnimationFrame(r)))))');
      await cdp.send('Page.captureScreenshot', { format: 'png', fromSurface: true, captureBeyondViewport: false });
    }

    const pad = (n) => String(n).padStart(5, '0');
    for (let i = 0; i < frames; i++) {
      const t = i / fps;
      await evaluate(cdp, `Promise.resolve(window.__framecap.seek(${t})).then(() => new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r))))`);
      // Settle: a paused, seeked page is static, so capture until two consecutive captures match.
      // Compositor-driven CSS animations can otherwise lag one capture behind the seek under load.
      let data = null;
      for (let k = 0; k < 6; k++) {
        const shot = (await cdp.send('Page.captureScreenshot', { format: 'png', fromSurface: true, captureBeyondViewport: false })).data;
        if (shot === data) break;
        data = shot;
        await evaluate(cdp, 'new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r)))');
        report.settleCaptures = (report.settleCaptures || 0) + 1;
      }
      writeFileSync(join(work, `f${pad(i)}.png`), Buffer.from(data, 'base64'));
      if (process.stdout.isTTY && i % fps === 0) process.stdout.write(`\rframe ${i}/${frames}`);
    }
    if (process.stdout.isTTY) process.stdout.write(`\rframe ${frames}/${frames}\n`);
  } finally {
    await cdp.close();
    if (server) server.close();
    if (tempHtml) rmSync(tempHtml, { force: true });
  }
  report.captureSeconds = (Date.now() - t0) / 1000;

  if (format !== 'png') {
    const args = ['-hide_banner', '-loglevel', 'error', '-y', '-framerate', String(fps), '-i', join(work, 'f%05d.png')];
    if (opts.audio) args.push('-i', opts.audio);
    args.push('-map', '0:v:0');
    if (format === 'mp4') args.push('-c:v', 'libx264', '-preset', 'medium', '-crf', String(opts.crf), '-pix_fmt', 'yuv420p', '-movflags', '+faststart');
    else if (opts.alpha) args.push('-c:v', 'prores_ks', '-profile:v', '4444', '-pix_fmt', 'yuva444p10le', '-alpha_bits', '16', '-vendor', 'apl0');
    else args.push('-c:v', 'prores_ks', '-profile:v', '3', '-pix_fmt', 'yuv422p10le');
    if (opts.audio) {
      // Pad or trim the audio so it ends exactly with the picture.
      args.push('-map', '1:a:0', '-af', `apad,atrim=0:${duration}`, '-c:a', format === 'mp4' ? 'aac' : 'pcm_s16le');
      if (format === 'mp4') args.push('-b:a', '192k');
    }
    args.push('-t', String(duration), out);
    run('ffmpeg', args);
    if (!opts.keepFrames) rmSync(work, { recursive: true, force: true });
  } else if (opts.audio) {
    report.note = 'PNG sequence output has no audio; the --audio file was not used.';
  }

  const v = verify(out, { width, height, fps, frames, duration, audio: !!opts.audio && format !== 'png' });
  Object.assign(report, { pass: v.pass, checks: v.checks, probe: v.probe, totalSeconds: (Date.now() - t0) / 1000 });
  writeFileSync(`${out}.report.json`, JSON.stringify(report, null, 2) + '\n');
  return report;
}

const isMain = process.argv[1] && pathToFileURL(resolve(process.argv[1])).href === import.meta.url;
if (isMain) {
  let opts;
  try { opts = parseArgs(process.argv.slice(2)); } catch (e) { console.error(e.message); process.exit(2); }
  if (opts.help || !opts.input) {
    const lines = readFileSync(new URL(import.meta.url)).toString().split('\n').slice(1);
    console.log(lines.slice(0, lines.findIndex((l) => !l.startsWith('//'))).map((l) => l.replace(/^\/\/ ?/, '')).join('\n'));
    process.exit(opts.help ? 0 : 2);
  }
  render(opts).then((r) => {
    for (const [k, ok] of Object.entries(r.checks)) console.log(`${ok ? 'PASS' : 'FAIL'}  ${k}`);
    console.log(`${r.pass ? 'OK' : 'CHECKS FAILED'}: ${r.output} (${r.frames} frames, ${r.mode} clock, ${r.totalSeconds.toFixed(1)} s)`);
    process.exit(r.pass ? 0 : 1);
  }).catch((e) => { console.error(e.stack || e.message); process.exit(2); });
}
