# Prior art: academic Slidev themes

**Question:** What can `legible-slides` borrow from existing academic Slidev themes?

Surveyed two, against our stance — Assertion-Evidence slide model, a single CVD-verified
`palette.json` token contract shared by deck CSS **and** a Python figure pipeline, and a
back-of-the-room large-type legibility floor. See [`docs/design-provenance.md`](../design-provenance.md).

Themes surveyed:

- **slidev-theme-academic** — alexanderdavide (Alexander Eble), v3.0.0, MIT.
  <https://github.com/alexanderdavide/slidev-theme-academic> ·
  demo <https://slidev-theme-academic.alexeble.de>
- **slidev-theme-scholarly** — jxpeng98 (Jiaxin Peng), v1.3.3, MIT, "LaTeX Beamer-style styling".
  <https://github.com/jxpeng98/slidev-theme-scholarly>

Sources are the GitHub repos' `package.json`, `layouts/`, `styles/`, `components/`, and READMEs,
read directly at time of writing (July 2026). npm mirrors: `slidev-theme-academic`,
`slidev-theme-scholarly`.

---

## 1. slidev-theme-academic (alexanderdavide)

A deliberately **minimal, disciplined** theme. Two runtime dependencies
(`@slidev/types`, `unocss`), six layouts, one configurable colour.

### 1.1 Layouts

| Layout | Purpose |
|---|---|
| `cover` | Title slide — props `coverAuthor`, `coverDate`, `coverBackgroundUrl`, source attribution |
| `intro` | Same visual family as cover (large `h1`, `text-6xl leading-20`) for an opener |
| `table-of-contents` | Content above an auto `<h1>Table of Contents</h1>` list |
| `index` | Generic list for **figures / references / tables**; `indexEntries: [{title, uri}]`, `indexRedirectType: external \| internal` |
| `figure` | Full-width image; `figureUrl` (req), `figureCaption`, `figureFootnoteNumber` |
| `figure-side` | Image beside a `<slot/>` of content; adds `figureX: 'l' \| 'r'` (default `r`) |

Plus Slidev's built-in `default`. Layouts are thin Vue files — `figure-side.vue` is a two-pane
flex box that reuses the `FigureWithOptionalCaption` component.

### 1.2 Typography

`package.json → slidev.defaults.fonts`:

```json
"fonts": { "sans": "Montserrat", "serif": "Roboto Slab", "mono": "Roboto Mono" }
```

Fonts are **self-hosted**: `assets/fonts/*` + `styles/fonts.css` declare `@font-face` for each
weight (woff2/woff/ttf, plus legacy eot/svg), e.g. a `Montserrat` 200 and 400. No CDN dependency.

Type **scale is almost entirely deferred to Slidev/UnoCSS defaults** — `layout.css` sets sizes only
for the cover/intro family (`h1 { text-6xl leading-20 }`) and a few spacing rules. There is no
per-context heading scale.

### 1.3 Colour / tokens

One token: `styles/layout.css` sets `--slidev-theme-primary: #5d8392`, "can be overridden by uses
`themeConfig` option." That's the whole colour system — a single primary, wired to Slidev's
conventional CSS variable so built-in Slidev UI inherits it. Light/dark handled by a UnoCSS
shortcut:

```ts
'bg-main': 'bg-white text-[#181818] dark:(bg-[#121212] text-[#ddd])'
```

`package.json → slidev.colorSchema: "both"` — follows the viewer's OS light/dark.

### 1.4 Packaging (the theme contract)

```
package.json         slidev: { colorSchema, defaults: { fonts, themeConfig } }
layouts/*.vue        cover, intro, table-of-contents, index, figure, figure-side
components/*.vue      FigureWithOptionalCaption, Footnote, Footnotes, Pagination, TextWithOptionalLink
styles/index.ts       entry that pulls in fonts.css + layout.css
styles/fonts.css      @font-face for the bundled fonts
styles/layout.css     the one --slidev-theme-primary token + minimal layout CSS
setup/shiki.ts        code-highlight theme hook
global-top.vue        injects <Pagination/> globally on every slide
uno.config.ts         UnoCSS shortcuts (bg-main)
assets/fonts/*        self-hosted font binaries
example.md            the demo deck (also the build/screenshot target)
```

`slidev.defaults.themeConfig` ships `{ paginationX: "r", paginationY: "t" }`.
`engines.slidev: ">=0.50.0"`.

### 1.5 Notable features

- **Footnotes, not BibTeX.** `Footnote` (needs a `number` to align with an in-text marker) nested in
  `Footnotes` (`filled`, `separator`, `x`, `y`). Manual, lightweight citation attribution.
- **Global pagination.** `Pagination` is injected via `global-top.vue`; placed with `themeConfig`
  `paginationX` (`l`/`r`), `paginationY` (`t`/`b`); suppressed per-slide with
  `paginationPagesDisabled: []`; fully disabled by setting both axes to `undefined`. By default it
  uses the current colour-schema colour.
- **`index` layout** doubles as a references / figure-list / table-list slide without a heavyweight
  bibliography engine.
- Prop-driven figure captions (`figureCaption` + `figureFootnoteNumber`) keep image + caption + cite
  marker together as data.

---

## 2. slidev-theme-scholarly (jxpeng98)

A **maximalist** theme emulating LaTeX Beamer: 26 layouts, 14 components, 9 colour palettes,
8 font themes, a CLI, and a VS Code extension. `aspectRatio: "4:3"`.

### 2.1 Layouts (26)

- **Structure:** `cover`, `default`, `intro`, `section`, `center`, `auto-center`, `auto-size`, `end`
- **Content:** `two-cols`, `image-left`, `image-right`, `bullets`, `figure`, `split-image`
- **Emphasis:** `quote`, `fact`, `statement`, `focus`
- **Academic:** `compare`, `methodology`, `results`, `timeline`, `agenda`, `acknowledgments`,
  `references`, `toc`

`references.vue` renders a bibliography slide with a `ScholarlyHeader`/`ScholarlyFooter` frame and
**auto-shrink-to-fit** font sizing (a `ResizeObserver`/`MutationObserver` loop scales the text to
fill without overflow); title flips to "References (cont.)" on continuation pages.

### 2.2 Typography

`package.json → slidev.defaults.fonts`:

```json
"fonts": { "sans": "Inter", "serif": "Merriweather", "mono": "JetBrains Mono" }
```

…but this is **contradicted** by `styles/themes/typography.css`, which defines 8 `data-font-theme`
presets over **system-font stacks** (not bundled). The default (`classic`) sets
`--scholarly-font-body: var(--scholarly-font-serif)` = `"Palatino Linotype", "Book Antiqua",
Palatino, "Times New Roman", serif`. Other presets: `modern` (Georgia/Source Sans),
`traditional` (Garamond), `contemporary` (Inter), `humanist`, `technical` (Computer Modern),
`elegant` (Cormorant), `sans-default` (Inter). So the shipped default body face is a **serif that
relies on the viewer's OS having Palatino** — otherwise it falls back to Times.

An extensive per-context heading scale lives in CSS vars, e.g. `--scholarly-h1-hero-scale: 3.25rem`,
`h1-display 2.65rem`, `h1-section 2.55rem`, `h1-content 2.15rem`, `h1-fact 3.7rem` (h2/h3 for each),
plus a `--scholarly-content-density: compact | normal | relaxed` knob.

### 2.3 Colour / tokens

Nine palettes selected by a root data attribute — `:root[data-color-theme="classic-blue"]` (default,
`#1e3a5f`), `oxford-burgundy`, `cambridge-green`, `princeton-orange`, `yale-blue`, `monochrome`,
`warm-sepia`, `nordic-blue`, `high-contrast`. Each sets five tokens:

```css
--slidev-theme-primary; --slidev-theme-primary-light;
--scholarly-accent; --scholarly-bg-warm; --scholarly-text-primary;
```

Chrome (header/footer/toolbar) colours are **derived** from the primary with `color-mix()` rather
than hand-specified, and a `data-color-mode="light|dark"` attribute swaps a dark-chrome vs
light-chrome variant (`styles/themes/mode.css`). `colorSchema: "both"`. Palettes are brand-styled;
none is documented as CVD-verified, and `--scholarly-accent` is used as a free decorative colour.

### 2.4 Packaging

```
package.json  slidev: { colorSchema, defaults: { aspectRatio, fonts } }, themeConfig: { author, conference }
              exports ./index.js + index.d.ts; bin: scholarly | sch | sts; type: module; pnpm
layouts/*.vue (26)   styles/{index.ts, layout.css, themes/{colors,typography,mode,section-mode,index}.css}
components/*.vue (14) Cite, Theorem, Steps, Columns, Keywords, Highlight, Block,
                      ScholarlyHeader, ScholarlyFooter, BeamerNavControls, FooterTocControl,
                      FooterTocPreviewCard, CenteredLayout, ThemePreview
cli/scholarly.mjs    init / theme list|apply / layout list / component list / snippet append / workflow apply
vscode-extension/    snippets (ss-…) + BibTeX autocomplete
docs/                VitePress site
setup/ shared/ utils/ vite.config.ts
```

Runtime deps include `@slidev/client` and `@jxpeng98/markdown-it-citation` (a published sibling
package). Semantic layout tokens: `--scholarly-header-height: 50px`, `--scholarly-footer-height:
36px`, `--scholarly-outline-width: 17rem`.

### 2.5 Notable features

- **BibTeX citations.** `@citekey` inline (numbered), `!@citekey` unnumbered, a `references.bib` /
  `references.md`, the `markdown-it-citation` plugin, and the auto-fit `references` layout. `Cite`
  component renders numeric `[n]` or author-year `(Smith, 2024)` markers.
- **Beamer chrome.** Persistent `ScholarlyHeader` + `ScholarlyFooter`; a footer TOC control with
  hover **preview cards** and `BeamerNavControls`; `themeConfig` `author`, `conference`,
  `footerMiddle`.
- **Authoring tooling.** `sch`/`sts` CLI scaffolds a deck and applies palette+font presets
  (`npx sch theme apply oxford-burgundy --font traditional --file slides.md`); VS Code snippets and
  BibTeX autocomplete lower authoring friction.
- Academic building blocks: `Theorem` blocks, `Steps`, `Keywords` tags, `compare` / `methodology` /
  `results` / `timeline` layouts.

---

## 3. Side-by-side

| | academic | scholarly | legible-slides (ours) |
|---|---|---|---|
| Layouts | 6, minimal | 26, catalog | 3 (assertion-evidence, two-col-evidence, cover) |
| Fonts | Montserrat / Roboto Slab / Roboto Mono, **self-hosted** | Inter/Merriweather default but body = **system** Palatino serif; 8 font themes | Inter + JetBrains Mono, **bundled in-repo** for figure parity |
| Type scale | deferred to Slidev defaults | rich per-context CSS-var scale | fixed floor: body 23px (~24px min), headline 37px, canvas 1280 |
| Colour model | one `--slidev-theme-primary` | 9 data-attr palettes, 5 tokens each, color-mix chrome | one CVD-verified `palette.json` → CSS `:root` **and** Python |
| colorSchema | `both` | `both` | **`light` locked** (dark destroyed figure contrast) |
| Accent | n/a | free decorative `--scholarly-accent` | attention-only, never a data series |
| Citations | manual `Footnote`/`Footnotes` | full BibTeX pipeline + CLI + VS Code | (open) |
| Chrome | global `Pagination` only | header + footer + TOC nav + preview cards | locator pill + accent rule + page number, nothing else |
| Section dividers | none | `section`/`agenda`/`end` | **forbidden** (locator carries orientation) |
| Deps | 2 (`@slidev/types`, unocss) | many + `@slidev/client`, markdown-it-citation | wants to start clean re: dep debt |
| License | MIT | MIT | — |

---

## 4. Borrow / avoid

### Borrow — directly reusable

1. **Academic's self-hosted-font mechanism** (`assets/fonts/*` + `styles/fonts.css` `@font-face`,
   pointed at by `styles/index.ts`). This is exactly our "bundle Inter in-repo so Python figures
   match the deck" requirement, proven as a Slidev-theme package pattern. Adopt it — but ship
   **woff2 only** (drop academic's eot/svg legacy cruft) and register the same TTFs Matplotlib loads.
2. **Global chrome injected via `global-top.vue`/`global-bottom.vue`.** Academic's `Pagination`
   pattern — a component rendered on every slide, placed by `themeConfig` axes, suppressed per-slide
   via a `pages-disabled` array, disabled by unsetting the axes. Reuse this shape for our **locator
   pill + page number** so cover/opener slides can opt out cleanly.
3. **Prop-driven figure layouts.** Academic's `figure` / `figure-side` (`figureUrl`, `figureCaption`,
   `figureFootnoteNumber`, `figureX`) keep image+caption+cite as data. `figure-side` is close to our
   `two-col-evidence`, specialised for an image — a good reference for the evidence pane.
4. **`index` layout** (`indexEntries: [{title, uri}]`, internal/external redirect) as our
   references / figure-index slide — a bibliography without a BibTeX engine, and no section divider.
5. **Manual `Footnote`/`Footnotes` numbering** (academic) as our citation-attribution primitive.
   Proportionate to a talk that cites a handful of sources; avoids a whole citation toolchain.
6. **Alias our brand token onto `--slidev-theme-primary`.** Both themes wire their primary to this
   conventional Slidev variable so built-in Slidev UI inherits the brand. `palette.json` should emit
   `--slidev-theme-primary` (plus our own named tokens) so nothing renders off-palette.
7. **Scholarly's data-attribute palette-swap** (`:root[data-color-theme="…"]`) and **`color-mix()`
   chrome derivation** — the mechanism (not the palettes) is a clean way to make "brand = swappable
   layer," and deriving chrome from one primary reduces the token count we hand-maintain.
8. **A named High-Contrast / accessibility palette variant** (scholarly ships one) — precedent that
   aligns with our CVD stance; ours would additionally be validator-verified.
9. **Packaging discipline of academic as the template to copy**, and **scholarly's CLI + VS Code
   snippets as an aspirational authoring-ergonomics idea** (scaffold a deck, insert a layout) —
   nice-to-have, not core.

### Avoid — conflicts with our stance

1. **`colorSchema: "both"`** (both themes default to it). We locked `light` (pmf-tsfm#126) because
   OS-dark rendered ink-on-white figures against near-black. Set `slidev.colorSchema: "light"` in
   our `defaults`; do **not** inherit "both", and skip scholarly's dark-chrome `data-color-mode`
   machinery.
2. **Scholarly's font system** — serif (Palatino) body default, 8 swappable font themes, and
   **system-font stacks**. Conflicts three ways: it isn't Inter; system fonts can't be bundled, so
   Python figures can't match (a viewer without Palatino gets Times); and 8 font themes reintroduce
   the multi-source problem `palette.json` exists to kill. Borrow the bundling mechanism, not the
   font catalog.
3. **Academic's font *choices*** (Montserrat / Roboto Slab, incl. a 200-weight face). Geometric
   display sans + hairline weights hurt back-row legibility. Take the loading mechanism, keep Inter.
4. **Scholarly's 9 brand palettes + free decorative `--scholarly-accent`.** None is CVD-verified;
   the accent is used as a colour anywhere. Conflicts with "accent = attention only, never a data
   series" and with verification-by-validator. Ship **one** verified set + the Machado validator, not
   a palette carousel.
5. **Scholarly's per-context heading scale** (hero/display/section/content/fact, h1–h3 each) and
   `content-density` knob. Assertion-Evidence has essentially **one** headline size (37px) + body
   (23px) + locator; a multi-size scale invites size drift below the legibility floor. Keep the
   two-size floor.
6. **Emphasis + divider layouts** — scholarly's `section`, `agenda`, `end`, `statement`, `focus`,
   `fact`, `quote`, `timeline`. Section dividers and single-word emphasis slides directly violate "no
   section-divider slides; the persistent locator carries orientation."
7. **Beamer footer-TOC navigation + preview cards** (scholarly). Heavy chrome; our model is locator
   pill + accent rule + page number and nothing else.
8. **The full BibTeX pipeline + `markdown-it-citation` dependency + CLI + VS Code extension**
   (scholarly). Large dependency and tooling surface for a template explicitly trying to start clean
   on dependency debt. Academic's manual `Footnote` is the proportionate choice unless reference
   volume forces otherwise.
9. **`aspectRatio: "4:3"`** (scholarly's Beamer nostalgia). Keep our `canvasWidth: 1280` logical
   16:9 canvas so px values render as designed and scale to the projector.

### What the packaging teaches us

- **The Slidev theme contract both confirm:** a `package.json` `slidev` block = `{ colorSchema,
  defaults: { fonts, themeConfig, aspectRatio? } }` (+ optional top-level `themeConfig` defaults);
  `layouts/<name>.vue` → usable as `layout: <name>`; `styles/index.ts` as the CSS entry pulling in
  `fonts.css` + `layout.css`; `components/*` auto-imported; `global-top.vue` / `global-bottom.vue`
  for persistent chrome; `setup/shiki.ts` for the code theme; `example.md` as demo + build target.
- **Model our package on academic** (2 deps, few layouts, one primary token, self-hosted fonts,
  global pagination) and **mine scholarly for individual mechanisms** (data-attr palette swap,
  `color-mix` chrome derivation, auto-fit references layout, CLI scaffolding).
- **Our cross-language token source is the differentiator.** Neither theme feeds a non-CSS consumer;
  our `palette.json` → CSS `:root` **and** Python figure pipeline is more principled. Preserve it,
  and additionally emit `--slidev-theme-primary` so Slidev's own components stay on-palette.
- **Both are MIT** — patterns and code are safe to adapt with attribution.

---

### Sources

- slidev-theme-academic — repo, `package.json`, `layouts/`, `styles/{fonts,layout}.css`,
  `components/`, `uno.config.ts`, README:
  <https://github.com/alexanderdavide/slidev-theme-academic> · demo
  <https://slidev-theme-academic.alexeble.de> · npm
  <https://www.npmjs.com/package/slidev-theme-academic>
- slidev-theme-scholarly — repo, `package.json`, `layouts/`, `styles/themes/{colors,typography,mode}.css`,
  `components/{Cite,ScholarlyFooter}.vue`, `layouts/references.vue`, README:
  <https://github.com/jxpeng98/slidev-theme-scholarly> · npm
  <https://www.npmjs.com/package/slidev-theme-scholarly>
- Slidev theme-authoring guide: <https://sli.dev/guide/write-theme.html>
- Our stance: [`docs/design-provenance.md`](../design-provenance.md)
