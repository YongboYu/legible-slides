# Design provenance

Everything in `legible-slides` was argued out somewhere else first: in
[`YongboYu/pmf-tsfm`](https://github.com/YongboYu/pmf-tsfm), building the CAiSE 2026 deck for
*Time Series Foundation Models for Process Model Forecasting*.

This file is the **capture** of those decisions — what was settled and why — so the extraction
starts from evidence rather than memory. It is deliberately descriptive: it records what the deck
does today, not what the template should do.

**It states no rules.** The rules the deck's practice became, and every number they turn on, live in
[`method.md`](method.md); this file is the trail of where they came from. The rule IDs named below
(`one-message`, `type-scale`, …) are defined there.

---

## 1. The slide model — Assertion-Evidence

*Source: [pmf-tsfm#108](https://github.com/YongboYu/pmf-tsfm/issues/108) · reached via a grill +
throwaway prototypes.*

Every content slide was **three zones plus chrome, nothing else** — a navy locator pill, the
assertion headline, an accent rule, the evidence, and the page number. That shape, less the accent
rule ([ADR 0001](adr/0001-personal-leuven-template.md)), is now fixed as `ae-skeleton`.

Two consequences were treated as load-bearing rather than cosmetic: the sentence headline absorbing
the takeaway, and the deck shipping no section dividers. Both became canon
(`assertion-headline`, `no-section-dividers`).

Implemented as three Slidev layouts: `assertion-evidence` (default), `two-col-evidence`
(`::left::` / `::right::` slots), and `cover`.

### The hard rules

The deck's `AGENTS.md` / `CLAUDE.md` carried the bullet and word ceilings, the one-question test, the
equation-plus-worked-example pairing and the animation ceiling. That list is the seed of
[`method.md`](method.md) §1–§6, which now states them and owns their numbers.

### The discipline, in the author's words

Quoted as source material. The rules these quotes became are `one-message`,
`message-before-visual` and `established-terminology`.

From `talk_design/revision_comments_minimal.md` — the clearest statement of the method, and the
reason this repo exists:

> Come up with one key message for one slide first, then figure out the best supporting
> material/visualization to show and answer, keep that sharp and clear to audience. Since now we
> compact some messages in one slide trying to save time, but it may cost me more time to explain
> and can make audiences confused and overwhelmed → avoid this.

And on terminology — a rule that generalises well beyond this one deck:

> If the words are already well-established, just use it and no need to rephrase it […] use the
> standard and clear terminology so that audiences can immediately know what I am saying without
> confusion and guessing.

---

## 2. Colour — one source of truth, CVD-verified

*Sources: [pmf-tsfm#76](https://github.com/YongboYu/pmf-tsfm/issues/76) (the problem),
[pmf-tsfm#107](https://github.com/YongboYu/pmf-tsfm/issues/107) (the fix).*

### The problem it solved

Colours had been living in **three places at once** — JS constants in `dfgFrameState.js`, a
`dfgData.accent` field, and hardcoded `fill`s plus scoped CSS in a Vue component. Recolouring was a
multi-spot edit, and a light/dark variant was effectively impossible. A non-brand placeholder
(`#1d4ee8`) had also leaked into the deck.

### The architecture

`palette.json` became the **single authoritative token set**, consumed by *both* consumers:

- `template/style.css` → `:root` custom properties, auto-loaded globally by Slidev
- `scripts/figure_manifest.py` → the Python figure pipeline

This indirection is the reason a recolour is a one-file edit in this repo rather than a hunt through
the deck — the mechanism already exists and is proven.

### The KU Leuven set

| Role | Hex | Notes |
|---|---|---|
| brand / highlighted group | `#00407A` | KU Leuven blue; white text ok |
| accent | `#DD8A2E` | the deck's attention-only role, carrying ink text; became `accent-is-attention` |
| baseline group | `#778496` | gray |
| ground truth | `#111111` | |
| family · Chronos | `#1B6FB0` | vivid azure — deliberately decoupled from brand navy |
| family · MOIRAI | `#57C0AE` | teal |
| family · TimesFM | `#4C3A78` | deep indigo (dark anchor) |

Neutrals carry documented contrast ratios: `--ink #102a43` (14.6:1 on white), `--neutral #486581`
(6.1:1), `--neutral-soft #93a4b8` (2.6:1, which the deck spent on rules and gridlines only — now
`decorative-neutral-never-text`).

### The accessibility verification

The family trio was **colour-vision-deficiency verified via Machado (2009) simulation**, and the deck
recorded the five-line plot set (truth + baseline + 3 families) as staying **≥39 apart** under
deuteranopia, protanopia, tritanopia *and* grayscale.

> **That `≥39` is retired**, and never means headroom above the canon's `separation-floor`. Why, in
> full: [`cvd-validator-contract.md`](cvd-validator-contract.md) §2.

The deck also never let colour carry meaning alone: multi-line plots carried **redundant dash +
marker cues** and bars carried **direct labels**, which is now `never-sole-channel`. Chronos was
decoupled from the brand navy specifically so it reads as its own colour rather than as chrome.

> This validator — run against an arbitrary palette rather than asserted about ours — is the single
> most transferable artifact in the whole project.

### Hybrid figure strategy

The deck's practice on *when* to spend colour: headline slides used **two groups** (baselines gray
vs. the highlighted group in one blue), and per-family hues appeared **only** on family-comparison
slides. That practice is now `spend-colour-on-discrimination`.

Also settled here: `colorSchema: light` was **locked**
([pmf-tsfm#126](https://github.com/YongboYu/pmf-tsfm/issues/126)) after following the viewer's OS
preference rendered an ink-on-white figure set against near-black and destroyed contrast. Now
`light-ground`.

---

## 3. Typography — tuned for the back of the room

*Source: [pmf-tsfm#108](https://github.com/YongboYu/pmf-tsfm/issues/108),
[pmf-tsfm#109](https://github.com/YongboYu/pmf-tsfm/issues/109).*

- **Inter** for headings and body; **JetBrains Mono** for the locator pill and nothing else. Now
  `fonts`.
- A **logical canvas**, so px values render as designed and scale to the projector — and a body size
  chosen from what the back row of a lecture hall can actually read, with the projection arithmetic
  written down in `style.css` beside it. Escape hatches for tight figure panels were marked as
  exceptions rather than offered as knobs. All of it, with the numbers, is now `type-scale`.
- **Inter TTFs bundled in-repo** and registered in `make_figures.py`, so Python-generated figures
  match the deck font on any machine. This is the failure `fonts` exists to prevent: a box lacking
  Inter silently fell back to DejaVu Sans and the figures stopped matching the slides.

A CSS gotcha worth carrying forward, documented in `style.css`: these rules are **global and
unscoped on purpose**. A Slidev layout's `<style scoped>` does *not* reach markdown slotted into it
— the slot keeps the page's scope.

---

## 4. Figures — regenerated, never redrawn

Result charts are **regenerated from data** (Python → committed PNG, faithful to the paper's
tables); conceptual diagrams are Vue/SVG components. `make_figures.py` is idempotent — rerunning it
rewrites every figure from `palette.json`, which is what makes a palette swap actually propagate.

Component logic (`dfgGeometry`, `frameForClicks`, `dfgFrameState`) is **unit-tested with vitest** —
worth noting that the deck treats figure geometry as code to be tested, not as artwork.

---

## 5. Open threads inherited from pmf-tsfm

Recorded honestly, because they affect the extraction:

- **The original brief is gone.** `SLIDES.md` and `talk_design/outline.md` were gitignored and
  removed from disk by [pmf-tsfm#143](https://github.com/YongboYu/pmf-tsfm/pull/143) ("keep design
  docs and speaker prep local, not public"). The rules survive only in `AGENTS.md` / `CLAUDE.md`,
  the layouts, and `style.css` comments. **This document is the reconstruction.**
- **Deferred migration.** #107 was deliberately additive: `slides.md` inline colours and the Vue
  diagram components were never migrated onto the tokens. Some hardcoded colour remains.
- **Dependency debt.** The Slidev toolchain accumulated Dependabot alerts
  ([#85](https://github.com/YongboYu/pmf-tsfm/issues/85), #86, #166) — a fresh extraction is a
  chance to start clean rather than inherit the override stack.
