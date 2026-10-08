# The agent-skill contract

_Resolves [#12](https://github.com/YongboYu/legible-slides/issues/12). Depends on the method canon
([#3](https://github.com/YongboYu/legible-slides/issues/3), `method.md` — the single source of
truth for the rules), and consumes the CVD-validator contract
([#9](https://github.com/YongboYu/legible-slides/issues/9),
[`cvd-validator-contract.md`](cvd-validator-contract.md)) and the Slidev reference impl
([#10](https://github.com/YongboYu/legible-slides/issues/10),
[`slidev-reference-impl.md`](slidev-reference-impl.md))._

The skill is the delivery that lets a **coding agent build to the method** — it stamps a
method-compliant starting point (**scaffold**) and holds a deck to the standard afterwards
(**review**). The review half is the high-value part: it turns the method's rules from prose a human
must remember into checks an agent runs. It never restates those rules — it points at `method.md`.

---

## 1. Shape — one `SKILL.md` skill, four modes

A single **Claude Code skill** defined by a `SKILL.md`, living in **`skill/`** at the repo root (a
shippable delivery, not a project-private `.claude/skills/` helper). One skill covering four modes.
`SKILL.md` is a router: it holds what every mode shares and points at one file per mode in
`skill/modes/`, so a run loads only the mode it takes:

- **draft** — write a talk plan from a paper and its codebase (§7).
- **build** — build a deck from a talk plan, and review it (§7).
- **scaffold** — start a new method-compliant Slidev deck of your own.
- **review** — check an existing deck against the method.

**Deferred to future work** (same "seed, extensible" posture as the rest of the map):

- **Plugin packaging** — distributing the skill as an installable Claude Code plugin.
- **Cross-agent targeting** — re-expressing the same contract as `AGENTS.md` guidance for non-Claude
  agents. The contract is designed to make this cheap: every rule lives in tool-neutral `method.md`,
  and every mechanical check is a tool-neutral CLI, so nothing about the skill is Claude-specific
  except the `SKILL.md` wrapper.

## 2. Rule sourcing — a thin pointer, never a second copy

`method.md` is the single source of truth (#3: `AGENTS.md` and `design-provenance.md` *point to* it
rather than restate). The skill obeys the same rule:

- The skill carries only the **procedure** — the ordered workflow, which checks are
  mechanical vs judgment, and the report format. It does **not** restate what a good slide is.
- The **rule content and thresholds are loaded from `method.md` at review time**. A rule change in
  `method.md` therefore never silently un-syncs the reviewer.
- Every rule there carries a **stable ID** (`one-message`, `bullet-ceiling`, `separation-floor`, …)
  and, where it has a number, a `key = value` **threshold line**. The skill addresses rules by ID and
  **quotes** those lines, so the thin pointer never forces the reviewer to re-derive a number at
  runtime.
- `method.md` also marks each rule **`script`** or **`judgment`**, which is the same seam §4 splits
  the engine along. The canon decides which side a rule falls on; the skill only implements it.

Built in **#23** as [`skill/SKILL.md`](../skill/SKILL.md), whose review procedure loads rules by
running `legible rules [RULE …] [--decided-by script|judgment] [--section SECTION]`. It prints the
canon's own markdown, and the package carries that canon into a wheel, so a review on a machine with
no checkout still reads the rules rather than remembering them. The filters matter as much as the
IDs: asking for a section and a side of the seam is how the anti-slop pass picks up a rule the canon
grows without an edit here. See [`python/README.md`](../python/README.md#legible-rules).

## 3. Review surface — Slidev-coupled for v1

The review parses a **Slidev deck**: the markdown slides, the `themes/*.json` palette, and the
generated figure PNGs. The mechanical linter is Slidev-markdown-aware. Slidev is the only
authoring surface.

## 4. Review engine — a hybrid seam

Checks split by whether a script can decide them with certainty. Mechanical checks are reproducible
and CI-able; semantic checks need an LLM's judgment.

### 4a. Mechanical — a deterministic linter

Lives in the existing **`legible` Python package** (one Python home, alongside the figure helper and
the validator, sharing the pinned `colorspacious`). Objective, reproducible, CI-integratable.

Built in **#19** as `legible lint DECK [--theme THEME …]`, exiting 0 clean, 1 on any violation and 2
when the deck or a theme could not be read — the same three the validator publishes. Its report is
grouped by slide and names each finding's rule; see
[`python/README.md`](../python/README.md#legible-lint).

| Check | Rule | How |
|---|---|---|
| Bullet ceiling | `bullet-ceiling` | count list items per slide, against the rule's threshold |
| Word ceiling | `word-ceiling` | word count per list item, against the rule's threshold |
| Headline fits two lines | `headline-shape` | set each headline outside the cover in the bundled face, at the canon's headline size and the theme's headline width, with the face's kerning, and count the lines against the rule's ceiling |
| No em-dashes in headlines | `no-em-dash-headline` | scan headline text |
| No inflated-register words | `no-inflated-register` | the rule's wordlist, at the severity the rule assigns |
| Sentence-opener distribution | `opener-variety` | opener share per passage, against the rule's ceiling |
| Section map fits | `section-locator` | the sections a deck declares, their count and each label's length, at the severity the rule assigns |
| Type floor holds | `type-scale` | every font size a slide's markup sets (style attributes, style blocks, UnoCSS text classes, SVG `font-size` attributes): an inline px size, and any size that resolves below the rule's floor; and every absolute size in the deck's own `components/`, `layouts/`, `styles/` and `style.css` that resolves below it |
| Closes on a conclusion | `conclusion-stays-up` | the last slide outside the backups: no headline, a closing label for one, or a thank-you, at the severity the rule assigns |
| **Palette passes CVD and contrast** | `separation-floor`, `accent-is-attention`, `decorative-neutral-never-text` | **shell out to `cvd-validate`** over `themes/*.json` — never reimplement CVD. It measures the data colours' separation and the attention and text pairings' contrast |
| Visual groups (advisory) | `element-ceiling` | the blocks at the top of each slide's body, beneath the headline, at the severity the rule assigns |
| Words on a slide (advisory) | `on-slide-words` | word count outside the headline, figures and footnotes, at the severity the rule assigns |
| Emphasis and callouts (advisory) | `signal-budget` | bold or highlighted spans, and callouts, per slide, at the severity the rule assigns |
| New abbreviations (advisory) | `acronym-budget` | runs of capitals over the talk's slides, backups aside, at the severity the rule assigns |
| Pace (advisory) | `pace-budget` | the notes' `Time:` budgets summed against the headmatter's `duration`, at the severity the rule assigns |

Each row's numbers, wordlist and severity are read from that rule in `method.md`. The linter carries
none of its own.

A slide's `Exception:` notes line, as the canon's "Departing from a default" sets it out, turns that
rule's findings on that slide into warnings carrying the reason. The linter reads which rules are
**Floor** from the canon and applies no exception to one.

Figure type is held where the figure is written: `legible.figures.save` refuses a figure whose
smallest type lands below the floor at the width it is shown at (`lands_at_px`).

### 4b. Semantic — LLM judgment

The calls that need understanding, applied by the agent against the rules loaded from `method.md`.
§4c lists which judgment rules the review covers and which it leaves to the plan. From the source
and the speaker notes:

- **`one-message`** — is this one slide or two?
- **`assertion-headline`** — claim, or bare label?
- **`never-sole-channel`, hand-made visuals only** — generated figures carry the redundancy by
  construction (#10), so this targets pasted-in images.
- **`no-script-on-slide`** — script on the slide, or the key terms
  ([#35](https://github.com/YongboYu/legible-slides/issues/35))?
- **`established-terminology`** — the paper's key terms, or a paraphrase standing in for one
  ([#42](https://github.com/YongboYu/legible-slides/issues/42))? Judged on its own rather than left
  to the voice rules below, because the canon states its precedence over them.
- **The canon's judgment anti-slop rules** (`no-contrast-for-emphasis`, `no-reflexive-tricolon`,
  `no-hedging-or-boilerplate`, `rhythm-variety`, `concrete-over-abstract`) — the structural tells a
  wordlist cannot catch.
- **`answer-first` and `conclusion-stays-up`** — does the second slide give the result and the
  questions, and does the last main slide answer each question by its number?
- **`equation-worked-example`**, **`no-section-dividers`** and the signpost half of
  **`section-locator`**.

From the rendered pages, at presentation size and with every reveal step exported, because a build
that succeeds says nothing about what the room sees:

- **`evidence-is-visual`**, **`coherence`**, **`layout-discipline`** and the hand-made half of
  **`figure-noise`** — does the visual prove the headline, and is anything there that does not?
- **`motion-purpose`** — does each reveal step add evidence, and does the final state read on its own?
- **What no rule names but every room notices** — clipped or overlapping content, an asset that did
  not load, raw markup where a component should be, a figure label too small or cut off.

### 4c. Coverage — what a PASS establishes, and what it does not

A PASS is the linter's exit code, and it says one thing: nothing the scripts check is broken. It
does not say the deck is ready to present. Every rule in the canon is listed here once, with what
covers it on a deck an author wrote, so a reader can see where the gate ends and the reading begins.
`python/tests/test_skill.py` holds this table to the canon: a rule added there fails the suite until
it has a row.

| Covered by | Means |
|---|---|
| gate | `legible lint` or `cvd-validate` settles it on any deck, and an error blocks |
| advisory | the linter counts it and warns; the review weighs it |
| theme | the theme is built to it and this repo's tests hold the theme to it; a deck that overrides the theme is not checked |
| review | review mode judges it on every deck, from the source and the speaker notes |
| render | review mode judges it on the rendered pages, at presentation size, every step revealed |
| plan | draft and build shape it from the talk plan; nothing judges it on a finished deck |
| none | nothing checks it yet |

| Rule | Covered by | What is left |
|---|---|---|
| `one-message` | review | |
| `assertion-headline` | review | |
| `headline-shape` | gate | the line ceiling is measured; that the headline reads as a claim is `assertion-headline`'s, and reviewed there |
| `ae-skeleton` | theme, render | a deck's own layout or component can add a zone; the rendered pages show it |
| `no-section-dividers` | theme, review | the theme ships no divider layout; a slide that is a bare section name is judged |
| `answer-first` | review | |
| `conclusion-stays-up` | advisory, review | the last main slide's headline is checked; that it answers each question by number is judged |
| `section-locator` | advisory, review | the signpost lines in the notes are judged |
| `evidence-is-visual` | render | |
| `equation-worked-example` | review | nothing detects an equation by script yet; the review looks for one |
| `message-before-visual` | plan | |
| `established-terminology` | review | |
| `no-script-on-slide` | review | |
| `bullet-ceiling` | gate | |
| `word-ceiling` | gate | |
| `coherence` | render | |
| `signaling` | plan, render | |
| `layout-discipline` | render | |
| `figure-noise` | theme, render | generated figures are drawn without chartjunk; hand-made visuals are judged |
| `element-ceiling` | advisory | |
| `on-slide-words` | advisory | |
| `signal-budget` | advisory | |
| `acronym-budget` | advisory | |
| `pace-budget` | advisory | |
| `type-scale` | gate, render | absolute sizes on slides, in components and in figures are measured; a relative size (`em`, `calc()`, a custom property) and the room itself are judged on the rendered pages |
| `fonts` | theme | |
| `light-ground` | theme | a deck's headmatter could override the scheme; nothing checks it |
| `never-sole-channel` | theme, review | generated figures carry the redundancy by construction; hand-made visuals are judged |
| `accent-is-attention` | gate, review | the contrast pairings are measured; the one locus per slide is judged |
| `spend-colour-on-discrimination` | plan, render | |
| `decorative-neutral-never-text` | gate | the roles the template sets as text are measured; a deck's own component that sets text in another role is not |
| `separation-floor` | gate | |
| `motion-purpose` | review, render | the reveals are judged step by step, and the final state as the exported page |
| `motion-ceiling` | none | nothing reads an animation's duration yet; the deck sets no transition and the method asks for little motion |
| `no-em-dash-headline` | gate | |
| `no-inflated-register` | advisory | |
| `opener-variety` | gate | |
| `no-contrast-for-emphasis` | review | |
| `no-reflexive-tricolon` | review | |
| `no-hedging-or-boilerplate` | review | |
| `rhythm-variety` | review | |
| `concrete-over-abstract` | review | |

So the report states two verdicts, not one: the **gate**, which is the exit code, and **readiness**,
which no script can give and which the review and the rendered pages answer between them.

## 5. Review posture & output

- **Flag + suggest, human applies.** Each finding is surfaced **with a proposed fix** (rewrite a
  label into a claim, split a two-message slide, trim a bullet), but the skill **never silently
  rewrites**. The author — or the agent under the author's direction — accepts or rejects. This keeps
  the skill honest to the method: it can enforce structure, but it cannot decide your message for
  you.
- **Two-tier authority.**
  - **Mechanical linter = hard gate** — exit 0/1, CI-integratable, mirroring `cvd-validate` (#9).
    Objective violations block. One exception, declared by the canon rather than by the skill: a rule
    whose threshold line sets its own severity to `warning` reports without blocking. The canon says
    which rules those are and why — `no-inflated-register` is one, because
    `established-terminology` can legitimately override it, and the budgets the canon calls
    **advisory** are the rest: a script finds them, and they belong to the advisory tier below.
  - **Semantic review = advisory** — LLM judgments are fallible, so they never block CI. The
    linter's warnings join them in this tier, and the review weighs each against what its rule says
    clears it ([#34](https://github.com/YongboYu/legible-slides/issues/34)).
- **Output = one merged per-slide markdown report.** Findings grouped by slide, each tagged severity
  **error** (mechanical gate) or **warning** (advisory judgment) and **linked to the `method.md`
  rule** it enforces; semantic findings carry a suggested rewrite.

The report's shape is fixed in [`skill/modes/review.md`](../skill/modes/review.md), and
[`skill/fixtures/`](../skill/fixtures) is a deck built to fail it with the answer key beside it —
every planted violation, by slide and by rule, and which half of the review surfaces it.

## 6. Scaffold — a minimal starter

Scaffold stamps a **fresh, method-compliant Slidev deck** — distinct from the flagship (which
remains the teaching artifact per #10). It is deliberately lean: a clean start that is review-ready
from slide one, not a fully worked deck.

It stamps:

- a new Slidev deck wired to the in-repo **`slidev-theme-legible`**;
- the **`palette.json → tokens.css`** pipeline wired (Python emits the committed `tokens.css`, per
  #10 — one palette authority);
- **`cvd-validate` + the mechanical lint hooked as checks** (pre-commit / CI stub);
- **one skeleton slide per AE layout** — `cover`, `assertion-evidence`, `two-col-evidence`,
  `references` — as fill-in placeholders.

**Theme = `leuven-blue`.** The repo ships one theme, and the scaffold stamps a copy of it. It carries no institution's marks, so nothing stamped claims an
endorsement: the cover's logo slots arrive as placeholders. Slidev only.

Built in **#24** as the scaffold mode of the skill, [`skill/modes/scaffold.md`](../skill/modes/scaffold.md), which stamps
[`skill/template/`](../skill/template) — files rather than instructions, so what a stamp produces is
something a suite can be run over. It is: the deck wired to a vendored copy of the theme, archived from the same commit its checks are
pinned to, the palette at
`themes/palette.json` with the stylesheet `legible gen-css` emits from it committed beside it, both
checks as a pre-commit config and a workflow, and one skeleton slide per layout.

The palette is named for its job rather than for the palette it arrives holding, because everything
else in the stamped deck points at that path: choosing another one is a change to the file's
contents and to nothing that names it, which is the same "one palette authority" this document asks
of the theme.

**The acceptance bar is §5's own review**, and it is enforced rather than asserted:
`python/tests/test_scaffold.py` lints the template, so a template that would stamp an error fails
this repo's CI, and the same suite holds it to the theme's layouts and to the palette it copies. CI
also stamps the template, recolours it, and builds it, which is where the claim that the deck's own
tokens outrank the theme checkout's is settled — a stamped deck wearing the wrong palette would be
visible in the built CSS and nowhere else.

## 7. Draft and build — a talk plan between the paper and the deck

Added in **[#36](https://github.com/YongboYu/legible-slides/issues/36)**. A **talk plan** is a
markdown file with one entry per slide (its section, its headline claim, its evidence and where that
comes from, its time budget), plus the talk's slot and its research questions. The format is
[`talk-plan.md`](talk-plan.md). The plan is where `message-before-visual` is done: every claim is
written before anything is drawn.

- **draft** reads a paper and its codebase, asks the author for the slide the talk rests on and the
  challenges they expect, and writes a plan: the paper's own questions, quoted from where it states
  them, a setup part before the findings, and the findings question by question
  ([#38](https://github.com/YongboYu/legible-slides/issues/38)). It checks each number against its
  source, sorts what the talk leaves out into two places, each with its reason: backups, for the
  questions the room is likely to ask, and cuts ([#40](https://github.com/YongboYu/legible-slides/issues/40)),
  and then stops: the author edits the plan, and the argument is settled there.
- **build** runs scaffold, fills each slide from its entry, draws the figures with the figure
  helper, builds, and runs review mode. An entry's optional fields, its callout, reveal, returning
  figure, terms and structured notes, go on the slide where the entry carries them
  ([#39](https://github.com/YongboYu/legible-slides/issues/39)). The plan's backups follow the
  conclusion, marked `backup: true`, outside `pace-budget`. The report is handed over with the
  deck. An error is fixed as part of the build, and the plan is updated to match; a warning is left
  for the author.

Neither mode states a rule. Draft loads the rules a plan is shaped by with `legible rules`, the way
review does, and build's acceptance bar is §5's review.

---

## Summary

| Facet | Decision |
|---|---|
| Packaging | One Claude Code `SKILL.md` in `skill/`; four modes; plugin + cross-agent deferred |
| Rule sourcing | Thin pointer — procedure in `SKILL.md`, rules + thresholds loaded from `method.md` |
| Review surface | Slidev only |
| Review engine | Hybrid — mechanical linter in `legible` (palette via `cvd-validate`) + LLM for 5 semantic checks |
| Review posture | Flag + suggest (human applies); two-tier gate/advisory; merged per-slide markdown report |
| Scaffold | Minimal Slidev starter on `leuven-blue`, review-ready from slide one |
| Draft & build | Paper and codebase → talk plan (author edits) → deck, reviewed |
