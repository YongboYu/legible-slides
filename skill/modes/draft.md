# Mode: draft

Write a talk plan from a paper and its codebase, in the format `docs/talk-plan.md` sets out. Read
that format first; this file names its parts. The plan is where the argument gets settled, one line
of text per slide, so it is the cheapest place for the author to change it.

## 1. Find the sources, and settle the brief

| What | Where |
|---|---|
| The paper | The LaTeX source or the PDF the author named. The source is better: its tables are text. |
| The codebase | The checkout the author named. Its outputs are where a number can be checked, and where data the paper only summarizes lives. |
| The slot, the venue, the speaker | Ask. A plan without a slot cannot be budgeted. Ask too whether questions come out of the slot or after it. |
| The audience | Ask who is in the room and what they already know: specialists in the paper's own area, the wider field, or a mixed room. It decides how much setup the talk builds, and which terms it can use undefined. |
| The takeaway | Ask what the room should leave with, or do afterwards: adopt the method, cite the result, ask for the code. The answer slide and the conclusion are written toward it. |
| The language and the room | Ask what language the talk is given in, and how big the room is. A large hall changes what the type can carry; `type-scale` says what to do about it. |
| The slide the talk rests on | Propose one from the sources: which one slide, cut, would most weaken the talk, and what would the room get wrong without it? It goes on that entry as **Load-bearing**. |
| The challenges they expect | Propose the ones the sources suggest, such as a limitation the paper states or a baseline a reviewer would ask about, and ask what is missing. Each goes under the plan's challenges. |

The brief goes in the plan's headmatter. Mark every proposal, and every item the author left
unanswered, **(assumed)**, with what in the sources it rests on: a proposal to correct costs the
author less than a blank to fill. Where the author has a deck, notes or a rehearsal from an earlier
version of the talk, quote what it says and where.

**Done when** every row above has an answer or an **(assumed)** entry.

## 2. Load the rules a plan is shaped by

```bash
legible rules message-before-visual answer-first conclusion-stays-up one-message assertion-headline
legible rules no-section-dividers section-locator pace-budget acronym-budget
legible rules signal-budget accent-is-attention motion-purpose established-terminology
```

## 3. Write the questions, then the answer

Take the questions from what the paper says it answers: its stated research questions, or the
contributions its introduction claims, at the level the plan's format sets out. Phrase each the way
the room would ask it, and under it quote the sentence the paper states it in, with its section, as
**Stated in**. A question with no sentence to quote is one the paper leaves unasked: put it under
the cuts with that reason.

Then the answer slide's entry, held to `answer-first`.

**Done when** every question carries a quote and a section, and the answer slide answers each.

## 4. Write the setup, then the findings, one entry per slide and the claim first

The setup first, beat by beat, from the paper's introduction, background and method, with the
load-bearing slide at its beat. Then the findings, question by question, each entry naming the
question it answers. Compare how many slides each question got with how much of the paper it takes
up, and say in the hand-over where they differ.

Write each entry in the order `message-before-visual` asks for, then say exactly where its evidence
is: a table or section of the paper, a file in the codebase. Evidence that is a structure or a
process (a pipeline, a model, a before and an after) is the `diagram` kind, with what it shows and
the order the room reads it in. Evidence that is numbers is a `figure` or a `table`.

The format's optional fields go where the evidence calls for them: a callout for the one number a
figure or table turns on, a reveal where the evidence arrives in steps, a figure that returns where a
later slide adds to one the room has seen, the terms each slide introduces, notes structured for
rehearsal, and an exception where a default would cost the argument. Each challenge from step 1 gets
a **Q&A** part on the slide that meets it.

Check every number against its source as you write it. Where the codebase holds the data behind a
figure, extract it into the plan's data directory with a script that says where it read from, so the
figure can be drawn again without the codebase.

**Done when** every entry has a claim, an evidence kind and a source you have checked.

## 5. Fit the slot, and sort what is left out

Give every entry a time budget and add them up against the slot, the way `pace-budget` does. Then
sort everything the talk leaves out, one item at a time:

| Goes under | When |
|---|---|
| the backups | its evidence held up when you checked it, and the room is likely to ask for it. Write it as an entry, with the question it answers as **Asked** and how long the answer takes as **Time**. |
| the cuts | it is off the argument, or its evidence could not be found or did not hold up. Write the reason. |

The challenges are where the likely questions come from: a challenge the talk meets only in Q&A,
from a table the slides leave out, is a backup to write. A backup's numbers are checked like any
slide's. Then say where each challenge is met, by the backup's number where one meets it.

**Done when** the budgets fit the slot by `pace-budget`, and every challenge names where it is met.

## 6. Hand the plan over, and stop

Open the hand-over with every item still marked **(assumed)**, so the author corrects those first.
The plan is the author's argument: the next step is theirs, and build starts from the plan once they
have read it.
