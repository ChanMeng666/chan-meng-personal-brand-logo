# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- `assets/anime/chan-monkey-live.svg` — an expressive animated mark: eight emoji-style
  expressions (happy, love, cool, sweat, thinking, wow, cozy, sleepy) across a four-season
  cycle with colored petals, sun, leaves and snow. CSS-only, 100 s loop, respects
  `prefers-reduced-motion`.
- `assets/anime/chan-monkey-blink.svg` — minimal animated mark (occasional blink).
- `docs/animating-the-mark.md` — build guide for CSS-only SVG character animation: the layer
  model and invariants, the master-clock and gate-keyframe patterns, geometry probing with
  `isPointInFill`, the ink-on-ink problem, particle-system construction, the verification
  harness, and a failure gallery.
- Raster and icon exports (`assets/raster/`, `assets/icons/`) plus the Node rasterize
  toolchain (`src/rasterize.js`, `npm run rasterize`).
- Standard community-health documentation (`CONTRIBUTING.md`, `SECURITY.md`, `SUPPORT.md`, `GOVERNANCE.md`, this changelog).

## [1.0.0]

### Added
- Initial documented release of Chan Meng Personal Brand Logo.
