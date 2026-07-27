# The Slidev reference implementation

_Resolves [#10](https://github.com/YongboYu/legible-slides/issues/10). Consumes the token contract
([#2](https://github.com/YongboYu/legible-slides/issues/2),
[`token-contract.md`](token-contract.md)), the method canon + 13-beat flagship outline
([#3](https://github.com/YongboYu/legible-slides/issues/3), [`method.md`](method.md)), the prior-art
survey
([#6](https://github.com/YongboYu/legible-slides/issues/6),
[`research/prior-art-themes.md`](research/prior-art-themes.md)), and the CVD-validator contract
([#9](https://github.com/YongboYu/legible-slides/issues/9),
[`cvd-validator-contract.md`](cvd-validator-contract.md))._

Slidev is the **full reference implementation** of the method — the one delivery that carries the
tokens, the validator, the components, and a self-presenting flagship deck. This doc fixes exactly
what it contains and what is extracted-and-generalized from `pmf-tsfm` versus left behind.

---

## 1. Shape — a theme package + a flagship deck

The reference impl is **two things**, not one monolith:

- **`slidev-theme-legible`** — a Slidev *theme package* (modeled on `slidev-theme-academic`) holding
  the reusable **method machinery**: layouts, chrome components, tokenised styles, bundled fonts, the
  `--slidev-theme-primary` alias, and the theme files the validator gates.
- **The flagship deck** — a *separate* deck (the 13-beat outline from #3) that consumes the theme.
  It is the **primary teaching artifact** (it teaches the method by being the method), not merely a
  demo — academic's `example.md` pattern, promoted to the real deliverable.

The split draws the seam the project promises — *"brand is a swappable layer," "present in the tool
you already use."* You cannot ship a reusable **template** if the machinery is welded into one
deck's content.

**v1 scope:** built *as* a theme package (proper structure), but **in-repo**, consumed by the deck
via a local `theme:` path. Publishing `slidev-theme-legible` to npm is a later flip, not a v1
blocker (cf. the KU Leuven public-flip).

## 2. Layouts (4)

| Layout | Covers | Origin |
|---|---|---|
| `cover` | beat 1 title; reused for the beat-13 close | pmf, generalized |
| `assertion-evidence` | the default — headline claim + one evidence pane | pmf, generalized |
| `two-col-evidence` | side-by-side evidence (beats 3, 6, 10) | pmf, generalized |
| `references` | a divider-free sources slide (`indexEntries: [{title, uri}]`) | borrow academic's `index` (#6) |

**Not shipped:** `intro`, `section`, `end`, and the `statement`/`fact`/`focus`/`quote` emphasis
layouts. `no-section-dividers` forbids them, and the theme enforces that rule by simply not offering
a layout that breaks it. The beat-13 close reuses `cover` or a plain `assertion-evidence`.

## 3. Components (4)

| Component | Role |
|---|---|
| locator + page-no **chrome** | the persistent AE identity — locator pill + accent rule + page number, injected globally with per-slide opt-out (academic's `Pagination` pattern). Generalizes pmf's `PageNo` + locator. **Built on the per-slide `slide-top.vue` layer, not `global-top.vue`** (#20): the chrome is per-slide, and Slidev provides a slide's frontmatter and number only inside that slide. A global layer is mounted outside every slide and can only ask where the deck currently *is* — the wrong question wherever more than one slide is on screen, as in the overview and a printed export. |
| **`Callout`** | inline emphasis box (pmf universal). |
| **`Footnote` / `Footnotes`** | manual citation markers (borrow academic, #6) — pairs with the `references` layout for the deck's Alley / Tversky / Machado cites. |
| **`Figure`** | image + caption + optional cite-marker, kept as *data* (borrow academic's prop-driven captions) — evidence panes carry image + caption + source together. |

**Left behind from pmf** (domain-specific): `DfgEvolution` and any other pmf data-figure Vue
components. Already dropped by the token contract: the `ft_shades` within-family ramp and per-dataset
colours.

## 4. The figure helper — minimal, bounded, ships in v1

`palette.json` has **three consumers**: the deck CSS, the CVD validator, and — decided here — a
**figure helper**. It ships in v1 because the flagship's two load-bearing demonstration slides
(**beat 3**: a CVD-muddy chart; **beat 10**: the 5-line chart *under deuteranopia + grayscale* with
dash/marker redundancy) must be the **real validated palette under real Machado simulation** — a
hand-drawn image would gut the demonstration, break the three-consumers promise, and contradict
provenance §4 ("figures — regenerated, never redrawn").

It is deliberately **not a charting library**. Scope = the archetypes the method prescribes:

1. **Multi-series line chart** — `series[]` with **mandatory** dash/marker redundancy, so
   `never-sole-channel` holds by construction rather than by review; an optional CVD-simulated
   render. This is the workhorse *and* the beat-3/10 demo.
2. **2-group labeled bar / line** — `muted` vs one highlight (`brand` or `series-1`), with direct
   labels (`spend-colour-on-discrimination`).

- Consumes `palette.json` + the **bundled Inter** (registered in matplotlib per `fonts`, so figure
  type matches the deck).
- **Shares infrastructure with the CVD validator** — one palette-loader over the token-contract
  schema, and the *same* pinned `colorspacious`. The validator and helper are two entry points of one
  small **`legible`** package; beat 10's "under deuteranopia" chart calls the validator's own
  simulation to render itself.

## 5. Structure & wiring

One repo, four sub-parts around the shared token source:

```
themes/     kuleuven.json (default) + neutral.json  [+ logos/]   ← token source of truth
theme/      slidev-theme-legible: layouts/ components/ styles/ (incl. generated tokens.css)
            assets/fonts/ (bundled woff2)  package.json
deck/       the flagship deck: slides.md, public/ (its generated figures)
python/     the `legible` package: pyproject.toml, palette-loader, cvd-validate, figure helper
docs/       method.md, design-provenance.md, *-contract.md, research/
```

- **Fonts** — Inter + JetBrains Mono bundled as woff2 in `theme/assets/fonts/` (borrow academic's
  self-hosted `@font-face`, drop the eot/svg legacy). The same TTFs the figure helper registers.
- **Deck ↔ theme** — the deck consumes the theme via a local `theme:` path.
- **Themes shipped** — `kuleuven` (default, validated, logo lockup) + `neutral` (brand-free).

### The palette → CSS wiring

The token contract fixes the *mapping* (`ink → --ink`, `series → --series-n`); this fixes *who
performs it*: **the Python `legible` package emits it.**

```
legible gen-css themes/kuleuven.json  →  theme/styles/tokens.css   (committed, regenerated on change)
```

- **One palette authority.** Python already loads `palette.json` to validate and to draw figures;
  letting it also emit the CSS means the token schema lives in exactly one place — no JS
  re-implementation to drift. This is the cross-language single-source-of-truth that neither prior-art
  theme has (#6).
- **No deck-build coupling** (consistent with #9): the Slidev build imports the committed
  `tokens.css`; it never runs Python. Python regenerates the file at authoring time, like a lockfile.

## 6. Open dependencies

- The **agent skill** [#12] scaffolds decks on this theme and reviews against `method.md`; this doc
  fixes the theme/deck structure it stamps.
- The **PPTX static proof** [#11] carries the same palette + AE masters + type scale into PowerPoint;
  it shares the `themes/*.json` source but not the Slidev machinery.
- A **validated dark variant** (a second `tokens.css` ground) stays **v2**, per the token contract's
  light-only lock.
