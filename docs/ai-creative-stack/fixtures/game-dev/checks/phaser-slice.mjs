// Phaser in headless Chrome: fall onto a platform, run right on a DevTools key press, collect a coin.
import { writeFileSync } from 'node:fs';
import { join } from 'node:path';
import { evaluate, launch, open, screenshot, serve } from '../../lib/cdp.mjs';
import { ROOT } from './versions.mjs';

const FALL = 90; const RUN = 75; const SETTLE = 10;
const RIGHT = { key: 'ArrowRight', code: 'ArrowRight', windowsVirtualKeyCode: 39, nativeVirtualKeyCode: 39 };

async function playOnce(cdp, url) {
  await open(cdp, url);
  const frozen = await evaluate(cdp, 'window.__slice.freeze()');
  if (frozen.loopRunning || frozen.physicsPaused) throw new Error('could not take over the game loop');
  const start = await evaluate(cdp, 'window.__slice.state()');
  const landed = await evaluate(cdp, `window.__slice.step(${FALL})`);
  await cdp.send('Input.dispatchKeyEvent', { type: 'rawKeyDown', ...RIGHT });
  const ran = await evaluate(cdp, `window.__slice.step(${RUN})`);
  await cdp.send('Input.dispatchKeyEvent', { type: 'keyUp', ...RIGHT });
  const stopped = await evaluate(cdp, `window.__slice.step(${SETTLE})`);
  return { start, landed, ran, stopped };
}

export default async function run() {
  const server = await serve(ROOT);
  const cdp = await launch(undefined, { width: 640, height: 360 });
  try {
    const url = `http://127.0.0.1:${server.address().port}/web/phaser.html`;
    const first = await playOnce(cdp, url);
    writeFileSync(join(ROOT, 'out', 'phaser-slice.png'), await screenshot(cdp));
    const second = await playOnce(cdp, url);
    const phaser = await evaluate(cdp, 'window.__slice.phaser');

    const { start, landed, ran, stopped } = first;
    const restY = 290 - 16; // platform top minus half the player height
    // Phaser runs the physics step before Scene.update(), so a velocity set in update() moves the body
    // from the next step on: a key held for RUN steps moves it RUN - 1 steps, and one step more after release.
    const stepPx = 160 / 60;
    const expectedRun = stepPx * (RUN - 1);
    const checks = {
      landsOnPlatform: landed.onFloor && Math.abs(landed.y - restY) < 1 && Math.abs(landed.vy) < 1e-6 && landed.x === start.x,
      movesRightWhileHeld: ran.rightDown && Math.abs(ran.x - landed.x - expectedRun) < 1e-6 && ran.onFloor && ran.vx === 160,
      stopsOnRelease: !stopped.rightDown && stopped.vx === 0 && Math.abs(stopped.x - ran.x - stepPx) < 1e-6,
      coinIncrementsScore: start.score === 0 && ran.score === 1 && !ran.coinActive,
      sameResultOnReload: JSON.stringify(first) === JSON.stringify(second),
    };
    return {
      pass: Object.values(checks).every(Boolean),
      details: { phaser, chrome: cdp.version, renderer: start.renderer, steps: { fall: FALL, run: RUN, settle: SETTLE, dtMs: 1000 / 60 }, start, landed, ran, stopped, expectedRunPx: expectedRun, checks, screenshot: 'out/phaser-slice.png' },
    };
  } finally {
    await cdp.close();
    server.close();
  }
}
