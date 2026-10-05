# Review — skill/examples/pmf-tsfm/deck/slides.md

**PASS** — 0 errors, 1 warning.
Errors are the gate tier and block. Warnings are the advisory tier, the linter's advisories and the
judgments alike, and never block. Palette: checked against skill/template/themes/palette.json, the
palette the template stamps. Read any rule below with `legible rules <rule-id>`.

This is review mode run over the deck build mode made from [`plan.md`](plan.md), as the last step
of the build. `legible lint` reported no findings, at either severity. The judgments below were made
against the rules as `legible rules` printed them: `one-message`, `assertion-headline`,
`never-sole-channel`, `no-script-on-slide`, and the voice rules the canon decides by judgment.

## Slide 13 — "Used as they are, pre-trained forecasters beat both baselines on all four logs, so they make a strong default to build on."

- **warning** · `assertion-headline` — the headline answers the first question and leaves out the
  third, which slide 11's notes call the most interesting finding. A listener who keeps only this
  line leaves with the error result and not with "the process models are no better", which is the
  half of the answer slide's headline that tells the room what to work on next.
  **Fix:** "Used as they are, pre-trained forecasters beat both baselines on all four logs, and the
  process model is the next problem."

## What was checked and found nothing

- `one-message`: each content slide makes one setup beat or answers one of the plan's questions.
  Slides 4 and 10 join two clauses in their headlines, and each pair makes a single claim: that the
  data is hard, and that fine-tuning doesn't pay. The answer slide joins the result and its limit,
  which is what an answer slide is for.
- `assertion-headline`: every headline is a full claim, written in the plan before its slide,
  including the five setup slides, none of which is a section label.
- `never-sole-channel`: the deck has no hand-made visuals. All six charts come from `figures.py`
  through the shipped archetypes, and the four tables carry no color.
- `no-script-on-slide`: the words on the slides are labels, numbers and short captions. Slide 6's
  table is the most wordy, and its cells are labels rather than sentences. Everything said aloud is
  in the notes, which is where build mode put each entry's paragraph.
- Voice: slide 6's notes say "we're not using a language model here". That names the alternative
  the plan says half the room would assume, so it's a real contrast, not a foil
  (`no-contrast-for-emphasis`).

The author applies the fix, or overrides it. The review edits nothing.
