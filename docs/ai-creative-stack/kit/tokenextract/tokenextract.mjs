#!/usr/bin/env node
// tokenextract: read a rendered page's design language from computed styles and write
// W3C DTCG tokens.json, tokens.css and a draft DESIGN.md.
// Usage: node tokenextract.mjs <url-or-html-file> [--out out/] [--width 1280] [--de 1.5] [--neutral-chroma 20]
// Node 22+, no npm dependencies. Uses the shared DevTools helper in fixtures/lib/cdp.mjs.
import { createServer } from 'node:http';
import { existsSync, mkdirSync, readFileSync, writeFileSync, statSync } from 'node:fs';
import { dirname, basename, extname, join, resolve, relative, sep } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const HERE = dirname(fileURLToPath(import.meta.url));
const { launch, evaluate } = await import(pathToFileURL(join(HERE, '..', '..', 'fixtures', 'lib', 'cdp.mjs')).href);

export const DRAFT_NOTE = 'draft, extracted — review before adopting; extract principles only from your own or permitted sites';

// ---------- loading ----------
const MIME = { '.html': 'text/html; charset=utf-8', '.htm': 'text/html; charset=utf-8', '.css': 'text/css', '.js': 'text/javascript', '.mjs': 'text/javascript',
  '.json': 'application/json', '.svg': 'image/svg+xml', '.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.gif': 'image/gif',
  '.webp': 'image/webp', '.avif': 'image/avif', '.woff': 'font/woff', '.woff2': 'font/woff2', '.ttf': 'font/ttf', '.otf': 'font/otf' };

async function resolveTarget(target) {
  if (/^(https?|file):\/\//i.test(target)) return { url: target, shown: target, close: async () => {} };
  const file = resolve(target);
  if (!existsSync(file)) throw new Error(`Not a URL or an existing file: ${target}`);
  const base = dirname(file);
  const server = createServer((req, res) => {
    const p = resolve(base, '.' + decodeURIComponent(new URL(req.url, 'http://x').pathname));
    if (!p.startsWith(base) || !existsSync(p) || statSync(p).isDirectory()) { res.writeHead(404); return res.end(); }
    res.writeHead(200, { 'content-type': MIME[extname(p).toLowerCase()] || 'application/octet-stream' });
    res.end(readFileSync(p));
  });
  await new Promise((ok) => server.listen(0, '127.0.0.1', ok));
  return { url: `http://127.0.0.1:${server.address().port}/${encodeURIComponent(basename(file))}`,
    shown: relative(process.cwd(), file).split(sep).join('/'), close: () => new Promise((ok) => server.close(ok)) };
}

async function loadPage(cdp, url) {
  await cdp.send('Page.enable');
  await cdp.send('Page.navigate', { url });
  const want = JSON.stringify(url);
  for (let i = 0; ; i++) {
    if (await evaluate(cdp, `location.href === ${want} && document.readyState === 'complete'`).catch(() => false)) break;
    if (i >= 300) throw new Error(`Page never finished loading: ${url}`);
    await new Promise((r) => setTimeout(r, 100));
  }
  await evaluate(cdp, 'document.fonts ? document.fonts.ready.then(() => true) : true');
  await evaluate(cdp, 'new Promise(r => requestAnimationFrame(() => requestAnimationFrame(() => r(true))))');
}

// ---------- in-page collection (serialized into the page) ----------
function pageCollect() {
  const SKIP = new Set(['SCRIPT', 'STYLE', 'NOSCRIPT', 'TEMPLATE', 'META', 'LINK', 'TITLE', 'HEAD', 'BR', 'WBR']);
  const canvas = document.createElement('canvas'); canvas.width = canvas.height = 1;
  const ctx = canvas.getContext('2d', { willReadFrequently: true });
  const cache = new Map();
  const rgba = (c) => {
    if (cache.has(c)) return cache.get(c);
    let out = null;
    if (c && c !== 'transparent' && c !== 'none' && !c.startsWith('url')) {
      const m = c.match(/^rgba?\(([^)]+)\)$/);
      if (m) { const p = m[1].split(/[\s,/]+/).filter(Boolean).map((v) => v.endsWith('%') ? parseFloat(v) / 100 : parseFloat(v)); out = [p[0], p[1], p[2], p.length > 3 ? p[3] : 1]; }
      else { ctx.clearRect(0, 0, 1, 1); ctx.fillStyle = '#000'; ctx.fillStyle = c; ctx.fillRect(0, 0, 1, 1); const d = ctx.getImageData(0, 0, 1, 1).data; out = [d[0], d[1], d[2], +(d[3] / 255).toFixed(3)]; }
      if (out && out[3] <= 0.001) out = null;
    }
    cache.set(c, out); return out;
  };
  const bump = (map, key, n = 1) => { map[key] = (map[key] || 0) + n; };
  const out = { colors: {}, pairs: {}, families: {}, sizes: {}, weights: {}, lineHeights: {}, letterSpacings: {}, styles: {}, spacing: {}, radii: {}, shadows: {},
    textShadows: {}, durations: {}, easings: {}, transitions: {}, maxWidths: {}, breakpoints: {}, keyframes: [], reducedMotion: false, unreadableSheets: 0, elements: 0, textElements: 0 };
  const addColor = (c, role, weight = 1, chars = 0) => { const p = rgba(c); if (!p) return; const k = p.join(','); const e = out.colors[k] || (out.colors[k] = { rgba: p, count: 0, area: 0, chars: 0, roles: {} }); e.count++; e.area += weight; e.chars += chars; bump(e.roles, role); };
  const directText = (el) => [...el.childNodes].filter((n) => n.nodeType === 3).map((n) => n.data).join('').replace(/\s+/g, ' ').trim().length;
  const ms = (v) => v.split(',').map((t) => { t = t.trim(); return t.endsWith('ms') ? parseFloat(t) : parseFloat(t) * 1000; });
  const splitTop = (v) => { const r = []; let d = 0, cur = ''; for (const ch of v) { if (ch === '(') d++; if (ch === ')') d--; if (ch === ',' && !d) { r.push(cur.trim()); cur = ''; } else cur += ch; } if (cur.trim()) r.push(cur.trim()); return r; };
  const bgOf = (el) => { // effective opaque background behind an element (ancestor walk)
    const layers = [];
    for (let e = el; e && e.nodeType === 1; e = e.parentElement) {
      const s = getComputedStyle(e);
      if (s.backgroundImage !== 'none') return null;
      const b = rgba(s.backgroundColor); if (b) { layers.push(b); if (b[3] >= 0.999) break; }
    }
    let bg = [255, 255, 255];
    for (let i = layers.length - 1; i >= 0; i--) { const a = layers[i][3]; bg = [0, 1, 2].map((j) => Math.round(layers[i][j] * a + bg[j] * (1 - a))); }
    return bg;
  };

  for (const el of document.body ? [document.documentElement, document.body, ...document.body.querySelectorAll('*')] : []) {
    if (SKIP.has(el.tagName)) continue;
    const s = getComputedStyle(el);
    if (s.display === 'none' || s.visibility === 'hidden') continue;
    const r = el.getBoundingClientRect();
    if (!el.getClientRects().length || r.width < 1 || r.height < 1) continue;
    out.elements++;
    const svgInner = el instanceof SVGElement && el.localName !== 'svg';
    const area = Math.min(r.width * r.height, 4e6);
    const text = !svgInner && directText(el);
    if (text) {
      out.textElements++;
      addColor(s.color, 'text', 0, text);
      const fg = rgba(s.color), bg = bgOf(el);
      if (fg && bg && fg[3] >= 0.999) bump(out.pairs, fg.slice(0, 3).join(',') + '|' + bg.join(','));
      bump(out.families, s.fontFamily);
      const fs = parseFloat(s.fontSize);
      bump(out.sizes, String(fs));
      bump(out.weights, s.fontWeight);
      const lh = s.lineHeight === 'normal' ? 'normal' : String(+(parseFloat(s.lineHeight) / fs).toFixed(2));
      bump(out.lineHeights, lh);
      if (s.letterSpacing !== 'normal' && parseFloat(s.letterSpacing)) bump(out.letterSpacings, s.letterSpacing);
      bump(out.styles, JSON.stringify([s.fontFamily, fs, s.fontWeight, lh, s.letterSpacing]));
    }
    addColor(s.backgroundColor, 'background', area);
    for (const side of ['Top', 'Right', 'Bottom', 'Left']) if (parseFloat(s[`border${side}Width`]) > 0 && s[`border${side}Style`] !== 'none') addColor(s[`border${side}Color`], 'border');
    if (svgInner) { addColor(s.fill, 'fill', area); if (s.stroke !== 'none') addColor(s.stroke, 'stroke'); }
    if (!svgInner) {
      const vals = [s.paddingTop, s.paddingRight, s.paddingBottom, s.paddingLeft, s.marginTop, s.marginBottom];
      if (s.marginLeft !== s.marginRight) vals.push(s.marginLeft, s.marginRight); // equal side margins are usually auto-centering
      if (/flex|grid/.test(s.display)) vals.push(s.rowGap, s.columnGap);
      for (const v of vals) { const n = Math.abs(parseFloat(v)); if (n && isFinite(n)) bump(out.spacing, String(+n.toFixed(2))); }
      for (const c of ['TopLeft', 'TopRight', 'BottomRight', 'BottomLeft']) { const v = s[`border${c}Radius`].split(' ')[0]; if (parseFloat(v)) bump(out.radii, v); }
      if (s.boxShadow !== 'none') bump(out.shadows, s.boxShadow);
      if (s.textShadow !== 'none') bump(out.textShadows, s.textShadow);
      if (s.maxWidth.endsWith('px')) bump(out.maxWidths, s.maxWidth);
    }
    const td = ms(s.transitionDuration), te = splitTop(s.transitionTimingFunction), tp = splitTop(s.transitionProperty), tdl = ms(s.transitionDelay);
    td.forEach((d, i) => { if (d > 0) { const e = te[i % te.length]; bump(out.durations, String(d)); bump(out.easings, e); bump(out.transitions, JSON.stringify([tp[i % tp.length], d, tdl[i % tdl.length] || 0, e])); } });
    if (s.animationName !== 'none') {
      const ad = ms(s.animationDuration), ae = splitTop(s.animationTimingFunction);
      ad.forEach((d, i) => { if (d > 0) { bump(out.durations, String(d)); bump(out.easings, ae[i % ae.length]); } });
    }
  }
  // Stylesheets: breakpoints, keyframes, reduced motion.
  const toPx = (n, u) => u === 'em' || u === 'rem' ? n * 16 : n;
  const walk = (rules) => {
    for (const r of rules) {
      const media = r.media ? (r.conditionText || r.media.mediaText || '') : '';
      if (media) {
        if (/prefers-reduced-motion/.test(media)) out.reducedMotion = true;
        for (const m of media.matchAll(/\((min|max)-width\s*:\s*([\d.]+)(px|em|rem)\)/g)) bump(out.breakpoints, `${m[1]}|${toPx(+m[2], m[3])}`);
        for (const m of media.matchAll(/width\s*(>=|>|<=|<)\s*([\d.]+)(px|em|rem)/g)) bump(out.breakpoints, `${m[1].startsWith('>') ? 'min' : 'max'}|${toPx(+m[2], m[3])}`);
        for (const m of media.matchAll(/([\d.]+)(px|em|rem)\s*(<=|<|>=|>)\s*width/g)) bump(out.breakpoints, `${m[3].startsWith('<') ? 'min' : 'max'}|${toPx(+m[1], m[2])}`);
      }
      if (r.type === CSSRule.KEYFRAMES_RULE) out.keyframes.push(r.name);
      if (r.cssRules) walk(r.cssRules);
    }
  };
  for (const sh of document.styleSheets) {
    if (sh.media && /prefers-reduced-motion/.test(sh.media.mediaText)) out.reducedMotion = true;
    try { walk(sh.cssRules); } catch { out.unreadableSheets++; }
  }
  out.title = document.title;
  return out;
}

// ---------- color science ----------
const lin = (v) => { v /= 255; return v <= 0.04045 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4); };
export function rgbToLab([r, g, b]) {
  const R = lin(r), G = lin(g), B = lin(b);
  const X = (0.4124564 * R + 0.3575761 * G + 0.1804375 * B) / 0.95047;
  const Y = (0.2126729 * R + 0.7151522 * G + 0.0721750 * B) / 1.0;
  const Z = (0.0193339 * R + 0.1191920 * G + 0.9503041 * B) / 1.08883;
  const f = (t) => t > 216 / 24389 ? Math.cbrt(t) : (24389 / 27 * t + 16) / 116;
  const fx = f(X), fy = f(Y), fz = f(Z);
  return [116 * fy - 16, 500 * (fx - fy), 200 * (fy - fz)];
}
// CIEDE2000 color difference, written from the published formula (Sharma, Wu, Dalal 2005).
export function deltaE2000([L1, a1, b1], [L2, a2, b2]) {
  const rad = Math.PI / 180, deg = 180 / Math.PI;
  const C1 = Math.hypot(a1, b1), C2 = Math.hypot(a2, b2), Cb = (C1 + C2) / 2;
  const G = 0.5 * (1 - Math.sqrt(Cb ** 7 / (Cb ** 7 + 25 ** 7)));
  const a1p = (1 + G) * a1, a2p = (1 + G) * a2;
  const C1p = Math.hypot(a1p, b1), C2p = Math.hypot(a2p, b2);
  const hue = (x, y) => { if (x === 0 && y === 0) return 0; const h = Math.atan2(y, x) * deg; return h < 0 ? h + 360 : h; };
  const h1p = hue(a1p, b1), h2p = hue(a2p, b2);
  const dLp = L2 - L1, dCp = C2p - C1p;
  let dhp = 0;
  if (C1p * C2p !== 0) { dhp = h2p - h1p; if (dhp > 180) dhp -= 360; else if (dhp < -180) dhp += 360; }
  const dHp = 2 * Math.sqrt(C1p * C2p) * Math.sin((dhp / 2) * rad);
  const Lbp = (L1 + L2) / 2, Cbp = (C1p + C2p) / 2;
  let hbp = h1p + h2p;
  if (C1p * C2p !== 0) hbp = Math.abs(h1p - h2p) <= 180 ? (h1p + h2p) / 2 : (h1p + h2p < 360 ? (h1p + h2p + 360) / 2 : (h1p + h2p - 360) / 2);
  const T = 1 - 0.17 * Math.cos((hbp - 30) * rad) + 0.24 * Math.cos(2 * hbp * rad) + 0.32 * Math.cos((3 * hbp + 6) * rad) - 0.20 * Math.cos((4 * hbp - 63) * rad);
  const dTheta = 30 * Math.exp(-(((hbp - 275) / 25) ** 2));
  const Rc = 2 * Math.sqrt(Cbp ** 7 / (Cbp ** 7 + 25 ** 7));
  const Sl = 1 + (0.015 * (Lbp - 50) ** 2) / Math.sqrt(20 + (Lbp - 50) ** 2);
  const Sc = 1 + 0.045 * Cbp, Sh = 1 + 0.015 * Cbp * T;
  const Rt = -Math.sin(2 * dTheta * rad) * Rc;
  return Math.sqrt((dLp / Sl) ** 2 + (dCp / Sc) ** 2 + (dHp / Sh) ** 2 + Rt * (dCp / Sc) * (dHp / Sh));
}
const hex = (c) => '#' + c.slice(0, 3).map((v) => Math.round(v).toString(16).padStart(2, '0')).join('');
const relLum = (c) => 0.2126 * lin(c[0]) + 0.7152 * lin(c[1]) + 0.0722 * lin(c[2]);
const contrast = (a, b) => { const x = relLum(a), y = relLum(b); return (Math.max(x, y) + 0.05) / (Math.min(x, y) + 0.05); };

// Greedy clustering: most frequent color first; each color joins the first cluster within the ΔE00 threshold and the same alpha.
// Clusters with Lab chroma below neutralChroma count as neutrals (this keeps tinted slates and grays out of the brand group).
export function clusterColors(entries, threshold = 1.5, neutralChroma = 20) {
  const sorted = [...entries].sort((a, b) => b.count - a.count || b.area - a.area);
  const clusters = [];
  for (const e of sorted) {
    const lab = rgbToLab(e.rgba);
    const hit = clusters.find((c) => Math.abs(c.rgba[3] - e.rgba[3]) < 0.05 && deltaE2000(c.lab, lab) < threshold);
    if (hit) { hit.count += e.count; hit.area += e.area; hit.chars += e.chars; hit.members.push(hex(e.rgba)); for (const [k, v] of Object.entries(e.roles)) hit.roles[k] = (hit.roles[k] || 0) + v; }
    else clusters.push({ rgba: e.rgba, lab, count: e.count, area: e.area, chars: e.chars, roles: { ...e.roles }, members: [hex(e.rgba)] });
  }
  for (const c of clusters) { c.chroma = Math.hypot(c.lab[1], c.lab[2]); c.group = c.chroma < neutralChroma ? 'neutral' : 'brand'; c.hex = hex(c.rgba); }
  return clusters;
}

// Merge near-equal numbers (within tol px or pct) into weighted centers.
export function clusterNumbers(counts, { tol = 1, pct = 0.04 } = {}) {
  const items = Object.entries(counts).map(([v, n]) => [parseFloat(v), n]).filter(([v]) => isFinite(v)).sort((a, b) => a[0] - b[0]);
  const out = [];
  for (const [v, n] of items) {
    const last = out[out.length - 1];
    if (last && v - last.max <= Math.max(tol, last.value * pct)) { last.sum += v * n; last.count += n; last.max = v; last.members.push(v); last.value = last.sum / last.count; }
    else out.push({ value: v, sum: v * n, count: n, max: v, members: [v] });
  }
  return out.map((c) => ({ value: +c.value.toFixed(2), count: c.count, members: c.members }));
}

export function detectBase(counts) {
  const total = Object.values(counts).reduce((a, b) => a + b, 0);
  for (const base of [8, 6, 5, 4, 3, 2]) {
    let on = 0;
    for (const [v, n] of Object.entries(counts)) { const r = parseFloat(v) % base; if (r < 0.05 || r > base - 0.05) on += n; }
    if (total && on / total >= 0.9) return { base, share: +(on / total).toFixed(3) };
  }
  return { base: null, share: 0 };
}

const EASE = { linear: [0, 0, 1, 1], ease: [0.25, 0.1, 0.25, 1], 'ease-in': [0.42, 0, 1, 1], 'ease-out': [0, 0, 0.58, 1], 'ease-in-out': [0.42, 0, 0.58, 1] };
export function easingToBezier(e) {
  if (EASE[e]) return EASE[e];
  const m = e.match(/^cubic-bezier\(([^)]+)\)$/);
  return m ? m[1].split(',').map((x) => +parseFloat(x).toFixed(3)) : null;
}

function parseShadow(v) {
  const layers = []; let d = 0, cur = '';
  for (const ch of v + ',') { if (ch === '(') d++; if (ch === ')') d--; if (ch === ',' && !d) { layers.push(cur.trim()); cur = ''; } else cur += ch; }
  return layers.filter(Boolean).map((l) => {
    const color = (l.match(/(rgba?\([^)]*\)|#[0-9a-f]{3,8}|[a-z]+\([^)]*\))/i) || ['rgba(0, 0, 0, 1)'])[0];
    const nums = l.replace(color, '').replace('inset', '').trim().split(/\s+/).filter(Boolean).map(parseFloat);
    const m = color.match(/\(([^)]+)\)/); const p = m ? m[1].split(/[\s,/]+/).map(parseFloat) : [0, 0, 0, 1];
    const dim = (n) => ({ value: n || 0, unit: 'px' });
    return { color: dtcgColor([p[0], p[1], p[2], p.length > 3 ? p[3] : 1]), offsetX: dim(nums[0]), offsetY: dim(nums[1]), blur: dim(nums[2]), spread: dim(nums[3]), inset: /\binset\b/.test(l) };
  });
}

function dtcgColor(c) {
  const v = { colorSpace: 'srgb', components: c.slice(0, 3).map((x) => +(x / 255).toFixed(4)), hex: hex(c) };
  if (c[3] !== undefined && c[3] < 1) v.alpha = +c[3].toFixed(3);
  return v;
}
const px = (n) => ({ value: +n, unit: 'px' });
const famList = (stack) => stack.split(',').map((f) => f.trim().replace(/^["']|["']$/g, ''));
const rank = (obj) => Object.entries(obj).sort((a, b) => b[1] - a[1]);

// ---------- build tokens from raw collection ----------
export function buildTokens(raw, { de = 1.5, neutralChroma = 20, source = '' } = {}) {
  const clusters = clusterColors(Object.values(raw.colors), de, neutralChroma);
  const ext = (o) => ({ 'kit.tokenextract': o });
  const T = { $description: `Design tokens extracted from computed styles (${DRAFT_NOTE}).`, $extensions: ext({ source, generated: new Date().toISOString().slice(0, 10) }) };

  T.color = { $type: 'color' };
  for (const group of ['brand', 'neutral']) {
    const list = clusters.filter((c) => c.group === group);
    if (!list.length) continue;
    T.color[group] = {};
    list.forEach((c, i) => { T.color[group][`${group}-${i + 1}`] = { $value: dtcgColor(c.rgba), $extensions: ext({ count: c.count, roles: c.roles, merged: c.members.length > 1 ? c.members : undefined }) }; });
  }

  const fams = rank(raw.families);
  T.font = { family: { $type: 'fontFamily' }, size: { $type: 'dimension' }, weight: { $type: 'fontWeight' }, lineHeight: { $type: 'number' } };
  fams.forEach(([stack, n], i) => { T.font.family[`family-${i + 1}`] = { $value: famList(stack), $extensions: ext({ count: n }) }; });
  const sizes = Object.keys(raw.sizes).map(Number).sort((a, b) => a - b);
  sizes.forEach((s, i) => { T.font.size[`size-${i + 1}`] = { $value: px(s), $extensions: ext({ count: raw.sizes[s] }) }; });
  Object.keys(raw.weights).map(Number).sort((a, b) => a - b).forEach((w) => { T.font.weight[`weight-${w}`] = { $value: w, $extensions: ext({ count: raw.weights[w] }) }; });
  Object.keys(raw.lineHeights).filter((l) => l !== 'normal').map(Number).sort((a, b) => a - b).forEach((l, i) => { T.font.lineHeight[`lineHeight-${i + 1}`] = { $value: l }; });

  T.typography = { $type: 'typography' };
  rank(raw.styles).slice(0, 8).forEach(([k, n], i) => {
    const [stack, size, weight, lh, ls] = JSON.parse(k);
    T.typography[`text-${i + 1}`] = { $value: { fontFamily: famList(stack), fontSize: px(size), fontWeight: +weight, lineHeight: lh === 'normal' ? 1.2 : +lh, letterSpacing: px(ls === 'normal' ? 0 : parseFloat(ls)) }, $extensions: ext({ count: n }) };
  });

  const space = clusterNumbers(raw.spacing, { tol: 0.5, pct: 0 });
  const base = detectBase(raw.spacing);
  T.space = { $type: 'dimension', $description: base.base ? `Base unit ${base.base}px (${Math.round(base.share * 100)}% of spacing values are multiples)` : 'No common base unit found' };
  space.forEach((s, i) => { T.space[`space-${i + 1}`] = { $value: px(s.value), $extensions: ext({ count: s.count }) }; });

  const radPx = Object.fromEntries(Object.entries(raw.radii).filter(([k]) => k.endsWith('px')));
  const radPct = Object.entries(raw.radii).filter(([k]) => k.endsWith('%'));
  T.radius = { $type: 'dimension' };
  clusterNumbers(radPx, { tol: 0.5, pct: 0 }).forEach((r, i) => { T.radius[`radius-${i + 1}`] = { $value: px(r.value), $extensions: ext({ count: r.count }) }; });
  if (radPct.length) T.radius['radius-round'] = { $value: px(9999), $description: `Source used percentage radii: ${radPct.map(([k]) => k).join(', ')}` };

  const shadows = rank(raw.shadows);
  if (shadows.length) { T.shadow = { $type: 'shadow' }; shadows.forEach(([v, n], i) => { const l = parseShadow(v); T.shadow[`shadow-${i + 1}`] = { $value: l.length === 1 ? l[0] : l, $extensions: ext({ count: n, css: v }) }; }); }

  const bps = Object.entries(raw.breakpoints).map(([k, n]) => { const [kind, v] = k.split('|'); return { kind, value: +v, count: n }; });
  const bpVals = [...new Set(bps.map((b) => Math.round(b.kind === 'max' && !Number.isInteger(b.value) ? Math.ceil(b.value) : b.value)))].sort((a, b) => a - b);
  if (bpVals.length) { T.breakpoint = { $type: 'dimension', $description: 'From @media width conditions in same-origin stylesheets' }; bpVals.forEach((v, i) => { T.breakpoint[`breakpoint-${i + 1}`] = { $value: px(v), $extensions: ext({ queries: bps.filter((b) => Math.round(b.value) === v || Math.ceil(b.value) === v).map((b) => `${b.kind}-width ${b.value}px`) }) }; }); }

  const durs = Object.keys(raw.durations).map(Number).sort((a, b) => a - b);
  if (durs.length) { T.duration = { $type: 'duration' }; durs.forEach((d, i) => { T.duration[`duration-${i + 1}`] = { $value: { value: d, unit: 'ms' }, $extensions: ext({ count: raw.durations[d] }) }; }); }
  const eases = rank(raw.easings);
  if (eases.length) {
    T.easing = { $type: 'cubicBezier' };
    eases.forEach(([e, n], i) => { const b = easingToBezier(e); T.easing[`easing-${i + 1}`] = b ? { $value: b, $extensions: ext({ css: e, count: n }) } : { $value: [0, 0, 1, 1], $description: `Not a cubic Bézier in source: ${e}`, $extensions: ext({ css: e, count: n }) }; });
  }
  const trans = rank(raw.transitions);
  if (trans.length) {
    T.transition = { $type: 'transition' };
    trans.slice(0, 8).forEach(([k, n], i) => { const [prop, d, delay, e] = JSON.parse(k); T.transition[`transition-${i + 1}`] = { $value: { duration: { value: d, unit: 'ms' }, delay: { value: delay, unit: 'ms' }, timingFunction: easingToBezier(e) || [0, 0, 1, 1] }, $extensions: ext({ property: prop, css: e, count: n }) }; });
  }
  return { tokens: T, clusters, space, base, bpVals, durs, eases };
}

// ---------- tokens.css ----------
function toCss(T) {
  const L = [`/* ${DRAFT_NOTE} */`, ':root {'];
  const val = (type, v) => {
    if (type === 'color') return v.alpha !== undefined ? `rgb(${v.components.map((c) => Math.round(c * 255)).join(' ')} / ${v.alpha})` : v.hex;
    if (type === 'dimension' || type === 'duration') return `${v.value}${v.unit}`;
    if (type === 'fontFamily') return v.map((f) => /\s/.test(f) ? `"${f}"` : f).join(', ');
    if (type === 'cubicBezier') return `cubic-bezier(${v.join(', ')})`;
    if (type === 'shadow') return (Array.isArray(v) ? v : [v]).map((s) => `${s.inset ? 'inset ' : ''}${s.offsetX.value}px ${s.offsetY.value}px ${s.blur.value}px ${s.spread.value}px ${val('color', s.color)}`).join(', ');
    if (type === 'typography') return `${v.fontWeight} ${v.fontSize.value}px/${v.lineHeight} ${val('fontFamily', v.fontFamily)}`;
    if (type === 'transition') return `${v.duration.value}ms cubic-bezier(${v.timingFunction.join(', ')}) ${v.delay.value}ms`;
    return String(v);
  };
  const walk = (node, type, path) => {
    for (const [k, v] of Object.entries(node)) {
      if (k.startsWith('$')) continue;
      const t = v.$type || type;
      if (v.$value !== undefined) {
        const name = k.startsWith(path.at(-1) + '-') ? [...path.slice(0, -1), k] : [...path, k];
        if (path[0] === 'breakpoint' && k.endsWith('-1')) L.push('  /* Breakpoints: custom properties cannot be used inside @media; values kept for reference. */');
        L.push(`  --${name.join('-').replace(/[A-Z]/g, (c) => '-' + c.toLowerCase())}: ${val(t, v.$value)};`);
      } else walk(v, t, [...path, k]);
    }
  };
  walk(T, undefined, []);
  L.push('}', '');
  return L.join('\n');
}

// ---------- DESIGN.md draft (section structure of templates/design-system.md) ----------
export const TEMPLATE_SECTIONS = ['Identity', 'Typography', 'Color tokens', 'Spacing and layout', 'Composition', 'Illustration language', 'Material language (3D)',
  'Lighting direction (3D and renders)', 'Motion rules', 'Accessibility', 'Approved references', 'Prohibited visual patterns', 'Change log'];

function designMd(raw, b, source) {
  const { clusters, space, base, bpVals, durs, eases } = b;
  const L = [];
  const fams = rank(raw.families);
  const styles = rank(raw.styles).map(([k, n]) => { const [stack, size, weight, lh] = JSON.parse(k); return { stack, size, weight, lh, n }; });
  const body = styles[0];
  const display = [...styles].sort((a, b) => b.size - a.size)[0];
  const mono = fams.find(([f]) => /mono|courier|consolas|menlo/i.test(f));
  const bgs = clusters.filter((c) => c.roles.background).sort((a, b) => b.area - a.area);
  const texts = clusters.filter((c) => c.roles.text).sort((a, b) => b.chars - a.chars);
  const bg = bgs[0], fg = texts[0], accent = clusters.find((c) => c.group === 'brand');
  const lhTxt = (s) => s.lh === 'normal' ? 'normal' : `${Math.round(s.size * s.lh * 10) / 10} px (${s.lh})`;

  L.push('# DESIGN.md (draft)', '', `> **Status: ${DRAFT_NOTE}.**`, `> Generated by kit/tokenextract from \`${source}\` on ${new Date().toISOString().slice(0, 10)}. Numbers come from computed styles at one viewport width; names and intent are not inferred. A person must fill in the blanks and approve before this becomes the authority.`, '');
  L.push('## Identity', '', `- **Name and purpose** _To fill in._ Page title: "${raw.title || 'untitled'}".`, '- **Personality** _To fill in: three adjectives it is, and three it must never be._', '- **Signature** _To fill in: the one element people should remember._', '');
  L.push('## Typography', '', '| Role | Family | Weight | Size / line height | License |', '| --- | --- | --- | --- | --- |');
  if (display) L.push(`| Display | \`${display.stack}\` | ${display.weight} | ${display.size} px / ${lhTxt(display)} | Unknown, confirm |`);
  if (body) L.push(`| Body | \`${body.stack}\` | ${body.weight} | ${body.size} px / ${lhTxt(body)} | Unknown, confirm |`);
  L.push(`| Mono | ${mono ? '`' + mono[0] + '`' : 'None found'} | | | |`, '');
  L.push(`Families by use: ${fams.map(([f, n]) => `\`${f}\` (${n})`).join(', ') || 'none'}.`, `Sizes: ${Object.keys(raw.sizes).map(Number).sort((a, b) => a - b).join(', ')} px. Weights: ${Object.keys(raw.weights).sort().join(', ')}.`, '');
  L.push('## Color tokens', '', '| Token | Light | Dark | Use | Contrast checked against |', '| --- | --- | --- | --- | --- |');
  if (bg) L.push(`| \`--bg\` | \`${bg.hex}\` | _not extracted_ | Page (largest background area) | — |`);
  if (fg) L.push(`| \`--fg\` | \`${fg.hex}\` | _not extracted_ | Text color covering the most characters | ${bg ? `\`--bg\`, ${contrast(fg.rgba, bg.rgba).toFixed(2)}:1` : '—'} |`);
  if (accent) L.push(`| \`--accent\` | \`${accent.hex}\` | _not extracted_ | Most used chromatic color (${Object.keys(accent.roles).join(', ')}) | ${bg ? `\`--bg\`, ${contrast(accent.rgba, bg.rgba).toFixed(2)}:1` : '—'} |`);
  for (const c of clusters) {
    if (c === bg || c === fg || c === accent) continue;
    L.push(`| \`--color-${c.group}-${clusters.filter((x) => x.group === c.group).indexOf(c) + 1}\` | \`${c.hex}\`${c.rgba[3] < 1 ? ` at ${c.rgba[3]} alpha` : ''} | _not extracted_ | ${Object.entries(c.roles).map(([r, n]) => `${r} ${n}`).join(', ')} | ${bg ? `\`--bg\`, ${contrast(c.rgba, bg.rgba).toFixed(2)}:1` : '—'} |`);
  }
  const merged = clusters.filter((c) => c.members.length > 1);
  if (merged.length) L.push('', `Near-duplicates merged (CIEDE2000 below the threshold): ${merged.map((c) => `${c.members.join(' + ')} → ${c.hex}`).join('; ')}.`);
  L.push('', '## Spacing and layout', '', `Spacing scale: ${space.map((s) => s.value).join(', ')} px.`, base.base ? `Base unit: ${base.base} px (${Math.round(base.share * 100)}% of values are multiples).` : 'No common base unit: spacing does not follow one grid.',
    `Breakpoints: ${bpVals.length ? bpVals.map((v) => v + ' px').join(', ') : 'none found in same-origin stylesheets'}.`, `Maximum widths: ${Object.keys(raw.maxWidths).join(', ') || 'none set'}.`,
    `Radii: ${Object.keys(raw.radii).sort((a, b) => parseFloat(a) - parseFloat(b)).join(', ') || 'none'}. Shadows: ${Object.keys(raw.shadows).length} distinct.`, '');
  L.push('## Composition', '', '_Not extracted. Describe the focal point, alignment, density and empty space after looking at the page._', '');
  L.push('## Illustration language', '', '_Not extracted from CSS._', '');
  L.push('## Material language (3D)', '', '_Not applicable or not extracted._', '');
  L.push('## Lighting direction (3D and renders)', '', '_Not applicable or not extracted._', '');
  L.push('## Motion rules', '', `Durations: ${durs.length ? durs.map((d) => d + ' ms').join(', ') : 'none'}. Easings: ${eases.map(([e]) => `\`${e}\``).join(', ') || 'none'}.`,
    `Animated properties: ${[...new Set(Object.keys(raw.transitions).map((k) => JSON.parse(k)[0]))].join(', ') || 'none'}. Keyframes: ${raw.keyframes.join(', ') || 'none'}.`,
    `Reduced motion: ${raw.reducedMotion ? 'a `prefers-reduced-motion` rule exists' : '**no `prefers-reduced-motion` rule found** — write one'}.`, '');
  L.push('## Accessibility', '', 'Text and background pairs seen on the page:', '', '| Text | Background | Ratio | Uses |', '| --- | --- | --- | --- |');
  for (const [k, n] of rank(raw.pairs).slice(0, 8)) { const [a, b2] = k.split('|').map((s) => s.split(',').map(Number)); const r = contrast(a, b2); L.push(`| \`${hex(a)}\` | \`${hex(b2)}\` | ${r.toFixed(2)}:1${r < 4.5 ? ' (below 4.5)' : ''} | ${n} |`); }
  L.push('', '_Focus style, touch targets and captions are not extracted. Run kit/designlint for those._', '');
  L.push('## Approved references', '', '| Reference | Rights status | What we take from it |', '| --- | --- | --- |', `| \`${source}\` | Unconfirmed. Extract principles only from your own or permitted sites. | Measured tokens above, pending review |`, '');
  L.push('## Prohibited visual patterns', '', '_To fill in._ Do not adopt another brand\'s palette, type pairing or signature element wholesale.', '');
  L.push('## Change log', '', '| Date | Change | Approved by |', '| --- | --- | --- |', `| ${new Date().toISOString().slice(0, 10)} | Draft extracted by kit/tokenextract | Not approved |`, '');
  return L.join('\n');
}

export async function extract(target, { out = 'out', width = 1280, height = 800, de = 1.5, neutralChroma = 20 } = {}) {
  mkdirSync(out, { recursive: true });
  const { url, shown, close } = await resolveTarget(target);
  const cdp = await launch(undefined, { width, height });
  let raw;
  try {
    await loadPage(cdp, url);
    raw = await evaluate(cdp, `(${pageCollect.toString()})()`);
  } finally { await cdp.close(); await close(); }
  const b = buildTokens(raw, { de, neutralChroma, source: shown });
  writeFileSync(join(out, 'tokens.json'), JSON.stringify(b.tokens, null, 2));
  writeFileSync(join(out, 'tokens.css'), toCss(b.tokens));
  writeFileSync(join(out, 'DESIGN.md'), designMd(raw, b, shown));
  writeFileSync(join(out, 'raw.json'), JSON.stringify({ source: shown, width, chrome: cdp.version, ...raw }, null, 1));
  return { raw, ...b };
}

if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  const a = process.argv.slice(2); const opts = { out: 'out', width: 1280, de: 1.5 }; let target = null;
  for (let i = 0; i < a.length; i++) {
    if (a[i] === '--out') opts.out = a[++i]; else if (a[i] === '--width') opts.width = +a[++i]; else if (a[i] === '--de') opts.de = +a[++i]; else if (a[i] === '--neutral-chroma') opts.neutralChroma = +a[++i];
    else if (!target && !a[i].startsWith('-')) target = a[i];
  }
  if (!target) { console.log('Usage: node tokenextract.mjs <url-or-html-file> [--out out/] [--width 1280] [--de 1.5] [--neutral-chroma 20]'); process.exit(2); }
  try {
    const r = await extract(target, opts);
    console.log(`tokenextract: ${r.clusters.length} colors, ${Object.keys(r.raw.families).length} families, ${r.space.length} spacing steps, ${r.bpVals.length} breakpoints -> ${opts.out}`);
  } catch (e) { console.error('tokenextract error:', e.message); process.exit(2); }
}
