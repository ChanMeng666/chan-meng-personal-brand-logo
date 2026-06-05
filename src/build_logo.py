#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_logo.py — High-fidelity mathematical reconstruction of the hand-drawn
"Chan Monkey" logo.

The original `chan-monkey-logo-black.svg` draws every shape as a dense polyline
of hundreds of hand-placed points (`L` commands) — smooth to the eye but rough,
unmeasurable and impossible to edit. This script turns each of those rough
contours into a small set of **smooth cubic Bézier curves**, i.e. real
parametric polynomial functions

        B(t) = (1-t)^3 P0 + 3(1-t)^2 t C1 + 3(1-t) t^2 C2 + t^3 P3 ,  t in [0,1]

so the result is fully mathematical, reproducible and editable, yet keeps the
round, full, cute character of the original — including the off-centre hair
curl, which is preserved because we follow the real outline instead of
replacing it with idealized primitives.

Pipeline per contour:
   tokenize original -> dedupe -> uniform arc-length resample
   -> light periodic smoothing (removes hand jitter, keeps fullness)
   -> closed Catmull-Rom spline -> exact cubic Bézier segments.

Output: `chan-monkey-logo-math.svg`, structurally identical to the original
(black head with white face/ear holes via even-odd fill, black features on top,
CHAN wordmark) but every path is a clean Bézier curve.
"""

import math
import os
import re

# Paths are resolved relative to the repo root (this file lives in src/), so the
# script works no matter what the current working directory is.
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "archive", "chan-meng-logo-original-handdrawn.svg")

W, H = 276, 356
BLACK = "#000000"
WHITE = "#ffffff"

# Per-contour tuning: (resample step in px, smoothing passes).
# Smaller step / fewer passes = more faithful; larger / more = rounder.
TUNING = {
    "head":     (5.0, 1),   # head silhouette incl. the hair curl
    "facemask": (5.0, 1),   # white face (hole)
    "ear":      (3.5, 1),   # ear inner holes
    "nostril":  (2.5, 1),
    "mouth":    (3.5, 1),
    "letter":   (4.0, 1),   # CHAN glyphs
}


# ---------------------------------------------------------------------------
# 1. Parse the original SVG path data into contours (lists of points)
# ---------------------------------------------------------------------------
def tokenize_path(d, c_samples=8):
    """Return a list of contours; each contour is a list of (x, y) points.
    Handles absolute M/L/H/V/C and Z (the only commands the original uses),
    sampling each cubic `C` into `c_samples` points so curved glyph parts keep
    their shape."""
    tokens = re.findall(r'([MLHVCZ])|(-?\d*\.?\d+(?:e-?\d+)?)', d)
    stream = []
    for cmd, num in tokens:
        stream.append(('c', cmd) if cmd else ('n', float(num)))

    contours, cur = [], []
    i, cx, cy, start = 0, 0.0, 0.0, (0.0, 0.0)
    cmd = None

    def take(k):
        nonlocal i
        vals = [stream[i + j][1] for j in range(k)]
        i += k
        return vals

    while i < len(stream):
        if stream[i][0] == 'c':
            cmd = stream[i][1]; i += 1
            if cmd == 'Z':
                if cur:
                    contours.append(cur); cur = []
                cx, cy = start
                continue
        if cmd == 'M':
            x, y = take(2); cx, cy = x, y; start = (x, y)
            if cur:
                contours.append(cur)
            cur = [(cx, cy)]; cmd = 'L'
        elif cmd == 'L':
            x, y = take(2); cx, cy = x, y; cur.append((cx, cy))
        elif cmd == 'H':
            x = take(1)[0]; cx = x; cur.append((cx, cy))
        elif cmd == 'V':
            y = take(1)[0]; cy = y; cur.append((cx, cy))
        elif cmd == 'C':
            x1, y1, x2, y2, x, y = take(6)
            for s in range(1, c_samples + 1):
                t = s / float(c_samples); mt = 1 - t
                bx = mt**3*cx + 3*mt*mt*t*x1 + 3*mt*t*t*x2 + t**3*x
                by = mt**3*cy + 3*mt*mt*t*y1 + 3*mt*t*t*y2 + t**3*y
                cur.append((bx, by))
            cx, cy = x, y
        else:
            i += 1
    if cur:
        contours.append(cur)
    return contours


# ---------------------------------------------------------------------------
# 2. Geometry helpers
# ---------------------------------------------------------------------------
def _dist(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])


def dedupe(pts, eps=0.01):
    out = [pts[0]]
    for p in pts[1:]:
        if _dist(p, out[-1]) > eps:
            out.append(p)
    if len(out) > 1 and _dist(out[0], out[-1]) < eps:
        out.pop()
    return out


def resample_closed(pts, step):
    """Walk the closed polyline at uniform arc-length spacing ~= step."""
    n = len(pts)
    seg = [_dist(pts[k], pts[(k + 1) % n]) for k in range(n)]
    total = sum(seg)
    if total == 0:
        return pts
    m = max(16, int(round(total / step)))
    d = total / m
    out = []
    s_idx, cur = 0, 0.0
    for k in range(m):
        target = k * d
        while s_idx < n - 1 and cur + seg[s_idx] < target:
            cur += seg[s_idx]; s_idx += 1
        t = (target - cur) / seg[s_idx] if seg[s_idx] > 0 else 0.0
        a, b = pts[s_idx], pts[(s_idx + 1) % n]
        out.append((a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t))
    return out


def smooth_closed(pts, passes):
    """Periodic 3-tap [0.25, 0.5, 0.25] smoothing — removes hand jitter."""
    P = pts
    for _ in range(passes):
        n = len(P)
        P = [(0.25*P[(i-1) % n][0] + 0.5*P[i][0] + 0.25*P[(i+1) % n][0],
              0.25*P[(i-1) % n][1] + 0.5*P[i][1] + 0.25*P[(i+1) % n][1])
             for i in range(n)]
    return P


def catmull_rom_closed(P):
    """Closed uniform Catmull-Rom spline -> list of cubic Bézier segments
    (P0, C1, C2, P3) interpolating every point smoothly."""
    n = len(P)
    segs = []
    for i in range(n):
        p0, p1 = P[(i - 1) % n], P[i]
        p2, p3 = P[(i + 1) % n], P[(i + 2) % n]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6.0, p1[1] + (p2[1] - p0[1]) / 6.0)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6.0, p2[1] - (p3[1] - p1[1]) / 6.0)
        segs.append((p1, c1, c2, p2))
    return segs


def fit_contour(points, step, passes):
    return catmull_rom_closed(
        smooth_closed(resample_closed(dedupe(points), step), passes))


def fit_circle(points):
    """Best simple circle for an (already circular) contour: bbox centre and
    mean radius. Used for the eyes, which are exact circles in the original."""
    xs = [p[0] for p in points]; ys = [p[1] for p in points]
    cx, cy = (min(xs) + max(xs)) / 2.0, (min(ys) + max(ys)) / 2.0
    r = sum(math.hypot(x - cx, y - cy) for x, y in points) / len(points)
    return cx, cy, r


# ---------------------------------------------------------------------------
# 3. SVG emission
# ---------------------------------------------------------------------------
def _f(v):
    return f"{v:.2f}".rstrip("0").rstrip(".")


def subpath_d(segs):
    p0 = segs[0][0]
    d = f"M{_f(p0[0])} {_f(p0[1])}"
    for _, c1, c2, p3 in segs:
        d += f"C{_f(c1[0])} {_f(c1[1])} {_f(c2[0])} {_f(c2[1])} {_f(p3[0])} {_f(p3[1])}"
    return d + "Z"


def path_el(contours_segs, fill, evenodd=False, note=""):
    d = "".join(subpath_d(s) for s in contours_segs)
    fr = ' fill-rule="evenodd"' if evenodd else ""
    c = f"  <!-- {note} -->\n" if note else ""
    return f'{c}  <path d="{d}" fill="{fill}"{fr}/>'


def circle_el(cx, cy, r, fill, note=""):
    c = f"  <!-- {note} -->\n" if note else ""
    return f'{c}  <circle cx="{_f(cx)}" cy="{_f(cy)}" r="{_f(r)}" fill="{fill}"/>'


# ---------------------------------------------------------------------------
# 4. Fit every contour once (shared by all variants)
# ---------------------------------------------------------------------------
def load_contours():
    svg = open(SRC, encoding="utf-8").read()
    d1, d2 = re.findall(r'<path d="(.*?)"', svg, re.S)[:2]
    head, facemask, ear_r, ear_l = tokenize_path(d1)
    (eye_l, eye_r, nos_l, nos_r, mouth,
     gC, gH, gA, gA_hole, gN) = tokenize_path(d2)

    def F(pts, key):
        return fit_contour(pts, *TUNING[key])

    monkey_h = max(p[1] for p in head)          # tight bottom of the chin
    return {
        "head": F(head, "head"),
        "face": [F(facemask, "facemask"), F(ear_r, "ear"), F(ear_l, "ear")],
        "eyes": [fit_circle(eye_l), fit_circle(eye_r)],
        "features": [F(nos_l, "nostril"), F(nos_r, "nostril"), F(mouth, "mouth")],
        "chan": [F(gC, "letter"), F(gH, "letter"), F(gA, "letter"),
                 F(gA_hole, "letter"), F(gN, "letter")],
        "monkey_h": monkey_h,
    }


# ---------------------------------------------------------------------------
# 5. Render one variant.  Single-colour (`ink`) knockout design, exactly like
# the original: the head is one even-odd path whose inner contours (the face
# and the inner ears) are HOLES. With a solid background they show that colour;
# with no background they are genuinely transparent — the face is see-through.
# Eyes / nostrils / mouth / CHAN are `ink` marks painted on top.
# ---------------------------------------------------------------------------
def render(C, ink=BLACK, background=WHITE, with_text=True):
    vb_h = H if with_text else int(math.ceil(C["monkey_h"]))
    out = [f'<svg width="{W}" height="{vb_h}" viewBox="0 0 {W} {vb_h}" '
           f'xmlns="http://www.w3.org/2000/svg">']
    if background is not None:
        out.append(f'  <rect width="{W}" height="{vb_h}" fill="{background}"/>')

    # head silhouette with the face + inner ears knocked out (even-odd holes)
    out.append(path_el([C["head"]] + C["face"], ink, evenodd=True,
                       note="head silhouette with see-through face/ear holes"))

    # ink features sitting inside the (transparent) face
    for cx, cy, r in C["eyes"]:
        out.append(circle_el(cx, cy, r, ink, note="eye"))
    out.append(path_el(C["features"], ink, note="nostrils + mouth"))

    if with_text:
        out.append(path_el(C["chan"], ink, evenodd=True, note="CHAN wordmark"))

    out.append("</svg>")
    return "\n".join(out)


# (relative path under the repo root, ink, background, with_text)
VARIANTS = [
    # Full lockup (monkey + CHAN)
    ("assets/full/chan-meng-logo-black-on-white.svg",    BLACK, WHITE, True),
    ("assets/full/chan-meng-logo-white-on-black.svg",    WHITE, BLACK, True),
    ("assets/full/chan-meng-logo-black-transparent.svg", BLACK, None,  True),
    ("assets/full/chan-meng-logo-white-transparent.svg", WHITE, None,  True),
    # Monkey only (no wordmark) — for avatars, app icons, favicons
    ("assets/monkey/chan-meng-monkey-black-on-white.svg",    BLACK, WHITE, False),
    ("assets/monkey/chan-meng-monkey-white-on-black.svg",    WHITE, BLACK, False),
    ("assets/monkey/chan-meng-monkey-black-transparent.svg", BLACK, None,  False),
    ("assets/monkey/chan-meng-monkey-white-transparent.svg", WHITE, None,  False),
]


if __name__ == "__main__":
    C = load_contours()
    for rel, ink, bg, txt in VARIANTS:
        path = os.path.join(ROOT, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(render(C, ink=ink, background=bg, with_text=txt))
        print(f"wrote {rel}")
