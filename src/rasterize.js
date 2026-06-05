#!/usr/bin/env node
/*
 * rasterize.js — generate raster (PNG) and icon (ICO) exports from the
 * ready-to-use SVG logo variants in ../assets. Companion to build_logo.py
 * (which produces the SVGs). Run from the repo root:  node src/rasterize.js
 *
 * Output:
 *   assets/raster/monkey-{black,white}-<size>.png   (transparent bg, square)
 *   assets/raster/full-{black,white}-<size>.png      (transparent bg, native aspect)
 *   assets/icons/favicon.ico                         (16/32/48, monkey black-on-white)
 *   assets/icons/apple-touch-icon.png                (180, monkey black-on-white, opaque)
 *
 * Requires: sharp, png-to-ico (local devDependencies).
 */
const fs = require('fs');
const path = require('path');
const sharp = require('sharp');
const pngToIco = require('png-to-ico').default || require('png-to-ico');

const ROOT = path.resolve(__dirname, '..');
const ASSETS = path.join(ROOT, 'assets');
const RASTER = path.join(ASSETS, 'raster');
const ICONS = path.join(ASSETS, 'icons');

const MONKEY_SIZES = [16, 32, 48, 64, 128, 180, 192, 256, 512];
const FULL_SIZES = [256, 512];

const SRC = {
  monkeyBlack: path.join(ASSETS, 'monkey', 'chan-meng-monkey-black-transparent.svg'),
  monkeyWhite: path.join(ASSETS, 'monkey', 'chan-meng-monkey-white-transparent.svg'),
  monkeyOnWhite: path.join(ASSETS, 'monkey', 'chan-meng-monkey-black-on-white.svg'),
  fullBlack: path.join(ASSETS, 'full', 'chan-meng-logo-black-transparent.svg'),
  fullWhite: path.join(ASSETS, 'full', 'chan-meng-logo-white-transparent.svg'),
};

function ensureDir(d) {
  fs.mkdirSync(d, { recursive: true });
}

// Render an SVG onto a transparent SQUARE canvas of `size`, preserving aspect
// with a little breathing-room padding (10% margin).
async function renderSquare(svgPath, size, outPath, { opaqueBg = null } = {}) {
  const inner = Math.round(size * 0.84); // 8% margin each side
  const logo = await sharp(svgPath, { density: 384 })
    .resize(inner, inner, { fit: 'contain', background: { r: 0, g: 0, b: 0, alpha: 0 } })
    .png()
    .toBuffer();
  const bg = opaqueBg || { r: 0, g: 0, b: 0, alpha: 0 };
  await sharp({ create: { width: size, height: size, channels: 4, background: bg } })
    .composite([{ input: logo, gravity: 'center' }])
    .png()
    .toFile(outPath);
}

// Render an SVG at a target WIDTH keeping native aspect ratio (transparent bg).
async function renderWidth(svgPath, width, outPath) {
  await sharp(svgPath, { density: 384 })
    .resize({ width, fit: 'contain', background: { r: 0, g: 0, b: 0, alpha: 0 } })
    .png()
    .toFile(outPath);
}

async function main() {
  ensureDir(RASTER);
  ensureDir(ICONS);

  // Monkey PNGs (transparent, square) — both ink colors.
  for (const size of MONKEY_SIZES) {
    await renderSquare(SRC.monkeyBlack, size, path.join(RASTER, `monkey-black-${size}.png`));
    await renderSquare(SRC.monkeyWhite, size, path.join(RASTER, `monkey-white-${size}.png`));
  }

  // Full lockup PNGs (transparent, native aspect) — both ink colors.
  for (const size of FULL_SIZES) {
    await renderWidth(SRC.fullBlack, size, path.join(RASTER, `full-black-${size}.png`));
    await renderWidth(SRC.fullWhite, size, path.join(RASTER, `full-white-${size}.png`));
  }

  // Favicon: opaque white square so it stays visible on light AND dark browser chrome.
  const WHITE = { r: 255, g: 255, b: 255, alpha: 1 };
  const icoSizes = [16, 32, 48];
  const icoBuffers = [];
  for (const size of icoSizes) {
    const buf = await sharp(SRC.monkeyOnWhite, { density: 384 })
      .resize(size, size, { fit: 'contain', background: WHITE })
      .flatten({ background: WHITE })
      .png()
      .toBuffer();
    icoBuffers.push(buf);
  }
  const ico = await pngToIco(icoBuffers);
  fs.writeFileSync(path.join(ICONS, 'favicon.ico'), ico);

  // Apple touch icon: 180px opaque white square.
  await renderSquare(SRC.monkeyOnWhite, 180, path.join(ICONS, 'apple-touch-icon.png'), {
    opaqueBg: WHITE,
  });
  // Also drop a 32px PNG favicon (modern browsers) and 192/512 for web manifests.
  for (const size of [32, 192, 512]) {
    await renderSquare(SRC.monkeyOnWhite, size, path.join(ICONS, `favicon-${size}.png`), {
      opaqueBg: WHITE,
    });
  }

  console.log('Done. Raster ->', path.relative(ROOT, RASTER), '| Icons ->', path.relative(ROOT, ICONS));
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
