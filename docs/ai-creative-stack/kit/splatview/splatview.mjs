// splatview: a small WebGL2 renderer for 3D Gaussian Splatting PLY files.
// Pure functions (parsePly, buildSplats, sortBackToFront, camera math) have no DOM
// access, so Node can import this module too. createViewer() needs a canvas.

const C0 = 0.28209479177387814;

const TYPE_INFO = {
  char: [1, 'getInt8'], int8: [1, 'getInt8'], uchar: [1, 'getUint8'], uint8: [1, 'getUint8'],
  short: [2, 'getInt16'], int16: [2, 'getInt16'], ushort: [2, 'getUint16'], uint16: [2, 'getUint16'],
  int: [4, 'getInt32'], int32: [4, 'getInt32'], uint: [4, 'getUint32'], uint32: [4, 'getUint32'],
  float: [4, 'getFloat32'], float32: [4, 'getFloat32'], double: [8, 'getFloat64'], float64: [8, 'getFloat64'],
};

/** Parse a binary little-endian PLY vertex element into named Float32Arrays. */
export function parsePly(buffer) {
  const bytes = new Uint8Array(buffer);
  const marker = 'end_header';
  let headerEnd = -1;
  const scanLimit = Math.min(bytes.length, 65536);
  let text = '';
  for (let i = 0; i < scanLimit; i++) text += String.fromCharCode(bytes[i]);
  const at = text.indexOf(marker);
  if (at < 0) throw new Error('PLY: no end_header');
  headerEnd = text.indexOf('\n', at) + 1;
  const lines = text.slice(0, headerEnd).split(/\r?\n/);
  if (lines[0].trim() !== 'ply') throw new Error('PLY: missing magic');
  let format = '';
  let count = 0;
  let inVertex = false;
  let beforeVertex = 0; // bytes of elements declared before "vertex" (unsupported unless 0)
  const props = [];
  for (const line of lines) {
    const p = line.trim().split(/\s+/);
    if (p[0] === 'format') format = p[1];
    else if (p[0] === 'element') {
      inVertex = p[1] === 'vertex';
      if (inVertex) count = parseInt(p[2], 10);
      else if (count === 0 && parseInt(p[2], 10) > 0) beforeVertex++;
    } else if (p[0] === 'property' && inVertex) {
      if (p[1] === 'list') throw new Error('PLY: list properties on vertex are not supported');
      const info = TYPE_INFO[p[1]];
      if (!info) throw new Error(`PLY: unknown type ${p[1]}`);
      props.push({ name: p[2], size: info[0], getter: info[1] });
    }
  }
  if (format !== 'binary_little_endian') throw new Error(`PLY: format ${format} not supported (binary_little_endian only)`);
  if (beforeVertex) throw new Error('PLY: vertex must be the first element');
  let stride = 0;
  for (const pr of props) { pr.offset = stride; stride += pr.size; }
  if (bytes.length < headerEnd + count * stride) throw new Error('PLY: file is truncated');
  const out = {};
  const allFloat = props.every((pr) => pr.getter === 'getFloat32');
  if (allFloat) {
    const body = new Float32Array(buffer.slice(headerEnd, headerEnd + count * stride));
    const nf = stride / 4;
    props.forEach((pr, k) => {
      const a = new Float32Array(count);
      for (let i = 0; i < count; i++) a[i] = body[i * nf + k];
      out[pr.name] = a;
    });
  } else {
    const dv = new DataView(buffer, headerEnd);
    for (const pr of props) {
      const a = new Float32Array(count);
      for (let i = 0; i < count; i++) a[i] = dv[pr.getter](i * stride + pr.offset, true);
      out[pr.name] = a;
    }
  }
  return { count, stride, headerBytes: headerEnd, fields: props.map((p) => p.name), data: out };
}

const sigmoid = (x) => 1 / (1 + Math.exp(-x));

/** Turn PLY fields into packed render data: centers, 3D covariances, colors. */
export function buildSplats(ply) {
  const { count, data: d } = ply;
  if (!d.x || !d.y || !d.z) throw new Error('PLY: needs x, y, z');
  const center = new Float32Array(count * 3);
  const cov = new Float32Array(count * 6); // xx xy xz yy yz zz
  const color = new Float32Array(count * 4);
  const min = [Infinity, Infinity, Infinity];
  const max = [-Infinity, -Infinity, -Infinity];
  const hasDC = d.f_dc_0 && d.f_dc_1 && d.f_dc_2;
  const hasRGB = d.red && d.green && d.blue;
  const hasScale = d.scale_0 && d.scale_1 && d.scale_2;
  const hasRot = d.rot_0 && d.rot_1 && d.rot_2 && d.rot_3;
  // fallback size for plain point clouds: a fraction of the bounds diagonal
  for (let i = 0; i < count; i++) {
    const p = [d.x[i], d.y[i], d.z[i]];
    for (let k = 0; k < 3; k++) { if (p[k] < min[k]) min[k] = p[k]; if (p[k] > max[k]) max[k] = p[k]; }
  }
  const diag = Math.hypot(max[0] - min[0], max[1] - min[1], max[2] - min[2]) || 1;
  const fallbackScale = diag / Math.cbrt(Math.max(count, 1)) * 0.3;
  for (let i = 0; i < count; i++) {
    center[i * 3] = d.x[i]; center[i * 3 + 1] = d.y[i]; center[i * 3 + 2] = d.z[i];
    let r, g, b;
    if (hasDC) { r = 0.5 + C0 * d.f_dc_0[i]; g = 0.5 + C0 * d.f_dc_1[i]; b = 0.5 + C0 * d.f_dc_2[i]; }
    else if (hasRGB) { r = d.red[i] / 255; g = d.green[i] / 255; b = d.blue[i] / 255; }
    else { r = g = b = 0.8; }
    color[i * 4] = Math.min(1, Math.max(0, r));
    color[i * 4 + 1] = Math.min(1, Math.max(0, g));
    color[i * 4 + 2] = Math.min(1, Math.max(0, b));
    color[i * 4 + 3] = d.opacity ? sigmoid(d.opacity[i]) : 1;
    const sx = hasScale ? Math.exp(d.scale_0[i]) : fallbackScale;
    const sy = hasScale ? Math.exp(d.scale_1[i]) : fallbackScale;
    const sz = hasScale ? Math.exp(d.scale_2[i]) : fallbackScale;
    let w = 1, x = 0, y = 0, z = 0;
    if (hasRot) { w = d.rot_0[i]; x = d.rot_1[i]; y = d.rot_2[i]; z = d.rot_3[i]; }
    const qn = Math.hypot(w, x, y, z) || 1; w /= qn; x /= qn; y /= qn; z /= qn;
    // rotation matrix (row-major) R; covariance = R S S R^T
    const R = [
      1 - 2 * (y * y + z * z), 2 * (x * y - w * z), 2 * (x * z + w * y),
      2 * (x * y + w * z), 1 - 2 * (x * x + z * z), 2 * (y * z - w * x),
      2 * (x * z - w * y), 2 * (y * z + w * x), 1 - 2 * (x * x + y * y),
    ];
    const s2 = [sx * sx, sy * sy, sz * sz];
    const c = (a, b2) => R[a * 3] * R[b2 * 3] * s2[0] + R[a * 3 + 1] * R[b2 * 3 + 1] * s2[1] + R[a * 3 + 2] * R[b2 * 3 + 2] * s2[2];
    cov[i * 6] = c(0, 0); cov[i * 6 + 1] = c(0, 1); cov[i * 6 + 2] = c(0, 2);
    cov[i * 6 + 3] = c(1, 1); cov[i * 6 + 4] = c(1, 2); cov[i * 6 + 5] = c(2, 2);
  }
  return { count, center, cov, color, bounds: { min, max } };
}

/**
 * Back-to-front order by view depth. Single-pass counting sort on 16-bit depth keys
 * (stable, so ties keep file order and the result is deterministic).
 * viewRow2 = third row of the view matrix (z_view = r . p + t). Returns Uint32Array.
 */
export function sortBackToFront(center, count, viewRow2, out, scratch) {
  const order = out && out.length === count ? out : new Uint32Array(count);
  const keys = scratch && scratch.keys && scratch.keys.length === count ? scratch.keys : new Float32Array(count);
  const [a, b, c, t] = viewRow2;
  let lo = Infinity, hi = -Infinity;
  for (let i = 0; i < count; i++) {
    // depth = -z_view (positive in front); larger depth = farther
    keys[i] = -(a * center[i * 3] + b * center[i * 3 + 1] + c * center[i * 3 + 2] + t);
    const dep = keys[i]; // read back the float32 value so lo/hi match the stored keys exactly
    if (dep < lo) lo = dep;
    if (dep > hi) hi = dep;
  }
  const BUCKETS = 65536;
  const counts = new Uint32Array(BUCKETS);
  const scale = hi > lo ? (BUCKETS - 1) / (hi - lo) : 0;
  const k16 = scratch && scratch.k16 && scratch.k16.length === count ? scratch.k16 : new Uint16Array(count);
  for (let i = 0; i < count; i++) {
    // invert so that the farthest splat gets key 0 and is drawn first
    const q = Math.min(BUCKETS - 1, Math.max(0, Math.floor((keys[i] - lo) * scale)));
    const k = (BUCKETS - 1) - q;
    k16[i] = k;
    counts[k]++;
  }
  let sum = 0;
  for (let k = 0; k < BUCKETS; k++) { const v = counts[k]; counts[k] = sum; sum += v; }
  for (let i = 0; i < count; i++) order[counts[k16[i]]++] = i;
  if (scratch) { scratch.keys = keys; scratch.k16 = k16; }
  return order;
}

// ---- camera math (column-major 4x4, like WebGL) ----
export function perspective(fovyRad, aspect, near, far) {
  const f = 1 / Math.tan(fovyRad / 2);
  const nf = 1 / (near - far);
  return new Float32Array([f / aspect, 0, 0, 0, 0, f, 0, 0, 0, 0, (far + near) * nf, -1, 0, 0, 2 * far * near * nf, 0]);
}

export function lookAt(eye, target, up) {
  let zx = eye[0] - target[0], zy = eye[1] - target[1], zz = eye[2] - target[2];
  let l = Math.hypot(zx, zy, zz) || 1; zx /= l; zy /= l; zz /= l;
  let xx = up[1] * zz - up[2] * zy, xy = up[2] * zx - up[0] * zz, xz = up[0] * zy - up[1] * zx;
  l = Math.hypot(xx, xy, xz) || 1; xx /= l; xy /= l; xz /= l;
  const yx = zy * xz - zz * xy, yy = zz * xx - zx * xz, yz = zx * xy - zy * xx;
  return new Float32Array([
    xx, yx, zx, 0, xy, yy, zy, 0, xz, yz, zz, 0,
    -(xx * eye[0] + xy * eye[1] + xz * eye[2]), -(yx * eye[0] + yy * eye[1] + yz * eye[2]), -(zx * eye[0] + zy * eye[1] + zz * eye[2]), 1,
  ]);
}

/** Orbit camera: azimuth around +Y measured from +Z toward +X, elevation up from the XZ plane. */
export function orbitEye(target, azDeg, elDeg, dist) {
  const az = azDeg * Math.PI / 180, el = elDeg * Math.PI / 180;
  return [target[0] + dist * Math.cos(el) * Math.sin(az), target[1] + dist * Math.sin(el), target[2] + dist * Math.cos(el) * Math.cos(az)];
}

const VS = `#version 300 es
precision highp float;
precision highp int;
layout(location=0) in vec2 corner;
layout(location=1) in uint splatIndex;
uniform highp sampler2D uCenter;  // xyz, alpha
uniform highp sampler2D uCovA;    // xx xy xz yy
uniform highp sampler2D uCovB;    // yz zz
uniform highp sampler2D uColor;   // rgb a
uniform mat4 uView;
uniform mat4 uProj;
uniform vec2 uFocal;     // pixels
uniform vec2 uViewport;  // pixels
uniform vec2 uTanFov;    // tan(fov/2) x, y
uniform int uTexW;
out vec4 vColor;
out vec2 vPos;
void main() {
  ivec2 tc = ivec2(int(splatIndex) % uTexW, int(splatIndex) / uTexW);
  vec4 c4 = texelFetch(uCenter, tc, 0);
  vec4 t = uView * vec4(c4.xyz, 1.0);
  float depth = -t.z;
  vec4 clip = uProj * t;
  if (depth <= 0.0 || abs(clip.x) > 1.3 * clip.w || abs(clip.y) > 1.3 * clip.w) {
    gl_Position = vec4(0.0, 0.0, 2.0, 1.0);
    return;
  }
  vec4 ca = texelFetch(uCovA, tc, 0);
  vec2 cb = texelFetch(uCovB, tc, 0).xy;
  mat3 V = mat3(ca.x, ca.y, ca.z,  ca.y, ca.w, cb.x,  ca.z, cb.x, cb.y);
  // Jacobian of the perspective projection at the centre (clamped like a guard band)
  float lx = 1.3 * uTanFov.x, ly = 1.3 * uTanFov.y;
  float tx = clamp(t.x / depth, -lx, lx) * depth;
  float ty = clamp(t.y / depth, -ly, ly) * depth;
  // screen x = fx * tx / depth, screen y = fy * ty / depth, depth = -t.z
  mat3 J = mat3(
    uFocal.x / depth, 0.0, 0.0,
    0.0, uFocal.y / depth, 0.0,
    uFocal.x * tx / (depth * depth), uFocal.y * ty / (depth * depth), 0.0);
  mat3 W = mat3(uView);
  mat3 T = J * W;
  mat3 cov2 = T * V * transpose(T);
  float a = cov2[0][0] + 0.3;
  float b = cov2[0][1];
  float d = cov2[1][1] + 0.3;
  float mid = 0.5 * (a + d);
  float rad = length(vec2(0.5 * (a - d), b));
  float l1 = mid + rad;
  float l2 = max(mid - rad, 0.1);
  vec2 e1 = abs(b) > 1e-12 ? normalize(vec2(b, l1 - a)) : (a >= d ? vec2(1.0, 0.0) : vec2(0.0, 1.0));
  vec2 e2 = vec2(-e1.y, e1.x);
  float r1 = min(3.0 * sqrt(l1), 1024.0);
  float r2 = min(3.0 * sqrt(l2), 1024.0);
  vec2 offPx = corner.x * r1 * e1 + corner.y * r2 * e2;
  vec2 ndc = clip.xy / clip.w + offPx * 2.0 / uViewport;
  gl_Position = vec4(ndc, clip.z / clip.w, 1.0);
  vColor = texelFetch(uColor, tc, 0);
  vPos = corner * 3.0;  // in units of standard deviations along the eigen axes
}`;

const FS = `#version 300 es
precision highp float;
in vec4 vColor;
in vec2 vPos;
out vec4 frag;
void main() {
  float p = -0.5 * dot(vPos, vPos);
  if (p < -4.5) discard;
  float alpha = min(0.99, vColor.a * exp(p));
  if (alpha < 1.0 / 255.0) discard;
  frag = vec4(vColor.rgb * alpha, alpha);  // premultiplied
}`;

function compile(gl, type, src) {
  const s = gl.createShader(type);
  gl.shaderSource(s, src);
  gl.compileShader(s);
  if (!gl.getShaderParameter(s, gl.COMPILE_STATUS)) throw new Error(gl.getShaderInfoLog(s));
  return s;
}

function floatTexture(gl, unit, w, h, data) {
  const tex = gl.createTexture();
  gl.activeTexture(gl.TEXTURE0 + unit);
  gl.bindTexture(gl.TEXTURE_2D, tex);
  gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.NEAREST);
  gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.NEAREST);
  gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE);
  gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE);
  gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA32F, w, h, 0, gl.RGBA, gl.FLOAT, data);
  return tex;
}

/** Create a viewer on a canvas. Returns an object with load/setView/render/stats. */
export function createViewer(canvas, { background = [0.07, 0.07, 0.09], fovDeg = 50 } = {}) {
  const gl = canvas.getContext('webgl2', { antialias: false, premultipliedAlpha: true, preserveDrawingBuffer: true, alpha: false });
  if (!gl) throw new Error('WebGL2 is not available');
  const prog = gl.createProgram();
  gl.attachShader(prog, compile(gl, gl.VERTEX_SHADER, VS));
  gl.attachShader(prog, compile(gl, gl.FRAGMENT_SHADER, FS));
  gl.linkProgram(prog);
  if (!gl.getProgramParameter(prog, gl.LINK_STATUS)) throw new Error(gl.getProgramInfoLog(prog));
  const loc = (n) => gl.getUniformLocation(prog, n);
  const U = { center: loc('uCenter'), covA: loc('uCovA'), covB: loc('uCovB'), color: loc('uColor'), view: loc('uView'),
    proj: loc('uProj'), focal: loc('uFocal'), viewport: loc('uViewport'), tanFov: loc('uTanFov'), texW: loc('uTexW') };

  const vao = gl.createVertexArray();
  gl.bindVertexArray(vao);
  const quad = gl.createBuffer();
  gl.bindBuffer(gl.ARRAY_BUFFER, quad);
  gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1, -1, 1, -1, -1, 1, 1, 1]), gl.STATIC_DRAW);
  gl.enableVertexAttribArray(0);
  gl.vertexAttribPointer(0, 2, gl.FLOAT, false, 0, 0);
  const orderBuf = gl.createBuffer();
  gl.bindBuffer(gl.ARRAY_BUFFER, orderBuf);
  gl.enableVertexAttribArray(1);
  gl.vertexAttribIPointer(1, 1, gl.UNSIGNED_INT, 0, 0);
  gl.vertexAttribDivisor(1, 1);
  gl.bindVertexArray(null);

  const state = { splats: null, order: null, scratch: {}, target: [0, 0, 0], az: 30, el: 20, dist: 5, file: null, sorts: 0, lastSortMs: 0 };
  let view = null, proj = null;

  function upload(s) {
    const texW = 2048;
    const texH = Math.max(1, Math.ceil(s.count / texW));
    const n = texW * texH;
    const a = new Float32Array(n * 4), b = new Float32Array(n * 4), c = new Float32Array(n * 4), col = new Float32Array(n * 4);
    for (let i = 0; i < s.count; i++) {
      a[i * 4] = s.center[i * 3]; a[i * 4 + 1] = s.center[i * 3 + 1]; a[i * 4 + 2] = s.center[i * 3 + 2]; a[i * 4 + 3] = s.color[i * 4 + 3];
      b[i * 4] = s.cov[i * 6]; b[i * 4 + 1] = s.cov[i * 6 + 1]; b[i * 4 + 2] = s.cov[i * 6 + 2]; b[i * 4 + 3] = s.cov[i * 6 + 3];
      c[i * 4] = s.cov[i * 6 + 4]; c[i * 4 + 1] = s.cov[i * 6 + 5];
      col.set(s.color.subarray(i * 4, i * 4 + 4), i * 4);
    }
    gl.useProgram(prog);
    state.tex = [floatTexture(gl, 0, texW, texH, a), floatTexture(gl, 1, texW, texH, b), floatTexture(gl, 2, texW, texH, c), floatTexture(gl, 3, texW, texH, col)];
    gl.uniform1i(U.center, 0); gl.uniform1i(U.covA, 1); gl.uniform1i(U.covB, 2); gl.uniform1i(U.color, 3);
    gl.uniform1i(U.texW, texW);
    state.order = new Uint32Array(s.count);
    gl.bindBuffer(gl.ARRAY_BUFFER, orderBuf);
    gl.bufferData(gl.ARRAY_BUFFER, state.order.byteLength, gl.DYNAMIC_DRAW);
  }

  function updateCamera() {
    const w = canvas.width, h = canvas.height;
    const eye = orbitEye(state.target, state.az, state.el, state.dist);
    const up = Math.abs(state.el) > 89.9 ? [0, 0, -Math.sign(state.el)] : [0, 1, 0];
    view = lookAt(eye, state.target, up);
    const fovy = fovDeg * Math.PI / 180;
    proj = perspective(fovy, w / h, Math.max(1e-4, state.dist * 0.01), state.dist * 100 + 10);
    state.eye = eye;
  }

  function sort() {
    const t0 = performance.now();
    const row2 = [view[2], view[6], view[10], view[14]];
    sortBackToFront(state.splats.center, state.splats.count, row2, state.order, state.scratch);
    gl.bindBuffer(gl.ARRAY_BUFFER, orderBuf);
    gl.bufferSubData(gl.ARRAY_BUFFER, 0, state.order);
    state.sorts++;
    state.lastSortMs = performance.now() - t0;
  }

  function render() {
    const w = canvas.width, h = canvas.height;
    gl.viewport(0, 0, w, h);
    gl.clearColor(background[0], background[1], background[2], 1);
    gl.clear(gl.COLOR_BUFFER_BIT);
    if (!state.splats) return;
    updateCamera();
    sort();
    const fovy = fovDeg * Math.PI / 180;
    const ty = Math.tan(fovy / 2), tx = ty * w / h;
    gl.useProgram(prog);
    for (let i = 0; i < 4; i++) { gl.activeTexture(gl.TEXTURE0 + i); gl.bindTexture(gl.TEXTURE_2D, state.tex[i]); }
    gl.uniformMatrix4fv(U.view, false, view);
    gl.uniformMatrix4fv(U.proj, false, proj);
    gl.uniform2f(U.focal, (w / 2) / tx, (h / 2) / ty);
    gl.uniform2f(U.viewport, w, h);
    gl.uniform2f(U.tanFov, tx, ty);
    gl.disable(gl.DEPTH_TEST);
    gl.enable(gl.BLEND);
    gl.blendFunc(gl.ONE, gl.ONE_MINUS_SRC_ALPHA);  // premultiplied, back to front
    gl.bindVertexArray(vao);
    gl.drawArraysInstanced(gl.TRIANGLE_STRIP, 0, 4, state.splats.count);
    gl.bindVertexArray(null);
  }

  return {
    gl,
    state,
    async loadUrl(url) {
      const res = await fetch(url);
      if (!res.ok) throw new Error(`fetch ${url}: ${res.status}`);
      return this.loadBuffer(await res.arrayBuffer(), url);
    },
    loadBuffer(buf, name = 'buffer') {
      const ply = parsePly(buf);
      const s = buildSplats(ply);
      state.splats = s;
      state.file = name;
      state.fields = ply.fields;
      const { min, max } = s.bounds;
      state.target = [(min[0] + max[0]) / 2, (min[1] + max[1]) / 2, (min[2] + max[2]) / 2];
      state.radius = Math.hypot(max[0] - min[0], max[1] - min[1], max[2] - min[2]) / 2 || 1;
      state.dist = state.radius / Math.tan(fovDeg * Math.PI / 360) * 1.1;
      upload(s);
      render();
      return s.count;
    },
    setView(az, el, dist) {
      state.az = az; state.el = Math.max(-89.99, Math.min(89.99, el));
      if (dist !== undefined && dist !== null) state.dist = dist;
      render();
      return { az: state.az, el: state.el, dist: state.dist };
    },
    render,
    project(x, y, z) {
      updateCamera();
      const v = [x, y, z, 1];
      const t = [0, 0, 0, 0], c = [0, 0, 0, 0];
      for (let r = 0; r < 4; r++) t[r] = view[r] * v[0] + view[4 + r] * v[1] + view[8 + r] * v[2] + view[12 + r];
      for (let r = 0; r < 4; r++) c[r] = proj[r] * t[0] + proj[4 + r] * t[1] + proj[8 + r] * t[2] + proj[12 + r] * t[3];
      const fovy = fovDeg * Math.PI / 180;
      const focalY = (canvas.height / 2) / Math.tan(fovy / 2);
      return { x: (c[0] / c[3] * 0.5 + 0.5) * canvas.width, y: (0.5 - c[1] / c[3] * 0.5) * canvas.height, depth: -t[2], pxPerUnit: focalY / -t[2] };
    },
    stats() {
      const s = state.splats;
      return s ? { count: s.count, bounds: { min: s.bounds.min, max: s.bounds.max }, file: state.file, fields: state.fields,
        width: canvas.width, height: canvas.height, view: { az: state.az, el: state.el, dist: state.dist, target: state.target },
        sorts: state.sorts, lastSortMs: state.lastSortMs } : { count: 0 };
    },
    pixels() {
      const w = canvas.width, h = canvas.height;
      const px = new Uint8Array(w * h * 4);
      gl.readPixels(0, 0, w, h, gl.RGBA, gl.UNSIGNED_BYTE, px);
      const flipped = new Uint8Array(w * h * 4);
      for (let y = 0; y < h; y++) flipped.set(px.subarray((h - 1 - y) * w * 4, (h - y) * w * 4), y * w * 4);
      return { width: w, height: h, data: flipped };
    },
  };
}
