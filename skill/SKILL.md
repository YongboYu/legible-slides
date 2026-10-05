---
name: legible-slides
description: Plan a talk from a paper and its codebase, build a Slidev deck from that plan, start a blank deck to the legible-slides method, or review an existing one against it — the mechanical gate a script settles, plus the judgments it cannot. Use when asked to turn a paper into a talk or a talk plan, build slides from a plan, scaffold or start a deck to the method, review a deck, check slides against the method, or vet a deck before it is presented or merged.
---

# legible-slides

This file is a **procedure**, not a rulebook. It states no rule of the method and no threshold,
because the method is stated once, in the canon at `docs/method.md`, and a second copy is a second
thing to keep true. What is here is the order to work in, which checks a script settles and which
need reading, and what the report looks like.

Rules are **loaded from the canon at review time** (review, step 3). A rule edited there changes
this review with nothing edited here.

Four modes. Review is the acceptance bar for the other three, and a talk plan is what joins the
first two:

- **draft** — read a paper and its codebase, and write a talk plan for the author to edit.
- **build** — turn a talk plan into a deck: scaffold it, fill every slide from the plan, review it.
- **scaffold** — start a new deck, method-compliant before a word of it is written.
- **review** — check a deck that exists, and say what breaks and how to fix it.

The talk plan's format is `docs/talk-plan.md` in the checkout of legible-slides. Read it before
drafting a plan or building from one; this file names its parts and does not restate them. The
worked example is `skill/examples/pmf-tsfm/`: a plan drafted from a paper and its code, the deck
built from it, and the review of that deck.

## Mode: draft

Write a talk plan from a paper and its codebase. The plan is where the argument gets settled, one
line of text per slide, so it is the cheapest place for the author to change it.

### 1. Find the sources, and ask for what they do not say

| What | Where |
|---|---|
| The paper | The LaTeX source or the PDF the author named. The source is better: its tables are text. |
| The codebase | The checkout the author named. Its outputs are where a number can be checked, and where data the paper only summarizes lives. |
| The slot, the venue, the speaker | Ask. A plan without a slot cannot be budgeted. |
| The slide the talk rests on | Ask: which one slide, cut, would most weaken the talk, and what would the room get wrong without it? It goes on that entry as **Load-bearing**. |
| The challenges they expect | Ask: what will the room push back on? Each goes under the plan's challenges, with where the talk meets it. |

The last two are the author's to answer, and no paper says them. If the author has a deck, notes or
a rehearsal from an earlier version of the talk, those may already say; quote them, and say where
you read them.

### 2. Load the rules a plan is shaped by

```bash
legible rules message-before-visual answer-first conclusion-stays-up one-message assertion-headline
legible rules no-section-dividers section-locator pace-budget acronym-budget
legible rules signal-budget accent-is-attention motion-purpose established-terminology
```

As in review mode: work from what these print, not from memory of them, and stop if one exits 2.

### 3. Write the questions, then the answer

Take the questions from what the paper says it answers: its stated research questions, or the
contributions its introduction claims, at the level the plan's format sets out.

Phrase each the way the room would ask it, and under it quote the sentence the paper states it in,
with its section, as the format's **Stated in**. A question you cannot quote is one the paper does
not ask; leave it out, or say why under the cuts.

Then the answer slide's entry, held to `answer-first` as step 2 printed it.

### 4. Write the setup, then the findings, one entry per slide and the claim first

Write the format's setup part first, beat by beat, from the paper's introduction, background and
method, and put the author's load-bearing slide where its beat is. Then the findings, question by
question, each entry naming the question it answers. Before going on, compare how many slides each
question got with how much of the paper it takes up, and say in the hand-over where they differ.

For every entry, write it in the order `message-before-visual` asks for, and then say exactly where
its evidence is: a table or section of the paper, a file in the codebase.

Then the format's optional fields, where the evidence calls for them and nowhere else: a callout
for the one number a figure or a table turns on, a reveal where the evidence arrives in steps, a
figure that returns where a later slide adds to one the room has seen, the terms each slide
introduces, and notes structured for rehearsal. Write the **Q&A** part on the slide each challenge
from step 1 is met on. A field added to every entry is decoration, and the rules it is held to will
say so.

Check every number in a claim against its source as you write it. Where the codebase holds the data
behind a figure, extract it into the plan's data directory with a script that says where it read
from, so the figure can be drawn again without the codebase.

### 5. Fit the slot, and write down the cuts

Give every entry a time budget and add them up against the slot, the way `pace-budget` does. What
does not fit, and every claim from the paper whose evidence you could not find or that
did not hold up when you checked it, goes under the plan's cuts, with the reason.

Then the challenges the author named in step 1: say where each is met, as the format asks.

### 6. Hand the plan over, and stop

The author edits it. Do not build a deck from a plan the author has not read: the plan is their
argument, and the deck only presents it.

## Mode: build

Turn a talk plan into a deck. Every headline, section, layout, piece of evidence and time budget
comes from the plan; nothing on a slide is decided here that the plan did not decide first.

### 1. Read the plan against its format

Every entry carries the fields `docs/talk-plan.md` asks for. If one is missing, or a claim has no
source, say which entry and ask, rather than filling it in.

### 2. Scaffold the deck

Run scaffold mode, steps 1 to 4, taking its answers from the plan's headmatter: the title, the
speaker, the venue, and the slot as the deck's `duration`.

### 3. Fill each slide from its entry, in order

Replace the template's skeleton slides with one slide per entry:

| From the entry | Onto the slide |
|---|---|
| its heading | the headline, word for word |
| **Layout** | the slide's `layout` |
| **Section** | the slide's `section`, set where it changes and left to carry forward otherwise |
| **Evidence** | a figure through the figure script, a markdown table, an equation (`equation-worked-example`), or a `Callout`; the plan's questions and answers on the slides `answer-first` and `conclusion-stays-up` name |
| **Source** | a footnote on the slide, and an entry on the references slide |
| **Time** | a `Time:` line in the speaker notes |
| the paragraph under it | the speaker notes, with a `Signpost:` line where the section changes |
| **Callout** | a `Callout` over or beside the evidence, its text word for word, held to `signal-budget` and `accent-is-attention` |
| **Reveal** | a `v-click` on each element that arrives, one per step, in the plan's order |
| **Returns** | the earlier slide's figure on this one, drawn by the same chart in the figure script, sized for its pane, beside what the entry adds |
| **Terms** | each term on the slide where the evidence names it, spelled as the plan spells it, and said in the notes where it is defined |
| **Notes** | a `Question:`, `In:`, `Out:` and `Q&A:` paragraph in the speaker notes, one per part the entry gives, in that order, after the `Time:` and `Signpost:` lines and before the paragraph |
| **Setup**, **Answers**, **Load-bearing** | nothing: they shape the argument in the plan, and the slide shows only what proves its claim |

An optional field the entry leaves out is left off the slide too: build mode adds no callout, click,
returning figure or term the plan did not ask for. Load what the optional fields are held to before
filling them:

```bash
legible rules signal-budget accent-is-attention motion-purpose established-terminology acronym-budget
```

Delete the placeholder image and anything else the template stamped that no entry asked for.

### 4. Draw the figures from data

A figure script beside the deck draws every chart an entry calls for, with the archetypes in
`legible.figures` and the deck's own palette. Numbers typed in from the paper say which table they
came from; data read from the codebase is committed beside the script. Commit the images it writes.

### 5. Build, review, and attach the report

```bash
pnpm install && pnpm build
```

Then run review mode over the deck and save its report beside the plan. That report is what the
author gets with the deck.

An error is a fault in the build, and fixing it is part of building. If the fix changes the words
of a slide, change its entry in the plan too, so the plan stays the deck's source. A warning is the
author's to weigh: report it with its fix, and leave the slide as the plan wrote it.

## Mode: scaffold

Stamp a new Slidev deck wired to the theme, to its palette and to both checks. It is a **clean
start, not a worked deck**: the flagship deck in this project is the artifact that teaches the
method, and a second one here would be a second thing to keep true.

### 1. Settle the four things the template cannot

Ask only for what the author has not already said.

| What | And what to take as given |
|---|---|
| Where the deck goes | a new directory, named by the author. |
| Where the theme is | slidev-theme-legible is not on npm yet, so a deck consumes it by path — the theme directory inside a checkout of legible-slides. Ask which checkout. |
| Which palette it wears | the one the template already carries, a copy of `themes/leuven-blue.json` in that same checkout. Change it only if the author names another. |
| Which marks the cover shows | none: the cover's venue and affiliation slots show placeholders the theme bundles. Put the author's own files in `public/` if they name them; otherwise leave the placeholders for them to replace. |

### 2. Stamp the template

`template/` beside this file is the deck. Copy all of it, in one go, from wherever this file lives:

```bash
cp -R /path/to/this/skill/template/. path/to/new-deck/
```

The trailing `/.` is load-bearing: the checks are dotfiles, and a copy that skipped them would stamp
a deck with no gate on it. Check that the deck's own workflow and its pre-commit config arrived
before going on, because a scaffold whose whole claim is that the checks are already wired is worth
nothing if they are not.

### 3. Fill in what the author named, and nothing else

| Where | What |
|---|---|
| the headmatter of `slides.md` | the theme's path, the title, the author, and the cover's own venue and date |
| `package.json` | the deck's name and its description |
| `themes/palette.json` | the chosen palette's contents, if it is not the one stamped. Keep the path — everything else in the deck points at it, which is what makes a recolour one edit. |
| `public/`, `themeConfig.venueLogo` and `themeConfig.affiliationLogo` | the author's own marks, if they named any, in place of the placeholders |
| `themeConfig.shareUrl`, `themeConfig.shareQr` and `themeConfig.contact` | where the slides will be shared and how to reach the author, if they said; a QR code for that link goes in `public/`. Otherwise leave the placeholder. |

A skeleton slide is a blank for the author to fill, and not a slide for you to write. The method is
about deciding what each slide is *for*, and that decision is theirs.

### 4. Regenerate the stylesheet

The palette reaches the slides as a committed stylesheet, so the deck's build never runs Python.
What is stamped is current; a palette changed in step 3 leaves it stale:

```bash
cvd-validate themes/palette.json
legible gen-css themes/palette.json --output styles/tokens.css
```

The floor first, deliberately. A palette that has not cleared it is not one to colour a deck from,
and the validator names the pair to move rather than only refusing.

### 5. Hand it over green

```bash
pnpm install && pnpm build
```

Then **run review mode below over the stamped deck**, and hand the report over with it. That is the
acceptance bar, and the reason to stamp rather than retrofit: the report should carry no error at
all, on a deck nobody has written a word of yet. If it carries one, the fault is in the template
rather than in the author's deck — fix it here, and stamp again.

It will carry warnings, and those are the blanks. A headline that says what belongs in it is not a
claim, so `assertion-headline` is expected to fire on every skeleton slide, and each of those
findings clears when the author writes the slide. Report them as what they are. Do not answer them
by writing the author's headlines for them.

## Mode: review

Check an existing Slidev deck against the method, and report what breaks and how to fix it.

### 1. Find what is under review

| What | How to find it |
|---|---|
| The deck | The Slidev markdown the author named. Its headmatter is the block before the first slide. |
| Its themes | The palette JSON the deck wears — `themes/*.json` beside the deck in a legible-slides layout, or whatever the deck's headmatter and README point at. Ask if nothing names one. |
| Its generated figures | The deck's figure script — a Python file importing `legible.figures` — and the paths it writes to. |

The last row is the only one the review changes shape over. `never-sole-channel` is judged over
**hand-made visuals only** — pasted screenshots, hand-drawn diagrams, inline SVG and HTML — which is
the scope `docs/agent-skill-contract.md` §4b fixes, and the canon's own `**Decided by**` line for
that rule says which half is which when you load it in step 3. Every image the deck does not
regenerate is hand-made.

### 2. Run the mechanical checks

```bash
legible lint DECK --theme THEME --json          # --theme is repeatable, once per palette
```

Findings come back tagged with the rule they enforce, the slide they are on, and a severity. Take
them **verbatim**: do not re-count a bullet, re-measure a word, or re-decide a colour by eye.

The severity is the tier. An **error** is the gate tier. A **warning** is the advisory tier: the
canon says which script-decided rules are advisory, and the linter reports them as warnings that
never touch the exit code. They go in the report beside the judgments, not above them. The
palette check inside that command shells out to `cvd-validate`, and its arithmetic is the only
arithmetic about colour anyone here does.

Read the exit code, and carry it into the verdict unchanged:

- **0** — nothing the canon decides by script is broken.
- **1** — at least one objective violation. The review's verdict is FAIL, whatever the judgments say.
- **2** — the deck or a theme could not be read. **Do not report a verdict.** Say what could not
  be read, and stop until it can be.

If no theme could be found in step 1, the palette went unchecked. Run the deck's slides anyway, and
say so in the report where a verdict would go — silence there reads as a pass.

### 3. Load the rules that need judgment

```bash
legible rules one-message assertion-headline never-sole-channel no-script-on-slide
legible rules --section voice --decided-by judgment
```

Both print the canon's own words. Judge against what they print, never from memory of what the
method says — that memory is what this skill exists not to rely on. The second command asks the
canon which rules those are rather than naming them, so a rule added to that section is reviewed
from the moment it is written.

Then load every rule the linter reported a **warning** for, by the IDs it printed:

```bash
legible rules RULE …                            # each rule the mechanical run warned on
```

An advisory is the one place a judgment and a script meet. Whether anything clears one is the
rule's own text to say, which is why it is loaded rather than remembered.

If any of these commands exits 2, the ID or the section it names has moved in the canon. Say so
and stop: a review that quietly loaded fewer rules finds fewer faults and reads as a pass.

### 4. Judge, slide by slide

Read each slide as the room receives it — the headline, the evidence, and the speaker notes — and
apply the five checks, in this order:

| Check | Applied to |
|---|---|
| `one-message` | every slide |
| `assertion-headline` | every slide carrying a headline |
| `never-sole-channel` | the hand-made visuals identified in step 1, and nothing else |
| `no-script-on-slide` | the words on the slide, read beside its speaker notes |
| the canon's judgment voice rules, loaded above | the headline, the prose and the speaker notes |

Four things hold a judgment to something:

- **Point at it.** Quote the words or name the element on the slide that triggered the finding. A
  finding nobody can locate cannot be argued with, and is not worth reporting.
- **One per rule per slide.** Report the clearest instance, not every instance. This is a restraint
  on judgments alone: the mechanical findings arrive as the linter reported them, and dropping one
  would hide a violation that gates.
- **Honour the canon's own precedence.** Where a rule you loaded defers to another rule, follow
  that; the canon says which wins, and this file does not.
- **Weigh each advisory, and keep it.** Where the rule's own text says what clears it and the slide
  meets that, say so on the finding, quoting what meets it. Never drop the finding: the author
  decides whether to override it, and a dropped advisory is a decision taken for them.
- **Carry a fix** — which every finding in the report does, the mechanical ones included. A
  rewritten headline, the split of a slide into two, the redundant channel a visual is missing. The
  linter says what broke; the review says what to do about it, and a finding without a fix is an
  opinion.

Judgments are **warnings**, always: the advisory tier, beside the linter's own advisories. They are
fallible, so they never gate.

### 5. Merge into one report

One markdown report, both halves in it, grouped per slide in the order the deck runs. Findings
against the deck rather than any one slide — the palette is the usual one — go in a final group.

```markdown
# Review — path/to/slides.md

**FAIL** — 2 errors, 2 warnings.
Errors are the gate tier and block. Warnings are the advisory tier, the linter's advisories and the
judgments alike, and never block. Palette: checked against themes/leuven-blue.json. Read any rule
below with `legible rules <rule-id>`.

## Slide 4 — "Cost falls with retrieval and accuracy holds"

- **error** · `bullet-ceiling` — … bullets, ceiling …
  **Fix:** move the last bullets to the notes; they answer a different question from the ones above them.
- **warning** · `assertion-headline` — the headline reads "Results", which names the slide rather than claiming anything.
  **Fix:** "Retrieval halves cost and holds accuracy at every window."
- **warning** · `on-slide-words` — … words outside the headline and figures, ceiling …
  **Fix:** the second paragraph is what you will say; move it to the notes.

## Deck

- **error** · `separation-floor` — FAIL themes/mine.json — min ΔE … (floor …); `cvd-validate themes/mine.json` names the pairs
  **Fix:** move `series-2` away from `series-1` in lightness, then re-run the validator.
```

The elisions are this file's, not the report's: a finding carries the linter's message word for word,
numbers included. What may not appear **here** is a number out of the canon, because a threshold
written into this procedure is a copy of it that can go stale.

- The **verdict** is the linter's exit code and nothing else. A judgment never turns a PASS into a
  FAIL; it also never softens a FAIL.
- Each finding names its **rule by ID**, which is how a reader looks it up and disagrees with it.
- The tally counts both halves. Errors can only come from the mechanical run; warnings come from
  both, and within a slide the gate tier is listed before the advisory tier.

## Posture

**Flag and suggest. The author applies.** Review proposes fixes and never edits a deck on its own.
If the author accepts one, apply that one, and leave the rest of the deck alone. It can enforce
structure; it cannot decide anybody's message for them.

Draft and build do write, and the same line holds for them. Draft proposes an argument, and the
author settles it in the plan. Build writes slides, but only what the plan says: it invents no
claim, and it does not reword one to clear an advisory.

## What this skill will not do

- **State a rule.** Rules live in the canon. This file names them by ID and loads them at review
  time, so nothing here can drift out of sync with them.
- **Re-implement a mechanical check.** They belong to `legible lint`, which is reproducible and
  runs in CI. A review that counted bullets by hand would produce a second verdict nobody can
  reproduce.
- **Decide colour.** `cvd-validate` measures it, through the linter. There is one implementation of
  the simulation, deliberately.
- **Gate on a judgment.** Only the mechanical half has an exit code, and only that half blocks.
