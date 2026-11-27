// Test for designlint: builds a deliberately bad page and a clean page, lints both, asserts the planted rules fire.
// Run: node kit/designlint/test.mjs
import { spawnSync } from 'node:child_process';
import { mkdirSync, readFileSync, writeFileSync, rmSync, existsSync, statSync, readdirSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const HERE = dirname(fileURLToPath(import.meta.url));
const OUT = join(HERE, 'out');
const FIX = join(OUT, 'fixtures');
rmSync(OUT, { recursive: true, force: true });
mkdirSync(FIX, { recursive: true });

// A tiny inline SVG used as an image source (no network).
const PIX = 'data:image/svg+xml,' + encodeURIComponent('<svg xmlns="http://www.w3.org/2000/svg" width="40" height="40"><rect width="40" height="40" fill="#1D6A84"/></svg>');

const bad = `<!doctype html><html lang="en"><head><meta charset="utf-8"><title>Bad page</title>
<style>
  body { margin: 0; font-family: Arial, sans-serif; color: #222; background: #fff; }
  h1 { font-family: Georgia, serif; margin: 13px 7px; }
  .grad { font-family: Impact, sans-serif; background: linear-gradient(90deg, #f0f, #0ff); -webkit-background-clip: text; background-clip: text; color: transparent; }
  p.faint { color: #bbb; font-family: "Courier New", monospace; padding: 7px 11px; }
  .wide { width: 600px; height: 30px; background: #eee; margin: 5px; }
  @media (min-width: 700px) { .wide { width: auto; } }
  button { font-family: inherit; }
  .stack p { margin: 0; }
  .tiny { font-size: 10px; font-family: Verdana, sans-serif; margin: 3px 9px; color: #333; }
  button:focus, a:focus { outline: none; }
  .icon-btn { width: 16px; height: 16px; padding: 0; border: 0; background: #c33; transition: background 300ms ease; }
  .stack { position: relative; height: 60px; padding: 5px 13px; }
  .stack .over { position: absolute; top: 5px; left: 13px; margin: 0; color: #a00; }
  .box { height: 22px; width: 120px; overflow: hidden; color: #014; background: #fec; padding: 3px; }
  .c1 { color: #123456; } .c2 { color: #345678; background: #fafafa; } .c3 { color: #563412; background: #f5f0e0; }
  .c4 { color: #0a6; border: 1px solid #f80; } .c5 { color: #606; background: #eef; border: 3px solid #9c9; }
</style></head><body>
  <h1>Launch day 🚀</h1>
  <h1 class="grad">Second headline</h1>
  <h4>Skipped to h4</h4>
  <p class="faint">This paragraph is very low contrast grey on white.</p>
  <div class="wide">Fixed 600px block</div>
  <img src="${PIX}" width="40" height="40">
  <p class="tiny">Tiny 10px legal text in a fifth family.</p>
  <button class="icon-btn" aria-label="Close"></button>
  <a href="#nowhere"><svg width="30" height="30"><circle cx="15" cy="15" r="12" fill="#0a0"/></svg></a>
  <button id="go">Go</button>
  <div class="stack"><p>Underlying paragraph text here</p><p class="over">Overlapping words placed on top</p></div>
  <div class="box">This long sentence does not fit inside its little fixed box at all.</div>
  <p class="c1">c1</p><p class="c2">c2</p><p class="c3">c3</p><p class="c4">c4</p><p class="c5">c5</p>
</body></html>`;

const clean = `<!doctype html><html lang="en"><head><meta charset="utf-8"><title>Clean page</title>
<style>
  :root { --bg: #F2F4F1; --fg: #17201E; --accent: #1D6A84; --muted: #3c4a47; }
  * { box-sizing: border-box; margin: 0; }
  body { font-family: system-ui, "Segoe UI", sans-serif; background: var(--bg); color: var(--fg); padding: 16px; line-height: 1.5; }
  main { max-width: 720px; margin: 0 auto; display: grid; gap: 24px; }
  h1 { font-size: 32px; line-height: 1.25; }
  h2 { font-size: 24px; }
  p { font-size: 16px; color: var(--muted); }
  img { display: block; max-width: 100%; height: auto; }
  .row { display: flex; flex-wrap: wrap; gap: 12px; }
  button, a.btn { font: inherit; padding: 8px 16px; min-height: 44px; border-radius: 8px; border: 0; background: var(--accent); color: #fff; text-decoration: none; display: inline-flex; align-items: center; transition: background-color 200ms ease-out; }
  button:hover { background: #17566b; }
  :focus-visible { outline: 3px solid var(--fg); outline-offset: 4px; }
  @media (prefers-reduced-motion: reduce) { * { transition: none !important; animation: none !important; } }
</style></head><body><main>
  <h1>A calm, legible page</h1>
  <p>Body copy sits at 16 px with strong contrast on the page background, inside a column that never exceeds 720 px.</p>
  <img src="${PIX}" width="40" height="40" alt="Teal square">
  <h2>Actions</h2>
  <div class="row"><button>Save changes</button><a class="btn" href="#more">Read more</a></div>
  <p>A sentence with an <a href="#inline">inline link</a> keeps the WCAG inline-link exception.</p>
</main></body></html>`;

writeFileSync(join(FIX, 'bad.html'), bad);
writeFileSync(join(FIX, 'clean.html'), clean);

const run = (name) => {
  // Relative paths and cwd = this folder, so reports never record machine-specific absolute paths.
  const r = spawnSync(process.execPath, ['designlint.mjs', `out/fixtures/${name}.html`, '--out', `out/${name}`], { cwd: HERE, encoding: 'utf8' });
  if (r.status === 2 || r.error) throw new Error(`${name} run failed: ${r.stderr || r.error}`);
  return { code: r.status, stdout: r.stdout.trim(), report: JSON.parse(readFileSync(join(OUT, name, 'report.json'), 'utf8')) };
};

const checks = [];
const check = (name, ok, detail = '') => { checks.push({ name, ok: !!ok, detail }); console.log(`${ok ? 'PASS' : 'FAIL'}  ${name}${detail ? '  -- ' + detail : ''}`); };
let B, C;
try {
  B = run('bad'); C = run('clean');
  const has = (rep, rule, tier, pred = () => true) => rep.findings.some((f) => f.rule === rule && f.tier === tier && pred(f));
  const b = B.report, c = C.report;
  console.log('bad:', B.stdout); console.log('clean:', C.stdout);

  // Planted in the bad page (the six the brief requires first).
  check('bad: low contrast (Floor)', has(b, 'contrast', 'Floor', (f) => f.selector.includes('faint') && f.value < 4.5), b.findings.find((f) => f.rule === 'contrast')?.message);
  check('bad: overflow at 390 only (Floor)', has(b, 'overflow-x', 'Floor', (f) => f.widths.includes(390)) && !b.findings.some((f) => f.rule === 'overflow-x' && f.widths.some((w) => w >= 768)));
  check('bad: img without alt (Floor)', has(b, 'img-alt', 'Floor'));
  check('bad: emoji heading (Finish)', has(b, 'emoji-heading', 'Finish'));
  check('bad: focus outline removed (Floor)', has(b, 'focus-outline', 'Floor', (f) => f.selector === '#go'), `${b.findings.filter((f) => f.rule === 'focus-outline').length} focus finding(s)`);
  check('bad: 5 font families (Reflex)', has(b, 'font-families', 'Reflex', (f) => f.value === 5), b.findings.find((f) => f.rule === 'font-families')?.message);
  // Extra planted rules.
  check('bad: link without accessible name (Floor)', has(b, 'accessible-name', 'Floor'));
  check('bad: gradient text (Finish)', has(b, 'gradient-text', 'Finish'));
  check('bad: font size below 12px (Reflex)', has(b, 'font-size-min', 'Reflex', (f) => f.value === 10));
  check('bad: 16x16 touch target at 390 (Reflex)', has(b, 'touch-target', 'Reflex', (f) => f.value === '16x16' && f.widths.includes(390)));
  check('bad: heading skip h1->h4 (Reflex)', has(b, 'heading-skip', 'Reflex', (f) => f.value === 'h1>h4'));
  check('bad: two h1 (Reflex)', has(b, 'multiple-h1', 'Reflex', (f) => f.value === 2));
  check('bad: overlapping text (Reflex)', has(b, 'text-overlap', 'Reflex'));
  check('bad: clipped text (Reflex)', has(b, 'text-clipped', 'Reflex'));
  check('bad: no reduced-motion rule (Reflex)', has(b, 'reduced-motion', 'Reflex'));
  check('bad: spacing off 4px grid (Finish)', has(b, 'spacing-grid', 'Finish'), `on-grid at 1440: ${b.metrics[1440].spacingOnGridPct}%`);
  check('bad: too many colors (Finish)', has(b, 'color-count', 'Finish'), `${b.metrics[1440].distinctColors} colors`);
  check('bad: exit code 1', B.code === 1);
  check('bad: one screenshot per width', [390, 768, 1024, 1440].every((w) => existsSync(join(OUT, 'bad', `shot-${w}.png`))));

  // Clean page.
  check('clean: zero Floor findings', c.summary.Floor === 0, JSON.stringify(c.summary));
  check('clean: zero Reflex findings', c.summary.Reflex === 0, c.findings.filter((f) => f.tier === 'Reflex').map((f) => f.rule).join(','));
  check('clean: exit code 0', C.code === 0);
  check('clean: spacing 100% on grid', Object.values(c.metrics).every((m) => m.spacingOnGridPct === 100));
  check('clean: focus visible on every tab stop', c.focus.reachedByTab >= 3, `${c.focus.reachedByTab} tab stops`);
} catch (e) {
  check('run without error', false, e.message);
}

const size = (d) => readdirSync(d, { withFileTypes: true }).reduce((s, e) => s + (e.isDirectory() ? size(join(d, e.name)) : statSync(join(d, e.name)).size), 0);
const pass = checks.length > 0 && checks.every((c) => c.ok);
const result = { tool: 'designlint', pass, checks, bad: B && { exit: B.code, summary: B.report.summary }, clean: C && { exit: C.code, summary: C.report.summary }, outBytes: size(OUT) };
writeFileSync(join(OUT, 'result.json'), JSON.stringify(result, null, 2));
console.log(`\n${pass ? 'PASS' : 'FAIL'}: ${checks.filter((c) => c.ok).length}/${checks.length} checks; out/ is ${(result.outBytes / 1024).toFixed(0)} KB`);
process.exit(pass ? 0 : 1);
