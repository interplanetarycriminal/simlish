// Test for tokenextract: builds a page with known tokens, extracts them, asserts they are recovered.
// Run: node kit/tokenextract/test.mjs
import { spawnSync } from 'node:child_process';
import { mkdirSync, readFileSync, writeFileSync, rmSync, readdirSync, statSync, existsSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { deltaE2000, rgbToLab, DRAFT_NOTE } from './tokenextract.mjs';

const HERE = dirname(fileURLToPath(import.meta.url));
const OUT = join(HERE, 'out');
rmSync(OUT, { recursive: true, force: true });
mkdirSync(join(OUT, 'fixtures'), { recursive: true });

const BRAND = ['#2363cf', '#bf315c', '#198047'];
const NEAR_DUP = '#2464cf'; // one unit off the blue; must merge into it

// Known tokens: 3 brand colors, spacing 4/8/12/16/24/32, Georgia + Verdana, radii 4/8/16,
// one 200ms ease-out transition, one @media (min-width: 768px).
const page = `<!doctype html><html lang="en"><head><meta charset="utf-8"><title>Token fixture</title>
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body { font-family: Verdana, sans-serif; font-size: 16px; line-height: 1.5; color: #152137; background: #fbfcff; padding: 32px; }
  h1, h2 { font-family: Georgia, serif; color: #152137; line-height: 1.25; }
  h1 { font-size: 32px; font-weight: 700; margin-bottom: 24px; }
  h2 { font-size: 20px; font-weight: 700; margin-bottom: 8px; }
  main { max-width: 960px; margin: 0 auto; display: grid; gap: 24px; }
  .grid { display: grid; gap: 16px; }
  @media (min-width: 768px) { .grid { grid-template-columns: 1fr 1fr; } }
  .card { background: #ffffff; border: 1px solid #d0d9e7; border-radius: 8px; padding: 16px 24px; box-shadow: 0 1px 2px rgba(21, 33, 55, 0.12); }
  .card p { color: #465773; margin-bottom: 16px; }
  button { font: inherit; border: 0; border-radius: 4px; padding: 8px 12px; color: #ffffff; cursor: pointer; transition: background-color 200ms ease-out; }
  .b1 { background: ${BRAND[0]}; } .b2 { background: ${BRAND[1]}; } .b3 { background: ${BRAND[2]}; }
  .badge { display: inline-block; border-radius: 16px; padding: 4px 8px; background: ${BRAND[0]}; color: #ffffff; font-size: 12px; }
  .note { color: ${NEAR_DUP}; }
  .rose { color: ${BRAND[1]}; } .green { color: ${BRAND[2]}; }
</style></head><body><main>
  <h1>Token fixture <span class="badge">new</span></h1>
  <div class="grid">
    <section class="card"><h2>First</h2><p>Body copy in the secondary text color.</p><button class="b1">Primary</button></section>
    <section class="card"><h2 class="rose">Second</h2><p>More copy. <span class="note">A near-duplicate blue.</span></p><button class="b2">Rose</button></section>
    <section class="card"><h2 class="green">Third</h2><p>Even more copy for frequency.</p><button class="b3">Green</button></section>
    <section class="card"><h2>Fourth</h2><p>Last card.</p><button class="b1">Again</button></section>
  </div>
</main></body></html>`;
writeFileSync(join(OUT, 'fixtures', 'tokens-page.html'), page);

const checks = [];
const check = (name, ok, detail = '') => { checks.push({ name, ok: !!ok, detail: String(detail) }); console.log(`${ok ? 'PASS' : 'FAIL'}  ${name}${detail !== '' ? '  -- ' + detail : ''}`); };
const hexRgb = (h) => [1, 3, 5].map((i) => parseInt(h.slice(i, i + 2), 16));

try {
  // Unit checks for the color math (Sharma et al. 2005 test pair 1: expected 2.0425).
  const d = deltaE2000([50, 2.6772, -79.7751], [50, 0, -82.7485]);
  check('CIEDE2000 matches published test pair', Math.abs(d - 2.0425) < 1e-3, d.toFixed(4));
  const white = rgbToLab([255, 255, 255]);
  check('sRGB white converts to L*=100, a*=b*=0', Math.abs(white[0] - 100) < 0.01 && Math.abs(white[1]) < 0.01 && Math.abs(white[2]) < 0.01, white.map((v) => v.toFixed(3)).join(','));

  const r = spawnSync(process.execPath, ['tokenextract.mjs', 'out/fixtures/tokens-page.html', '--out', 'out/extract'], { cwd: HERE, encoding: 'utf8' });
  console.log(r.stdout.trim(), r.stderr.trim());
  check('tool exits 0', r.status === 0, r.status);
  const T = JSON.parse(readFileSync(join(OUT, 'extract', 'tokens.json'), 'utf8'));
  const css = readFileSync(join(OUT, 'extract', 'tokens.css'), 'utf8');
  const md = readFileSync(join(OUT, 'extract', 'DESIGN.md'), 'utf8');
  const tok = (g) => Object.entries(g || {}).filter(([k]) => !k.startsWith('$')).map(([k, v]) => ({ k, ...v }));

  // Colors.
  const brand = tok(T.color?.brand);
  check('exactly 3 brand colors after clustering', brand.length === 3, brand.map((b) => b.$value.hex).join(' '));
  for (const want of BRAND) {
    const best = Math.min(...brand.map((b) => deltaE2000(rgbToLab(hexRgb(b.$value.hex)), rgbToLab(hexRgb(want)))));
    check(`brand color ${want} recovered`, best < 1, `ΔE00 ${best.toFixed(3)}`);
  }
  const blue = brand.find((b) => b.$value.hex === BRAND[0]);
  check(`near-duplicate ${NEAR_DUP} merged into ${BRAND[0]}`, blue && (blue.$extensions['kit.tokenextract'].merged || []).includes(NEAR_DUP));
  check('brand colors are frequency-ranked (blue first)', brand[0]?.$value.hex === BRAND[0]);
  const neutrals = tok(T.color?.neutral).map((n) => n.$value.hex);
  check('neutrals recovered', ['#152137', '#fbfcff', '#465773', '#d0d9e7', '#ffffff'].every((h) => neutrals.includes(h)), neutrals.join(' '));

  // Typography.
  const fams = tok(T.font?.family).map((f) => f.$value[0]);
  check('exactly 2 font families: Georgia and Verdana', fams.length === 2 && fams.includes('Georgia') && fams.includes('Verdana'), fams.join(', '));
  const sizes = tok(T.font?.size).map((s) => s.$value.value);
  check('type sizes 12/16/20/32 recovered', JSON.stringify(sizes) === '[12,16,20,32]', sizes.join(','));
  check('weights 400 and 700', tok(T.font?.weight).map((w) => w.$value).join(',') === '400,700');

  // Spacing.
  const space = tok(T.space).map((s) => s.$value.value);
  check('spacing scale is 4/8/12/16/24/32', JSON.stringify(space) === '[4,8,12,16,24,32]', space.join(','));
  check('spacing base unit detected as 4px', /Base unit 4px/.test(T.space.$description), T.space.$description);

  // Radii, shadow, breakpoints, motion.
  const radii = tok(T.radius).map((x) => x.$value.value);
  check('radii are 4/8/16', JSON.stringify(radii) === '[4,8,16]', radii.join(','));
  const sh = tok(T.shadow)[0]?.$value;
  check('shadow parsed into DTCG fields', sh && sh.offsetY.value === 1 && sh.blur.value === 2 && Math.abs(sh.color.alpha - 0.12) < 0.01, JSON.stringify(sh));
  const bps = tok(T.breakpoint).map((b) => b.$value.value);
  check('breakpoint 768px recovered', JSON.stringify(bps) === '[768]', bps.join(','));
  const durs = tok(T.duration).map((x) => x.$value.value);
  check('duration 200ms recovered', JSON.stringify(durs) === '[200]', durs.join(','));
  const eases = tok(T.easing);
  check('easing ease-out as cubic-bezier(0, 0, 0.58, 1)', eases.length === 1 && JSON.stringify(eases[0].$value) === '[0,0,0.58,1]', JSON.stringify(eases.map((e) => e.$value)));
  const tr = tok(T.transition)[0];
  check('transition composite on background-color', tr && tr.$extensions['kit.tokenextract'].property === 'background-color' && tr.$value.duration.value === 200);

  // DTCG shape: every token has $value and a resolvable $type.
  const bad = [];
  const walk = (node, type, path) => { for (const [k, v] of Object.entries(node)) { if (k.startsWith('$')) continue; const t = v.$type || type; if (v.$value !== undefined) { if (!t) bad.push(path.concat(k).join('.')); } else walk(v, t, path.concat(k)); } };
  walk(T, undefined, []);
  check('every token has $value and a $type (DTCG)', bad.length === 0, bad.join(','));

  // tokens.css
  for (const needle of ['--color-brand-1: #2363cf;', '--space-1: 4px;', '--radius-3: 16px;', '--duration-1: 200ms;', '--easing-1: cubic-bezier(0, 0, 0.58, 1);', '--font-family-', '--breakpoint-1: 768px;']) check(`tokens.css has ${needle}`, css.includes(needle));

  // DESIGN.md follows the template's section order and carries the draft notice.
  const tplPath = join(HERE, '..', '..', 'templates', 'design-system.md');
  const tplHeads = existsSync(tplPath) ? [...readFileSync(tplPath, 'utf8').matchAll(/^## (.+)$/gm)].map((m) => m[1].trim()) : [];
  const mdHeads = [...md.matchAll(/^## (.+)$/gm)].map((m) => m[1].trim());
  check('DESIGN.md sections match templates/design-system.md in order', tplHeads.length > 5 && JSON.stringify(tplHeads) === JSON.stringify(mdHeads), mdHeads.length + ' sections');
  check('DESIGN.md is marked draft, extracted', md.includes(DRAFT_NOTE));
} catch (e) {
  check('run without error', false, e.stack);
}

const size = (d) => readdirSync(d, { withFileTypes: true }).reduce((s, e) => s + (e.isDirectory() ? size(join(d, e.name)) : statSync(join(d, e.name)).size), 0);
const pass = checks.length > 0 && checks.every((c) => c.ok);
writeFileSync(join(OUT, 'result.json'), JSON.stringify({ tool: 'tokenextract', pass, checks, outBytes: size(OUT) }, null, 2));
console.log(`\n${pass ? 'PASS' : 'FAIL'}: ${checks.filter((c) => c.ok).length}/${checks.length} checks`);
process.exit(pass ? 0 : 1);
