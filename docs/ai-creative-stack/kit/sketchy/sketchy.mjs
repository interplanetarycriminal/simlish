// sketchy.mjs: hand-drawn looking SVG shapes from a seeded generator.
// No dependencies. Works in Node and in the browser.
//
//   import { createGenerator, toSvg } from './sketchy.mjs';
//   const g = createGenerator(7);
//   const box = g.rectangle(20, 20, 200, 120, { fill: '#f6c', fillStyle: 'hachure' });
//   const svg = toSvg([box], { width: 240, height: 160 });
//
// Every shape returns { shape, options, sets }, where sets is a list of
// { type: 'stroke' | 'fill', d } holding SVG path data strings.

const DEFAULTS = {
  roughness: 1,        // 0 = clean geometry; 1 = light hand jitter; 3 = very loose
  bowing: 1,           // how much a straight line bends in the middle
  stroke: '#222',
  strokeWidth: 1.5,
  fill: null,          // fill line color; null = no fill
  fillStyle: 'hachure',// 'hachure' | 'zigzag' | 'none'
  fillWeight: null,    // fill line width; defaults to strokeWidth / 2
  hachureAngle: -50,   // degrees
  hachureGap: 8,       // px between fill lines
  passes: 2,           // strokes per outline (two slightly different pens)
  curveSteps: 16,      // samples per curve when a path is flattened for fill
  seed: null,          // per-shape seed; null = take the next values from the generator stream
};

// ---------- seeded random ----------

function mixSeed(seed) {
  // Scramble the seed so nearby seeds (1, 2, 3) give unrelated streams.
  let h = (Number(seed) | 0) ^ 0x2c1b3c6d;
  h = Math.imul(h ^ (h >>> 16), 0x297a2d39);
  h = Math.imul(h ^ (h >>> 15), 0x5f356495);
  h ^= h >>> 16;
  return (h >>> 0) || 0x1f123bb5;
}

export function randomStream(seed) {
  let s = mixSeed(seed);
  // xorshift32: small, fast and fully deterministic across engines.
  return () => {
    s ^= s << 13; s >>>= 0;
    s ^= s >>> 17;
    s ^= s << 5; s >>>= 0;
    return s / 4294967296;
  };
}

// ---------- number formatting ----------

const f = (n) => {
  const r = Math.round(n * 100) / 100;
  return Object.is(r, -0) ? '0' : String(r);
};
const pt = (p) => `${f(p[0])} ${f(p[1])}`;

// ---------- geometry helpers ----------

const lerp = (a, b, t) => [a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t];
const dist = (a, b) => Math.hypot(b[0] - a[0], b[1] - a[1]);
const rotate = (p, c, s) => [p[0] * c - p[1] * s, p[0] * s + p[1] * c];

export function cubicAt(p0, c1, c2, p3, t) {
  const u = 1 - t;
  const a = u * u * u, b = 3 * u * u * t, c = 3 * u * t * t, d = t * t * t;
  return [a * p0[0] + b * c1[0] + c * c2[0] + d * p3[0], a * p0[1] + b * c1[1] + c * c2[1] + d * p3[1]];
}

/** Even-odd point-in-polygon over several rings. */
export function insidePolygons(p, rings) {
  let inside = false;
  for (const ring of rings) {
    for (let i = 0, j = ring.length - 1; i < ring.length; j = i++) {
      const a = ring[i], b = ring[j];
      if ((a[1] > p[1]) !== (b[1] > p[1]) && p[0] < ((b[0] - a[0]) * (p[1] - a[1])) / (b[1] - a[1]) + a[0]) inside = !inside;
    }
  }
  return inside;
}

/**
 * How far a rough line of length `len` may stray, for roughness r and bowing b.
 * endpoint: max distance of a drawn end from the true end.
 * curve: max distance of any drawn point from the true segment.
 */
export function strayBounds(len, roughness = DEFAULTS.roughness, bowing = DEFAULTS.bowing) {
  const j = jitterFor(len, roughness);
  const bow = bowFor(len, roughness, bowing);
  return { jitter: j, endpoint: j * Math.SQRT2, curve: bow + j * 1.5 + j * Math.SQRT2 };
}
const jitterFor = (len, r) => r * Math.max(0.5, Math.min(2, len / 100));
const bowFor = (len, r, b) => (b * r * len) / 200;

// ---------- SVG path parsing (M L H V C Q Z, absolute and relative) ----------

export function parsePath(d) {
  const tokens = d.match(/[MLHVCQZmlhvcqz]|[-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?/g) || [];
  const out = []; // absolute commands: { cmd: 'M'|'L'|'C'|'Z', pts: [[x,y]...] }
  let i = 0, cmd = null, cur = [0, 0], start = [0, 0];
  const num = () => {
    const v = Number(tokens[i++]);
    if (!Number.isFinite(v)) throw new Error(`Bad number in path near token ${i}`);
    return v;
  };
  const isNum = () => i < tokens.length && !/^[A-Za-z]$/.test(tokens[i]);
  while (i < tokens.length) {
    if (/^[A-Za-z]$/.test(tokens[i])) cmd = tokens[i++];
    else if (!cmd) throw new Error('Path must start with a command');
    const rel = cmd === cmd.toLowerCase();
    const C = cmd.toUpperCase();
    const abs = (x, y) => (rel ? [cur[0] + x, cur[1] + y] : [x, y]);
    if (C === 'Z') { out.push({ cmd: 'Z', pts: [start.slice()] }); cur = start.slice(); continue; }
    if (!isNum()) throw new Error(`Command ${cmd} has no numbers`);
    if (C === 'M') {
      cur = abs(num(), num()); start = cur.slice(); out.push({ cmd: 'M', pts: [cur.slice()] });
      cmd = rel ? 'l' : 'L'; // extra pairs after M are line-tos
    } else if (C === 'L') {
      cur = abs(num(), num()); out.push({ cmd: 'L', pts: [cur.slice()] });
    } else if (C === 'H') {
      const x = num(); cur = [rel ? cur[0] + x : x, cur[1]]; out.push({ cmd: 'L', pts: [cur.slice()] });
    } else if (C === 'V') {
      const y = num(); cur = [cur[0], rel ? cur[1] + y : y]; out.push({ cmd: 'L', pts: [cur.slice()] });
    } else if (C === 'C') {
      const c1 = abs(num(), num()), c2 = abs(num(), num()), p = abs(num(), num());
      out.push({ cmd: 'C', pts: [c1, c2, p] }); cur = p;
    } else if (C === 'Q') {
      const q = abs(num(), num()), p = abs(num(), num());
      // Exact quadratic-to-cubic conversion.
      const c1 = lerp(cur, q, 2 / 3), c2 = lerp(p, q, 2 / 3);
      out.push({ cmd: 'C', pts: [c1, c2, p] }); cur = p;
    } else throw new Error(`Unsupported path command ${cmd}`);
  }
  return out;
}

/** Flatten parsed path commands into closed rings (for fill). */
function flatten(cmds, steps) {
  const rings = []; let ring = null, cur = [0, 0];
  for (const c of cmds) {
    if (c.cmd === 'M') { if (ring && ring.length > 2) rings.push(ring); ring = [c.pts[0]]; cur = c.pts[0]; }
    else if (c.cmd === 'L') { ring ||= [cur]; ring.push(c.pts[0]); cur = c.pts[0]; }
    else if (c.cmd === 'C') {
      ring ||= [cur];
      for (let k = 1; k <= steps; k++) ring.push(cubicAt(cur, c.pts[0], c.pts[1], c.pts[2], k / steps));
      cur = c.pts[2];
    } else if (c.cmd === 'Z') { if (ring && ring.length > 2) rings.push(ring); ring = null; cur = c.pts[0]; }
  }
  if (ring && ring.length > 2) rings.push(ring);
  return rings;
}

// ---------- the generator ----------

export function createGenerator(seed = 1, defaults = {}) {
  const base = { ...DEFAULTS, ...defaults };
  const stream = randomStream(seed);

  const begin = (opts) => {
    const o = { ...base, ...opts };
    const rnd = o.seed == null ? stream : randomStream(o.seed);
    const range = (a, b) => a + (b - a) * rnd();
    const sym = (m) => (rnd() * 2 - 1) * m;
    return { o, rnd, range, sym };
  };

  // One pen pass along a straight segment, as a cubic. Returns [p0, c1, c2, p3].
  function roughSegment(ctx, a, b, pass, scale = 1) {
    const { o, range, sym } = ctx;
    const len = dist(a, b);
    if (len < 1e-9 || o.roughness <= 0) return [a, lerp(a, b, 1 / 3), lerp(a, b, 2 / 3), b];
    const r = o.roughness * scale;
    const j = jitterFor(len, r) * (pass === 0 ? 1 : 0.7);
    const bowMax = bowFor(len, r, o.bowing) * (pass === 0 ? 1 : 0.8);
    const nx = -(b[1] - a[1]) / len, ny = (b[0] - a[0]) / len;
    const bow = sym(bowMax);
    const p0 = [a[0] + sym(j), a[1] + sym(j)];
    const p3 = [b[0] + sym(j), b[1] + sym(j)];
    const at = (t, k) => {
      const q = lerp(p0, p3, t);
      const off = bow * k + sym(j * 0.5);
      return [q[0] + nx * off, q[1] + ny * off];
    };
    return [p0, at(range(0.2, 0.35), 1), at(range(0.65, 0.8), range(0.6, 1)), p3];
  }

  const segD = (s) => `M${pt(s[0])} C${pt(s[1])} ${pt(s[2])} ${pt(s[3])}`;

  function outlineFromSegments(ctx, segs) {
    const parts = [];
    for (let pass = 0; pass < ctx.o.passes; pass++) {
      for (const [a, b] of segs) parts.push(segD(roughSegment(ctx, a, b, pass)));
    }
    return parts.join(' ');
  }

  // Scanline fill: returns straight segments [[x,y],[x,y]] inside the rings (even-odd).
  function scanlines(rings, angleDeg, gap) {
    const th = (angleDeg * Math.PI) / 180;
    const c = Math.cos(-th), s = Math.sin(-th);
    const rr = rings.map((r) => r.map((p) => rotate(p, c, s)));
    let ymin = Infinity, ymax = -Infinity;
    for (const r of rr) for (const p of r) { ymin = Math.min(ymin, p[1]); ymax = Math.max(ymax, p[1]); }
    const rows = [];
    const back = (p) => rotate(p, Math.cos(th), Math.sin(th));
    for (let y = ymin + gap / 2; y < ymax; y += gap) {
      const xs = [];
      for (const r of rr) {
        for (let i = 0, k = r.length - 1; i < r.length; k = i++) {
          const a = r[k], b = r[i];
          if ((a[1] <= y) !== (b[1] <= y)) xs.push(a[0] + ((y - a[1]) * (b[0] - a[0])) / (b[1] - a[1]));
        }
      }
      xs.sort((p, q) => p - q);
      const spans = [];
      for (let k = 0; k + 1 < xs.length; k += 2) if (xs[k + 1] - xs[k] > 1e-6) spans.push([xs[k], xs[k + 1]]);
      rows.push({ y, spans, back });
    }
    return rows;
  }

  // Draw one fill segment roughly, but keep it inside the shape: inset the ends, then verify by
  // sampling and fall back to calmer pens, and finally to the exact straight line.
  function containedSegment(ctx, rings, a, b, inset = Math.min(dist(a, b) * 0.2, 1 + jitterFor(dist(a, b), ctx.o.roughness * 0.5))) {
    const len = dist(a, b);
    if (len - 2 * inset < 0.5) return null;
    const a2 = lerp(a, b, inset / len), b2 = lerp(a, b, 1 - inset / len);
    for (const scale of inset > 0 ? [0.5, 0.25, 0.1] : [0.25, 0.1, 0.03]) {
      const seg = roughSegment(ctx, a2, b2, 0, scale);
      let ok = true;
      for (let k = 0; k <= 24 && ok; k++) ok = insidePolygons(cubicAt(...seg, k / 24), rings);
      if (ok) return seg;
    }
    const mid = insidePolygons(lerp(a2, b2, 0.5), rings);
    return mid ? [a2, lerp(a2, b2, 1 / 3), lerp(a2, b2, 2 / 3), b2] : null;
  }

  function fillPaths(ctx, rings) {
    const { o } = ctx;
    if (!o.fill || o.fillStyle === 'none' || !rings.length) return null;
    const gap = Math.max(1, o.hachureGap);
    const rows = scanlines(rings, o.hachureAngle, gap);
    const parts = [];
    if (o.fillStyle === 'hachure') {
      for (const row of rows) {
        for (const [x0, x1] of row.spans) {
          const seg = containedSegment(ctx, rings, row.back([x0, row.y]), row.back([x1, row.y]));
          if (seg) parts.push(segD(seg));
        }
      }
    } else if (o.fillStyle === 'zigzag') {
      // Diagonal teeth between neighbouring scan rows, wherever their spans overlap.
      for (let r = 0; r + 1 < rows.length; r++) {
        const A = rows[r], B = rows[r + 1];
        for (const [a0, a1] of A.spans) {
          for (const [b0, b1] of B.spans) {
            // Keep the tooth tips a little away from the outline so the chain stays inside.
            const lo = Math.max(a0, b0) + 1.5, hi = Math.min(a1, b1) - 1.5;
            if (hi - lo < gap * 0.5) continue;
            const step = gap / 2;
            let x = lo, up = true;
            while (x + step <= hi + 1e-9) {
              const p = A.back([x, up ? A.y : B.y]);
              const q = A.back([x + step, up ? B.y : A.y]);
              const seg = containedSegment(ctx, rings, p, q, 0);
              if (seg) parts.push(segD(seg));
              x += step; up = !up;
            }
          }
        }
      }
    } else throw new Error(`Unknown fillStyle ${o.fillStyle}`);
    return parts.length ? parts.join(' ') : null;
  }

  function finish(shape, ctx, strokeD, rings) {
    const sets = [];
    const fd = fillPaths(ctx, rings);
    if (fd) sets.push({ type: 'fill', d: fd });
    if (strokeD) sets.push({ type: 'stroke', d: strokeD });
    return { shape, options: ctx.o, sets };
  }

  function polygonDrawable(shape, points, opts, closed = true) {
    const ctx = begin(opts);
    const segs = [];
    for (let i = 0; i + 1 < points.length; i++) segs.push([points[i], points[i + 1]]);
    if (closed && points.length > 2) segs.push([points[points.length - 1], points[0]]);
    return finish(shape, ctx, outlineFromSegments(ctx, segs), closed ? [points] : []);
  }

  // Smooth closed-ish curve through points (Catmull-Rom converted to cubic segments).
  function smoothThrough(pts) {
    let d = `M${pt(pts[0])}`;
    for (let i = 0; i + 1 < pts.length; i++) {
      const p0 = pts[Math.max(0, i - 1)], p1 = pts[i], p2 = pts[i + 1], p3 = pts[Math.min(pts.length - 1, i + 2)];
      const c1 = [p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6];
      const c2 = [p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6];
      d += ` C${pt(c1)} ${pt(c2)} ${pt(p2)}`;
    }
    return d;
  }

  return {
    options: base,

    line(x1, y1, x2, y2, opts = {}) {
      return polygonDrawable('line', [[x1, y1], [x2, y2]], { ...opts, fill: null }, false);
    },

    rectangle(x, y, w, h, opts = {}) {
      return polygonDrawable('rectangle', [[x, y], [x + w, y], [x + w, y + h], [x, y + h]], opts);
    },

    polygon(points, opts = {}) {
      if (points.length < 2) throw new Error('polygon needs at least two points');
      return polygonDrawable('polygon', points.map((p) => [p[0], p[1]]), opts);
    },

    ellipse(cx, cy, w, h, opts = {}) {
      const ctx = begin(opts);
      const { o, range, sym } = ctx;
      const rx = Math.abs(w) / 2, ry = Math.abs(h) / 2;
      const perim = Math.PI * (3 * (rx + ry) - Math.sqrt((3 * rx + ry) * (rx + 3 * ry)));
      const n = Math.max(8, Math.min(24, Math.round(perim / 40)));
      const ringPts = (steps) => Array.from({ length: steps }, (_, k) => {
        const a = (k / steps) * Math.PI * 2;
        return [cx + rx * Math.cos(a), cy + ry * Math.sin(a)];
      });
      const parts = [];
      for (let pass = 0; pass < o.passes; pass++) {
        const wob = o.roughness * 0.025 * (pass === 0 ? 1 : 0.7);
        const a0 = range(0, Math.PI * 2);
        const overlap = o.roughness > 0 ? range(0.15, 0.45) : 0; // the pen runs a little past its start
        const total = Math.PI * 2 + overlap;
        const steps = Math.ceil(n * (total / (Math.PI * 2)));
        const pts = [];
        for (let k = 0; k <= steps; k++) {
          const a = a0 + (k / steps) * total;
          const kr = 1 + sym(wob);
          pts.push([cx + rx * kr * Math.cos(a) + sym(o.roughness * 0.5), cy + ry * kr * Math.sin(a) + sym(o.roughness * 0.5)]);
        }
        parts.push(smoothThrough(pts));
      }
      return finish('ellipse', ctx, parts.join(' '), [ringPts(96)]);
    },

    path(d, opts = {}) {
      const ctx = begin(opts);
      const { o, sym } = ctx;
      const cmds = parsePath(d);
      const parts = [];
      for (let pass = 0; pass < o.passes; pass++) {
        let cur = [0, 0];
        for (const c of cmds) {
          if (c.cmd === 'M') { cur = c.pts[0]; continue; }
          if (c.cmd === 'L' || c.cmd === 'Z') {
            const to = c.pts[0];
            if (dist(cur, to) > 1e-9) parts.push(segD(roughSegment(ctx, cur, to, pass)));
            cur = to;
          } else if (c.cmd === 'C') {
            const [c1, c2, p] = c.pts;
            const len = dist(cur, c1) + dist(c1, c2) + dist(c2, p);
            const j = jitterFor(len, o.roughness) * (pass === 0 ? 1 : 0.7);
            const jit = (q, m) => [q[0] + sym(j * m), q[1] + sym(j * m)];
            parts.push(segD([jit(cur, 1), jit(c1, 1.5), jit(c2, 1.5), jit(p, 1)]));
            cur = p;
          }
        }
      }
      return finish('path', ctx, parts.join(' '), flatten(cmds, o.curveSteps));
    },
  };
}

// ---------- SVG output ----------

const esc = (s) => String(s).replace(/&/g, '&amp;').replace(/"/g, '&quot;').replace(/</g, '&lt;');

export function toSvgElement(drawable) {
  const o = drawable.options;
  return drawable.sets.map((set) => {
    if (set.type === 'fill') {
      const w = o.fillWeight ?? o.strokeWidth / 2;
      return `<path d="${set.d}" fill="none" stroke="${esc(o.fill)}" stroke-width="${f(w)}" stroke-linecap="round" data-set="fill"/>`;
    }
    return `<path d="${set.d}" fill="none" stroke="${esc(o.stroke)}" stroke-width="${f(o.strokeWidth)}" stroke-linecap="round" stroke-linejoin="round" data-set="stroke"/>`;
  }).join('\n');
}

export function toSvg(drawables, { width = 400, height = 300, background = '#fff', title = null } = {}) {
  const bg = background ? `<rect width="100%" height="100%" fill="${esc(background)}"/>\n` : '';
  const t = title ? `<title>${esc(title)}</title>\n` : '';
  const body = drawables.map((d) => `<g data-shape="${d.shape}">\n${toSvgElement(d)}\n</g>`).join('\n');
  return `<svg xmlns="http://www.w3.org/2000/svg" width="${width}" height="${height}" viewBox="0 0 ${width} ${height}">\n${t}${bg}${body}\n</svg>\n`;
}
