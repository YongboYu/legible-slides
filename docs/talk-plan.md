# The talk plan

_Resolves part of [#36](https://github.com/YongboYu/legible-slides/issues/36); the questions'
sources, the setup part and the author's answers are
[#38](https://github.com/YongboYu/legible-slides/issues/38)'s, the optional fields are
[#39](https://github.com/YongboYu/legible-slides/issues/39)'s, and the backups are
[#40](https://github.com/YongboYu/legible-slides/issues/40)'s._

A talk plan is a markdown file with one entry per slide: the slide's section, its headline claim,
the evidence that proves it and where that evidence comes from, plus the talk's slot, the
questions it answers and where the paper states them, the backups held for questions from the
room, and the challenges the author expects. It is where `message-before-visual` gets done: every
claim is written down, and argued over, before anything is drawn.

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

1. The first question the talk answers, the way the room would ask it?
   - **Stated in:** Section 1, the contributions: "the paper's own sentence that states it".
2. The second?
   - **Stated in:** Section 4.1: "…".

## Slides

### 1. The talk's title, as the cover shows it

- **Layout:** cover
- **Evidence:** subtitle. The one sentence the room should leave with.
- **Time:** 30s

### 2. The result of the whole talk, written as a sentence.

- **Layout:** answer
- **Evidence:** questions. The numbered questions above.
- **Time:** 1min 30s

### 3. Why the problem matters, written as a claim.

- **Section:** Problem
- **Setup:** stakes
- **Layout:** assertion-evidence
- **Evidence:** figure. What it shows, and what the reader should see in it.
- **Source:** Section 1 of the paper; `data/…` in the code.
- **Time:** 1min

What to say while it is up. This becomes the slide's speaker notes.

### 4. What makes the problem hard, written as a claim.

- **Section:** Problem
- **Setup:** difficulty
- …

### 5. Where existing work falls short, written as a claim.

- **Section:** Problem
- **Setup:** gap
- …

### 6. Why the approach should close the gap, written as a claim.

- **Section:** Approach
- **Setup:** approach
- **Load-bearing:** What the room gets wrong if this slide is cut, in the author's words.
- **Layout:** assertion-evidence
- **Evidence:** table. …
- **Source:** Table 1 of the paper.
- **Time:** 1min

### 7. The claim this slide proves, written as a sentence.

- **Section:** Findings
- **Answers:** 1
- **Layout:** assertion-evidence
- **Evidence:** figure. What it shows, and what the reader should see in it.
- **Source:** Table 4 of the paper; `outputs/zero_shot/…` in the code.
- **Callout:** The number the evidence turns on, as the box shows it.
- **Time:** 1min

### 8. The claim this slide proves, written as a sentence.

- **Section:** Findings
- **Answers:** 1
- **Layout:** two-col-evidence
- **Evidence:** figure. What it shows, and what the reader should see in it.
- **Source:** Table 7 of the paper.
- **Returns:** Slide 7, beside the new figure, so the room sees both results at once.
- **Reveal:** slide 7's figure, after the new one.
- **Terms:** a term this slide introduces, another
- **Time:** 1min
- **Notes:**
  - **Question:** The question this slide answers, the way the room would ask it?
  - **In:** The line that takes the room here from the slide before.
  - **Out:** The line that hands over to the slide after.
  - **Q&A:** The question the author expects here, and the answer, with its source.

## Backup

### 9. The claim this backup proves, written as a sentence.

- **Asked:** The question it answers, the way the room would ask it?
- **Layout:** assertion-evidence
- **Evidence:** table. …
- **Source:** Table 5 of the paper.

## Challenges

- **The pushback the author expects.** Where the talk meets it: Slide 6, or Slide 9 in Q&A.

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

They are the paper's questions, not ones read off its tables. Each is phrased the way the room
would ask it, and carries one field, indented under it:

| Field | What |
|---|---|
| **Stated in** | The section of the paper that states the question, as `Section N`, and the paper's own sentence, quoted. |

A paper may state its questions at two levels: the contributions its introduction claims, and the
narrower questions its experiments are designed around. The talk's questions are the level the
abstract argues at, and the narrower ones become the evidence under them. A question no section of
the paper states is one the paper does not answer, so it does not belong here.

### One entry per slide

Each slide of the talk is a `###` heading, numbered in the order the deck runs, whose text is the
slide's headline, word for word. That makes the headline the first thing written for every slide,
which is the point: a slide whose claim nobody could write down is not ready to be drawn. Under it,
a list of fields:

| Field | What | When |
|---|---|---|
| **Section** | The part of the talk the slide belongs to, the label the footer shows (`section-locator`). Write it on every entry; the deck only sets it where it changes. | every content slide |
| **Setup** | The beat of the setup the slide makes: `stakes`, `difficulty`, `gap` or `approach`. | every slide of the setup |
| **Answers** | The number of the question the slide answers. | every slide of the findings |
| **Load-bearing** | What the room gets wrong if this slide is cut, as the author put it. | the one slide the author says carries the talk |
| **Layout** | The theme layout the slide uses: `cover`, `answer`, `assertion-evidence`, `two-col-evidence` or `conclusion`. | every slide |
| **Evidence** | What proves the claim: a kind, then a full stop, then what it shows. The kinds are `figure`, `table`, `equation` and `callout`, plus `subtitle`, `questions` and `answers` on the cover, the answer and the conclusion. | every slide |
| **Source** | Where the evidence comes from: a table or section of the paper, a file in the codebase, a dataset. Build mode turns these into footnotes and the references slide. | every slide that shows evidence |
| **Time** | The slide's time budget, written the way a deck's `Time:` line is. Build mode copies it into the notes, and `pace-budget` adds them up. | every slide |

Any paragraph after the fields is what to say while the slide is up. Build mode puts it in the
speaker notes, so a plan that has it is also a first draft of the script, kept off the slide
(`no-script-on-slide`).

### Optional fields

An entry can carry five more fields, each where its evidence calls for it and nowhere else. Draft
mode fills them as it writes the entry; build mode puts each one on the slide, and leaves it off
where the entry does. Each is held to the rules the table names: the linter's advisories check the
ones decided by script, and review mode reads the slide for the rest.

| Field | What | Held to |
|---|---|---|
| **Callout** | The text of a box set over or beside the evidence: the number it turns on, or the definition it leans on. | `signal-budget`, `accent-is-attention` |
| **Reveal** | What each click adds, in order, separated by semicolons: one step per click. | `motion-purpose` |
| **Returns** | The figure brought back from an earlier slide, as `Slide N`, then what is added to it here. The figure is the same chart the room saw, redrawn for its pane at most. | `one-message` |
| **Terms** | The terms the slide introduces and later slides lean on, separated by commas. Each is spelled the way the field spells it, shown on the slide, and introduced on one entry only. | `established-terminology`, `acronym-budget` |
| **Notes** | Speaker notes as a rehearsal script, in parts indented under it (below). | `no-script-on-slide` |

A callout takes its height from the pane it sits in, so under a figure that fills the pane it
shrinks the figure, and the figure's type with it (`type-scale`). It fits beside a table, or in a
column of its own.

**Notes** has four parts, each one line, in this order, and an entry gives the ones it needs:

| Part | What |
|---|---|
| **Question** | The question the slide answers, the way the room would ask it (`one-message`). |
| **In** | The line that takes the room here from the slide before. The first slide of a section has its signpost instead (`section-locator`), so it leaves this out. |
| **Out** | The line that hands over to the slide after. |
| **Q&A** | The pushback the author expects while this slide is up, and the answer, with its source. A challenge the plan says this slide meets is answered here. |

The paragraph after the fields stays what it was: what to say while the slide is up. **Notes**
adds the parts a rehearsal needs around it.

### The setup, then the findings

The content slides fall in two parts, in this order, and the slides that are neither, like how the
experiment was run, sit between them or among the findings.

**The setup** makes the case that the question is worth asking and the approach worth trying,
before any result is shown. It is what makes the results land: a finding the room has no stake in
is a number. It makes four beats, each on one slide or more, in this order:

| Beat | What its slides claim |
|---|---|
| `stakes` | why the problem matters, and to whom |
| `difficulty` | what makes it hard: the data, the scale, the shape of the problem |
| `gap` | where existing work falls short of it, with evidence rather than a citation alone |
| `approach` | why the approach should close that gap, before the room sees whether it does |

The setup comes after the answer slide, because the answer comes first (`answer-first`), and every
setup slide is a claim with its evidence like any other (`assertion-headline`), not a section
divider (`no-section-dividers`).

**The findings** answer the questions, in their order. Each slide names the question it answers,
every question has at least one, and the conclusion then answers them by the same numbers. A
question the plan gives one slide is a question the talk treats as minor; that is a choice to make
in the plan, where it shows.

### The conclusion

The conclusion's evidence lists one answer per question, by number, under the field:

```markdown
- **Evidence:** answers.
  1. The answer to the first question
  2. The answer to the second
```

### The slide the talk rests on

Two things in a plan only the author knows, and draft mode asks for both rather than guess. The
first is the slide that, cut, would most weaken the talk, usually because the room would get
something basic wrong without it. Its entry carries **Load-bearing**, with what the room would get
wrong, and exactly one entry does.

### Backup

The slides held for questions after the talk, shown only if someone asks. Each is an entry like the
talk's, numbered on from the conclusion, because that is where the deck puts it: its headline is a
claim, and it carries **Layout**, **Evidence** and **Source**, and any of the optional fields but
**Terms**, since a term the talk leans on is introduced in the talk. It does not carry **Time**,
because a backup is not part of the slot (`pace-budget`), nor **Section**, **Setup**, **Answers** or
**Load-bearing**, because it is not part of the argument. In their place, one field:

| Field | What |
|---|---|
| **Asked** | The question the backup answers, the way the room would ask it. It is the reason the slide exists, so a backup nobody would ask for is a cut. |

A backup comes from the cuts. Something left out of the talk whose evidence held up, and that the
room is likely to ask about, moves here; the challenges the author expects are the first place to
look for those questions. Something off the argument, or whose evidence did not hold up, stays
under **Cut**: a backup has to survive a question, so one whose evidence would not is worse than
none.

### Challenges

The second is what the author expects the room to push back on. One line each: the challenge in
bold, then where the talk meets it, by slide number, or the source the answer comes from in Q&A. A
challenge no slide and no source meets is one to settle before the talk, not during it.

### Cut

What the plan left out, and why, one line each: what was cut, in bold, then the reason. Draft mode
records here any claim from the paper that it could not back with evidence in the sources, or that
was off the argument. A claim that held up but did not fit the slot is a backup instead, if the
room is likely to ask for it. A cut written down is one the author can overrule, and one nobody has
to rediscover when the deck comes back up for revision.

## What build mode holds itself to

A deck built from a plan matches it slide for slide: the same headlines, in the same order, on the
same layouts, in the same sections, with the same time budgets, and the plan's questions on the
answer slide and its answers on the conclusion. Where an entry carries an optional field, its slide
shows it: the callout's text in its one callout, one click per step of the reveal, the returning
figure drawn by the chart its first slide shows, every term on the slide, and the notes' parts in
its speaker notes, in order. After the conclusion come the plan's backups, one slide per entry, in
order, under a backup section the first of them declares, each with its question at the head of its
notes and no time budget; then the references, which no entry plans. `python/tests/test_plan.py`
holds the worked example to all of that, so the format and the example cannot drift apart.
