// matter-js: a box pyramid stepped at a fixed 1/60 s twice must end bitwise equal and at rest.
import Matter from 'matter-js';
import { version } from './versions.mjs';
import { bitsOf } from './bits.mjs';

const STEPS = 300;

function simulate() {
  const { Engine, Bodies, Composite } = Matter;
  const engine = Engine.create({ positionIterations: 10, velocityIterations: 8 });
  const ground = Bodies.rectangle(400, 610, 900, 40, { isStatic: true, label: 'ground' });
  const boxes = [];
  // A 4-3-2-1 pyramid of 40 px boxes, dropped from a little above the ground.
  for (let row = 0; row < 4; row++) {
    for (let col = 0; col < 4 - row; col++) {
      boxes.push(Bodies.rectangle(340 + row * 20 + col * 41, 560 - row * 41, 40, 40, { label: `box-${row}-${col}`, friction: 0.6 }));
    }
  }
  Composite.add(engine.world, [ground, ...boxes]);
  for (let i = 0; i < STEPS; i++) Engine.update(engine, 1000 / 60);
  return boxes.map((b) => ({ label: b.label, x: b.position.x, y: b.position.y, angle: b.angle, speed: b.speed, angularSpeed: b.angularSpeed }));
}

export default async function run() {
  const a = simulate();
  const b = simulate();
  const bitwiseEqual = JSON.stringify(a.map(bitsOf)) === JSON.stringify(b.map(bitsOf));
  const maxSpeed = Math.max(...a.map((s) => s.speed));
  const maxAngular = Math.max(...a.map((s) => s.angularSpeed));
  const atRest = maxSpeed < 0.05 && maxAngular < 0.005;
  // The pyramid should still stand: the top box sits about three box heights above the bottom row.
  const bottom = a.filter((s) => s.label.startsWith('box-0')).map((s) => s.y);
  const top = a.find((s) => s.label === 'box-3-0');
  const standing = bottom.every((y) => Math.abs(y - 570) < 2) && Math.abs(top.y - (570 - 3 * 40)) < 6;
  return {
    pass: bitwiseEqual && atRest && standing,
    details: { matter: version('matter-js'), steps: STEPS, dtMs: 1000 / 60, bodies: a.length, bitwiseEqual, atRest, maxSpeed, maxAngularSpeed: maxAngular, standing, topBox: { x: top.x, y: top.y } },
  };
}
