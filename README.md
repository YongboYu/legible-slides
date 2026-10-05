# legible-slides

**Slides that stay readable — from the back row, and for every pair of eyes.**

> **Status: charting.** This repo is being planned with [`/wayfinder`](https://github.com/mattpocock/skills).
> The map and its open questions live in [GitHub Issues](../../issues?q=label%3Awayfinder%3Amap).
> Nothing here is settled until its ticket is closed.

---

## Why

Most presentation templates give you *files* — a colour scheme, some layouts, a font pairing. They
leave the hard part to you: deciding what any given slide is actually **for**.

They also quietly fail two audiences. The person in the back row, who cannot read the 14px caption
a template shrank to fit. And the roughly 1 in 12 men and 1 in 200 women with a colour vision
deficiency, for whom the average "nice palette" collapses into indistinguishable mud the moment it
becomes a five-line chart.

`legible-slides` is the opposite bet: a small amount of **method**, verified against both of those
failure modes, delivered as a Slidev theme.

## What

Three things, in order of how much they matter:

1. **A method.** A short set of rules about what a slide is *for*, built on Assertion-Evidence
   (Alley & Neeley) and the cognitive-load research underneath it. They live in
   [`docs/method.md`](docs/method.md) — the canon, and the only place any of them is stated. The
   ones a script can settle are settled by one (`legible lint`), reproducibly and in CI.
2. **A verified accessibility floor.** A type scale stated for the rooms it suits, with a floor no
   text goes under, and a colour-vision-deficiency validator you can run against *your* palette —
   not just a promise that ours passes.
3. **A Slidev theme** that carries the method, and a skill so a coding agent can build to this
   standard on your behalf.

### One palette, in one file

The theme is `leuven-blue`, one palette file in [`themes/`](themes) that passes the validator. It is
the author's own template for academic talks, and it ships no institution's marks: the cover's venue
and affiliation slots show placeholder logos until a deck points them at its own files.

> **Note:** the palette is inspired by KU Leuven's house colours. It is not affiliated with or
> endorsed by the university.

Editing that one file recolours the whole deck. The same Python that validates a palette also emits
its CSS custom properties (`legible gen-css`), so the token schema is understood in one language
and no second copy of it can drift. The generated stylesheet is committed and CI checks it against
its palette — which is why building a deck needs no Python at all.

Charts are regenerated from data rather than redrawn, so a recolour reaches them too. There are two
chart shapes, deliberately — the multi-series comparison, where every line gets a dash and a marker
of its own because colour is never allowed to be the only channel, and the headline chart, where a
de-emphasised comparison stands against one highlight. Either can render itself as a
colour-vision deficiency sees it, using the validator's own simulation. See
[`python/README.md`](python/README.md#the-figure-helper).

## Running the floor

The validator is a command with an exit code, so the accessibility claim is evidence rather than a
promise — including for a palette this project has never seen:

```bash
uv tool install "git+https://github.com/YongboYu/legible-slides#subdirectory=python"
cvd-validate my-theme.json
```

It names each failing pair by role rather than by hex, prints the achieved minimum even when you
pass — so you can see whether you have headroom — and exits non-zero if any pair falls below the
floor, or an attention or text pairing falls short of its contrast (`accent-is-attention`,
`decorative-neutral-never-text`). See
[`python/README.md`](python/README.md).

Inside this repo the same command gates CI over the theme in [`themes/`](themes) on push and pull
request: a palette that fails cannot merge. The hook in `.pre-commit-config.yaml` runs it locally and
is opt-in, because enforcement belongs somewhere nobody can skip. Your own palettes are yours — the
command is offered, not imposed.

## Running the method

Bullet ceilings, word ceilings, em-dashes in a headline, inflated register and monotonous sentence
openers are all decidable, so a script decides them rather than a reader:

```bash
legible lint deck/slides.md --theme themes/leuven-blue.json
```

Findings arrive grouped by slide and named by the rule they enforce, which is what makes one
possible to look up and disagree with. Every threshold comes out of `docs/method.md` at import, so
changing a rule there changes what the command enforces and nothing here holds a second copy of the
number. The palette check is the validator above, shelled out to: there is exactly one
implementation of the simulation in this project, and the linter is deliberately not it. See
[`python/README.md`](python/README.md#legible-lint).

What is left is judgment — whether a slide carries one message, whether its headline is a claim —
and judgment stays with a reader, or with the coding-agent skill that reviews on your behalf.

## Starting and reviewing with a coding agent

[`skill/`](skill) is that skill, and it has four modes.

**draft** reads a paper and its codebase and writes a [talk plan](docs/talk-plan.md): the
questions the paper says it answers, a setup that makes the case for them, then one entry per
slide with its headline claim, its evidence and where that comes from. You edit the plan, which is the cheap place to change an argument. **build**
turns the plan into a deck on the template, draws its figures from data, and hands it over with a
review. [`skill/examples/pmf-tsfm/`](skill/examples/pmf-tsfm) is both, run on a real paper.

**review** runs the linter for everything a script settles, loads the rules that need reading
straight from the canon (`legible rules`), and reports both halves as one review, grouped per slide,
with a proposed fix on every finding. The two halves keep different authority: the mechanical one
has an exit code and blocks, the judgments are advisory and never do. And it flags rather than
edits — it can hold a deck to a structure, but deciding your message stays yours.

**scaffold** stamps a new deck already wired to the theme, to a palette that clears the floor, and
to both checks, with one skeleton slide per layout to fill in. It is lean on purpose — a correct
starting point, not a second flagship — and it hands the deck over having run the review over it,
so a deck is review-ready from slide one rather than retrofitted at the end. It stamps a copy of
the `leuven-blue` palette, which the deck is free to edit.

No mode states a rule of its own, which is what stops a review drifting from the method it
claims to enforce. See [`skill/README.md`](skill/README.md).

## Presenting with Slidev

[`theme/`](theme) is `slidev-theme-legible`, the method as machinery: six layouts, among them an
opening answer and a closing conclusion, the persistent chrome that carries orientation so no slide
has to be spent on navigation, and styles that read nothing but the generated palette. Both typefaces are bundled, so a deck renders in the family it was
designed in on a lecture-room laptop with no network — and in the same one the figures were drawn in.

What it refuses is as much the point. There is no section-divider, no opener, no closer and no
single-word-emphasis layout, because the method forbids the slides they build.

A deck stamped by the skill carries its own copy of it, taken from one commit of this repo, with its
checks pinned to that same commit, so it builds from a clean clone. See
[`theme/README.md`](theme/README.md), and
[`theme/example.md`](theme/example.md) for every layout exercised once.

[`deck/`](deck) is the flagship: the deck that teaches the method by being it, and the artifact to
read if you would rather see the rules applied than read them. It runs the fourteen beats the canon
outlines, plus a references slide, and is built and linted in CI. See
[`deck/README.md`](deck/README.md).

A green lint is the gate, not a verdict on the deck: what the scripts cover, rule by rule, and what
they leave to a reader of the rendered pages, is
[`docs/agent-skill-contract.md`](docs/agent-skill-contract.md) §4c.

## Provenance

This is not a greenfield idea. It is an extraction from a deck that shipped: the CAiSE 2026
presentation of [`pmf-tsfm`](https://github.com/YongboYu/pmf-tsfm). The layouts, the token
architecture, the CVD verification and the figure pipeline were all built and argued out there,
across a long trail of issues and PRs.

See [`docs/design-provenance.md`](docs/design-provenance.md) for what was decided, and why.

## License

MIT — see [LICENSE](LICENSE).
