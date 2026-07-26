# The theme/token contract

_Resolves [#2](https://github.com/YongboYu/legible-slides/issues/2). Generalized from
`pmf-tsfm` `palette.json` (see [`design-provenance.md`](design-provenance.md) §2)._

A **theme** is a palette file plus an optional logo. Everything else that makes a deck legible —
the type scale, the font pairing, the Assertion-Evidence layout structure, the light colour scheme —
is **fixed by the method** ([`method.md`](method.md)), not swappable per brand. That split is the
whole point: a brand may recolour, but it cannot opt out of the accessibility floor.

This document fixes the palette's **shape**: which roles exist, what they are named, and how they
reach CSS. The **rules** governing how those roles may be used are the canon's, and are linked by
rule ID rather than repeated here.

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
  "neutral-soft": "#93a4b8",   // rules, gridlines, ghost edges         (`decorative-neutral-never-text`)
  "surface":      "#ffffff",
  "surface-alt":  "#f4f7fb",
  "hairline":     "#dde5ee",

  // ── brand & accent (universal) ──
  "brand":        "#00407a",   // headings, the "highlighted group" in 2-group charts
  "brand-strong": "#1d8db0",   // emphasis / links / chrome        (`decorative-neutral-never-text`)
  "accent":       "#dd8a2e",   // the attention role: arrows, "our method"  (`accent-is-attention`)

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

A theme carries colour and a logo. It cannot touch the type scale, the font pairing, the
Assertion-Evidence layout skeleton, or the light ground — those are canon rules
(`type-scale`, `fonts`, `ae-skeleton`, `light-ground`), and the numbers behind them live there.

A validated **dark** variant is **v2** (`themes/*.dark.json`, validator run on both grounds), because
`light-ground` fixes the ground every colour decision here was verified on.

## 4. How these roles may be used

The rules are the canon's; this table is the map from a role to the rule that governs it. None of
them is restated here.

| Role | Governing rule |
|---|---|
| `accent` | `accent-is-attention` |
| `muted` + one highlight vs. the full `series[]` ramp | `spend-colour-on-discrimination` |
| `series[]` in a chart | `never-sole-channel` |
| `neutral-soft` | `decorative-neutral-never-text` |
| every `series[]` pair, plus `reference` / `muted` / `brand` | `separation-floor` (validator-gated) |

The review skill ([#12](https://github.com/YongboYu/legible-slides/issues/12)) enforces them and the
validator ([#9](https://github.com/YongboYu/legible-slides/issues/9)) checks the last one.

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

Who performs the mapping is fixed by
[`slidev-reference-impl.md`](slidev-reference-impl.md) §5: `legible gen-css`, and nothing else. Its
output is committed at `theme/styles/tokens.css` and CI checks it against this palette, so the deck
build imports a stylesheet rather than running a Python toolchain.

## 6. Open dependencies

- The **validator metric + threshold** that gates `series[]` was decided in **#9**
  ([`cvd-validator-contract.md`](cvd-validator-contract.md)) and now lives in the canon as
  `separation-floor`. This contract fixes the *shape*; the canon owns the *number*.
- Whether a **Python figure helper** is a third consumer in v1 is decided in **#10**.
