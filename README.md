# legible-slides

**Slides that stay readable — from the back row, and for every pair of eyes.**

> **Status: charting.** This repo is being planned with [`/wayfinder`](https://github.com/mattpocock/skills).
> The map and its open questions live in [GitHub Issues](../../issues?q=label%3Awayfinder%3Amap).
> Nothing here is settled until its ticket is closed.

---

## Why

Most presentation templates give you *files* — a colour scheme, some layouts, a font pairing. They
leave the hard part to you: deciding what any given slide is actually **for**.

They also quietly fail two audiences. The person in the back row of a lecture hall, who cannot read
20px body text off a projector. And the roughly 1 in 12 men and 1 in 200 women with a colour vision
deficiency, for whom the average "nice palette" collapses into indistinguishable mud the moment it
becomes a five-line chart.

`legible-slides` is the opposite bet: a small amount of **method**, verified against both of those
failure modes, delivered in whatever tool you already present with.

## What

Three things, in order of how much they matter:

1. **A method.** A short set of rules about what a slide is *for*, built on Assertion-Evidence
   (Alley & Neeley) and the cognitive-load research underneath it. They live in
   [`docs/method.md`](docs/method.md) — the canon, and the only place any of them is stated. The
   ones a script can settle are settled by one (`legible lint`), reproducibly and in CI.
2. **A verified accessibility floor.** A type scale tuned for real projection distance, and a
   colour-vision-deficiency validator you can run against *your* palette — not just a promise that
   ours passes.
3. **Deliveries** for the tools people actually use: PowerPoint, Keynote, Google Slides, Slidev —
   and a skill so a coding agent can build to this standard on your behalf.

### Brand as a layer, not a hard-coding

The method is brand-neutral. A palette is a swappable theme file that must pass the validator.
KU Leuven ships as the default, worked, already-verified reference theme — because a template that
proves itself on one real brand is worth more than one that proves itself on lorem ipsum.

> **Note:** the KU Leuven theme is derived from the university's house style for use by its own
> researchers. This project is not an official KU Leuven product and carries no endorsement.

Editing that one file recolours the whole deck. The same Python that validates a palette also emits
its CSS custom properties (`legible gen-css`), so the token schema is understood in one language
and no second copy of it can drift. The generated stylesheet is committed and CI checks it against
its palette — which is why building a deck needs no Python at all.

Charts are regenerated from data rather than redrawn, so the swap reaches them too. There are two
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
floor. See [`python/README.md`](python/README.md).

Inside this repo the same command gates CI over every theme in [`themes/`](themes) on push and pull
request: a palette that fails cannot merge. The hook in `.pre-commit-config.yaml` runs it locally and
is opt-in, because enforcement belongs somewhere nobody can skip. Your own themes are yours — the
command is offered, not imposed.

## Running the method

Bullet ceilings, word ceilings, em-dashes in a headline, inflated register and monotonous sentence
openers are all decidable, so a script decides them rather than a reader:

```bash
legible lint deck/slides.md --theme themes/kuleuven.json
```

Findings arrive grouped by slide and named by the rule they enforce, which is what makes one
possible to look up and disagree with. Every threshold comes out of `docs/method.md` at import, so
changing a rule there changes what the command enforces and nothing here holds a second copy of the
number. The palette check is the validator above, shelled out to: there is exactly one
implementation of the simulation in this project, and the linter is deliberately not it. See
[`python/README.md`](python/README.md#legible-lint).

What is left is judgment — whether a slide carries one message, whether its headline is a claim —
and judgment stays with a reader, or with the coding-agent skill that reviews on your behalf.

## Provenance

This is not a greenfield idea. It is an extraction from a deck that shipped: the CAiSE 2026
presentation of [`pmf-tsfm`](https://github.com/YongboYu/pmf-tsfm). The layouts, the token
architecture, the CVD verification and the figure pipeline were all built and argued out there,
across a long trail of issues and PRs.

See [`docs/design-provenance.md`](docs/design-provenance.md) for what was decided, and why.

## License

MIT — see [LICENSE](LICENSE).
