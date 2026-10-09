# legible-slides

A Slidev template for academic talks, with a short set of rules for what goes on each slide and
two commands that check a deck against them.

![Four slides from the flagship deck: a numbered list of the talk's questions, a topic label set
against a claim, the back-row reading distance drawn as a diagram, and a chart of palette distances
under colour-vision deficiency](docs/images/flagship.png)

- **The rules** are in [`docs/method.md`](docs/method.md): one message per slide, a headline that
  states the claim, text sized for the back row, and colors that stay distinct for color-blind
  viewers.
- **`legible lint`** checks a deck's mechanical rules, such as bullet counts, type sizes and wording.
- **`cvd-validate`** checks that a palette's colors stay apart under color-vision deficiency.
- **A skill for coding agents** drafts a talk from a paper, builds the deck and reviews it.

## Quickstart

You need [Node](https://nodejs.org) 22.12+, [pnpm](https://pnpm.io) 10 and
[uv](https://docs.astral.sh/uv/).

Start your own deck:

```bash
npm create legible-slides my-talk
cd my-talk
pnpm install && pnpm dev
```

The theme comes from npm and the checks from PyPI, both at the version the deck pins.

Check it, and export a PDF:

```bash
bin/legible lint slides.md --theme themes/palette.json
bin/cvd-validate themes/palette.json
pnpm exec playwright install chromium   # once per machine
pnpm export                             # writes dist/slides.pdf
```

To have a coding agent do this for you, see [`skill/README.md`](skill/README.md).

See the flagship deck, which explains the rules by following them:

```bash
git clone https://github.com/YongboYu/legible-slides
cd legible-slides/deck
pnpm install && pnpm dev
```

## Read more

| | |
|---|---|
| [`docs/method.md`](docs/method.md) | every rule, with its threshold and its source |
| [`deck/`](deck) | the flagship deck |
| [`theme/README.md`](theme/README.md) | the layouts and components |
| [`python/README.md`](python/README.md) | the `legible` and `cvd-validate` commands, and the figure helper |
| [`skill/README.md`](skill/README.md) | the coding-agent skill |
| [`docs/design-provenance.md`](docs/design-provenance.md) | where the rules came from: the [`pmf-tsfm`](https://github.com/YongboYu/pmf-tsfm) talk at CAiSE 2026 |

## Credits and license

The slide structure is Assertion-Evidence, by Michael Alley and colleagues (Alley & Neeley,
*Technical Communication* 52(4), 2005; Alley, *The Craft of Scientific Presentations*, 2013). This
project is not affiliated with its authors. The other sources are in
[`docs/research/presentation-methods.md`](docs/research/presentation-methods.md).

The palette is inspired by KU Leuven's colors, and the project is not affiliated with or endorsed by
the university. Earlier commits contain KU Leuven logo files, which belong to the university and are
not covered by this license.

The bundled fonts, Inter and JetBrains Mono, are under the SIL Open Font License 1.1. Everything
else is [MIT](LICENSE).
