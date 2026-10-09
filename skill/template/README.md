# A deck, built to the method

Scaffolded from [`legible-slides`](https://github.com/YongboYu/legible-slides). One skeleton slide
per layout the theme ships, wired to a palette that clears the accessibility floor and to the checks
that hold the deck to the rules. It is a clean start, not a worked deck: fill the blanks in, delete
the slides you do not need, and add the ones you do.

The rules themselves are not stated here. They live in
[`docs/method.md`](https://github.com/YongboYu/legible-slides/blob/main/docs/method.md), which is
the only place any of them is stated, and this deck names them by ID — `one-message`,
`no-section-dividers`, `no-script-on-slide` — so you can read one and disagree with it:

```bash
bin/legible rules one-message
```

## Running it

```bash
pnpm install
pnpm dev      # with hot reload
pnpm build
pnpm exec playwright install chromium   # once per machine, for the two below
pnpm export   # the PDF, every slide in its final state, into dist/
pnpm render   # a PNG per click step, into render/, to look at before you present
```

The theme is the npm package `slidev-theme-legible`, and `slides.md` names it as `legible`.
`package.json` pins it to one exact version. Every check runs through `bin/legible`, which installs
the `legible-slides` checks from PyPI at that same version, set on its `VERSION=` line. The hooks,
the workflow and you all run the same checks, so the deck is held to the rules it was built to.

To update, change the version in both places to the same later release, then run `pnpm install`.
Nothing else is configured here. The canvas, the type scale, the bundled typefaces and the light
ground all arrive with the theme.

`package.json` holds markdown-it to its 14.x line under `pnpm.overrides`. Slidev's markdown plugin
imports a file the next major version of markdown-it no longer exports, and with no lockfile a fresh
install picks that version up and the build fails before it reads a slide. Drop the override once
Slidev ships a plugin that works with it.

It holds UnoCSS to 66.7 the same way, the line the theme's and the flagship's lockfiles pin. UnoCSS
66.10 writes a rule for Slidev's code line numbers that the CSS minifier rejects, and the build
fails on its last step. Drop that override once a later UnoCSS builds the stamped template.

A PDF to present from is Slidev's own export, and the renderer it needs is not stamped here because
a browser download is something you should have asked for:

```bash
pnpm add -D playwright-chromium
pnpm exec slidev export slides.md --format pdf --output dist/slides.pdf
```

## The palette

One file, `themes/palette.json`, and every colour on these slides comes from it. It arrives as a
copy of the project's `leuven-blue` theme; edit it, or replace it with your own, and the whole deck
recolours.

Whatever you change it to has to clear the floor, and that is a command rather than a promise:

```bash
bin/cvd-validate themes/palette.json
```

The palette reaches the slides as `styles/tokens.css`, generated from that file and **committed like
a lockfile** — which is what lets the build import a stylesheet instead of running Python.
Regenerate it whenever the palette changes:

```bash
bin/legible gen-css themes/palette.json --output styles/tokens.css
```

Charts read the same file, so a swap reaches them too — see [`public/README.md`](public/README.md).

## Held to the method

```bash
bin/legible lint slides.md --theme themes/palette.json
```

Every rule the canon marks *decided by script*, with an exit code. `.pre-commit-config.yaml` runs it
locally and is opt-in; `.github/workflows/method.yml` runs it where nobody can skip it, and is the
gate. Both run it through `bin/legible`, and all that needs is
[uv](https://docs.astral.sh/uv/): the first run installs the pinned version and caches it.

A green run is the gate and nothing more: the deck has none of the faults a script can find. What is
left is judgment, and what the rendered pages show — whether a slide carries one message, whether its headline is a claim.
That is a reader's, or the review mode of the
[legible-slides skill](https://github.com/YongboYu/legible-slides/tree/main/skill), which reports
both halves as one review with a proposed fix on every finding.

## What lives where

| | |
|---|---|
| `bin/` | the checks, at the version the theme is pinned to. `bin/legible` holds the pin; run every `legible` command through it. |
| `package.json` | the theme, pinned exactly. Change its version and the one in `bin/legible` together. |
| `slides.md` | the deck. The first frontmatter block is the headmatter *and* the cover's own frontmatter, which is why the cover's props sit up there. |
| `themes/palette.json` | the palette. One file, and the only place a colour is written. |
| `styles/tokens.css` | generated from it, committed, imported by `styles/index.ts`. Do not edit. |
| `public/` | what the deck serves: figures, and your own marks for the cover's two logo slots, which show the theme's placeholders until you name them. |
