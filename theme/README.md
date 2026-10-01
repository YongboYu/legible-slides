# slidev-theme-legible

The reusable half of [`legible-slides`](../README.md): the Assertion-Evidence layouts, the
persistent chrome, and styles that read nothing but the palette. A deck consumes it; it carries no
deck's content of its own.

The rules it enforces are not stated here. They live in [`docs/method.md`](../docs/method.md), and
this file names them by ID — `ae-skeleton`, `type-scale`, `light-ground`, `no-section-dividers` —
so that a rule can change in one place. What gets built and why is
[`docs/slidev-reference-impl.md`](../docs/slidev-reference-impl.md).

> **v1 is in-repo.** The package is structured to be published and is not published: a deck consumes
> it by local path. `example.md` beside it is the theme's own build target, exercising every layout
> once. The teaching artifact is the flagship deck, not that file.

## Using it

```yaml
---
theme: ../theme # a path, until the package is on npm
---
```

Nothing else is required. The canvas, the aspect ratio, the font families and the locked light
colour scheme arrive with the theme.

```bash
pnpm install
pnpm dev      # the example deck, with hot reload
pnpm build    # what CI builds
```

## Layouts

| Layout | For |
|---|---|
| `cover` | the title slide, and nothing else |
| `assertion-evidence` | the default: a claim, and the one pane of evidence that proves it |
| `two-col-evidence` | evidence in two panes — `::left::` and `::right::`, on an optional `ratio` |
| `references` | the sources, rendered from `indexEntries: [{ title, uri }]` |

`default` is an alias for `assertion-evidence` rather than a fifth layout, so a slide that names no
layout still gets the skeleton and has to opt *out* of it.

There is no `section`, `intro`, `end`, `statement`, `fact`, `focus` or `quote`. `no-section-dividers`
forbids the slides they build, and the theme enforces that by offering no way to build one. The close
of a talk is a `cover` or an ordinary `assertion-evidence`.

On a content slide the headline is the markdown's `#`, and everything after it is the evidence. On
`two-col-evidence` the headline is what comes before the first `::left::`.

### Cover props

| Prop | |
|---|---|
| `speaker` | who is speaking. Defaults to the deck's own `author`. |
| `venue` | the conference, the seminar, the course |
| `date` | written however the deck wants it read |
| `venueLogo` | the venue's logo URL, above the title, overriding `themeConfig.venueLogo` |
| `affiliationLogo` | the affiliation's logo URL, bottom left, overriding `themeConfig.affiliationLogo` |

`speaker` rather than `author` because Slidev reserves that word: on the first slide of a deck —
which is where a cover normally lives — `author` belongs to the headmatter and never reaches a layout
as a prop. The title and subtitle are the slide's `#` and `##`.

A mark is the deck's to serve, from its own `public/`, because it belongs to the deck and not to the
machinery. This project ships none: until a deck names an image, each slot shows a placeholder the
theme bundles (`assets/placeholders/`). Pointing a slot at a real mark is one line of `themeConfig`,
and `''` leaves the slot empty.

## Chrome

The footer is one component, injected on every slide by `slide-top.vue`: the section locator at
bottom left, the page number opposite it. No layout opts in, so none can forget, and the deck never
places them. A content slide opens straight on its headline.

```yaml
---
section: Method # this slide opens the Method section, and every slide after it is in it
---

---
section: Sources
backup: true # held for questions: its own name in the footer, and no position
---

---
chrome: false # this slide carries none of it
---
```

The section **carries forward**: a run of slides on one part of the argument is one section, and
making each of them restate its name is the repetition that ends in two of them disagreeing. Set it
on the first slide of a section; `section: ''` clears it. This is what pays for having no section
dividers — orientation is on every slide, so no slide is spent announcing where the talk has got to.
How many sections and how long a name still fit is `section-locator`'s, and `legible lint` warns
past it.

By default the footer shows the **section map**: every section in the order the deck first declares
them, the current one in the brand colour and a heavier weight. A deck that would rather show the
current section alone, with its position, says so once:

```yaml
themeConfig:
  locator: label # PROBLEM · 1/4 rather than PROBLEM · METHOD · LEGIBILITY · DELIVERY
```

Say every section change aloud as well: the footer is the backup channel. The speaker notes of a
section's first slide open with a `Signpost:` line for it.

The `cover` layout carries no chrome, whether or not it says so.

A per-slide layer (`slide-top.vue`) rather than the global one this borrows from
`slidev-theme-academic`, because the chrome is per-slide. Slidev hands a slide's frontmatter and its
number to components inside that slide; a global layer is mounted outside every slide and can only ask
where the deck currently *is* — a different question, and the wrong one wherever more than one slide
is on screen, as in the overview and a printed export.

## Components

| Component | |
|---|---|
| `Callout` | an inline box for the one thing that has to read as set apart. `title`, and `accent` for the attention variant (`accent-is-attention`). |
| `Figure` | `src`, `caption`, `cite`, `alt` — image, caption and citation as one thing, so a swapped figure cannot keep the old caption. |
| `Footnotes` / `Footnote` | the foot of the evidence pane. `Footnote` takes the `number` you wrote as the in-text marker. |
| `Chrome` | the chrome above. Injected for you; you should not need to place it. |

Citations are numbered by hand, which is the whole mechanism: write `<sup>1</sup>` where the claim is,
give the matching `Footnote` the same number, and put the source at that position in the references
slide's `indexEntries`. A talk cites a handful of sources, and a BibTeX toolchain is a large
dependency bought for a small job.

**Leave a blank line inside a component** if its content is markdown:

```md
<Callout title="Refused">

No `section`, no `intro`, no one-word emphasis.

</Callout>
```

Without the blank lines markdown-it takes the whole block for raw HTML, and backticks, emphasis and
links stay as typed. On one line, write the HTML instead (`<code>…</code>`).

## Styles

Three files, in this order:

- `styles/tokens.css` — **generated**. `legible gen-css` writes it from the theme file and CI checks
  the two agree, which is what lets this build import a stylesheet rather than run Python.
- `styles/fonts.css` — the `@font-face` rules over the bundled woff2. No provider, no `@import`, no
  external request.
- `styles/layout.css` — everything else, and the only file that states a size.

**No colour is written anywhere in the theme.** Every one is a custom property from `tokens.css`, so
recolouring a deck is one palette edit — and the palette had to pass `cvd-validate` to be shipped at
all.

The stylesheets are **unscoped on purpose**. A Slidev layout's `<style scoped>` does not reach the
markdown slotted into it, because the slot keeps the page's scope; scoping the layouts would style
the theme's own chrome and miss every word the deck writes. The layouts and components here carry
markup and nothing else.

`type-scale` fixes the sizes and the theme quotes them: one headline size, one body size, and the
canon's two dense sizes for tight panels — a caption, a citation, a source line, a code block. Each
use of a dense size in `layout.css` names which exception it is. There is no h2–h6 scale on a content
slide: a subhead is a second message, and a per-context scale is how a deck drifts below the floor one
slide at a time.

The chrome is the one thing set at the smallest size deliberately. The section locator and the page
number are orientation rather than evidence, and the back-row floor is about the material the audience has to
read.

`light-ground` is locked in `package.json` (`colorSchema: light`) and again in CSS
(`color-scheme: light`), because a viewer's OS preference would set this ink-on-white figure set
against near-black.

## Fonts

Inter for headings and body, JetBrains Mono for the locator and nothing else, both bundled — see
[`assets/fonts/README.md`](assets/fonts/README.md). Only four weights of Inter ship, so nothing here
may ask for a fifth, and no italic ships at all: `*emphasis*` comes out upright and one weight
heavier rather than in the skewed shapes a browser would synthesise. A code block inherits the mono
family because that is what Slidev's `mono` setting is for; `fonts` reserves it from *display* use,
not from code.

## The example's figure

`public/example-figure.png` is generated from the same palette the slides are coloured from, using
the archetypes in the `legible` package — figures are regenerated, never redrawn:

```bash
uv run --project ../python python -c "
from legible import load_palette
from legible.figures import save, two_group
palette = load_palette('../themes/leuven-blue.json')
save(two_group(palette,
               {'protanomaly': 16.5, 'tritanomaly': 20.8},
               {'deuteranomaly': 15.0},
               value_format='{:.1f}', y_label='min ΔE', size_px=(650, 370)),
     'public/example-figure.png')
"
```

Its numbers are the achieved minima for `themes/leuven-blue.json`, which the package's tests pin.

## Borrowed from

`slidev-theme-academic` (MIT, Alexander Eble) — the self-hosted-font mechanism, the globally injected
chrome, the prop-driven figure, the manual `Footnote`/`Footnotes` pair, and the `index` layout this
theme narrows into `references`. The survey that picked them out, and what was deliberately left
behind, is [`docs/research/prior-art-themes.md`](../docs/research/prior-art-themes.md).
