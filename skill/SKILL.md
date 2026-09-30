---
name: legible-slides
description: Start a Slidev deck to the legible-slides method, or review an existing one against it — the mechanical gate a script settles, plus the judgments it cannot. Use when asked to scaffold or start a deck to the method, review a deck, check slides against the method, or vet a deck before it is presented or merged.
---

# legible-slides

This file is a **procedure**, not a rulebook. It states no rule of the method and no threshold,
because the method is stated once, in the canon at `docs/method.md`, and a second copy is a second
thing to keep true. What is here is the order to work in, which checks a script settles and which
need reading, and what the report looks like.

Rules are **loaded from the canon at review time** (review, step 3). A rule edited there changes
this review with nothing edited here.

Two modes, and the second is the first one's acceptance bar:

- **scaffold** — start a new deck, method-compliant before a word of it is written.
- **review** — check a deck that exists, and say what breaks and how to fix it.

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
| Which marks the cover shows | none: the template carries placeholders for the venue's and the affiliation's logos. Put the author's own files in `public/` if they name them; otherwise leave the placeholders for them to replace. |

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
| `public/` and `themeConfig.logo` | the author's own marks, if they named any, in place of the placeholders |

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

Findings come back tagged with the rule they enforce and the slide they are on. Take them
**verbatim**: do not re-count a bullet, re-measure a word, or re-decide a colour by eye. The
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
legible rules one-message assertion-headline never-sole-channel
legible rules --section voice --decided-by judgment
```

Both print the canon's own words. Judge against what they print, never from memory of what the
method says — that memory is what this skill exists not to rely on. The second command asks the
canon which rules those are rather than naming them, so a rule added to that section is reviewed
from the moment it is written.

If either command exits 2, the ID or the section it names has moved in the canon. Say so and stop:
a review that quietly loaded fewer rules finds fewer faults and reads as a pass.

### 4. Judge, slide by slide

Read each slide as the room receives it — the headline, the evidence, and the speaker notes — and
apply the four checks, in this order:

| Check | Applied to |
|---|---|
| `one-message` | every slide |
| `assertion-headline` | every slide carrying a headline |
| `never-sole-channel` | the hand-made visuals identified in step 1, and nothing else |
| the canon's judgment voice rules, loaded above | the headline, the prose and the speaker notes |

Four things hold a judgment to something:

- **Point at it.** Quote the words or name the element on the slide that triggered the finding. A
  finding nobody can locate cannot be argued with, and is not worth reporting.
- **One per rule per slide.** Report the clearest instance, not every instance. This is a restraint
  on judgments alone: the mechanical findings arrive as the linter reported them, and dropping one
  would hide a violation that gates.
- **Honour the canon's own precedence.** Where a rule you loaded defers to another rule, follow
  that; the canon says which wins, and this file does not.
- **Carry a fix** — which every finding in the report does, the mechanical ones included. A
  rewritten headline, the split of a slide into two, the redundant channel a visual is missing. The
  linter says what broke; the review says what to do about it, and a finding without a fix is an
  opinion.

Judgments are **warnings**, always. They are fallible, so they never gate.

### 5. Merge into one report

One markdown report, both halves in it, grouped per slide in the order the deck runs. Findings
against the deck rather than any one slide — the palette is the usual one — go in a final group.

```markdown
# Review — path/to/slides.md

**FAIL** — 2 errors, 3 warnings.
Mechanical checks gate; judgments are advisory and never block. Palette: checked against
themes/leuven-blue.json. Read any rule below with `legible rules <rule-id>`.

## Slide 4 — "Cost falls with retrieval and accuracy holds"

- **error** · `bullet-ceiling` — … bullets, ceiling …
  **Fix:** move the last bullets to the notes; they answer a different question from the ones above them.
- **warning** · `assertion-headline` — the headline reads "Results", which names the slide rather than claiming anything.
  **Fix:** "Retrieval halves cost and holds accuracy at every window."

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
- The tally counts both halves. Errors can only come from the mechanical run.

## Posture

**Flag and suggest. The author applies.** This skill proposes fixes and never edits a deck on its
own. If the author accepts one, apply that one, and leave the rest of the deck alone. It can
enforce structure; it cannot decide anybody's message for them.

## What this skill will not do

- **State a rule.** Rules live in the canon. This file names them by ID and loads them at review
  time, so nothing here can drift out of sync with them.
- **Re-implement a mechanical check.** They belong to `legible lint`, which is reproducible and
  runs in CI. A review that counted bullets by hand would produce a second verdict nobody can
  reproduce.
- **Decide colour.** `cvd-validate` measures it, through the linter. There is one implementation of
  the simulation, deliberately.
- **Gate on a judgment.** Only the mechanical half has an exit code, and only that half blocks.
