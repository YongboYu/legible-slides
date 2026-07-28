# legible-slides

A presentation template that is a **method** first, files second: a short set of rules about what a
slide is for, an accessibility floor anyone can re-run against their own palette, and deliveries for
PowerPoint, Keynote, Google Slides and Slidev — plus a skill for coding agents. The rules are in
[`docs/method.md`](docs/method.md).

Extracted from the CAiSE 2026 deck in
[`YongboYu/pmf-tsfm`](https://github.com/YongboYu/pmf-tsfm); see
[`docs/design-provenance.md`](docs/design-provenance.md) for the decisions and their sources.

## Status

Being planned with `/wayfinder`. The map and open questions are GitHub issues labelled
`wayfinder:map` / `wayfinder:*`. Structure below is provisional until its ticket closes.

## The method

Every rule of the method — and every number it turns on — lives in
[`docs/method.md`](docs/method.md). That file is the single source of truth. **Read it before
writing a slide, a layout, a palette or a check, and quote its thresholds rather than re-deriving
them.**

Nothing else in this repo restates a rule. If you need one somewhere, name it by its rule ID
(`one-message`, `separation-floor`, `bullet-ceiling`, …) so a rule change can never leave a copy
behind. Where the rules came from is [`docs/design-provenance.md`](docs/design-provenance.md);
how an agent stamps a deck to them and turns them into a review is
[`docs/agent-skill-contract.md`](docs/agent-skill-contract.md), and the skill that does both is
[`skill/SKILL.md`](skill/SKILL.md) — which states no rule either, and loads them with
`legible rules` at review time. What it stamps is [`skill/template/`](skill/template), and that
states none either: it names rules by ID, like everything else here.

## Agent skills

### Issue tracker

Issues live in this repo's GitHub Issues, via the `gh` CLI. See `docs/agents/issue-tracker.md`.

### Domain docs

Single-context: one `CONTEXT.md` + `docs/adr/` at the repo root. See `docs/agents/domain.md`.
