# The coding-agent skill

[`SKILL.md`](SKILL.md) is a [Claude Code](https://claude.com/claude-code) skill that holds a Slidev
deck to the method. It turns the rules from prose an author has to remember into checks something
runs, and reports what breaks, per slide, with a fix for each. It can also take a talk from a paper
to a deck, by way of a plan the author edits.

Four modes, and review is the acceptance bar for the other three:

- **draft** — read a paper and its codebase, and write a [talk plan](../docs/talk-plan.md): one
  entry per slide, with its section, its headline claim, and its evidence and where that comes from.
- **build** — turn a talk plan into a deck: scaffold it, fill each slide from its entry, draw the
  figures, and review the result.
- **scaffold** — stamp a new deck, wired to the theme, its palette and both checks, from
  [`template/`](template). Review-ready from slide one rather than retrofitted at the end.
- **review** — check a deck that exists, and say what breaks and how to fix it.

## Installing it

The skill is one directory. Copy or link it where your agent looks for skills — beside a project,
or once for every project you open:

```bash
ln -s "$PWD/skill" ~/.claude/skills/legible-slides          # yours, everywhere
ln -s "$PWD/skill" path/to/deck/.claude/skills/legible-slides   # one project's
```

It needs the commands it delegates to, which is the whole `legible` package
([`python/README.md`](../python/README.md)):

```bash
uv tool install "git+https://github.com/YongboYu/legible-slides#subdirectory=python"
```

That install carries the canon with it, so the skill reads the rules it reviews against on a machine
with no checkout of this repo.

## What scaffold does

Copies [`template/`](template) — one skeleton slide per layout the theme ships, a palette that
clears the accessibility floor, the stylesheet generated from it, and both checks wired as a
pre-commit hook and a workflow. Then it fills in the blanks the author named, regenerates the
stylesheet if the palette changed, builds, and **runs review mode over what it stamped**.

That last step is the point. The acceptance bar for the scaffold is the review, so a stamped deck
carrying an error is a bug in the template rather than in anybody's talk — which is what "correct
starting point" has to mean if it is to mean anything.

It is deliberately **lean**: a clean start, not a worked deck. The teaching artifact is
[the flagship](../deck), and a second one here would be a second thing to keep true. It stamps a
copy of the project's one palette, `leuven-blue`, and the cover's two logo slots show placeholders: no
institution's mark ships, so the author points the cover at their own.

## What draft and build do

Draft reads the paper for the argument and the codebase for the numbers, and asks the author for
what neither says: the slide the talk rests on, and the challenges they expect. It writes a plan: the
questions the talk answers, taken from the paper's stated research questions or contributions and
quoting where; a setup that makes the case for the problem and the approach; then the findings,
question by question. Every entry is one slide, its headline written before its evidence is picked
(`message-before-visual`). Every number is checked against its source as it goes in, and
whatever didn't fit the slot, or didn't hold up, is listed under the plan's cuts with the reason.
Then it stops. The author edits the plan, and that's where the argument gets settled, because
changing a line is cheaper than redrawing a slide.

Build stamps the template and fills each slide from its entry: the headline word for word, the
layout, the section, the evidence, footnotes for the sources, and the notes. It draws every chart
from data with the figure helper, builds the deck, and runs review mode over it. The report goes to
the author with the deck. An error is fixed as part of the build; a warning is left for the author.

[`examples/pmf-tsfm/`](examples/pmf-tsfm) is both modes run end to end on a real paper, with the
review attached, and `python/tests/test_plan.py` holds the deck to its plan.

## What review does

Four steps, in order: find the deck, its palette and its generated figures; run `legible lint` for
everything a script settles; load the rules that need judgment with `legible rules`; read the deck
against them. The result is one report, grouped per slide, each finding tagged and named by the
rule it enforces.

**The two halves carry different authority.** The mechanical half has an exit code, runs in CI, and
blocks. The judgments are advisory, because a reading of a slide is fallible in a way a bullet count
is not — they never gate.

**It flags and suggests; you apply.** Every finding arrives with a proposed fix, and the skill edits
nothing on its own. It can hold a deck to a structure. It cannot decide your message for you.

## What it does not carry

Not one rule of the method, and not one threshold. Rules live in
[`docs/method.md`](../docs/method.md), and the skill loads them at review time:

```bash
legible rules one-message assertion-headline never-sole-channel
legible rules --section voice --decided-by judgment
```

Editing a rule there changes what a review finds, with nothing edited here — and the second command
asks the canon which rules a section holds rather than naming them, so a rule added to it is
reviewed from the moment it is written. `python/tests/test_skill.py` holds `SKILL.md` to that: a
rule's statement, a threshold's name or one of the canon's numbers, copied into it, fails the suite.

The template says no rule either. It names them by ID where an author needs to look one up, the way
every other file in this project does.

## Trying it

[`fixtures/non-compliant.md`](fixtures/non-compliant.md) is a deck built to fail, and
[`fixtures/README.md`](fixtures/README.md) is the answer key: every planted violation, by slide and
by rule, and which half of the review is expected to surface it.

The other direction is the template, which is built to pass — `python/tests/test_scaffold.py` runs
the linter over it and fails if a stamped deck would arrive carrying an error, which is the
acceptance bar as something that runs rather than something asserted. The same suite holds the
template to the theme's layouts, to the palette it copies, and to the stylesheet that palette emits,
so a deck stamped a year from now is stamped from files nothing has drifted underneath.
