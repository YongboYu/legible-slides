# The theme/token contract

_Resolves [#2](https://github.com/YongboYu/legible-slides/issues/2). Generalized from
`pmf-tsfm` `palette.json` (see [`design-provenance.md`](design-provenance.md) §2)._

A **theme** is a palette file plus an optional logo. Everything else that makes a deck legible —
the type scale, the font pairing, the Assertion-Evidence layout structure, the light colour scheme —
is **fixed by the method**, not swappable per brand. That split is the whole point: a brand may
recolour, but it cannot opt out of the accessibility floor.

---

## 1. What a theme is

```
themes/
  kuleuven.json   ← palette + logo lockup   (default, validated)
  neutral.json    ← palette                  (brand-free reference)
```

A theme file is the **single source of truth** for one palette, consumed by three things at once —
the deck CSS, the (optional) figure helper, and the CVD validator. Nothing downstream hardcodes a
colour.

## 2. The palette schema

Keys are **kebab-case**, mirroring the CSS custom properties they become (`ink` → `--ink`).

```jsonc
{
  "meta": {
    "name": "kuleuven",
    "description": "KU Leuven house-style-derived theme. Not an official KU Leuven product.",
    "logo": "logos/kuleuven-liris.png"    // optional; omit for brand-free themes
  },

  // ── structural neutrals (universal; ported from pmf as-is) ──
  "ink":          "#102a43",   // primary text, dark structural lines   (≥14:1 on surface)
  "neutral":      "#486581",   // secondary text, axis labels           (≥6:1)
  "neutral-soft": "#93a4b8",   // rules, gridlines, ghost edges — DECORATIVE ONLY, never text
  "surface":      "#ffffff",
  "surface-alt":  "#f4f7fb",
  "hairline":     "#dde5ee",

  // ── brand & accent (universal) ──
  "brand":        "#00407a",   // headings, the "highlighted group" in 2-group charts
  "brand-strong": "#1d8db0",   // emphasis / links / chrome — large text only
  "accent":       "#dd8a2e",   // ATTENTION ONLY — arrows, "our method". Never a data series. Ink text on it.

  // ── data-encoding roles (the generalization) ──
  "reference":    "#111111",   // ground-truth / anchor series      (was pmf `truth`)
  "muted":        "#778496",   // de-emphasized / comparison group  (was pmf `baseline`)
  "series": [                  // ordered, CVD-safe categorical ramp (was pmf family hues)
    "#1b6fb0",                 // series-1
    "#57c0ae",                 // series-2
    "#4c3a78"                  // series-3
  ]
}
```

### Role mapping from pmf

| pmf role | general role | note |
|---|---|---|
| `truth` | `reference` | the anchor/ground-truth line |
| `baseline` | `muted` | the de-emphasized comparison group |
| `tsfm` (= brand) | `brand` | the highlighted group in a 2-group view |
| `chronos` / `moirai` / `timesfm` | `series[0..n]` | ordered categorical list, arbitrary length |
| `ft_shades` (within-family ramp) | — | **dropped from core** — domain-specific; a sequential ramp is v2 |
| `dataset` colours | — | **dropped from core** — a second categorical axis is v2 |

## 3. What is fixed by the method (NOT in a theme)

- **Type scale** — body 23 / headline 37 on `canvasWidth: 1280` (≈34px / 55px projected @1920).
  The back-row legibility floor. Escape hatches (`.dense` 18, `.dense--xs` 16) are exceptions, not
  knobs.
- **Fonts** — Inter (headings/body) + JetBrains Mono (locator only). Both SIL OFL, bundled in-repo.
- **Layout structure** — the Assertion-Evidence skeleton (locator → assertion → rule → evidence →
  page no).
- **Colour scheme** — **`colorSchema: light`, locked** (matches pmf #126). The CVD verification and
  the ink-on-white figures are done on white; a validated dark variant is **v2** (`themes/*.dark.json`,
  validator run on both grounds).

## 4. Usage rules (carried from pmf, generalized)

These are the rules the review skill (#12) will enforce and the validator (#9) will check:

- **`accent` is attention, not data.** Never colour a series with it; use `ink` text on top of it.
- **Spend colour only where the message needs discrimination** (pmf's "hybrid strategy"): a 2-group
  view uses `muted` vs. one highlight (`brand` or `series-1`); reach for the full `series[]` ramp
  only on genuine per-series comparison slides.
- **Colour is never the sole channel.** Pair `series[]` with redundant dash/marker in line charts;
  put direct labels on bars.
- **`neutral-soft` is decorative only** (~2.6:1) — never used for text.
- **`series[]` is validator-gated.** Every pair must stay above the CVD threshold under
  deuteranopia / protanopia / tritanopia **and** grayscale. Add as many series as you like; the
  validator tells you when you've added one too many.

## 5. CSS binding

Each scalar key becomes a `:root` custom property of the same name; `series` becomes
`--series-1 … --series-n`. The deck's `style.css` reads only these variables — the same contract
pmf proved, now brand-swappable.

```css
:root {
  --ink: #102a43;  --neutral: #486581;  /* … */
  --brand: #00407a;  --accent: #dd8a2e;
  --reference: #111111;  --muted: #778496;
  --series-1: #1b6fb0;  --series-2: #57c0ae;  --series-3: #4c3a78;
}
```

## 6. Open dependencies

- The exact **validator metric + threshold** that gates `series[]` is decided in **#9** (blocked by
  research **#4**). This contract fixes the *shape*; #9 fixes the *number*.
- Whether a **Python figure helper** is a third consumer in v1 is decided in **#10**.
