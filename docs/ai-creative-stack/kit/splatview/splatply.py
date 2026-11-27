"""Shared helpers: oriented surface Gaussians and the 3DGS PLY writer."""
from __future__ import annotations

from pathlib import Path

import numpy as np
from scipy.spatial import cKDTree

SH_C0 = 0.28209479177387814
FIELDS = ["x", "y", "z", "nx", "ny", "nz", "f_dc_0", "f_dc_1", "f_dc_2", "opacity",
          "scale_0", "scale_1", "scale_2", "rot_0", "rot_1", "rot_2", "rot_3"]


def _unit(v):
    return v / np.maximum(np.linalg.norm(v, axis=-1, keepdims=True), 1e-12)


def tangent_frame(normals):
    """Any orthonormal tangent per normal (stable choice of helper axis)."""
    helper = np.where(np.abs(normals[:, 1:2]) < 0.9, [[0.0, 1.0, 0.0]], [[1.0, 0.0, 0.0]])
    t = _unit(np.cross(helper, normals))
    return t


def rotmat_to_quat(R):
    """(N,3,3) rotation matrices -> (N,4) unit quaternions (w, x, y, z), w >= 0."""
    m = R
    m00, m11, m22 = m[:, 0, 0], m[:, 1, 1], m[:, 2, 2]
    tr = m00 + m11 + m22
    # Shepperd's method: pick the largest of 4w^2, 4x^2, 4y^2, 4z^2 for stability
    cand = np.stack([tr, m00, m11, m22], axis=1)
    pick = np.argmax(cand, axis=1)
    q = np.zeros((len(m), 4))
    s = np.sqrt(np.maximum(1.0 + tr, 1e-12)) * 2  # pick 0
    i = pick == 0
    q[i, 0] = 0.25 * s[i]
    q[i, 1] = (m[i, 2, 1] - m[i, 1, 2]) / s[i]
    q[i, 2] = (m[i, 0, 2] - m[i, 2, 0]) / s[i]
    q[i, 3] = (m[i, 1, 0] - m[i, 0, 1]) / s[i]
    i = pick == 1
    s = np.sqrt(np.maximum(1.0 + m00 - m11 - m22, 1e-12)) * 2
    q[i, 0] = (m[i, 2, 1] - m[i, 1, 2]) / s[i]
    q[i, 1] = 0.25 * s[i]
    q[i, 2] = (m[i, 0, 1] + m[i, 1, 0]) / s[i]
    q[i, 3] = (m[i, 0, 2] + m[i, 2, 0]) / s[i]
    i = pick == 2
    s = np.sqrt(np.maximum(1.0 + m11 - m00 - m22, 1e-12)) * 2
    q[i, 0] = (m[i, 0, 2] - m[i, 2, 0]) / s[i]
    q[i, 1] = (m[i, 0, 1] + m[i, 1, 0]) / s[i]
    q[i, 2] = 0.25 * s[i]
    q[i, 3] = (m[i, 1, 2] + m[i, 2, 1]) / s[i]
    i = pick == 3
    s = np.sqrt(np.maximum(1.0 + m22 - m00 - m11, 1e-12)) * 2
    q[i, 0] = (m[i, 1, 0] - m[i, 0, 1]) / s[i]
    q[i, 1] = (m[i, 0, 2] + m[i, 2, 0]) / s[i]
    q[i, 2] = (m[i, 1, 2] + m[i, 2, 1]) / s[i]
    q[i, 3] = 0.25 * s[i]
    q = _unit(q)
    q[q[:, 0] < 0] *= -1
    return q


def quat_to_rotmat(q):
    q = _unit(np.asarray(q, dtype=np.float64))
    w, x, y, z = q[:, 0], q[:, 1], q[:, 2], q[:, 3]
    return np.stack([
        np.stack([1 - 2 * (y * y + z * z), 2 * (x * y - w * z), 2 * (x * z + w * y)], -1),
        np.stack([2 * (x * y + w * z), 1 - 2 * (x * x + z * z), 2 * (y * z - w * x)], -1),
        np.stack([2 * (x * z - w * y), 2 * (y * z + w * x), 1 - 2 * (x * x + y * y)], -1),
    ], axis=1)


def surface_gaussians(points, normals, k=8, size_factor=1.0, thin_ratio=0.08, max_aniso=3.0):
    """Flat Gaussians on a sampled surface.

    For each sample, the k nearest neighbours are projected into the tangent
    plane. The 2x2 covariance of those offsets gives the in-plane principal
    directions and the two in-plane scales (local sample spacing). The third
    axis lies along the normal and is thin. Returns (scales (N,3), quats (N,4)).
    """
    n = len(points)
    normals = _unit(normals)
    k = int(min(k, max(2, n - 1)))
    tree = cKDTree(points)
    dist, idx = tree.query(points, k=k + 1)
    dist, idx = dist[:, 1:], idx[:, 1:]
    t1 = tangent_frame(normals)
    t2 = np.cross(normals, t1)
    off = points[idx] - points[:, None, :]  # (N,k,3)
    a = np.einsum("nkd,nd->nk", off, t1)
    b = np.einsum("nkd,nd->nk", off, t2)
    caa = (a * a).mean(1)
    cbb = (b * b).mean(1)
    cab = (a * b).mean(1)
    # eigen-decomposition of [[caa, cab], [cab, cbb]]
    mid = 0.5 * (caa + cbb)
    rad = np.sqrt(np.maximum(0.25 * (caa - cbb) ** 2 + cab * cab, 0.0))
    l1 = mid + rad
    l2 = np.maximum(mid - rad, 1e-20)
    ang = 0.5 * np.arctan2(2 * cab, caa - cbb)
    e1 = np.cos(ang)[:, None] * t1 + np.sin(ang)[:, None] * t2
    e2 = np.cross(normals, e1)
    # local sample spacing from the k-th neighbour radius: density = k / (pi r_k^2),
    # spacing = 1 / sqrt(density). (Nearest-neighbour distance alone underestimates it.)
    spacing = dist[:, k - 1] * np.sqrt(np.pi / k)
    s1 = np.sqrt(l1)
    s2 = np.sqrt(l2)
    s2 = np.maximum(s2, s1 / max_aniso)
    # rescale so the mean in-plane scale tracks the nearest-neighbour spacing
    norm = np.sqrt(s1 * s2)
    s1 = s1 / np.maximum(norm, 1e-12) * spacing * size_factor
    s2 = s2 / np.maximum(norm, 1e-12) * spacing * size_factor
    global_sp = np.median(spacing)
    lo, hi = 0.25 * global_sp * size_factor, 4.0 * global_sp * size_factor
    s1 = np.clip(s1, lo, hi)
    s2 = np.clip(s2, lo, hi)
    s3 = np.minimum(s1, s2) * thin_ratio
    R = np.stack([e1, e2, normals], axis=2)  # columns are local axes
    quats = rotmat_to_quat(R)
    return np.stack([s1, s2, s3], axis=1), quats


def write_ply(path, xyz, normals, rgb, opacity, scales, quats):
    """Write a standard 3D Gaussian Splatting PLY (binary little endian, SH degree 0).

    rgb in [0, 1]; opacity in (0, 1); scales linear (stored as log); quats (w,x,y,z).
    """
    n = len(xyz)
    rgb = np.clip(np.asarray(rgb, dtype=np.float64), 0.0, 1.0)
    op = np.clip(np.asarray(opacity, dtype=np.float64), 1e-4, 1 - 1e-4)
    data = np.zeros((n, len(FIELDS)), dtype="<f4")
    data[:, 0:3] = xyz
    data[:, 3:6] = normals
    data[:, 6:9] = (rgb - 0.5) / SH_C0
    data[:, 9] = np.log(op / (1.0 - op))
    data[:, 10:13] = np.log(np.maximum(scales, 1e-12))
    data[:, 13:17] = _unit(quats)
    header = "ply\nformat binary_little_endian 1.0\n"
    header += f"comment written by kit/splatview\nelement vertex {n}\n"
    header += "".join(f"property float {f}\n" for f in FIELDS)
    header += "end_header\n"
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "wb") as fh:
        fh.write(header.encode("ascii"))
        fh.write(data.tobytes())
    return path


def read_ply(path):
    """Read back a float-only binary little-endian PLY into a dict of arrays."""
    raw = Path(path).read_bytes()
    end = raw.index(b"end_header\n") + len(b"end_header\n")
    head = raw[:end].decode("ascii").splitlines()
    n = 0
    names = []
    for line in head:
        p = line.split()
        if p[:2] == ["element", "vertex"]:
            n = int(p[2])
        elif p and p[0] == "property":
            if p[1] != "float":
                raise ValueError("read_ply only handles float properties")
            names.append(p[2])
    arr = np.frombuffer(raw, dtype="<f4", count=n * len(names), offset=end).reshape(n, len(names))
    return {name: arr[:, i] for i, name in enumerate(names)}
