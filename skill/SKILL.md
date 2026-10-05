---
name: legible-slides
description: Slidev talks to the legible-slides method. Use to turn a paper into a talk plan, build a deck from a plan, start a new deck, or review a deck before it is presented or merged.
---

# legible-slides

This skill is a **procedure**. The method's rules and every number they turn on live once, in the
**canon** at `docs/method.md` in a checkout of legible-slides, and this skill reaches them by rule ID
through `legible rules <rule-id>`, which prints the canon's own words. Work from what it prints.
If it exits 2, the ID has moved in the canon: say so and stop, because a run that quietly loaded
fewer rules finds fewer faults.

## Pick the mode, then read its file

| The author has | Mode | Read |
|---|---|---|
| a paper and its codebase, and wants a talk | **draft**: write a talk plan for the author to edit | [`modes/draft.md`](modes/draft.md) |
| a talk plan the author has read | **build**: turn it into a deck, then review it | [`modes/build.md`](modes/build.md) |
| nothing yet, and wants a deck to write into | **scaffold**: stamp a new deck, checks wired | [`modes/scaffold.md`](modes/scaffold.md) |
| a deck | **review**: say what breaks and how to fix it | [`modes/review.md`](modes/review.md) |

Review is the acceptance bar for the other three: build and scaffold both end by running it. The
talk plan joins draft to build, and its format is `docs/talk-plan.md` in the same checkout. The
worked example of draft, build and review on one real paper is `skill/examples/pmf-tsfm/`.

## Two verdicts

Every review reports two, and keeps them apart:

- The **gate** is `legible lint`'s exit code: whether anything a script checks is broken. Errors
  come only from it, and only it blocks.
- **Readiness** is the review's judgment: whether the deck, rendered, shows what it should and every
  finding has been weighed. It never blocks, and it is never written as PASS.

`docs/agent-skill-contract.md` §4c lists, rule by rule, which of the two covers it.

## Posture

**Flag and suggest; the author applies.** Every finding carries a fix, and review edits a deck only
where the author accepts a fix, that fix alone. Draft proposes an argument and the author settles it
in the plan. Build writes exactly what the plan says, word for word. The author decides what each
slide is for; the skill holds the deck to the method.

The scripts own the arithmetic: `legible lint` counts, and `cvd-validate`, through it, measures
colour. Take their findings verbatim.
