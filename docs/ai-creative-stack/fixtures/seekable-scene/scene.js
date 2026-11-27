// One scene, two clocks.
// Every visible value is a pure function of story time t (seconds) and a seed.
// No wall clock, no requestAnimationFrame deltas, no unseeded randomness.
// The live page drives setTime() from a wall clock; the renderer drives it from frame / fps.
import * as THREE from 'three';

// Mechanism speed (driver turns per story second, as a multiple of OMEGA) across the timeline.
// Speed 0 means the mechanism holds still while the camera or captions carry the beat.
const OMEGA = Math.PI / 2; // driver gear: one turn every 4 s at speed 1
const SPEED = [
  // [start, speed]
  [0, 1],
  [7, 0.25],   // slow motion
  [10.5, 1],
  [14, 0],     // predict: hold still
  [16, 1],     // observe: half a driver turn (2 s at speed 1)
  [18, 0],     // explain: hold
];
export const DURATION = 20;

export const BEATS = [
  { t: 0, id: 'turn', caption: 'Turn the key. The big gear turns.' },
  { t: 3.5, id: 'mesh', caption: 'The small gear turns the other way, twice as fast.' },
  { t: 7, id: 'slow', caption: 'Slow motion: one turn of the big gear is two turns of the small one.' },
  { t: 10.5, id: 'xray', caption: 'X-ray: a cam on the small gear lifts the rod.' },
  { t: 14, id: 'predict', caption: 'Predict: the big gear turns half a turn. Where will the rod be?', choices: ['Higher', 'Same place', 'Lower'], answer: 1 },
  { t: 16, id: 'observe', caption: 'Half a turn of the big gear is one whole turn of the small gear, so the rod comes back to the same place.' },
];

// Closed-form integral of the speed profile: story progress S(t) in "speed-1 seconds".
function progress(t) {
  let s = 0;
  for (let i = 0; i < SPEED.length; i++) {
    const [start, speed] = SPEED[i];
    const end = i + 1 < SPEED.length ? SPEED[i + 1][0] : Infinity;
    if (t <= start) break;
    s += (Math.min(t, end) - start) * speed;
  }
  return s;
}

export function beatAt(t) {
  let k = 0;
  for (let i = 0; i < BEATS.length; i++) if (t >= BEATS[i].t - 1e-9) k = i;
  return k;
}

const smooth = (x) => { x = Math.min(1, Math.max(0, x)); return x * x * (3 - 2 * x); };
const lerp = (a, b, k) => a + (b - a) * k;

// Seeded PRNG (mulberry32): same seed, same dust, on every machine and every load.
function rng(seed) {
  let a = seed >>> 0;
  return () => {
    a = (a + 0x6d2b79f5) >>> 0;
    let x = a;
    x = Math.imul(x ^ (x >>> 15), x | 1);
    x ^= x + Math.imul(x ^ (x >>> 7), x | 61);
    return ((x ^ (x >>> 14)) >>> 0) / 4294967296;
  };
}

// Gear geometry. Module m, n teeth: pitch radius r = m n / 2.
const M = 0.1;
const N1 = 24, N2 = 12;
const R1 = (M * N1) / 2, R2 = (M * N2) / 2;
const DRIVER_X = -(R1 + R2) / 2, FOLLOWER_X = (R1 + R2) / 2;
const CAM_E = 0.16, CAM_R = 0.3, CAM_Z = -0.42; // cam sits behind the small gear, hidden in the case

function gearShape(n, r) {
  const p = (2 * Math.PI) / n, tip = r + M, root = r - 1.25 * M;
  const s = new THREE.Shape();
  for (let i = 0; i < n; i++) {
    const c = i * p;
    const pts = [[root, c - 0.3 * p], [tip, c - 0.14 * p], [tip, c + 0.14 * p], [root, c + 0.3 * p]];
    pts.forEach(([rad, a], j) => {
      const x = rad * Math.cos(a), y = rad * Math.sin(a);
      if (i === 0 && j === 0) s.moveTo(x, y); else s.lineTo(x, y);
    });
  }
  s.closePath();
  const hole = new THREE.Path();
  hole.absarc(0, 0, 0.09, 0, Math.PI * 2, true);
  s.holes.push(hole);
  return s;
}

function gearMesh(n, r, color) {
  const geo = new THREE.ExtrudeGeometry(gearShape(n, r), { depth: 0.16, bevelEnabled: true, bevelSize: 0.012, bevelThickness: 0.012, bevelSegments: 1, curveSegments: 4 });
  geo.translate(0, 0, -0.08);
  const g = new THREE.Group();
  g.add(new THREE.Mesh(geo, new THREE.MeshStandardMaterial({ color, roughness: 0.45, metalness: 0.25 })));
  // Marker on one tooth so turns can be counted.
  const marker = new THREE.Mesh(new THREE.SphereGeometry(0.05, 16, 12), new THREE.MeshStandardMaterial({ color: 0xe8e2d0, roughness: 0.3 }));
  marker.position.set(r - 0.1, 0, 0.1);
  g.add(marker);
  return g;
}

// Camera pose for each beat: [position, target].
const POSES = [
  [[0, 0.8, 5.6], [0, 0.25, 0]],
  [[0.45, 0.4, 5.3], [0.45, 0.22, 0]],
  [[0.45, 0.4, 5.3], [0.45, 0.22, 0]],
  [[2.9, 1.5, -2.9], [FOLLOWER_X, 0.35, -0.3]],
  [[2.4, 1.3, 4.6], [0.4, 0.45, -0.2]],
  [[2.4, 1.3, 4.6], [0.4, 0.45, -0.2]],
];
const CAMERA_MOVE = 1.4; // seconds of camera move, finishing exactly as the next beat starts

export function createScene(canvas, { width, height, pixelRatio = 1, seed = 7 } = {}) {
  const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, preserveDrawingBuffer: true });
  renderer.setPixelRatio(pixelRatio);
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.setClearColor(0xf2f4f1, 1);

  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(38, 16 / 9, 0.05, 50);
  scene.add(new THREE.HemisphereLight(0xffffff, 0xb8c2bc, 1.4));
  const key = new THREE.DirectionalLight(0xffffff, 2.2);
  key.position.set(2.5, 4, 5);
  scene.add(key);

  const driver = gearMesh(N1, R1, 0x1d6a84);
  driver.position.x = DRIVER_X;
  const follower = gearMesh(N2, R2, 0xb57900);
  follower.position.x = FOLLOWER_X;
  scene.add(driver, follower);

  // Wind-up key on the driver's shaft.
  const keyGroup = new THREE.Group();
  const steel = new THREE.MeshStandardMaterial({ color: 0x8b9693, roughness: 0.35, metalness: 0.7 });
  const shaft = new THREE.Mesh(new THREE.CylinderGeometry(0.05, 0.05, 0.5, 20), steel);
  shaft.rotation.x = Math.PI / 2; shaft.position.z = 0.3;
  const bow = new THREE.Mesh(new THREE.TorusGeometry(0.22, 0.045, 12, 32), steel);
  bow.position.set(0, 0.24, 0.55); bow.rotation.y = Math.PI / 2;
  keyGroup.add(shaft, bow);
  driver.add(keyGroup);

  // Cam on the follower's shaft, in front of the gear.
  const cam = new THREE.Mesh(new THREE.CylinderGeometry(CAM_R, CAM_R, 0.12, 40), new THREE.MeshStandardMaterial({ color: 0x7a5200, roughness: 0.5 }));
  cam.rotation.x = Math.PI / 2;
  scene.add(cam);
  const camShaft = new THREE.Mesh(new THREE.CylinderGeometry(0.045, 0.045, Math.abs(CAM_Z) + 0.1, 16), steel);
  camShaft.rotation.x = Math.PI / 2;
  camShaft.position.set(FOLLOWER_X, 0, CAM_Z / 2);
  scene.add(camShaft);

  // Rod resting on the cam, guided by a housing.
  const ROD_LEN = 0.75;
  const rod = new THREE.Mesh(new THREE.CylinderGeometry(0.05, 0.05, ROD_LEN, 20), steel);
  const foot = new THREE.Mesh(new THREE.BoxGeometry(0.32, 0.04, 0.2), steel);
  rod.add(foot); foot.position.y = -ROD_LEN / 2;
  scene.add(rod);
  const housingMat = new THREE.MeshStandardMaterial({ color: 0xd9ddd6, roughness: 0.8, transparent: true });
  const housing = new THREE.Mesh(new THREE.BoxGeometry(1.0, 1.3, 0.42), housingMat);
  housing.position.set(FOLLOWER_X, 0.3, CAM_Z);
  scene.add(housing);

  // Ghost line: where the rod top sits when the prediction is asked.
  const ghost = new THREE.Mesh(new THREE.BoxGeometry(0.42, 0.016, 0.016), new THREE.MeshBasicMaterial({ color: 0xb00020, transparent: true }));
  scene.add(ghost);

  // Seeded dust in the light.
  const rand = rng(seed);
  const DUST = 48;
  const dust = [];
  const dustGeo = new THREE.SphereGeometry(0.012, 6, 4);
  const dustMat = new THREE.MeshBasicMaterial({ color: 0x9aa49f });
  for (let i = 0; i < DUST; i++) {
    const m = new THREE.Mesh(dustGeo, dustMat);
    m.userData = { x: (rand() - 0.5) * 4, y: (rand() - 0.2) * 2.2, z: (rand() - 0.5) * 1.6, w: 0.3 + rand() * 0.6, ph: rand() * Math.PI * 2 };
    dust.push(m); scene.add(m);
  }

  const rodTop = (t) => {
    const a2 = followerAngle(t);
    return CAM_E * Math.sin(a2) + CAM_R + ROD_LEN; // flat-foot follower on an eccentric cam
  };
  const driverAngle = (t) => OMEGA * progress(t);
  const followerAngle = (t) => -(N1 / N2) * driverAngle(t) + Math.PI / N2;

  const state = {};

  function setTime(t) {
    t = Math.min(DURATION, Math.max(0, t));
    const k = beatAt(t);
    const a1 = driverAngle(t), a2 = followerAngle(t);
    driver.rotation.z = a1;
    follower.rotation.z = a2;
    cam.position.set(FOLLOWER_X + CAM_E * Math.cos(a2), CAM_E * Math.sin(a2), CAM_Z);
    const top = rodTop(t);
    rod.position.set(FOLLOWER_X, top - ROD_LEN / 2, CAM_Z);

    // Every beat time is a settled state: transitions finish by the beat, so a deep link or a
    // paused question shows what the caption describes.
    const xray = smooth((t - (BEATS[3].t - 1.2)) / 1.2);
    housingMat.opacity = lerp(1, 0.14, xray);
    housingMat.depthWrite = xray < 0.5;

    const ghostOn = t >= BEATS[4].t ? 1 : 0;
    ghost.material.opacity = ghostOn * 0.9;
    ghost.position.set(FOLLOWER_X, rodTop(BEATS[4].t), CAM_Z); // level with the rod top, same depth

    const from = POSES[k], to = POSES[Math.min(POSES.length - 1, k + 1)];
    const m = k + 1 < BEATS.length ? smooth((t - (BEATS[k + 1].t - CAMERA_MOVE)) / CAMERA_MOVE) : 0;
    const prev = from, next = to;
    camera.position.set(lerp(prev[0][0], next[0][0], m), lerp(prev[0][1], next[0][1], m), lerp(prev[0][2], next[0][2], m));
    camera.lookAt(lerp(prev[1][0], next[1][0], m), lerp(prev[1][1], next[1][1], m), lerp(prev[1][2], next[1][2], m));

    for (const d of dust) {
      const u = d.userData;
      d.position.set(u.x + 0.06 * Math.sin(t * u.w + u.ph), u.y + 0.04 * Math.sin(t * u.w * 1.3 + u.ph * 2), u.z);
    }

    Object.assign(state, { t, beat: k, a1, a2, rodTop: top, housing: housingMat.opacity, cam: camera.position.toArray() });
    renderer.render(scene, camera);
    return state;
  }

  // Landscape frames keep the left third for captions: render a wider frustum and show its left part,
  // so the mechanism sits right of centre. Portrait frames stay centred.
  const CAPTION_SHIFT = 1.32;
  function setSize(w, h) {
    renderer.setSize(w, h, false);
    if (w / h >= 1.2) {
      camera.aspect = (w * CAPTION_SHIFT) / h;
      camera.setViewOffset(w * CAPTION_SHIFT, h, 0, 0, w, h);
    } else {
      camera.aspect = w / h;
      camera.clearViewOffset();
    }
    camera.updateProjectionMatrix();
  }
  if (width && height) setSize(width, height);

  const round = (v) => (Array.isArray(v) ? v.map(round) : typeof v === 'number' ? Math.round(v * 1e6) / 1e6 : v);
  function digest() {
    return JSON.stringify(Object.fromEntries(Object.entries(state).map(([k, v]) => [k, round(v)])));
  }

  return { setTime, setBeat: (n) => setTime(BEATS[Math.max(0, Math.min(BEATS.length - 1, n))].t), setSize, digest, beats: BEATS, duration: DURATION, three: THREE.REVISION };
}
