# Review — skill/examples/pmf-tsfm/deck/slides.md

**PASS** — 0 errors, 1 warning.
Errors are the gate tier and block. Warnings are the advisory tier, the linter's advisories and the
judgments alike, and never block. Palette: checked against skill/template/themes/palette.json, the
palette the template stamps. Read any rule below with `legible rules <rule-id>`.

This is review mode run over the deck build mode made from [`plan.md`](plan.md), as the last step
of the build. `legible lint` reported no findings, at either severity. The judgments below were made
against the rules as `legible rules` printed them: `one-message`, `assertion-headline`,
`never-sole-channel`, `no-script-on-slide`, and the voice rules the canon decides by judgment.

## Slide 11 — "Pre-trained forecasters, used as they are, make a strong default for process model forecasting."

- **warning** · `concrete-over-abstract` — "a strong default" is a verdict without its number. The
  four answers below it carry the evidence, but the headline is the one line a listener keeps.
  **Fix:** "Pre-trained forecasters, used as they are, beat every baseline we tried on all four
  logs."

## What was checked and found nothing

- `one-message`: each content slide answers one of the plan's questions, or sets one up. Slides 8
  and 9 join two clauses in their headlines, and each pair answers a single question (whether
  fine-tuning helps, and which family to pick), so neither needs splitting.
- `assertion-headline`: every headline is a full claim, written in the plan before its slide.
- `never-sole-channel`: the deck has no hand-made visuals. All five charts come from `figures.py`
  through the shipped archetypes, and the three tables carry no color.
- `no-script-on-slide`: the words on the slides are labels, numbers and short captions. Everything
  said aloud is in the notes, which is where build mode put each entry's paragraph.

The author applies the fix, or overrides it. The review edits nothing.
