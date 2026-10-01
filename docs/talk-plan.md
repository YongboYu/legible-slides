# The talk plan

_Resolves part of [#36](https://github.com/YongboYu/legible-slides/issues/36)._

A talk plan is a markdown file with one entry per slide: the slide's section, its headline claim,
the evidence that proves it and where that evidence comes from, plus the talk's slot and the
questions it answers. It is where `message-before-visual` gets done: every claim is written down,
and argued over, before anything is drawn.

It sits between the paper and the deck, and the skill works on both sides of it
([`skill/SKILL.md`](../skill/SKILL.md)):

- **draft** reads a paper and its codebase and writes a plan. The author edits it, and the argument
  is settled there, where a change is a line of text rather than a slide.
- **build** stamps a deck from the template, fills each slide from its entry, draws the figures,
  and runs review mode over the result.

This file says what a plan holds. It states no rule of the method; where a plan's shape leans on
one, it names the rule by ID, and `legible rules <rule-id>` prints it.

The worked example is [`skill/examples/pmf-tsfm/`](../skill/examples/pmf-tsfm): a plan drafted from
a paper and its codebase, the deck built from it, and the review of that deck.

## The format

```markdown
---
title: The talk's title, as the cover shows it
speaker: Who gives the talk
venue: Where, and when
duration: 15min
paper: Where the paper is, a path or a link
code: Where its codebase is, a path or a link
---

# The talk's title, as the cover shows it

## Questions

1. The first question the talk answers?
2. The second?

## Slides

### 1. The talk's title, as the cover shows it

- **Layout:** cover
- **Evidence:** subtitle. The one sentence the room should leave with.
- **Time:** 30s

### 2. The result of the whole talk, written as a sentence.

- **Layout:** answer
- **Evidence:** questions. The numbered questions above.
- **Time:** 1min 30s

### 3. The claim this slide proves, written as a sentence.

- **Section:** Findings
- **Layout:** assertion-evidence
- **Evidence:** figure. What it shows, and what the reader should see in it.
- **Source:** Table 4 of the paper; `outputs/zero_shot/…` in the code.
- **Time:** 1min

What to say while it is up. This becomes the slide's speaker notes.

## Cut

- **What was left out.** And why: it was off the argument, or its evidence did not hold up.
```

### The headmatter

| Key | What |
|---|---|
| `title` | The talk's title. The cover shows it, and so does the plan's own `#` heading. |
| `speaker`, `venue` | Who gives it, where and when. They go on the cover. |
| `duration` | The slot, written the way `pace-budget` reads a deck's own `duration`. The deck's headmatter gets the same value. |
| `paper`, `code` | Where the plan was drafted from. A plan written by hand can leave them out. |

### Questions

The research questions the talk answers, numbered. The answer slide asks them and the conclusion
answers them, by the same numbers (`answer-first`, `conclusion-stays-up`), so they are written once,
here, and both slides are built from this list.

### One entry per slide

Each slide of the talk is a `###` heading, numbered in the order the deck runs, whose text is the
slide's headline, word for word. That makes the headline the first thing written for every slide,
which is the point: a slide whose claim nobody could write down is not ready to be drawn. Under it,
a list of fields:

| Field | What | When |
|---|---|---|
| **Section** | The part of the talk the slide belongs to, the label the footer shows (`section-locator`). Write it on every entry; the deck only sets it where it changes. | every content slide |
| **Layout** | The theme layout the slide uses: `cover`, `answer`, `assertion-evidence`, `two-col-evidence` or `conclusion`. | every slide |
| **Evidence** | What proves the claim: a kind, then a full stop, then what it shows. The kinds are `figure`, `table`, `equation` and `callout`, plus `subtitle`, `questions` and `answers` on the cover, the answer and the conclusion. | every slide |
| **Source** | Where the evidence comes from: a table or section of the paper, a file in the codebase, a dataset. Build mode turns these into footnotes and the references slide. | every slide that shows evidence |
| **Time** | The slide's time budget, written the way a deck's `Time:` line is. Build mode copies it into the notes, and `pace-budget` adds them up. | every slide |

Any paragraph after the fields is what to say while the slide is up. Build mode puts it in the
speaker notes, so a plan that has it is also a first draft of the script, kept off the slide
(`no-script-on-slide`).

The conclusion's evidence lists one answer per question, by number, under the field:

```markdown
- **Evidence:** answers.
  1. The answer to the first question
  2. The answer to the second
```

### Cut

What the plan left out, and why, one line each. Draft mode records here any claim from the paper
that it could not back with evidence in the sources, or that would not fit the slot. A cut written
down is one the author can overrule, and one nobody has to rediscover when the deck comes back up
for revision.

## What build mode holds itself to

A deck built from a plan matches it slide for slide: the same headlines, in the same order, on the
same layouts, in the same sections, with the same time budgets, and the plan's questions on the
answer slide and its answers on the conclusion. Backup slides, like the references, come after the
plan's entries and are not part of it. `python/tests/test_plan.py` holds the worked example to all
of that, so the format and the example cannot drift apart.
