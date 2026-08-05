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

## 6. Animated variants (`assets/anime/`)

> This section states the contract. For the full build guide — patterns, geometry probing,
> the verification harness and the failure gallery — see
> [`animating-the-mark.md`](animating-the-mark.md).

The two animated files are hand-maintained, not generated. Three invariants keep them
honest, and any edit must preserve all three:

1. **The base nodes are byte-identical** to
   `assets/monkey/chan-meng-monkey-black-transparent.svg`: the even-odd head path, the
   `<g class="cv-blink-1">` eye group, and the nostrils+mouth path, in that order. Every
   added element is a *sibling*, never a modification.
2. **No new bare `<path>` / `<circle>` / `<ellipse>` may be a direct child of `<svg>`.**
   New content goes inside a `<g>` or `<defs>`. `chan-monkey-live.svg` gates the base mouth
   with the structural selector `svg > path:nth-of-type(2)`, which silently retargets if
   this rule is broken. (The base nodes are gated purely from CSS, which is how they can
   stay byte-identical while still being animated.)
3. **Every overlay group's static, un-animated state is `opacity: 0`**, so the
   `@media (prefers-reduced-motion: reduce) { * { animation: none !important } }` fallback
   leaves exactly the neutral mark.

`chan-monkey-live.svg` runs one master loop of $D = 100\text{ s}$ (`linear`, `infinite`).
That value is chosen so $1\text{ s} = 1\,\%$ — every percentage in the stylesheet is simply
the second at which it fires, which makes the fifteen interlocking gate keyframes readable
and checkable by hand. It is divided into four 25 s seasonal acts, each holding two 8.5 s
expressions separated by neutral gaps:

| Act | 0–2.5 s | 2.5–11 s | 11–14 s | 14–22.5 s | 22.5–25 s |
|---|---|---|---|---|---|
| spring / summer / autumn / winter | neutral | expression A | neutral | expression B | neutral |

Act boundaries fall on 25 / 50 / 75 %, where the seasonal particle groups cross-dissolve over
1 s. The pacing is intentionally unhurried: a visitor should be able to watch for a minute
without the loop becoming obvious.

The original 5 s blink is left untouched and layered on as a second animation on the same
element — legal only because the blink animates `transform` while the new gate animates
`opacity`. Its blinks land at $t = 4.8 + 5k$ s. Those that fall inside a window where the
base eyes are gated off are simply invisible; the ones that land in a neutral gap, or inside
the two windows that keep the base eyes (😅 sweat and 🤔 thinking), read as ordinary blinking
and are left in deliberately.

Two geometric facts constrain where facial overlays may sit, both measured from the fitted
outline rather than assumed:

- The face hole is **not** an oval — a forehead wedge splits it into two lobes above
  $y \approx 137.5$ (at $y = 122$ they span $x \in [99.0, 115.6]$ and $[160.4, 177.1]$), so
  nothing may occupy $x \in [133, 142]$ above $y = 138$.
- The hole has a **cheek waist at $y \approx 183$**, where its left edge reaches $x = 91.6$.

Colour appears only in the seasonal particles, the winter props and the 😅 sweat drop,
declared as CSS custom
properties on the `svg` selector and applied through classes (`var()` inside a presentation
attribute is not portable). Particles use a three-level nesting — static `transform`
attribute, then a fall group, then a spin node — because a CSS `transform` overrides the
`transform` presentation attribute on the same element.

## 7. Reproduce and tweak

```bash
python src/build_logo.py        # read the archived original -> write all assets/
```

No third-party dependencies. Adjust the `(step, smoothing_passes)` for any contour in
the `TUNING` dict of `src/build_logo.py` to control smoothness vs. fidelity; the exact
control points all land in the output SVG, where each segment is the parametric cubic
polynomial from Section 1.
