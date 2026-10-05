# Mode: build

Turn a talk plan into a deck. Every headline, section, layout, piece of evidence and time budget
comes from the plan, in the format `docs/talk-plan.md` sets out.

## 1. Read the plan against its format

Every entry carries the fields the format asks for. Where one is missing, or a claim has no source,
name the entry and ask the author.

**Done when** every entry has its fields, or the author has answered for it.

## 2. Scaffold the deck

Run [scaffold](scaffold.md), steps 1 to 4, taking its answers from the plan's headmatter: the title,
the speaker, the venue, and the slot as the deck's `duration`.

## 3. Fill each slide from its entry, in order

Replace the template's skeleton slides with one slide per entry:

| From the entry | Onto the slide |
|---|---|
| its heading | the headline, word for word |
| **Layout** | the slide's `layout` |
| **Section** | the slide's `section`, set where it changes and left to carry forward otherwise |
| **Evidence** | a figure through the figure script, a concept diagram (step 4), a markdown table, an equation (`equation-worked-example`), or a `Callout`; the plan's questions and answers on the slides `answer-first` and `conclusion-stays-up` name |
| **Source** | a footnote on the slide, and an entry on the references slide |
| **Time** | a `Time:` line in the speaker notes |
| the paragraph under it | the speaker notes, with a `Signpost:` line where the section changes |
| **Callout** | a `Callout` over or beside the evidence, its text word for word |
| **Reveal** | a `v-click` on each element that arrives, one per step, in the plan's order |
| **Returns** | the earlier slide's figure on this one, drawn by the same chart in the figure script, sized for its pane, beside what the entry adds |
| **Terms** | each term on the slide where the evidence names it, spelled as the plan spells it, and said in the notes where it is defined |
| **Notes** | a `Question:`, `In:`, `Out:` and `Q&A:` paragraph in the speaker notes, one per part the entry gives, in that order, after the `Time:` and `Signpost:` lines and before the paragraph |
| **Exception** | an `Exception:` line in the speaker notes: the rule's ID and the plan's reason, word for word |
| **Setup**, **Answers**, **Load-bearing** | nothing: they shape the argument in the plan |

A slide carries exactly the optional fields its entry carries. Load what they are held to first:

```bash
legible rules signal-budget accent-is-attention motion-purpose established-terminology acronym-budget
```

Then the backups, after the conclusion and before the references, one slide per entry in the plan's
order, filled the same way. The first declares `section: Backup` and `backup: true`, and the rest
carry it forward, so the footer labels them and `pace-budget` leaves them out. Each backup's notes
open on its **Time** as a `Time:` line and then its **Asked** as a `Question:` line.

Delete the placeholder image and everything else the template stamped that no entry asked for.

**Done when** the deck has one slide per entry, in the plan's order, and nothing else from the
template.

## 4. Draw the figures from data, and the diagrams from tokens

```bash
legible rules evidence-is-visual figure-noise never-sole-channel accent-is-attention type-scale
```

A figure script beside the deck draws every chart an entry calls for, with the archetypes in
`legible.figures` and the deck's own palette. Numbers typed in from the paper say which table they
came from; data read from the codebase is committed beside the script. Pass `save` the width each
figure lands at on its slide as `lands_at_px`: it refuses a figure whose type would land under the
floor there. Commit the images it writes. Pick the archetype by what the evidence compares:

| The evidence compares | Draw it with |
|---|---|
| a few series over one shared axis, like time | `multi_series` |
| one highlighted group against a de-emphasised one, on one scale | `two_group` |
| the same few series on several groups that don't share a scale, like one measure on four datasets | `small_multiples`, a panel per group, with the baseline as the `reference` series |

Keep one kind of category per axis. A "best baseline" bar on an axis of datasets puts two kinds on
one axis and hides which baseline won where: that evidence is small multiples.

A comparison is a figure even when the plan's numbers came from a table (`evidence-is-visual`). A
markdown table is for a lookup, where the room reads one value off it, and for evidence that is
words in rows.

A `diagram` entry has no data behind it, so draw it by hand: inline SVG on the slide, or a component
of the deck's own in `components/` when it needs more than a few shapes or comes back on a later
slide.

- Style it with classes in the component's own stylesheet, the way the theme's components are:
  colours from the palette's roles and type sizes from the type scale, each as `var(--…)`. A
  recolour then reaches the diagram as it reaches the charts. An SVG drawn with a `viewBox` is drawn
  at the width it lands, so its sizes are the canvas's.
- `never-sole-channel` and `accent-is-attention` decide what its colours may say.
- Give it a caption and a source, the way `Figure` does.

**Done when** every figure and diagram an entry names is on its slide, and the figure script runs
clean from the committed data.

## 5. Build, review, and attach the report

```bash
pnpm install && pnpm build
```

Then run [review](review.md) over the deck. It renders every page and reads them, which a build
cannot. Save its report beside the plan, and hand it over with the deck and the exported PDF.

An error is a fault in the build: fix it. If the fix changes a slide's words, change its entry in
the plan too, so the plan stays the deck's source. A warning is the author's to weigh: report it with
its fix, and leave the slide as the plan wrote it.

**Done when** the gate passes, and the report's readiness verdict names whatever is left for the
author.
