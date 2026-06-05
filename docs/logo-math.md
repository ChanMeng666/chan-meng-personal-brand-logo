# Chan Monkey Logo — Mathematical Definition (Cubic Bézier Fit)

The original draws every shape as a polyline of **hundreds of hand-placed points**
(`L` commands) — smooth to the eye, but rough, unmeasurable and uneditable. This
project turns each contour into a **small set of smooth cubic Bézier curves**, i.e.
genuine parametric polynomial functions. That keeps the original's smooth, full,
cute character — including the **asymmetric hair curl on top** — while making the
artwork fully mathematical, reproducible, infinitely scalable and parametrically
tweakable.

## 1. The core object: the cubic Bézier curve

Each segment is defined by four control points $P_0,C_1,C_2,P_3$ and is a parametric
cubic polynomial:

$$\mathbf{B}(t)=(1-t)^3\,P_0+3(1-t)^2t\,C_1+3(1-t)\,t^2\,C_2+t^3\,P_3,\qquad t\in[0,1].$$

The whole logo = a set of **piecewise cubic Bézier curves** (each contour a closed
chain), plus **two exact circles** for the eyes. Every control point lives in the
`<path d="…C…">` data of the generated SVGs in `assets/`
(e.g. `assets/full/chan-meng-logo-black-on-white.svg`).

## 2. Coordinate system

SVG `viewBox="0 0 276 356"`, origin top-left, $y$ pointing down — identical to the
original, so it is a drop-in replacement. (For a face-centered, $y$-up Cartesian
frame, use $X=x-138,\ Y=178-y$.)

## 3. From the original polyline to Bézier curves

For each closed contour, in order:

1. **Parse** the original path into a polyline (handling `M/L/H/V/C/Z`);
2. **De-duplicate** (drop repeated / near-coincident points);
3. **Resample at uniform arc length**, step $h$ (see table) — even point spacing;
4. **Periodic smoothing**: $P_i \leftarrow \tfrac14 P_{i-1}+\tfrac12 P_i+\tfrac14 P_{i+1}$,
   repeated $k$ times — removes hand jitter while keeping the shape full;
5. **Closed Catmull–Rom spline → cubic Bézier**: for consecutive points
   $P_{i-1},P_i,P_{i+1},P_{i+2}$, the segment from $P_i$ to $P_{i+1}$ uses control points

$$C_1=P_i+\frac{P_{i+1}-P_{i-1}}{6},\qquad C_2=P_{i+1}-\frac{P_{i+2}-P_i}{6}.$$

This guarantees the curve **passes through every sample point** and is everywhere
$C^1$ (tangent-continuous) — the mathematical source of the smoothness. A larger
step $h$ or more smoothing passes $k$ → smoother and fewer segments; smaller → closer
to the original.

## 4. Shape structure (mirrors the original, two colors)

| Layer | Elements | Fill |
|---|---|---|
| 1 | Head silhouette + white face hole + two inner-ear holes (one `even-odd` path) | black (holes show the white background) |
| 2 | Two nostrils + mouth (one path) | black |
| 2 | Two eyes (`<circle>`, exact circles) | black |
| 3 | `CHAN` (one `even-odd` path; the A has a counter) | black |

The `even-odd` fill rule turns inner sub-contours into holes automatically (white
face, inner ears, the counter of the letter A).

## 5. Per-contour fit parameters and segment counts

| Contour | Raw points | Resample step $h$ | Smoothing $k$ | Bézier segments |
|---|---|---|---|---|
| Head silhouette (incl. curl) | 251 | 5.0 | 1 | 189 |
| White face | 125 | 5.0 | 1 | 89 |
| Right ear / left ear | 40 / 40 | 3.5 | 1 | 29 / 29 |
| Left eye / right eye | 33 / 33 | — | — | exact circle $r=16.6$ |
| Left nostril / right nostril | 33 / 33 | 2.5 | 1 | 22 / 22 |
| Mouth (smile) | 43 | 3.5 | 1 | 40 |
| C / H / A / A-hole / N | 98/64/54/15/72 | 4.0 | 1 | 69/80/58/16/81 |

Total ≈ **724 cubic Bézier segments + 2 circles**. Eye centers are
$(104.6,152.6)$ and $(170.8,152.6)$, radius $16.6$.

## 6. Reproduce and tweak

```bash
python src/build_logo.py        # read the archived original -> write all assets/
```

No third-party dependencies. Adjust the `(step, smoothing_passes)` for any contour in
the `TUNING` dict of `src/build_logo.py` to control smoothness vs. fidelity; the exact
control points all land in the output SVG, where each segment is the parametric cubic
polynomial from Section 1.
