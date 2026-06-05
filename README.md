# Chan Meng — Personal Brand Logo

A personal-brand monkey logo, reconstructed from a hand-drawn original into clean
**mathematical curves**. The hand-drawn source was made of hundreds of hand-placed
points (`L` segments) — rough, unmeasurable and hard to edit. Every contour is now
fitted to a small set of **smooth cubic Bézier curves** (genuine parametric
polynomial functions), with the eyes emitted as **exact circles**.

The result **faithfully preserves the original** — smooth, full and cute, right down
to the **off-center hair curl** — while being fully mathematical: reproducible,
infinitely scalable, and parametrically tweakable.

![original vs reconstruction vs diff](docs/comparison.png)

> In the diff panel the image is almost entirely black (only hair-thin edges remain),
> which means the reconstruction matches the original very closely.

## Logo variants

Ready-to-use exports live in [`assets/`](assets) — the **full lockup** (monkey + CHAN)
in [`assets/full/`](assets/full) and the **monkey only** (cropped, for avatars / app
icons / favicons) in [`assets/monkey/`](assets/monkey), each in four color schemes.

Each variant is a **single-color knockout**: the head is one ink colour and the face
+ inner ears are **transparent holes**. On the solid-background versions those holes
show the background colour; on the transparent versions they are genuinely
see-through, so the backdrop shows through the monkey's face. Use the **black**
variants on light backgrounds and the **white** variants on dark ones.

![all variants on a checkerboard](docs/variants-preview.png)

| File | Content | Ink | Background | Best on |
|---|---|---|---|---|
| `assets/full/chan-meng-logo-black-on-white.svg` | monkey + CHAN | black | white | light surfaces |
| `assets/full/chan-meng-logo-white-on-black.svg` | monkey + CHAN | white | black | dark surfaces |
| `assets/full/chan-meng-logo-black-transparent.svg` | monkey + CHAN | black | transparent | light / colored |
| `assets/full/chan-meng-logo-white-transparent.svg` | monkey + CHAN | white | transparent | dark / colored |
| `assets/monkey/chan-meng-monkey-black-on-white.svg` | monkey only | black | white | light surfaces |
| `assets/monkey/chan-meng-monkey-white-on-black.svg` | monkey only | white | black | dark surfaces |
| `assets/monkey/chan-meng-monkey-black-transparent.svg` | monkey only | black | transparent | light / colored |
| `assets/monkey/chan-meng-monkey-white-transparent.svg` | monkey only | white | transparent | dark / colored |

## Project structure

```
.
├── assets/                     # ready-to-use logos
│   ├── full/                   #   monkey + CHAN wordmark (4 color schemes)
│   └── monkey/                 #   monkey only, cropped (4 color schemes)
├── src/
│   └── build_logo.py           # generator (Python stdlib, no dependencies)
├── docs/
│   ├── logo-math.md            # the math write-up
│   ├── comparison.png          # original / reconstruction / diff
│   └── variants-preview.png    # all variants on a checkerboard
├── archive/
│   └── chan-meng-logo-original-handdrawn.svg   # the original hand-drawn source
└── README.md
```

## Usage

```bash
python src/build_logo.py        # regenerates everything under assets/
```

No third-party dependencies (Python standard library only). The script reads the
archived original and rewrites all variants. To trade smoothness against fidelity,
edit the `(resample_step, smoothing_passes)` for each contour in the `TUNING` dict at
the top of `src/build_logo.py` (larger step → smoother and fewer curves; smaller →
closer to the original); to add a color scheme, extend the `VARIANTS` list at the
bottom. Re-run to regenerate — fully reproducible.

## The mathematical method (why this version is smooth and full)

Rather than *approximating* the shape with a few idealized primitives (which throws
away the hand-drawn fullness and charm), this approach **fits smooth curves along
the original's real outline**. Each contour is resampled to uniform arc length,
lightly smoothed to remove hand jitter, then turned into a chain of cubic Bézier
segments via a closed Catmull-Rom spline. Each segment is a parametric polynomial:

```
B(t) = (1-t)³P₀ + 3(1-t)²t·C₁ + 3(1-t)t²·C₂ + t³P₃,  t ∈ [0,1]
```

The curve passes through every sample point and is everywhere tangent-continuous
(C¹), so it hugs the original shape while staying naturally smooth. See
[`docs/logo-math.md`](docs/logo-math.md) for the full details.

## Brand & usage

The **code** (`src/build_logo.py`) is free to read, learn from, and adapt. The
**Chan Meng monkey logo and the “CHAN” wordmark are a personal brand identity** —
please don't use them to represent yourself, your project, or your organization.
