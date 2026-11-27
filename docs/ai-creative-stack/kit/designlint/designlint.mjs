#!/usr/bin/env node
// designlint: deterministic design-quality rules on a rendered page, tiered Floor / Reflex / Finish.
// Usage: node designlint.mjs <url-or-html-file> [--widths 390,768,1024,1440] [--out out/] [--height 800]
// Node 22+, no npm dependencies. Uses the shared DevTools helper in fixtures/lib/cdp.mjs.
import { createServer } from 'node:http';
import { existsSync, mkdirSync, readFileSync, writeFileSync, statSync } from 'node:fs';
import { dirname, basename, extname, join, resolve, relative, sep } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const HERE = dirname(fileURLToPath(import.meta.url));
const cdpLib = await import(pathToFileURL(join(HERE, '..', '..', 'fixtures', 'lib', 'cdp.mjs')).href);
const { launch, evaluate, screenshot } = cdpLib;

export const TIERS = ['Floor', 'Reflex', 'Finish'];

// ---------- arguments ----------
function parseArgs(argv) {
  const opts = { target: null, widths: [390, 768, 1024, 1440], out: 'out', height: 800 };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a === '--widths') opts.widths = argv[++i].split(',').map((s) => parseInt(s, 10)).filter((n) => n > 0);
    else if (a === '--out') opts.out = argv[++i];
    else if (a === '--height') opts.height = parseInt(argv[++i], 10);
    else if (a === '-h' || a === '--help') opts.help = true;
    else if (!opts.target) opts.target = a;
  }
  return opts;
}

// ---------- static server for local files (with correct CSS MIME so stylesheets apply and stay same-origin) ----------
const MIME = { '.html': 'text/html; charset=utf-8', '.htm': 'text/html; charset=utf-8', '.css': 'text/css', '.js': 'text/javascript', '.mjs': 'text/javascript',
  '.json': 'application/json', '.svg': 'image/svg+xml', '.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.gif': 'image/gif',
  '.webp': 'image/webp', '.avif': 'image/avif', '.woff': 'font/woff', '.woff2': 'font/woff2', '.ttf': 'font/ttf', '.otf': 'font/otf' };

function serveDir(root) {
  const base = resolve(root);
  const server = createServer((req, res) => {
    const p = resolve(base, '.' + decodeURIComponent(new URL(req.url, 'http://x').pathname));
    if (!p.startsWith(base) || !existsSync(p) || statSync(p).isDirectory()) { res.writeHead(404); return res.end(); }
    res.writeHead(200, { 'content-type': MIME[extname(p).toLowerCase()] || 'application/octet-stream' });
    res.end(readFileSync(p));
  });
  return new Promise((ok) => server.listen(0, '127.0.0.1', () => ok(server)));
}

export async function resolveTarget(target) {
  if (/^(https?|file):\/\//i.test(target)) return { url: target, close: async () => {} };
  const file = resolve(target);
  if (!existsSync(file)) throw new Error(`Not a URL or an existing file: ${target}`);
  const server = await serveDir(dirname(file));
  const url = `http://127.0.0.1:${server.address().port}/${encodeURIComponent(basename(file))}`;
  return { url, close: () => new Promise((ok) => server.close(ok)) };
}

export async function loadPage(cdp, url) {
  await cdp.send('Page.enable');
  await cdp.send('Page.navigate', { url });
  const want = JSON.stringify(url);
  for (let i = 0; i < 300; i++) {
    const ok = await evaluate(cdp, `location.href === ${want} && document.readyState === 'complete'`).catch(() => false);
    if (ok) break;
    if (i === 299) throw new Error(`Page never finished loading: ${url}`);
    await new Promise((r) => setTimeout(r, 100));
  }
  await evaluate(cdp, 'document.fonts ? document.fonts.ready.then(() => true) : true');
}

export async function setWidth(cdp, width, height) {
  await cdp.send('Emulation.setDeviceMetricsOverride', { width, height, deviceScaleFactor: 1, mobile: false });
  await evaluate(cdp, 'new Promise(r => requestAnimationFrame(() => requestAnimationFrame(() => r(true))))');
}

// ---------- in-page rule engine (serialized into the page) ----------
function pageAnalyze(opts) {
  const W = window.innerWidth;
  const findings = [];
  const metrics = { width: W, scrollWidth: document.documentElement.scrollWidth };
  const add = (rule, tier, el, message, value) => findings.push({ rule, tier, selector: el ? sel(el) : null, message, value });

  // --- helpers ---
  function sel(el) {
    if (el.id) return '#' + CSS.escape(el.id);
    const parts = [];
    let e = el;
    while (e && e.nodeType === 1 && parts.length < 4) {
      if (e.id) { parts.unshift('#' + CSS.escape(e.id)); break; }
      let s = e.localName + [...e.classList].slice(0, 2).map((c) => '.' + CSS.escape(c)).join('');
      const parent = e.parentElement;
      if (parent) {
        const same = [...parent.children].filter((c) => c.localName === e.localName);
        if (same.length > 1) s += `:nth-of-type(${same.indexOf(e) + 1})`;
      }
      parts.unshift(s);
      if (e === document.body || e === document.documentElement) break;
      e = parent;
    }
    return parts.join(' > ');
  }
  const canvas = document.createElement('canvas'); canvas.width = canvas.height = 1;
  const ctx = canvas.getContext('2d', { willReadFrequently: true });
  const colorCache = new Map();
  function parseColor(c) { // -> [r,g,b,a] with a in 0..1, or null for fully transparent
    if (colorCache.has(c)) return colorCache.get(c);
    let out = null;
    if (c && c !== 'transparent' && c !== 'none') {
      const m = c.match(/^rgba?\(([^)]+)\)$/);
      if (m) {
        const p = m[1].split(/[\s,/]+/).filter(Boolean).map((v) => v.endsWith('%') ? parseFloat(v) / 100 : parseFloat(v));
        out = [p[0], p[1], p[2], p.length > 3 ? p[3] : 1];
      } else {
        ctx.clearRect(0, 0, 1, 1); ctx.fillStyle = '#000'; ctx.fillStyle = c; ctx.fillRect(0, 0, 1, 1);
        const d = ctx.getImageData(0, 0, 1, 1).data; out = [d[0], d[1], d[2], d[3] / 255];
      }
      if (out && out[3] <= 0.001) out = null;
    }
    colorCache.set(c, out); return out;
  }
  const lin = (v) => { v /= 255; return v <= 0.04045 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4); };
  const lum = (c) => 0.2126 * lin(c[0]) + 0.7152 * lin(c[1]) + 0.0722 * lin(c[2]);
  const ratio = (a, b) => { const x = lum(a), y = lum(b); return (Math.max(x, y) + 0.05) / (Math.min(x, y) + 0.05); };
  const over = (top, under) => { const a = top[3]; return [0, 1, 2].map((i) => top[i] * a + under[i] * (1 - a)).concat(1); };
  const hex = (c) => '#' + c.slice(0, 3).map((v) => Math.round(v).toString(16).padStart(2, '0')).join('') + (c[3] < 1 ? Math.round(c[3] * 255).toString(16).padStart(2, '0') : '');

  const SKIP = new Set(['SCRIPT', 'STYLE', 'NOSCRIPT', 'TEMPLATE', 'META', 'LINK', 'TITLE', 'HEAD', 'BR', 'WBR']);
  const styleOf = new Map();
  const cs = (el) => { let s = styleOf.get(el); if (!s) { s = getComputedStyle(el); styleOf.set(el, s); } return s; };
  const opacityCache = new Map();
  function opacityOf(el) {
    if (!el || el.nodeType !== 1) return 1;
    if (opacityCache.has(el)) return opacityCache.get(el);
    const v = parseFloat(cs(el).opacity) * opacityOf(el.parentElement);
    opacityCache.set(el, v); return v;
  }
  const directText = (el) => [...el.childNodes].filter((n) => n.nodeType === 3).map((n) => n.data).join('').replace(/\s+/g, ' ').trim();
  const inSvg = (el) => el instanceof SVGElement && el.localName !== 'svg';

  const rendered = [];
  for (const el of document.body ? [document.body, ...document.body.querySelectorAll('*')] : []) {
    if (SKIP.has(el.tagName)) continue;
    const s = cs(el);
    if (s.display === 'none') continue;
    const rects = el.getClientRects();
    if (!rects.length) continue;
    const r = el.getBoundingClientRect();
    const hidden = s.visibility === 'hidden' || s.visibility === 'collapse' || opacityOf(el) <= 0.01 || r.width <= 1 || r.height <= 1 ||
      /rect\(0(px)?,? 0(px)?,? 0(px)?,? 0(px)?\)/.test(s.clip) || s.clipPath === 'inset(50%)';
    rendered.push({ el, s, r, hidden, text: inSvg(el) ? '' : directText(el) });
  }
  const textEls = rendered.filter((x) => x.text && !x.hidden);

  // --- Floor: contrast (per width) ---
  let contrastChecked = 0, contrastUnknown = 0;
  for (const x of textEls) {
    const fg0 = parseColor(x.s.color); if (!fg0) continue;
    let layers = [], unknown = false, e = x.el;
    while (e && e.nodeType === 1) {
      const s = cs(e);
      if (s.backgroundImage && s.backgroundImage !== 'none') { unknown = true; break; }
      if (['IMG', 'VIDEO', 'CANVAS', 'IFRAME'].includes(e.tagName)) { unknown = true; break; }
      const bg = parseColor(s.backgroundColor);
      if (bg) { layers.push(bg); if (bg[3] >= 0.999) break; }
      e = e.parentElement;
    }
    if (unknown) { contrastUnknown++; continue; }
    let bg = [255, 255, 255, 1];
    for (let i = layers.length - 1; i >= 0; i--) bg = over(layers[i], bg);
    const fg = over([fg0[0], fg0[1], fg0[2], fg0[3] * opacityOf(x.el)], bg);
    const size = parseFloat(x.s.fontSize), weight = parseInt(x.s.fontWeight, 10) || 400;
    const large = size >= 24 || (size >= 18.66 && weight >= 700);
    const need = large ? 3 : 4.5;
    const cr = ratio(fg, bg);
    contrastChecked++;
    if (cr < need) add('contrast', 'Floor', x.el, `Text contrast ${cr.toFixed(2)}:1 is below ${need}:1 (${large ? 'large' : 'normal'} text, ${hex(fg)} on ${hex(bg)})`, +cr.toFixed(2));
  }
  metrics.contrastChecked = contrastChecked; metrics.contrastUnknownBackground = contrastUnknown;

  // --- Floor: horizontal overflow (per width) ---
  const clippedByAncestor = (el) => {
    for (let p = el.parentElement; p && p !== document.body && p !== document.documentElement; p = p.parentElement) {
      if (cs(p).overflowX !== 'visible') return true;
    }
    return false;
  };
  if (metrics.scrollWidth > W + 1) {
    const culprits = rendered.filter((x) => (x.r.right > W + 1 || x.r.left < -1) && x.s.position !== 'fixed' && !clippedByAncestor(x.el));
    const set = new Set(culprits.map((x) => x.el));
    const top = culprits.filter((x) => !set.has(x.el.parentElement));
    if (!top.length) add('overflow-x', 'Floor', document.documentElement, `Page scrolls sideways: ${metrics.scrollWidth}px wide in a ${W}px viewport`, metrics.scrollWidth);
    for (const x of top.slice(0, 5)) add('overflow-x', 'Floor', x.el, `Element spans ${Math.round(x.r.left)}..${Math.round(x.r.right)}px in a ${W}px viewport; page scrolls sideways to ${metrics.scrollWidth}px`, Math.round(x.r.right));
  }

  // --- Reflex: clipped text (per width) ---
  for (const x of textEls) {
    const s = x.s, el = x.el;
    const hx = ['hidden', 'clip'].includes(s.overflowX) && el.scrollWidth > el.clientWidth + 1;
    const hy = ['hidden', 'clip'].includes(s.overflowY) && el.scrollHeight > el.clientHeight + 1;
    if (hx || hy) add('text-clipped', 'Reflex', el, `Text is cut off ${hx ? 'horizontally' : 'vertically'}${s.textOverflow === 'ellipsis' ? ' (ellipsis)' : ''}: content ${hx ? el.scrollWidth : el.scrollHeight}px in a ${hx ? el.clientWidth : el.clientHeight}px box`, hx ? el.scrollWidth - el.clientWidth : el.scrollHeight - el.clientHeight);
  }

  // --- Reflex: overlapping text (per width) ---
  const clipCache = new Map();
  const clipOf = (el) => { // visible area left by ancestors that clip overflow, in page coordinates
    if (!el || el === document.body || el === document.documentElement) return { l: -1e9, t: -1e9, r: 1e9, b: 1e9 };
    if (clipCache.has(el)) return clipCache.get(el);
    let c = clipOf(el.parentElement);
    const s = cs(el);
    if (s.overflowX !== 'visible' || s.overflowY !== 'visible') {
      const r = el.getBoundingClientRect();
      c = { l: Math.max(c.l, r.left + scrollX), t: Math.max(c.t, r.top + scrollY), r: Math.min(c.r, r.right + scrollX), b: Math.min(c.b, r.bottom + scrollY) };
    }
    clipCache.set(el, c); return c;
  };
  const boxes = [];
  for (const x of textEls.slice(0, 1500)) {
    const c = clipOf(x.el);
    for (const n of x.el.childNodes) {
      if (n.nodeType !== 3 || !n.data.trim()) continue;
      const range = document.createRange(); range.selectNodeContents(n);
      for (const r of range.getClientRects()) {
        const b = { el: x.el, l: Math.max(c.l, r.left + scrollX), t: Math.max(c.t, r.top + scrollY), r: Math.min(c.r, r.right + scrollX), b: Math.min(c.b, r.bottom + scrollY) };
        if (b.r - b.l > 1 && b.b - b.t > 1) boxes.push(b);
      }
    }
  }
  boxes.sort((a, b) => a.t - b.t);
  const overlapPairs = new Set();
  for (let i = 0; i < boxes.length; i++) {
    const A = boxes[i];
    for (let j = i + 1; j < boxes.length && boxes[j].t < A.b; j++) {
      const B = boxes[j];
      if (A.el === B.el || A.el.contains(B.el) || B.el.contains(A.el)) continue;
      const iw = Math.min(A.r, B.r) - Math.max(A.l, B.l), ih = Math.min(A.b, B.b) - Math.max(A.t, B.t);
      if (iw <= 2 || ih <= 2) continue;
      const minArea = Math.min((A.r - A.l) * (A.b - A.t), (B.r - B.l) * (B.b - B.t));
      if (iw * ih < 0.25 * minArea) continue;
      const key = sel(A.el) + ' | ' + sel(B.el);
      if (overlapPairs.has(key)) continue;
      overlapPairs.add(key);
      if (overlapPairs.size <= 20) add('text-overlap', 'Reflex', A.el, `Text overlaps text of ${sel(B.el)} (${Math.round(iw)}x${Math.round(ih)}px)`, Math.round(iw * ih));
    }
  }

  // --- Reflex: font sizes below 12px (per width) ---
  const small = new Map();
  for (const x of textEls) {
    const fs = parseFloat(x.s.fontSize);
    if (fs < 12) { const k = fs.toFixed(1); if (!small.has(k)) small.set(k, []); small.get(k).push(x.el); }
  }
  for (const [k, els] of small) add('font-size-min', 'Reflex', els[0], `${els.length} text element(s) at ${k}px, below the 12px minimum`, parseFloat(k));

  // --- Reflex: touch targets under 24x24 at the narrow width ---
  if (opts.touch) {
    const Q = 'a[href], button, input:not([type=hidden]), select, textarea, summary, [role=button], [role=link], [role=checkbox], [role=tab], [role=switch], [tabindex]:not([tabindex="-1"])';
    for (const x of rendered) {
      if (x.hidden || !x.el.matches(Q)) continue;
      if (x.el.localName === 'a' && x.s.display === 'inline' && x.el.parentElement && directText(x.el.parentElement)) continue; // inline link in a sentence: WCAG exception
      if (x.r.width < 24 || x.r.height < 24) add('touch-target', 'Reflex', x.el, `Touch target is ${Math.round(x.r.width)}x${Math.round(x.r.height)}px, under 24x24px`, `${Math.round(x.r.width)}x${Math.round(x.r.height)}`);
    }
  }

  // --- Finish: spacing on a 4px grid (per width) ---
  let onGrid = 0, total = 0; const offVals = new Map();
  for (const x of rendered) {
    if (inSvg(x.el)) continue;
    const s = x.s;
    const vals = [s.paddingTop, s.paddingRight, s.paddingBottom, s.paddingLeft, s.marginTop, s.marginBottom];
    if (s.marginLeft !== s.marginRight) vals.push(s.marginLeft, s.marginRight); // equal side margins are usually auto-centering
    if (/flex|grid/.test(s.display)) vals.push(s.rowGap, s.columnGap);
    for (const v of vals) {
      const n = Math.abs(parseFloat(v));
      if (!n || !isFinite(n)) continue;
      total++;
      const rem = n % 4;
      if (rem < 0.05 || rem > 3.95) onGrid++; else { const k = +n.toFixed(2); offVals.set(k, (offVals.get(k) || 0) + 1); }
    }
  }
  metrics.spacingValues = total;
  metrics.spacingOnGridPct = total ? +(100 * onGrid / total).toFixed(1) : 100;
  if (total >= 6 && metrics.spacingOnGridPct < 80) {
    const worst = [...offVals].sort((a, b) => b[1] - a[1]).slice(0, 6).map(([v, c]) => `${v}px x${c}`).join(', ');
    add('spacing-grid', 'Finish', null, `Only ${metrics.spacingOnGridPct}% of ${total} spacing values sit on a 4px grid (off-grid: ${worst})`, metrics.spacingOnGridPct);
  }

  // --- Finish: distinct colors (per width) ---
  const colors = new Map();
  const note = (c) => { const p = parseColor(c); if (!p) return; const k = hex(p); colors.set(k, (colors.get(k) || 0) + 1); };
  for (const x of rendered) {
    if (x.hidden) continue;
    const s = x.s;
    if (x.text) note(s.color);
    note(s.backgroundColor);
    for (const side of ['Top', 'Right', 'Bottom', 'Left']) if (parseFloat(s[`border${side}Width`]) > 0 && s[`border${side}Style`] !== 'none') note(s[`border${side}Color`]);
    if (inSvg(x.el)) { if (s.fill && !s.fill.startsWith('url')) note(s.fill); if (s.stroke && s.stroke !== 'none' && !s.stroke.startsWith('url')) note(s.stroke); }
  }
  metrics.distinctColors = colors.size;
  metrics.topColors = [...colors].sort((a, b) => b[1] - a[1]).slice(0, 12).map(([c, n]) => `${c} x${n}`);
  if (colors.size > opts.maxColors) add('color-count', 'Finish', null, `${colors.size} distinct colors in use (limit ${opts.maxColors}); consolidate into tokens`, colors.size);

  if (opts.first) {
    // --- Reflex: font families ---
    const fams = new Map();
    for (const x of textEls) {
      const first = x.s.fontFamily.split(',')[0].trim().replace(/^["']|["']$/g, '').toLowerCase();
      fams.set(first, (fams.get(first) || 0) + 1);
    }
    metrics.fontFamilies = [...fams].sort((a, b) => b[1] - a[1]).map(([f, n]) => `${f} x${n}`);
    if (fams.size > 3) add('font-families', 'Reflex', null, `${fams.size} font families in use (more than 3): ${[...fams.keys()].join(', ')}`, fams.size);

    // --- Floor: images without alt ---
    for (const img of document.querySelectorAll('img:not([alt])')) {
      if (img.closest('[aria-hidden="true"]') || ['presentation', 'none'].includes(img.getAttribute('role'))) continue;
      add('img-alt', 'Floor', img, `Image has no alt attribute (use alt="" if decorative): ${(img.getAttribute('src') || '').slice(0, 60)}`, null);
    }

    // --- Floor: buttons and links without an accessible name ---
    const renderedSet = new Set(rendered.map((x) => x.el));
    const accName = (el) => {
      const lb = el.getAttribute('aria-labelledby');
      if (lb) { const t = lb.split(/\s+/).map((id) => document.getElementById(id)?.textContent || '').join(' ').trim(); if (t) return t; }
      const al = el.getAttribute('aria-label'); if (al && al.trim()) return al.trim();
      if (el.localName === 'input') {
        if (['submit', 'reset'].includes(el.type)) return el.value || el.type;
        if (el.type === 'button') return el.value || '';
        if (el.type === 'image') return el.alt || '';
      }
      const t = (el.innerText || el.textContent || '').trim(); if (t) return t;
      for (const img of el.querySelectorAll('img[alt]')) if (img.alt.trim()) return img.alt.trim();
      for (const d of el.querySelectorAll('[aria-label]')) if (d.getAttribute('aria-label').trim()) return d.getAttribute('aria-label').trim();
      const st = el.querySelector('svg title'); if (st && st.textContent.trim()) return st.textContent.trim();
      return (el.getAttribute('title') || '').trim();
    };
    for (const el of document.querySelectorAll('a[href], button, input[type=button], input[type=submit], input[type=reset], input[type=image], [role=button], [role=link]')) {
      if (!renderedSet.has(el) || el.closest('[aria-hidden="true"]')) continue;
      if (!accName(el)) add('accessible-name', 'Floor', el, `${el.localName === 'a' || el.getAttribute('role') === 'link' ? 'Link' : 'Button'} has no accessible name`, null);
    }

    // --- Reflex: heading structure ---
    const heads = [...document.querySelectorAll('h1,h2,h3,h4,h5,h6,[role=heading]')].filter((h) => renderedSet.has(h));
    let prev = 0;
    for (const h of heads) {
      const lvl = /^h[1-6]$/.test(h.localName) ? +h.localName[1] : (parseInt(h.getAttribute('aria-level'), 10) || 2);
      if (prev && lvl > prev + 1) add('heading-skip', 'Reflex', h, `Heading level jumps from h${prev} to h${lvl}`, `h${prev}>h${lvl}`);
      prev = lvl;
    }
    const h1s = heads.filter((h) => h.localName === 'h1');
    if (h1s.length > 1) add('multiple-h1', 'Reflex', h1s[1], `${h1s.length} h1 elements on the page; use one`, h1s.length);

    // --- Finish: lazy-default markers ---
    for (const x of rendered) {
      if (x.hidden || !x.el.textContent.trim()) continue;
      const clip = x.s.backgroundClip === 'text' || x.s.getPropertyValue('-webkit-background-clip') === 'text';
      if (clip && /gradient\(/.test(x.s.backgroundImage)) add('gradient-text', 'Finish', x.el, 'Gradient-filled text (a common lazy default)', x.s.backgroundImage.slice(0, 80));
    }
    const emoji = /(?![\u00A9\u00AE\u2122\u2139])\p{Extended_Pictographic}/u;
    for (const h of heads) { const m = h.textContent.match(emoji); if (m) add('emoji-heading', 'Finish', h, `Emoji in heading (a common lazy default): "${h.textContent.trim().slice(0, 50)}"`, m[0]); }

    // --- Reflex: reduced motion ---
    const ms = (v) => v.split(',').map((t) => { t = t.trim(); return t.endsWith('ms') ? parseFloat(t) : parseFloat(t) * 1000; });
    let motionEls = 0;
    for (const x of rendered) {
      const anim = x.s.animationName !== 'none' && ms(x.s.animationDuration).some((d) => d > 0);
      const trans = ms(x.s.transitionDuration).some((d) => d > 0);
      if (anim || trans) motionEls++;
    }
    let rmFound = false, unreadable = 0;
    const walk = (rules) => { for (const r of rules) { if (r.media && /prefers-reduced-motion/.test(r.media.mediaText || '')) rmFound = true; if (r.cssRules) walk(r.cssRules); } };
    for (const sh of document.styleSheets) {
      if (sh.media && /prefers-reduced-motion/.test(sh.media.mediaText)) rmFound = true;
      try { walk(sh.cssRules); } catch { unreadable++; }
    }
    metrics.motionElements = motionEls; metrics.reducedMotionRule = rmFound; metrics.unreadableStylesheets = unreadable;
    if (motionEls && !rmFound) add('reduced-motion', 'Reflex', null, `${motionEls} element(s) animate or transition, but no @media (prefers-reduced-motion) rule was found${unreadable ? ` (${unreadable} cross-origin stylesheet(s) could not be read)` : ''}`, motionEls);
  }
  return { findings, metrics };
}

// ---------- focus visibility via real Tab key presses ----------
function pagePrepareFocus() {
  const Q = 'a[href], button:not([disabled]), input:not([disabled]):not([type=hidden]), select:not([disabled]), textarea:not([disabled]), summary, [tabindex]:not([tabindex="-1"])';
  const snap = (el) => { const s = getComputedStyle(el); return { o: s.outlineStyle, ow: s.outlineWidth, oc: s.outlineColor, bs: s.boxShadow, bc: s.borderColor, bw: s.borderWidth, bg: s.backgroundColor, c: s.color, td: s.textDecorationLine, tf: s.transform }; };
  if (document.activeElement && document.activeElement !== document.body) document.activeElement.blur();
  window.__dlFocus = [...document.querySelectorAll(Q)].map((el) => ({ el, base: snap(el) }));
  window.__dlSnap = snap;
  return window.__dlFocus.length;
}
function pageCheckFocus() {
  document.getAnimations().forEach((a) => { try { a.finish(); } catch { /* infinite */ } });
  const el = document.activeElement;
  if (!el || el === document.body || el === document.documentElement) return null;
  const rec = window.__dlFocus.find((r) => r.el === el);
  const now = window.__dlSnap(el);
  const sel = (() => { if (el.id) return '#' + CSS.escape(el.id); const p = []; let e = el; while (e && e !== document.body && p.length < 4) { let s = e.localName + [...e.classList].slice(0, 2).map((c) => '.' + CSS.escape(c)).join(''); const par = e.parentElement; if (par) { const same = [...par.children].filter((c) => c.localName === e.localName); if (same.length > 1) s += `:nth-of-type(${same.indexOf(e) + 1})`; } p.unshift(s); if (e.id) break; e = par; } return p.join(' > '); })();
  const outline = now.o !== 'none' && parseFloat(now.ow) > 0 && !/rgba\(\d+, \d+, \d+, 0\)|transparent/.test(now.oc);
  if (outline) return { sel, visible: true, how: 'outline' };
  if (!rec) return { sel, visible: true, how: 'untracked' };
  const changed = ['bs', 'bc', 'bw', 'bg', 'c', 'td', 'tf'].filter((k) => now[k] !== rec.base[k]);
  return { sel, visible: changed.length > 0, how: changed.join(',') || 'none', outline: now.o };
}

async function focusFindings(cdp, maxTabs = 60) {
  await cdp.send('Emulation.setFocusEmulationEnabled', { enabled: true }).catch(() => {});
  const count = await evaluate(cdp, `(${pagePrepareFocus.toString()})()`);
  const findings = []; const seen = new Set(); let visited = 0;
  for (let i = 0; i < Math.min(maxTabs, count + 2); i++) {
    await cdp.send('Input.dispatchKeyEvent', { type: 'rawKeyDown', key: 'Tab', code: 'Tab', windowsVirtualKeyCode: 9, nativeVirtualKeyCode: 9 });
    await cdp.send('Input.dispatchKeyEvent', { type: 'keyUp', key: 'Tab', code: 'Tab', windowsVirtualKeyCode: 9, nativeVirtualKeyCode: 9 });
    const r = await evaluate(cdp, `(${pageCheckFocus.toString()})()`);
    if (!r) { if (visited) break; continue; }
    if (seen.has(r.sel)) break;
    seen.add(r.sel); visited++;
    if (!r.visible) findings.push({ rule: 'focus-outline', tier: 'Floor', selector: r.sel, message: 'Keyboard focus is invisible: outline-style is none and no other style changes on focus', value: r.outline });
  }
  await evaluate(cdp, 'document.activeElement && document.activeElement.blur(), scrollTo(0, 0), true');
  return { findings, focusablesReached: visited, focusables: count };
}

// ---------- report writers ----------
function mergeFindings(list) {
  const map = new Map();
  for (const f of list) {
    // Identical findings at several widths collapse into one entry with a widths list.
    // Overflow messages name the viewport width, so they stay separate per width.
    const key = [f.rule, f.selector, f.message, JSON.stringify(f.value)].join('|');
    if (map.has(key)) { const m = map.get(key); if (f.width != null && !m.widths.includes(f.width)) m.widths.push(f.width); continue; }
    map.set(key, { ...f, widths: f.width == null ? [] : [f.width] });
  }
  return [...map.values()];
}

function markdown(report) {
  const L = [];
  L.push(`# designlint report`, '', `- Target: ${report.target}`, `- Widths: ${report.widths.join(', ')} px`, `- Chrome: ${report.chrome}`,
    `- Result: **${report.summary.Floor ? 'FAIL' : 'PASS'}** (Floor ${report.summary.Floor}, Reflex ${report.summary.Reflex}, Finish ${report.summary.Finish})`, '');
  L.push('| Width | Page width | Spacing on 4px grid | Distinct colors | Contrast checks |', '| --- | --- | --- | --- | --- |');
  for (const w of report.widths) { const m = report.metrics[w]; L.push(`| ${w} | ${m.scrollWidth} | ${m.spacingOnGridPct}% of ${m.spacingValues} | ${m.distinctColors} | ${m.contrastChecked} (${m.contrastUnknownBackground} on images/gradients skipped) |`); }
  L.push('');
  for (const tier of TIERS) {
    const fs = report.findings.filter((f) => f.tier === tier);
    L.push(`## ${tier} (${fs.length})`, '');
    if (!fs.length) { L.push('None.', ''); continue; }
    L.push('| Rule | Widths | Selector | Message |', '| --- | --- | --- | --- |');
    for (const f of fs.slice(0, 60)) L.push(`| ${f.rule} | ${f.widths.length ? f.widths.join(', ') : 'all'} | \`${(f.selector || 'page').replace(/\|/g, '\\|')}\` | ${f.message.replace(/\|/g, '\\|')} |`);
    if (fs.length > 60) L.push('', `...and ${fs.length - 60} more in report.json.`);
    L.push('');
  }
  return L.join('\n');
}

export async function lint(target, { widths = [390, 768, 1024, 1440], out = 'out', height = 800, maxColors = 12 } = {}) {
  mkdirSync(out, { recursive: true });
  const { url, close: closeServer } = await resolveTarget(target);
  const cdp = await launch(undefined, { width: widths[0], height });
  const touchWidth = widths.includes(390) ? 390 : Math.min(...widths);
  const all = []; const metrics = {}; let focus = null;
  try {
    await loadPage(cdp, url);
    for (let i = 0; i < widths.length; i++) {
      const w = widths[i];
      await setWidth(cdp, w, height);
      const res = await evaluate(cdp, `(${pageAnalyze.toString()})(${JSON.stringify({ first: i === 0, touch: w === touchWidth, maxColors })})`);
      for (const f of res.findings) all.push({ ...f, width: ['font-families', 'img-alt', 'accessible-name', 'heading-skip', 'multiple-h1', 'gradient-text', 'emoji-heading', 'reduced-motion'].includes(f.rule) ? null : w });
      metrics[w] = res.metrics;
      if (i === 0) { focus = await focusFindings(cdp); for (const f of focus.findings) all.push({ ...f, width: null }); }
      writeFileSync(join(out, `shot-${w}.png`), await screenshot(cdp));
    }
  } finally {
    await cdp.close();
    await closeServer();
  }
  const findings = mergeFindings(all).sort((a, b) => TIERS.indexOf(a.tier) - TIERS.indexOf(b.tier) || a.rule.localeCompare(b.rule));
  const summary = Object.fromEntries(TIERS.map((t) => [t, findings.filter((f) => f.tier === t).length]));
  const shown = /^(https?|file):\/\//i.test(target) ? target : relative(process.cwd(), resolve(target)).split(sep).join('/');
  const report = { tool: 'designlint', version: '0.1.0', target: shown, url: /^https?:\/\/127\.0\.0\.1/.test(url) ? 'local file' : url, chrome: cdp.version,
    widths, summary, pass: summary.Floor === 0, focus: focus && { focusables: focus.focusables, reachedByTab: focus.focusablesReached },
    metrics, findings, screenshots: widths.map((w) => `shot-${w}.png`) };
  writeFileSync(join(out, 'report.json'), JSON.stringify(report, null, 2));
  writeFileSync(join(out, 'report.md'), markdown(report));
  return report;
}

// ---------- CLI ----------
if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  const opts = parseArgs(process.argv.slice(2));
  if (opts.help || !opts.target) {
    console.log('Usage: node designlint.mjs <url-or-html-file> [--widths 390,768,1024,1440] [--out out/] [--height 800]');
    process.exit(opts.help ? 0 : 2);
  }
  try {
    const r = await lint(opts.target, opts);
    console.log(`designlint: Floor ${r.summary.Floor}, Reflex ${r.summary.Reflex}, Finish ${r.summary.Finish} -> ${join(opts.out, 'report.md')}`);
    process.exit(r.summary.Floor ? 1 : 0);
  } catch (e) {
    console.error('designlint error:', e.message);
    process.exit(2);
  }
}
