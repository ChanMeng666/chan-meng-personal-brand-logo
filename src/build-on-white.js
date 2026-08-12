#!/usr/bin/env node
/*
 * build-on-white.js — derive the on-white card variant of the animated mark.
 * Companion to build_logo.py (static SVGs) and rasterize.js (PNG/ICO).
 * Run from the repo root:  node src/build-on-white.js
 *
 * Output:
 *   assets/anime/chan-monkey-live-on-white.svg
 *
 * Why this variant exists
 * -----------------------
 * The animated marks are single-color knockouts in #070607 on transparency, so
 * they are the "black-transparent" cell of the variant grid and nothing else.
 * The static grid answers dark backgrounds with a white-INK variant, but an
 * <img>-loaded SVG has no prefers-color-scheme hook (see docs/animating-the-mark.md
 * section 9), so a consumer that wants one file to work on BOTH a light and a
 * dark page cannot swap inks — it has to bring its own background. On GitHub's
 * dark theme the transparent original reads as a black shape on a near-black
 * page.
 *
 * This variant supplies that background: the same animation, unchanged, sitting
 * on a white card. It is the animated counterpart of
 * assets/monkey/chan-meng-monkey-black-on-white.svg, with two differences that
 * are deliberate rather than stylistic drift:
 *
 *   1. The card is padded and rounded, not a flush full-bleed rect. The head
 *      geometry fills its 276x263 box edge to edge (measured, not assumed —
 *      getBBox gives x 0.2 .. 275.8, y 0.4 .. 262.8), so a flush rect would put
 *      the ink hard against all four sides. The static variants can get away
 *      with that because they are usually placed inside someone else's frame;
 *      an animated mark dropped straight into a README is the frame.
 *   2. The drawing is clipped to the card. The seasonal particles are authored
 *      to overflow the art box and be cut off by the viewBox edge; widening the
 *      viewBox for padding un-clips them, and petals drift out through the
 *      rounded corners onto the page.
 *
 * Requires: nothing (Node standard library only).
 */
const fs = require('fs');
const path = require('path');

const ROOT = path.resolve(__dirname, '..');
const ANIME = path.join(ROOT, 'assets', 'anime');
const SRC = path.join(ANIME, 'chan-monkey-live.svg');
const OUT = path.join(ANIME, 'chan-monkey-live-on-white.svg');

// The source art box. Both the head path and the base overlays live inside it;
// the seasonal particle groups deliberately exceed it (y -28.5 .. 269).
const ART_W = 276;
const ART_H = 263;

// Card geometry. PAD is breathing room around the art box; the radius is kept
// as a ratio so the card stays proportionally the same shape if PAD changes.
const PAD = 16;
const RADIUS_RATIO = 20 / 98;
const CARD_FILL = '#ffffff';
const CARD_STROKE = '#e6e4df';
const CARD_STROKE_W = 1.5;

const W = ART_W + PAD * 2;
const H = ART_H + PAD * 2;
const RX = Math.round(RADIUS_RATIO * (Math.min(W, H) - 2));
const CARD = `x="${1 - PAD}" y="${1 - PAD}" width="${W - 2}" height="${H - 2}" rx="${RX}"`;

const raw = fs.readFileSync(SRC, 'utf8');
const EOL = raw.includes('\r\n') ? '\r\n' : '\n';
let svg = raw.split('\r\n').join('\n');

// 1. Pad the root viewBox outward. Every artwork coordinate is left exactly as
//    authored — only the window onto it grows — so the head geometry stays
//    byte-identical to chan-meng-monkey-black-transparent.svg (Invariant 1).
//    The clip-path goes on the ROOT rather than a wrapper <g>: wrapping the
//    artwork would stop the base paths being direct <svg> children and would
//    silently retarget the `svg > path:nth-of-type(2)` mouth gate (Invariant 2).
const root = svg.match(/<svg\b[^>]*>/)?.[0];
if (!root) throw new Error('no <svg> root element in ' + SRC);
const padded = root
  .replace(new RegExp(`\\bwidth="${ART_W}"`), `width="${W}"`)
  .replace(new RegExp(`\\bheight="${ART_H}"`), `height="${H}"`)
  .replace(
    new RegExp(`\\bviewBox="0 0 ${ART_W} ${ART_H}"`),
    `viewBox="${-PAD} ${-PAD} ${W} ${H}"`
  )
  .replace(/>$/, ' clip-path="url(#cv-card-clip)">');
if (padded === root) {
  throw new Error(
    `root tag did not change — expected width="${ART_W}" height="${ART_H}" ` +
      `viewBox="0 0 ${ART_W} ${ART_H}", got: ${root}`
  );
}
svg = svg.replace(root, padded);

svg = svg.replace(
  '<title>Chan Monkey — Live</title>',
  '<title>Chan Monkey — Live (on white)</title>'
);

// 2. The clip shape, in <defs> beside the particle symbols. Same geometry as
//    the card, so the hairline's outer half is clipped away and the border
//    reads at ~0.75px — imperceptible at any size this renders at, and the
//    price of corners that actually contain the animation.
const clip = `  <clipPath id="cv-card-clip"><rect ${CARD}/></clipPath>\n`;

// 3. The card itself, painted before anything else. It lives in a <g> because
//    Invariant 2 forbids new bare shapes as direct children of <svg>. A <rect>
//    would not in fact shift the mouth gate (that selector counts <path>
//    siblings only), but honouring the invariant literally keeps this file
//    diffable against its source and keeps the rule un-eroded.
//
//    Note for Invariant 3 / the accessibility contract: the card is static and
//    always visible BY DESIGN, so under prefers-reduced-motion this file falls
//    back to the neutral mark on its card — the counterpart of
//    chan-meng-monkey-black-on-white.svg, not of the transparent one.
const card = [
  '',
  '<!-- ============ ON-WHITE CARD (this variant only) ============',
  '     Generated by src/build-on-white.js from chan-monkey-live.svg — do not',
  '     hand-edit; re-run the script instead. Four differences from the source,',
  '     and no others: this group, the #cv-card-clip shape in <defs>, the',
  '     clip-path on the root, and the root viewBox padded outward. Every',
  '     artwork node is untouched, so all three INVARIANTs still hold. -->',
  `<g class="cv-card"><rect ${CARD} fill="${CARD_FILL}" stroke="${CARD_STROKE}" stroke-width="${CARD_STROKE_W}"/></g>`,
  '',
].join('\n');

const anchor = '</defs>\n';
if (!svg.includes(anchor)) throw new Error('no </defs> anchor in ' + SRC);
// Function replacers: the inserted text is literal, and a string replacement
// would let any $-sequence in it be read as a capture reference.
svg = svg.replace(anchor, () => clip + anchor + card);

fs.writeFileSync(OUT, EOL === '\n' ? svg : svg.split('\n').join(EOL));
console.log(
  `✓ ${path.relative(ROOT, OUT)}  ${W}x${H}  viewBox ${-PAD} ${-PAD} ${W} ${H}  rx ${RX}`
);
