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
legible rules one-message
```

## Running it

```bash
pnpm install
pnpm dev      # with hot reload
pnpm build
```

The `theme` key in `slides.md`'s headmatter is a **path**, which is how a deck consumes
`slidev-theme-legible` until the package is on npm — point it at your checkout of this project, and
nowhere else names it. Nothing else is configured here, because everything the method fixes — the
canvas, the type scale, the bundled typefaces, the light ground — arrives with the theme.

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
cvd-validate themes/palette.json
```

The palette reaches the slides as `styles/tokens.css`, generated from that file and **committed like
a lockfile** — which is what lets the build import a stylesheet instead of running Python.
Regenerate it whenever the palette changes:

```bash
legible gen-css themes/palette.json --output styles/tokens.css
```

Charts read the same file, so a swap reaches them too — see [`public/README.md`](public/README.md).

## Held to the method

```bash
legible lint slides.md --theme themes/palette.json
```

Every rule the canon marks *decided by script*, with an exit code. `.pre-commit-config.yaml` runs it
locally and is opt-in; `.github/workflows/method.yml` runs it where nobody can skip it, and is the
gate. Both need the `legible` package:

```bash
uv tool install "git+https://github.com/YongboYu/legible-slides#subdirectory=python"
```

What is left is judgment — whether a slide carries one message, whether its headline is a claim.
That is a reader's, or the review mode of the
[legible-slides skill](https://github.com/YongboYu/legible-slides/tree/main/skill), which reports
both halves as one review with a proposed fix on every finding.

## What lives where

| | |
|---|---|
| `slides.md` | the deck. The first frontmatter block is the headmatter *and* the cover's own frontmatter, which is why the cover's props sit up there. |
| `themes/palette.json` | the palette. One file, and the only place a colour is written. |
| `styles/tokens.css` | generated from it, committed, imported by `styles/index.ts`. Do not edit. |
| `public/` | what the deck serves: figures, and the two logo placeholders your own marks replace. |
