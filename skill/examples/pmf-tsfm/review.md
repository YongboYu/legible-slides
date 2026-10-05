# Review — skill/examples/pmf-tsfm/deck/slides.md

**PASS** — 0 errors, 7 warnings.
Errors are the gate tier and block. Warnings are the advisory tier, the linter's advisories and the
judgments alike, and never block. Palette: checked against skill/template/themes/palette.json, the
palette the template stamps. Read any rule below with `legible rules <rule-id>`.

This is review mode run over the deck build mode made from [`plan.md`](plan.md), as the last step
of the build. `legible lint` reported no findings, at either severity. The judgments below were made
against the rules as `legible rules` printed them: `one-message`, `assertion-headline`,
`never-sole-channel`, `no-script-on-slide`, `established-terminology`, and the voice rules the canon
decides by judgment. The key terms are the plan's **Terms**: slide 6 introduces "time series
foundation model" and "zero-shot", and the paper's title and abstract use both.

## Slide 1 — "Time series foundation models for process model forecasting"

- **warning** · `established-terminology` — the subtitle reads "Pre-trained forecasters, used as
  they are", a paraphrase of the title's own term and of "zero-shot", right under the title.
  **Fix:** "Used zero-shot, they can forecast how a process changes."

## Slide 2 — "Used as they are, pre-trained forecasters cut the error by 17 to 28%, but the process models they forecast are no better."

- **warning** · `established-terminology` — "Used as they are, pre-trained forecasters" stands in
  for "zero-shot, time series foundation models", in the headline and again in Q1 ("a pre-trained
  forecaster, used as it is"). This is where the room first meets both terms, so it's where the
  paraphrase costs most: slide 6 defines the terms four slides later, after the room has learned
  to call them something else.
  **Fix:** "Zero-shot, time series foundation models cut the error by 17 to 28%, but the process
  models they forecast are no better." Q1: "Can a time series foundation model, used zero-shot,
  beat the best methods?" Gloss each term in a sentence in the notes; slide 6 still sets them out.
  The headline stays at two lines.

## Slide 8 — "On every log, the best pre-trained model beats the best baseline by 17 to 28%."

- **warning** · `established-terminology` — "the best pre-trained model" for the best foundation
  model, while the figure's caption says "Zero-shot".
  **Fix:** "On every log, the best foundation model beats the best baseline by 17 to 28%."

## Slide 12 — "On the sparse Sepsis log, process models forecast by pre-trained models fit fewer than one trace in five."

- **warning** · `established-terminology` — "pre-trained models" for the foundation models.
  **Fix:** "On the sparse Sepsis log, process models forecast by foundation models fit fewer than
  one trace in five."

## Slide 13 — "Used as they are, pre-trained forecasters beat both baselines on all four logs, so they make a strong default to build on."

- **warning** · `assertion-headline` — the headline answers the first question and leaves out the
  third, which slide 11's notes call the most interesting finding. A listener who keeps only this
  line leaves with the error result and not with "the process models are no better", which is the
  half of the answer slide's headline that tells the room what to work on next.
  **Fix:** "Zero-shot, time series foundation models beat both baselines on all four logs, and the
  process model is the next problem."
- **warning** · `established-terminology` — the conclusion closes on the same paraphrase as slide
  2, "Used as they are, pre-trained forecasters", and it stays up through Q&A, so it's the wording
  the room takes away. The fix above uses the terms.
  **Fix:** as above: "Zero-shot, time series foundation models …"

## Slide 14 — "Measured by RMSE, the best pre-trained model still beats the best baseline on every log, by 22 to 33%."

- **warning** · `established-terminology` — "the best pre-trained model" again, on a backup the
  room will ask for by the paper's terms.
  **Fix:** "Measured by RMSE, the best foundation model still beats the best baseline on every log,
  by 22 to 33%."

## What was checked and found nothing

- `headline-shape`: the linter set every headline in the theme's headline box and found none past
  two lines. Every content headline takes two lines but slide 9's, which takes one, and the longest,
  slides 2 and 13 at 22 words, run most of the way along the second. The fixes above keep each at
  two.
- `one-message`: each content slide makes one setup beat or answers one of the plan's questions,
  and each of the five backups, slides 14 to 18, answers the one question its notes open on.
  Slides 4 and 10 join two clauses in their headlines, and each pair makes a single claim: that the
  data is hard, and that fine-tuning doesn't pay. The answer slide joins the result and its limit,
  which is what an answer slide is for. Slide 3's two panes are one argument: the diagram says a
  process model's arrows are counts, and the chart beside it shows those counts moving week to
  week. Slide 11's two panes are one argument: the relevance that proves its headline, and slide
  8's error beside it, which is what makes "yet" true.
- `assertion-headline`: every headline is a full claim, written in the plan before its slide,
  including the five setup slides and the five backups, none of which is a section label.
- `never-sole-channel`: the deck has one hand-made visual, slide 3's diagram, drawn by
  `deck/components/ForecastPipeline.vue`. Its one use of color sets the forecast graph, the last
  step, apart from the observed one, and the forecast's arrows are also dashed where the observed
  graph's are solid, and its label says "forecast". In grayscale it still reads. The other steps
  differ by shape and by their labels, and the arrows between them are labeled in words. All eight
  images come from `figures.py` through the shipped archetypes, slide 11's returning figure and
  slides 8 and 14's small multiples included, and the eight tables carry no color. Slide 10's callout is the theme's component, and its text
  says what its fill marks.
- `no-script-on-slide`: the words on the slides are labels, numbers and short captions. Slides 6
  and 18 have the wordiest tables, and their cells are labels rather than sentences. Slide 10's
  callout, "Full fine-tuning on BPI 2019: from 12.3 to 23.1", is a label with its numbers, not a
  sentence to read out. Everything said aloud is in the notes, which is where build mode put each
  entry's paragraph.
- `established-terminology`, beyond the slides above: slide 6 defines both terms and uses them,
  and the captions on slides 8, 9 and 14 say "Zero-shot". Slides 9 and 15 call models by their
  own names (MOIRAI, Chronos-Bolt), which is the field's usage. "LoRA" and "fine-tuning" are the
  paper's terms, used as it uses them. The plan's other terms are on their slides beside their
  glosses, not replaced by them: slide 3's headline says "how often one step follows another" and
  its caption names the directly-follows relations; slide 5's says "repeating last week" and its
  caption names the seasonal naive forecast; slide 11's headline names entropic relevance.
- Voice: slide 6's notes say "we're not using a language model here". That names the alternative
  the plan says half the room would assume, so it's a real contrast, not a foil
  (`no-contrast-for-emphasis`).

The author applies the fix, or overrides it. The review edits nothing.
