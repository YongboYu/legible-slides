# The PowerPoint static-proof recipe

_Resolves [#11](https://github.com/YongboYu/legible-slides/issues/11). Consumes the export-fidelity
finding ([#5](https://github.com/YongboYu/legible-slides/issues/5),
[`research/slidev-export.md`](research/slidev-export.md)), the token contract
([#2](https://github.com/YongboYu/legible-slides/issues/2), [`token-contract.md`](token-contract.md)),
the reference-impl structure ([#10](https://github.com/YongboYu/legible-slides/issues/10),
[`slidev-reference-impl.md`](slidev-reference-impl.md)), and the method canon
([#3](https://github.com/YongboYu/legible-slides/issues/3), [`method.md`](method.md))._

The v1 static proof is **ONE PowerPoint delivery** that carries the method — the Assertion-Evidence
masters, the palette as native theme colours, and the type scale — into a tool the audience already
uses **and can edit**. Its job is to prove the method is not Slidev-specific, and to hand over a
recipe that reruns in Keynote / Google Slides in v2. **Plan-only: this doc fixes the recipe; building
the `.pptx` is execution, deferred to handoff.**

---

## 1. Shape — a hand-authored native master, not a flat export

[#5](https://github.com/YongboYu/legible-slides/issues/5) established that
`slidev export --format pptx` emits **flat, non-editable images** — one background PNG per slide, zero
editable masters, text, or theme colours (it screenshots the deck into a `.pptx` shell). That is
useless as a "starter" and proves nothing about portability beyond "Slidev can screenshot itself."

The proof is therefore a **hand-authored native PowerPoint master** — a real Slide Master with custom
AE layouts, the palette wired as PowerPoint theme colours, the type scale in points, and embedded
fonts. Editable, reusable, and — being native — the only path that yields a recipe generalizing to
Keynote / Google Slides.

The flat `slidev export` output is **not** shipped; it is kept purely as a **pixel reference** to
author the master against.

## 2. Palette — mirrors the flagship on `kuleuven`

The recipe is palette-agnostic (it consumes `themes/*.json`), but the shipped worked example commits
to **`kuleuven`** — the same palette and logo lockup as the Slidev flagship. The proof's rhetorical
force is _"the same deck, the same method, in PowerPoint,"_ so it must be a faithful twin, not a
different-coloured cousin.

Building on `kuleuven` rides the **existing [#8](https://github.com/YongboYu/legible-slides/issues/8)
public-flip gate** — it creates no new gate. Both v1 deliveries (Slidev flagship + this proof) flip to
public together once the KU Leuven visual-identity confirmation lands. Anyone wanting a brand-free
starter swaps to `neutral.json` — a one-file change, since the mapping (§4) is palette-agnostic.

## 3. Layouts (4) — full mirror of the theme, chrome in the master

The proof carries all four theme layouts ([#10](https://github.com/YongboYu/legible-slides/issues/10))
as PowerPoint custom Slide-Master layouts:

| PowerPoint layout | Mirrors | Covers |
|---|---|---|
| `Cover` | Slidev `cover` | beat-1 title; reused for the beat-13 close |
| `Assertion-Evidence` | Slidev `assertion-evidence` | the default — headline claim + one evidence pane |
| `Two-Col Evidence` | Slidev `two-col-evidence` | side-by-side evidence |
| `References` | Slidev `references` | divider-free sources list |

The **persistent AE chrome** — locator pill + accent rule + page number — lives on the **Slide Master**
so every content layout inherits it:

- **Locator pill** and **accent rule** are master placeholders; the presenter edits the pill text per
  section. The pill is the orientation device that `no-section-dividers` relies on, so there is no
  divider layout to add.
- **Page number** uses PowerPoint's native slide-number placeholder.
- **Per-slide opt-out** (the cover carries no chrome) is handled by the `Cover` layout simply omitting
  those placeholders — the native equivalent of the theme's `global-*` opt-out.

## 4. Theme colour mapping — the 12 slots

A PowerPoint theme has exactly **12 colour slots** (4 text/background + 6 accents + 2 hyperlink). The
palette's chromatic roles alone number 8, overflowing the 6 accents — **but that overflow dissolves**
because of a fact from #10: **figures are regenerated, never redrawn.** The multi-series charts are
Python-`legible`-generated, CVD-validated PNGs imported as pictures, so the **data-encoding roles
(`reference`, `muted`, `series[]`) live _inside_ the figure images, never in native PowerPoint shapes.**
The 12 theme slots therefore carry only the **native-surface roles**.

| PowerPoint slot | palette role | hex |
|---|---|---|
| Text 1 | `ink` | `#102a43` |
| Background 1 | `surface` | `#ffffff` |
| Text 2 | `neutral` | `#486581` |
| Background 2 | `surface-alt` | `#f4f7fb` |
| Accent 1 | `brand` | `#00407a` |
| Accent 2 | `accent` | `#dd8a2e` |
| Accent 3 | `brand-strong` | `#1d8db0` |
| Accent 4 | `neutral-soft` | `#93a4b8` |
| Accent 5 | `reference` | `#111111` |
| Accent 6 | `muted` | `#778496` |
| Hyperlink | `brand-strong` | `#1d8db0` |
| Followed Hyperlink | `muted` | `#778496` |

- **`series[]` is deliberately absent** — it exceeds the 6 accent slots _and_ lives only in figures.
- **`hairline` (`#dde5ee`)** is a manual fixed fill for rules, not a theme slot.
- Accents 5–6 (`reference` / `muted`) are present only so a presenter has swatches matching the
  figures (e.g. a legend chip); the actual data always arrives as a validated figure image.
- **Accent 2 carries `accent`**, which `accent-is-attention` governs in PowerPoint exactly as it does
  in the deck.

## 5. Type scale and fonts

**Type scale — height-ratio derived.** `type-scale` fixes the canvas sizes; this is the one place they
are converted, never restated. PowerPoint's 16:9 slide is 13.333″×7.5″ = 960×540pt, and the canon's
canvas is `canvas-aspect-ratio` at `canvas-width-px`, so the slide is **0.75×** the canvas height in
the units each is expressed in. Point sizes preserve
the **font-height-to-slide-height ratio** at that factor (the ratio is what actually governs back-row
legibility), rounded to even points and **never below the legibility floor**:

| Method role (`type-scale` key) | PowerPoint pt |
|---|---|
| Headline (claim) — `headline-px` | **28** |
| Body — `body-px` | **18** |
| `dense-px` | **14** |
| `dense-xs-px` | **12** |
| Locator (mono) | **~11** |

These are baked into the master's placeholder text styles. Fonts come from `fonts`: Inter for
headline and body, JetBrains Mono for the locator only.

**Fonts — embed + fallback + install.** Inter and JetBrains Mono are both SIL OFL (embeddable) and
already bundled in the theme. For a cross-platform academic audience the proof does all three:

1. **Embed** the fonts in the shipped `.pptx` (best fidelity on Windows PowerPoint);
2. Set a **graceful fallback** in the theme font scheme (Inter → generic sans; JetBrains Mono →
   Consolas/mono) for Mac / web that strip embeds;
3. Ship the font files alongside with a one-line install note.

## 6. Source coupling — hand-set once, the mapping is canonical

The PowerPoint theme is **hand-set once** from the §4 table in the theme editor; the **documented
mapping is the authoritative, tool-portable artifact.** No codegen path is added in v1:

- The v1 palette is **locked** (`kuleuven` fixed, light-only; new brands and the dark variant are v2),
  so drift risk is negligible.
- More decisively, the proof's point is a recipe that **generalizes to Keynote and Google Slides** —
  and those tools cannot consume a PowerPoint `.thmx`. The portable artifact must be the documented
  hand-mapping applied per tool, not a PowerPoint-only generator.

A `legible gen-thmx themes/<palette>.json → <palette>.thmx` command (colour scheme + font scheme,
parallel to `gen-css`) is a clean **future add** the moment palette churn or the v2 dark ground
justifies it. **Deferred, not built.**

## 7. Worked example, and where it lives

**Worked example — a 4-slide example deck, one slide per layout**, populated with **real flagship
content** (not lorem ipsum): the beat-1 cover, a representative `Assertion-Evidence` beat with a
**validated figure imported as a picture**, a `Two-Col Evidence` beat, and the `References` slide. This
exercises all four masters _and_ is the worked example in one artifact. The figure is the same
Python-generated, CVD-validated PNG the flagship uses — figures regenerated, never redrawn.

**Repo location.** A new sibling directory alongside `deck/` (structure fixed in #10):

```
pptx/       the static proof: legible-master.pptx (master + 4-slide example deck),
            embedded font files, README (build + font-install notes)
```

## 8. The recipe (tool-agnostic — reruns in Keynote / Google Slides for v2)

The ordered steps below _are_ the deliverable; PowerPoint is the v1 execution, and v2 reruns them
verbatim in Keynote / Google Slides (a v2 item, per the map's Out-of-scope):

1. **Colours** — set the tool's theme palette from the §4 12-slot mapping (read hexes from the chosen
   `themes/*.json`).
2. **Masters** — build the 4 AE layouts (§3) on the tool's master, with the locator-pill + accent-rule
   + page-number chrome inherited by every content layout and omitted on the cover.
3. **Type scale** — set placeholder text styles to the height-ratio point sizes derived in §5.
4. **Fonts** — embed Inter + JetBrains Mono where the tool allows, with a declared fallback; ship the
   font files with an install note.
5. **Figures** — import the Python-`legible`-generated, CVD-validated PNGs as pictures (never redraw
   data natively; data roles stay in the images).
6. **Populate** — build the 4-slide example deck from real flagship content.

## 9. Open dependencies & scope

- **Public flip** is gated by [#8](https://github.com/YongboYu/legible-slides/issues/8) (KU Leuven
  visual-identity confirmation) — the same gate as the flagship, not a new one.
- **Building the `.pptx`** is execution, out of scope for this plan-only map (per the map's
  Out-of-scope) — it happens after handoff via `/to-prd → /to-issues → /tdd`.
- **Keynote / Google Slides** executions are **v2**, produced by rerunning §8 verbatim.
- **`gen-thmx`** codegen is deferred future work (§6).
