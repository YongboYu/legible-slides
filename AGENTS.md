# legible-slides

A presentation template that is a **method** first, files second: one message per slide,
Assertion-Evidence structure, a CVD-verified colour system, and a type scale tuned for the back of
a lecture hall. Delivered for PowerPoint, Keynote, Google Slides, Slidev — and as a skill for coding
agents.

Extracted from the CAiSE 2026 deck in
[`YongboYu/pmf-tsfm`](https://github.com/YongboYu/pmf-tsfm); see
[`docs/design-provenance.md`](docs/design-provenance.md) for the decisions and their sources.

## Status

Being planned with `/wayfinder`. The map and open questions are GitHub issues labelled
`wayfinder:map` / `wayfinder:*`. Structure below is provisional until its ticket closes.

## First principles (non-negotiable, inherited from the source deck)

- **Every slide answers exactly one question.** If you can't state it, the slide is wrong.
- **The headline is the claim.** Assertion-Evidence (Alley & Neeley): sentence headline, then the
  evidence that proves it. No separate "takeaway" strip.
- **Decide the message before the visual.** Never reach for a chart and then caption it.
- **Use established terms as-is.** If a word is standard, don't rephrase it — audiences shouldn't
  have to guess.
- **Legibility floor is real.** Body type is sized for the back row on a projector, not the laptop.
- **Colour must survive CVD + grayscale**, and never be the sole channel (pair with dash/marker/label).
- Max 5 bullets per slide; max 12 words per bullet. Animations ≤15s and purposeful.

## Agent skills

### Issue tracker

Issues live in this repo's GitHub Issues, via the `gh` CLI. See `docs/agents/issue-tracker.md`.

### Domain docs

Single-context: one `CONTEXT.md` + `docs/adr/` at the repo root. See `docs/agents/domain.md`.
