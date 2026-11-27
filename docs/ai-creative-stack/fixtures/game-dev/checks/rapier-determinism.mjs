// Rapier 2D: the same box stack stepped twice in fresh worlds must end bitwise equal and at rest.
import RAPIER from '@dimforge/rapier2d-compat';
import { createHash } from 'node:crypto';
import { version } from './versions.mjs';
import { bitsOf } from './bits.mjs';

const STEPS = 300;

function simulate() {
  const world = new RAPIER.World({ x: 0, y: -9.81 });
  world.timestep = 1 / 60;
  const ground = world.createRigidBody(RAPIER.RigidBodyDesc.fixed().setTranslation(0, -0.5));
  world.createCollider(RAPIER.ColliderDesc.cuboid(10, 0.5), ground);
  const boxes = [];
  // Five 0.5 m boxes in a column plus a 3-box row beside it, all starting slightly apart.
  for (let i = 0; i < 5; i++) boxes.push([`col-${i}`, 0, 0.26 + i * 0.52]);
  for (let i = 0; i < 3; i++) boxes.push([`row-${i}`, 2 + i * 0.52, 0.3]);
  const bodies = boxes.map(([label, x, y]) => {
    const body = world.createRigidBody(RAPIER.RigidBodyDesc.dynamic().setTranslation(x, y));
    world.createCollider(RAPIER.ColliderDesc.cuboid(0.25, 0.25).setFriction(0.7), body);
    return { label, body };
  });
  for (let i = 0; i < STEPS; i++) world.step();
  const state = bodies.map(({ label, body }) => {
    const p = body.translation(); const v = body.linvel();
    return { label, x: p.x, y: p.y, angle: body.rotation(), vx: v.x, vy: v.y, w: body.angvel(), sleeping: body.isSleeping() };
  });
  const snapshot = createHash('sha256').update(world.takeSnapshot()).digest('hex');
  world.free();
  return { state, snapshot };
}

export default async function run() {
  await RAPIER.init();
  const a = simulate();
  const b = simulate();
  const bitwiseEqual = JSON.stringify(a.state.map(bitsOf)) === JSON.stringify(b.state.map(bitsOf));
  const snapshotsEqual = a.snapshot === b.snapshot;
  const maxSpeed = Math.max(...a.state.map((s) => Math.hypot(s.vx, s.vy)));
  const atRest = a.state.every((s) => s.sleeping || Math.hypot(s.vx, s.vy) < 1e-3);
  const top = a.state.find((s) => s.label === 'col-4');
  const standing = Math.abs(top.y - 2.25) < 0.02 && Math.abs(top.x) < 0.02;
  return {
    pass: bitwiseEqual && snapshotsEqual && atRest && standing,
    details: { rapier: version('@dimforge/rapier2d-compat'), engineVersion: RAPIER.version(), steps: STEPS, dt: 1 / 60, bodies: a.state.length, bitwiseEqual, snapshotsEqual, snapshotSha256: a.snapshot.slice(0, 16), atRest, sleeping: a.state.filter((s) => s.sleeping).length, maxSpeed, standing, topBox: { x: top.x, y: top.y } },
  };
}
