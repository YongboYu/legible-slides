# The PowerPoint static proof

The method, carried into PowerPoint as a **native, editable Slide Master** — the same four layouts
as [the Slidev theme](../theme/README.md), the same palette, the same type scale, with a four-slide
worked example built from real flagship content.

Its job is to prove the method is not Slidev-specific. `slidev export --format pptx` cannot do that:
it emits one background image per slide and zero editable masters, which proves only that a deck can
screenshot itself. Everything here is hand-authored native XML, and the recipe that produced it
reruns in Keynote and Google Slides.

The recipe is [`docs/pptx-static-proof.md`](../docs/pptx-static-proof.md), and **it is the artifact
that matters** — the tools this has to generalise to cannot read a PowerPoint theme file, so the
authority is the documented mapping applied per tool, not this `.pptx`.

> **Not an endorsement.** These slides wear a palette derived from KU Leuven's house style. This is
> not an official KU Leuven product and carries no endorsement. The sentence travels inside the file
> too, in its document properties, because a `.pptx` gets forwarded on its own.

## Using it

Open `legible-master.pptx` and start from **File → New from Template**, or delete the four example
slides and keep the master. The layout gallery offers four:

| Layout | Mirrors | For |
|---|---|---|
| `Cover` | Slidev `cover` | the title slide, and the only slide with no chrome |
| `Assertion-Evidence` | Slidev `assertion-evidence` | the default: a headline claim and one evidence pane |
| `Two-Col Evidence` | Slidev `two-col-evidence` | side-by-side evidence, still one message |
| `References` | Slidev `references` | the sources, auto-numbered |

The **locator pill**, the **accent rule** and the **page number** live on the Slide Master, so every
content layout inherits them and no slide can be built without them. The cover omits all three —
that is the native equivalent of the theme's per-slide opt-out, and choosing the `Cover` layout is
the whole of it.

The locator is PowerPoint's own **footer** placeholder and the page number its **slide number** one,
so both are editable where a PowerPoint user already looks: click the pill and retype it when the
section changes, or use Insert → Header & Footer. The accent rule is not a placeholder, because a
rule is not yours to type into.

**Figures are regenerated, never redrawn.** Slide 2 imports a Python-generated, CVD-validated PNG as
a picture. Do the same: draw the chart with [`legible.figures`](../python/README.md#the-figure-helper)
against your palette, check it with `cvd-validate`, and place the image. This is not a style
preference — the colour mapping below only works because the data-encoding colours stay inside
validated images and never need a theme slot.

## Fonts

Inter and JetBrains Mono are **embedded whole** in the file, not subset, so the deck stays editable
on a machine that has neither. Both are SIL OFL, so that is a licence the file carries rather than
one it borrows.

Mac PowerPoint and the web viewer strip embeddings. OOXML has no named-alternate list, so what it
gives a renderer to substitute on is a PANOSE fingerprint and a pitch family, and **every place
either family is named carries both** — a generic sans stands in for Inter, a mono for JetBrains
Mono, instead of whatever is first in that renderer's own list. Inter is named in the theme's font
scheme, which has two slots and spends both on the text family; JetBrains Mono is named on the
locator, which under `fonts` is the only thing it sets.

If you would rather have the real thing, **install the two families**. The files ship with this repo:

```
theme/assets/fonts/Inter-Regular.ttf  Inter-Bold.ttf  JetBrainsMono-Regular.ttf
```

Double-click each and choose Install (macOS Font Book; on Windows, right-click → Install). They are
the same outlines the figures are drawn in, which is what keeps a chart and the slide around it in
one typeface.

**One known difference from the Slidev delivery.** PowerPoint's embedding slots are regular / bold /
italic / bold-italic per family, so the theme's Medium and SemiBold have nowhere to go: a headline
here is set in Inter Bold where the deck sets it in SemiBold. It is one weight heavier, in the
direction that costs a projected slide nothing.

## The twelve colour slots

A PowerPoint theme has exactly twelve. The mapping — and why the data-encoding roles are absent from
it — is [`docs/pptx-static-proof.md`](../docs/pptx-static-proof.md) §4, stated there and nowhere
else. `ppt/theme/theme1.xml` is the only part of the package that writes a hex down; every shape asks
the theme for its colour, so **recolouring the proof is that one file**.

`python/tests/test_pptx.py` reads the shipped `.pptx` back and fails if any slot has drifted from
[`themes/kuleuven.json`](../themes/kuleuven.json), if a series colour has reached a slot, or if a
shape has started writing its own hex.

## Type

Four sizes, and no fifth. `type-scale` fixes them on the canon's logical canvas; a PowerPoint slide
is a smaller share of the same shape, so a point size preserving the font-height-to-slide-height
ratio is the canvas px scaled by the ratio of the two heights, taken **up** to an even point — the
direction that cannot land under the ratio. The conversion is
[`docs/pptx-static-proof.md`](../docs/pptx-static-proof.md) §5; the numbers are the canon's, in
[`docs/method.md`](../docs/method.md).

They are written out in `ppt/slideMasters/slideMaster1.xml` and derived from the canon again by the
test suite, so changing a threshold there fails here rather than quietly leaving the master behind.

## Rebuilding it

```bash
python pack.py            # write legible-master.pptx
python pack.py --check    # fail if the shipped file is not what src/ packs to
```

Stdlib only, and **it derives nothing**: every XML part is hand-authored under `src/`, and `pack.py`
puts them in a zip alongside the binary parts it takes from where this repo already keeps them — the
typefaces from `theme/assets/fonts/`, the brand mark from `themes/logos/`, and the figure from
`deck/public/`. So regenerating the figure with `deck/figures.py` and repacking is what keeps slide 2
current; there is no second copy of the data anywhere in the package.

The `.pptx` is **committed**, the way [`theme/styles/tokens.css`](../theme/styles/tokens.css) is: it
is what a presenter downloads without running anything. The test suite packs the sources again and
compares bytes, so a part edited without a repack turns the build red.

## What lives where

| | |
|---|---|
| `legible-master.pptx` | the shipped file: the master, the four layouts, the four-slide example, and both typefaces inside it. |
| `src/` | every XML part, hand-authored. Each one says in a comment what it is for and which rule it is serving. |
| `pack.py` | the container step, and the map from a part in the package to the file in this repo it comes from. |

## Status

The public flip is gated by [#8](../../issues/8) — the KU Leuven visual-identity confirmation — which
is the same gate the flagship deck sits behind, not a new one. Anyone who wants a brand-free starter
swaps `themes/neutral.json` into `ppt/theme/theme1.xml` by the §4 mapping and repacks; the mapping is
palette-agnostic, and the test suite will tell you if the swap missed a slot.

Keynote and Google Slides are next, produced by rerunning the recipe rather than by exporting this.
