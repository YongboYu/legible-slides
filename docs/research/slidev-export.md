# Research: Can `slidev export` seed a static PowerPoint proof, and with what fidelity?

**Ticket:** legible-slides — evaluate `slidev export --format pptx` as a way to ship a static `.pptx` starter from the reference Slidev deck.

**Verdict (TL;DR):** **Partly — but not as an _editable_ starter.** `slidev export --format pptx` is real and supported, but every slide is embedded as a **full-page raster image** (a PNG set as the slide background), not editable shapes or text. It is excellent for producing a **pixel-faithful, presentable** `.pptx` proof, and useless as a deck a presenter can retype/restyle inside PowerPoint. If the goal is an _editable_ themed `.pptx` master, `slidev export` is the wrong tool and you should hand-author a PowerPoint master (or use a shapes-based generator). Details and recipe below.

---

## 1. Supported output formats + PPTX version support

Per the official docs, `slidev export` supports four formats via `--format`: **PDF, PPTX, PNG, and Markdown**.

- `--format pdf` (default), `png`, `pptx`, `md`.
- Source: [Exporting | Slidev](https://sli.dev/guide/exporting)

**PPTX support was added in Slidev v0.49.4** (released May 2024), via PR [#1603 "Export to PPTX" by @kermanx](https://github.com/slidevjs/slidev/pull/1603). Source: [slidevjs/slidev releases](https://github.com/slidevjs/slidev/releases?q=pptx&expanded=true). It has been a first-class, maintained feature ever since — so any recent Slidev (`@slidev/cli`) has it.

Basic command:

```bash
slidev export --format pptx
# or shorthand: slidev export slides.md --format pptx --output deck.pptx
```

---

## 2. HOW export works — raster images, NOT editable shapes/text

This is the crucial finding. **Export renders slides in headless Chromium via Playwright**, screenshots each slide, and (for PPTX) wraps those screenshots in a PowerPoint container using `pptxgenjs`.

### Official docs wording (authoritative)

> "Note that all the slides in the PPTX file will be exported as images, so the text will not be selectable. Presenter notes will be conveyed into the PPTX file on a per-slide basis. In this mode, the `--with-clicks` option is enabled by default."
> — [Exporting | Slidev](https://sli.dev/guide/exporting)

> "Exporting to PDF, PPTX, or PNG relies on Playwright for rendering the slides. Therefore `playwright-chromium` is required to be installed in your project."
> — [Exporting | Slidev](https://sli.dev/guide/exporting)

### Confirmed in the source implementation

The PPTX generator in `packages/slidev/node/commands/export.ts` confirms the mechanism exactly:

- Imports `pptxgenjs`: `const { default: PptxGenJS } = await import('pptxgenjs')`.
- Defines a layout sized from the render canvas, converting px→inches at 96 DPI:
  `pptx.defineLayout({ name, width: width / 96, height: height / 96 })` (so aspect ratio matches the deck, e.g. 16:9).
- **Each rendered PNG becomes the slide _background_**, not a shape or text:
  `slide.background = { data: "data:image/png;base64,..." }` for each captured page.
- Presenter notes attached per slide: `if (note) slide.addNotes(note)`.
- Deck title/author/subject metadata are set from the first slide's frontmatter.
- Source: [export.ts on GitHub (main)](https://github.com/slidevjs/slidev/blob/main/packages/slidev/node/commands/export.ts)

**Conclusion:** the `.pptx` is a container of one background image per (slide/step). There are **zero editable text boxes, shapes, charts, tables, or layout placeholders**. Opening it in PowerPoint shows a flat picture on each slide — you can add your own new shapes on top, but you cannot edit any content that came from Slidev.

This is corroborated by a user report, [Discussion #2417 "Exported PPTX File Contains Only Non-Editable Images"](https://github.com/slidevjs/slidev/discussions/2417) — the behavior is by design, not a bug.

---

## 3. Known limitations & how features are handled

| Concern | Behavior on PPTX export |
| --- | --- |
| **Editable text/shapes** | None. Everything is a flattened raster image (see §2). |
| **Custom fonts** | Rendered *visually* correctly because Chromium rasterizes them into the image — but they are baked into pixels, not embedded/selectable fonts. Web fonts that load slowly can render as fallback/blank if the page isn't ready; mitigate with `--wait <ms>` / `--wait-until`. |
| **Custom layouts / Vue components** | Rendered faithfully as images (whatever the browser shows is what you get). Not preserved as editable structure. |
| **Animations / clicks / build steps** | **Flattened into separate slides.** Globally `--with-clicks` defaults to *false* (one page per slide), **but in PPTX mode `--with-clicks` is enabled by default**, so each click/`v-click` step becomes its own full-slide image. Motion/transitions themselves are lost (static snapshots only). Disable with `--with-clicks false` to get one image per slide. |
| **Backgrounds** | Slide `background:` / cover imagery is captured into the single background PNG — handled correctly visually. `--omit-background` can export transparent background where supported. |
| **Dark/light** | `--dark` exports the dark theme; otherwise light. Whatever renders is baked in. |
| **Presenter notes** | Preserved per slide via `addNotes` (editable text in the PPTX notes pane — the one genuinely editable part). |
| **Interactivity** | Lost. Monaco editors, clickable links inside components, live counters, embeds, etc. become static pictures. |

Relevant CLI flags (from the docs): `--format`, `--output`, `--with-clicks`, `--dark`, `--timeout`, `--wait`, `--wait-until`, `--executable-path`, `--with-toc`, `--omit-background`, `--range`. Source: [Exporting | Slidev](https://sli.dev/guide/exporting).

---

## 4. Is the exported PPTX a usable *editable* starter? + Recipe

**No — it is not an editable starter.** It is a **flat picture-per-slide deck**: high visual fidelity, presenter notes intact, but nothing on the canvas can be tweaked in PowerPoint. A presenter can *present* it anywhere PowerPoint runs (the original motivation for the feature), but cannot "retype a headline" or "restyle a chart" as the ticket's editability bar requires.

### Recipe A — pixel-faithful static PPTX proof (what export IS good for)

Use this if "static PowerPoint proof" means *a presentable, on-brand deck that looks exactly like the Slidev reference*, and edits are not required.

```bash
# 1. Install the Chromium renderer (required for pptx/pdf/png export)
npm i -D playwright-chromium
#    (or: npx playwright install chromium)

# 2. Export, keeping build steps as separate slides (default in pptx mode)
npx slidev export slides.md \
  --format pptx \
  --output dist/legible-slides.pptx \
  --wait 1000            # give custom/web fonts time to load before capture

# Optional variants:
#   --with-clicks false   # one flat image per slide (no per-step expansion)
#   --dark                # export dark theme
#   --timeout 60000       # raise Playwright timeout for big decks
```

Post-processing: essentially none needed — you get a self-contained `.pptx`. If you need selectable *text somewhere*, the notes pane carries presenter notes. That is the ceiling of editability from native export.

### Recipe B — a genuinely EDITABLE themed .pptx starter (export is inadequate — do this instead)

Native `slidev export` cannot produce editable shapes, and there is **no flag to change that**. Options, roughly in order of effort vs. payoff:

1. **Hand-author a PowerPoint master/template** (recommended for a "themed starter"). Build a `.potx`/`.pptx` with real Slide Master + layouts, placeholders, theme colors, and fonts that mirror the legible-slides Slidev theme. This is the only path that yields a first-class, editable PowerPoint starter, and it's a one-time design cost. Use the Slidev-exported images (Recipe A) as a pixel reference while authoring.
2. **Generate shapes programmatically with `pptxgenjs`** yourself (the same lib Slidev uses, but calling `addText`/`addShape`/`addTable` instead of `addImage`). Feasible for simple, structured content; you re-implement layout from the deck's Markdown/frontmatter. High effort, brittle for rich Vue components.
3. **Third-party `slidev2pptx`** — *not* a solution to editability: it also embeds PNG images (and is now **archived**, explicitly superseded by native export since Slidev officially added PPTX). Source: [zhangyu94/slidev2pptx](https://github.com/zhangyu94/slidev2pptx). Skip it.

---

## Sources (primary)

- [Exporting | Slidev — official docs](https://sli.dev/guide/exporting) — formats, "exported as images / text not selectable", Playwright requirement, `--with-clicks` default-on for pptx, flag list.
- [slidevjs/slidev — export.ts implementation (main)](https://github.com/slidevjs/slidev/blob/main/packages/slidev/node/commands/export.ts) — pptxgenjs usage, image-as-background, `addNotes`, `defineLayout`.
- [slidevjs/slidev releases (pptx)](https://github.com/slidevjs/slidev/releases?q=pptx&expanded=true) — PPTX added in v0.49.4 (PR #1603, May 2024).
- [PR #1603 "Export to PPTX"](https://github.com/slidevjs/slidev/pull/1603) — feature origin.
- [Discussion #2417 — "Exported PPTX File Contains Only Non-Editable Images"](https://github.com/slidevjs/slidev/discussions/2417) — confirms images-only is expected behavior.
- [zhangyu94/slidev2pptx](https://github.com/zhangyu94/slidev2pptx) — archived third-party tool, also image-based, superseded by native export.
