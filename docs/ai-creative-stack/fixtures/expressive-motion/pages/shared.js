// Shared by every page and by run.mjs: the pinned library versions, the CDN URL builder
// and a small cubic-bezier solver used to compute expected eased values independently.

export const VERSIONS = {
  motion: '14.14.0',
  gsap: '3.15.1',
  '@theatre/core': '0.7.2',
  react: '19.3.1',
  'react-dom': '19.3.1',
  three: '0.187.0',
  '@react-three/fiber': '9.8.2',
  // Transitive dependencies of @react-three/fiber, pinned so esm.sh does not float them within semver ranges.
  scheduler: '0.28.0',
  'its-fine': '2.1.1',
  zustand: '5.1.0',
  'suspend-react': '0.1.3',
  'react-use-measure': '2.1.7',
  'use-sync-external-store': '1.7.0',
};

const pin = (names) => names.map((n) => `${n}@${VERSIONS[n]}`).join(',');

/** esm.sh URL for a package at its pinned version, with optional sub-path and pinned dependencies. */
export function esm(name, subpath = '', deps = []) {
  const q = deps.length ? `?deps=${pin(deps)}` : '';
  return `https://esm.sh/${name}@${VERSIONS[name]}${subpath}${q}`;
}

export const R3F_DEPS = ['react', 'react-dom', 'three', 'scheduler', 'its-fine', 'zustand', 'suspend-react', 'react-use-measure', 'use-sync-external-store'];

/**
 * Cubic-bezier timing function through (0,0), (x1,y1), (x2,y2), (1,1), evaluated at progress x.
 * Bisection on the x polynomial, so it is robust for any control points with x1, x2 in [0, 1].
 */
export function bezier(x1, y1, x2, y2, x) {
  const coord = (a, b, s) => 3 * a * s * (1 - s) ** 2 + 3 * b * s * s * (1 - s) + s ** 3;
  if (x <= 0) return 0;
  if (x >= 1) return 1;
  let lo = 0, hi = 1, s = x;
  for (let i = 0; i < 60; i++) {
    s = (lo + hi) / 2;
    if (coord(x1, x2, s) < x) lo = s; else hi = s;
  }
  return coord(y1, y2, s);
}

/** Translate-x of an element as the browser resolved it (0 when there is no transform). */
export function readX(el) {
  const t = getComputedStyle(el).transform;
  return !t || t === 'none' ? 0 : new DOMMatrixReadOnly(t).m41;
}

export const twoFrames = () => new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(r)));

/** Third-party module URLs this page actually fetched, for the evidence file. */
export function fetchedModules() {
  return performance.getEntriesByType('resource').map((e) => e.name).filter((u) => !u.startsWith(location.origin));
}
