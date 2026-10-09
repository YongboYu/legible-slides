# Mode: review

Check a Slidev deck against the method, and report what breaks and how to fix it, with both
verdicts: the gate and readiness.

## 1. Find what is under review

| What | How to find it |
|---|---|
| The deck | The Slidev markdown the author named. Its headmatter is the block before the first slide. |
| Its themes | The palette JSON the deck wears: `themes/*.json` beside the deck, or whatever its headmatter and README point at. Ask if nothing names one. |
| Its generated figures | The deck's figure script, a Python file importing `legible.figures`, and the paths it writes to. |
| Its hand-made visuals | Everything else: pasted images, inline SVG and HTML on a slide, and the components in the deck's `components/` its slides use. |
| Its exceptions | The `Exception:` lines in the speaker notes, each a rule ID and a reason. |
| Its key terms | The plan's **Terms** fields, where the deck was built from a plan; otherwise the paper's title and abstract; otherwise the terms the speaker notes use, and ask for the paper. |

`never-sole-channel` and `figure-noise` are judged on the hand-made visuals only, the scope
`docs/agent-skill-contract.md` §4b fixes; generated figures carry the redundancy by construction.

## 2. Run the mechanical checks

```bash
legible lint DECK --theme THEME --json          # --theme is repeatable, once per palette
```

In a deck with a `bin/legible`, a stamped one, run this and every `legible` and `cvd-validate`
command below through `bin/legible` and `bin/cvd-validate`. They install the checks at the version
the deck is pinned to, so its review applies the rules it was built to, whatever is on PATH.

Each finding names its rule, its slide and its severity. Take them **verbatim**: the linter's count
is the count. An **error** is the gate tier. A **warning** is the advisory tier: the canon's
advisory budgets, and any finding a slide's exception turned into one, carrying its reason. The
palette check inside the linter runs `cvd-validate`.

Carry the exit code into the gate unchanged:

- **0**: the gate passes. Readiness is still open, and the steps below decide it.
- **1**: the gate fails, whatever the judgments say.
- **2**: the deck or a theme could not be read. Say what, and stop until it can be: report no
  verdict.

Where step 1 found no theme, the palette went unchecked: say so where the gate verdict goes.

## 3. Render the deck, and look at every page

A build compiles the deck; only the pages show whether a figure loaded, a component rendered rather
than showing as raw markup, a headline fit its zone, or a label survived being scaled into its pane.

```bash
pnpm exec playwright install chromium          # once per machine
pnpm run render                                # a PNG per click step, into render/
pnpm run export                                # the PDF: each slide in its final state
```

A deck stamped before these scripts existed runs the same `slidev export` commands directly.

Open every image and the PDF, at the size they come out at, which is the canvas the room sees, and
note on each page:

- **Broken**: a missing image, raw HTML or a component's tag where a visual should be, an error
  message, a placeholder left from the template.
- **Unfit**: text clipped or off the canvas, elements overlapping each other or the footer, a
  headline crowding its evidence.
- **Unreadable**: a tick label, caption or diagram label too small to read. The linter measures
  absolute sizes; a size relative to the page is measured only here.
- **Each reveal step** in order, and the final state in the PDF, which is what a handout shows.

What you note feeds the judgments in step 5, under the rules it bears on. A broken page is a finding
in its own right, with no rule ID: the room needs the slide to render. Where the deck cannot be
exported, say so where the readiness verdict goes, and report none.

**Done when** you have looked at every PNG and every page of the PDF.

## 4. Load the rules that need judgment

```bash
legible rules one-message assertion-headline never-sole-channel no-script-on-slide
legible rules established-terminology answer-first conclusion-stays-up no-section-dividers
legible rules evidence-is-visual coherence layout-discipline figure-noise motion-purpose
legible rules equation-worked-example section-locator ae-skeleton signaling accent-is-attention
legible rules spend-colour-on-discrimination
legible rules --section voice --decided-by judgment
legible rules RULE …                            # each rule the linter warned on, by its ID
```

The voice command asks the canon which rules the section holds, so a rule added there is reviewed
from the day it is written. A warned rule is loaded because its own text says what clears it.

## 5. Judge, slide by slide

Read each slide as the room receives it: its rendered pages from step 3, the headline, the evidence
and the speaker notes. Apply every check, in this order:

| Check | Applied to |
|---|---|
| `one-message` | every slide |
| `assertion-headline` | every slide carrying a headline |
| `evidence-is-visual` | every rendered page: does what is drawn prove the headline? |
| `coherence`, `layout-discipline`, `ae-skeleton` | every rendered page; for the second, the pages side by side; for the third, a zone the deck's own component or layout added |
| `signaling`, `accent-is-attention`, `spend-colour-on-discrimination` | every rendered page: what the eye is pointed at, and whether colour is spent where the comparison needs it |
| `figure-noise`, `never-sole-channel` | the hand-made visuals from step 1 |
| `motion-purpose` | every slide with a reveal: each step's image, and the final state in the PDF |
| `equation-worked-example` | every slide that shows an equation |
| `no-script-on-slide` | the words on the slide, beside its speaker notes |
| `established-terminology` | the words on the slide against the key terms from step 1, the cover and the answer slide first; the fix is the term |
| `answer-first` | the slide after the cover |
| `conclusion-stays-up` | the last slide before the backups, against the answer slide's questions, by number |
| `no-section-dividers`, `section-locator` | a slide that is only a section's name; a section's first slide and its `Signpost:` line |
| the voice rules, loaded above | the headline, the prose and the speaker notes |

A paraphrase reads as plain, so the voice rules pass it: `established-terminology` is the check that
finds one.

Where a slide takes an exception, judge the reason: it holds when the slide still carries one claim
and its evidence still reads. Report a reason that holds as the author's decision, quoted, and one
that does not as a finding with a fix.

Every judgment is held to five things:

- **Point at it.** Quote the words or name the element that triggered it, so the author can argue
  with it.
- **One per rule per slide.** The clearest instance. The linter's findings arrive as it reported
  them, every one.
- **The canon's precedence.** Where a loaded rule defers to another, the canon says which wins.
- **Keep each advisory.** Where the rule's text says what clears it and the slide meets that, say so
  on the finding, quoting what meets it. Overriding it is the author's decision.
- **Carry a fix**, every finding, the mechanical ones included: a rewritten headline, a slide split
  in two, the redundant channel a visual is missing.

Judgments are **warnings**, the advisory tier, beside the linter's own.

**Done when** every check in the table has been applied to every slide it names.

## 6. Merge into one report

One markdown report, both halves, grouped per slide in the order the deck runs. Findings against
the deck as a whole, the palette usually, go in a final group.

```markdown
# Review — path/to/slides.md

**Gate: FAIL** — 2 errors, 2 warnings.
**Readiness: not ready** — slide 4's figure did not load in the export.
**Material, still the author's:** none; the warnings below are advisory.
Errors are the gate tier and block. Warnings are the advisory tier, the linter's advisories and the
judgments alike, and never block. Palette: checked against themes/leuven-blue.json. Rendered: every
page, every reveal step, and the PDF. Read any rule below with `legible rules <rule-id>`.

## Slide 4 — "Cost falls with retrieval and accuracy holds"

- **error** · `bullet-ceiling` — … bullets, ceiling …
  **Fix:** move the last bullets to the notes; they answer a different question from the ones above them.
- **warning** · `assertion-headline` — the headline reads "Results", which names the slide rather than claiming anything.
  **Fix:** "Retrieval halves cost and holds accuracy at every window."
- **warning** · `on-slide-words` — … words outside the headline and figures, ceiling …
  **Fix:** the second paragraph is what you will say; move it to the notes.

## Deck

- **error** · `decorative-neutral-never-text` — themes/mine.json: neutral on surface contrasts …:1 (min …)
  **Fix:** darken `neutral` until it clears the ratio on both grounds; the data colours are not the problem.
```

Each palette finding sits under the rule it breaks: two data colours too close are
`separation-floor`, naming the pair and each condition it fails under, and text or attention
colours too faint are their own rules, naming the pairing and its ratio. The elisions are this
file's: a report carries the linter's message word for word, numbers
included. This file carries none of the canon's numbers, so none can go stale here.

- The **gate** is the exit code from step 2. Judgments leave it as it is, PASS or FAIL.
- **Readiness** is the first of these that applies, with its reason:
  - **not ready**: the gate fails, a page did not render as intended, or a finding on a rule the
    canon marks **Floor** is open. No reason clears a floor, so only its fix does.
  - **review complete**: the review is finished, and a **material** finding is still the author's
    to settle. Name each one.
  - **ready**: none of the above. Every material finding is fixed, or the author accepted it with a
    reason the report quotes. What is left is advisory, and the author may present with it.
- A finding is **material** when the room would leave with the wrong message: on `one-message`,
  `evidence-is-visual`, `answer-first`, `conclusion-stays-up` or `established-terminology`, or an
  exception whose reason does not hold. The rest (voice, layout, the budgets) is listed and never
  waited on.
- An author **accepts** a material finding by writing the slide an `Exception:` line for its rule,
  so the next review sees the decision and weighs the reason. A reason that holds settles the
  finding, and one that does not stays material.
- Each finding names its **rule by ID**, so a reader can look it up and disagree with it.
- The tally counts both halves; within a slide, the gate tier comes first.
