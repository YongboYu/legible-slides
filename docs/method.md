# The method

_Resolves [#14](https://github.com/YongboYu/legible-slides/issues/14). Captures the canon settled in
[#3](https://github.com/YongboYu/legible-slides/issues/3), sharpened by the presentation-method
research ([#7](https://github.com/YongboYu/legible-slides/issues/7),
[`research/presentation-methods.md`](research/presentation-methods.md))._

This is the canon: **every rule of the method, stated once, in tool-neutral language.** It is what a
human reads to learn the method, what an agent loads to review a deck, and what a linter quotes to
get a number.

> **One copy, here.** No other document in this repo states a rule or repeats one of these numbers.
> They link to a rule by its ID instead. A second copy is a second thing to keep true, and the day
> they disagree is the day the reviewer starts enforcing a rule nobody decided.

## How to read a rule

Each rule carries a stable **ID** in backticks, its statement, and a footer:

- **Decided by** — `script` when a linter can settle it, `judgment` when a reader must. Mixed rules
  say which half is which.
- **Threshold** — `key = value`, present only where the rule has a number. **Quote it; never
  re-derive it.** A reviewer that recomputes a threshold at runtime is a reviewer that can drift
  from the canon.
- **Advisory** — a script-decided rule whose threshold sets its own severity to `warning`. A
  script finds it and reports it; it never gates. The review reports it on its slide, in the advisory tier
  beside the judgments, and the author may override it. The budgets at the end of
  [§3](#3-density-and-noise) are all advisory: their point is balance, not minimalism.

- **Floor** — the rule is part of the accessibility floor: whether someone in the room can read
  the slide at all, whatever their eyes and wherever they sit. Everything else is a **default**:
  the method's opinion of how a research talk lands, held firmly but not absolutely.

### Departing from a default

A default is right for almost every slide, and a rigid reading of it can still weaken one. A
subheading may organise one message rather than start a second; a derivation may need more words
than evidence usually does. Where a default would cost the argument, the author departs from it on
that slide and says why, in a line of the speaker notes of its own:

```
Exception: on-slide-words the derivation needs every step on screen while it is walked through
```

The line names one rule by its ID and gives the reason. A script finding of that rule on that slide
is then reported as a warning carrying the reason, and a reviewer weighs the reason rather than the
rule: it holds if the slide still carries one claim and its evidence still reads. An exception
never hides a finding, and it never reaches a **Floor** rule, which no reason clears. A line with no
reason, or naming a floor, is reported and not applied.

Rules are grouped: [structure](#1-structure), [authoring order](#2-authoring-order),
[density and noise](#3-density-and-noise), [legibility](#4-legibility), [colour](#5-colour),
[motion](#6-motion), [voice](#7-voice). The [14-beat flagship outline](#the-flagship-deck-14-beats)
follows the rules it teaches.

---

## 1. Structure

### `one-message`: every slide answers exactly one question

If you cannot state that question in a sentence, the slide is wrong. Two questions means two
slides. The usual failure is compressing three messages onto one slide to save time, which costs
more time to explain and leaves the room behind.

**Decided by** judgment

### `assertion-headline`: the headline is the claim, not a label

A sentence assertion, not a topic phrase. Someone who reads only the headlines still gets the
argument. The claim lives in the headline and nowhere else: no separate takeaway strip, no
key-message footnote. If the claim is not the headline, the slide has two messages.

**Decided by** judgment

### `headline-shape`: a full sentence, left-justified, two lines at most

Long enough to be a claim, short enough to be read in a glance. Alley's band of roughly 8 to 14 words
is the sweet spot, offered as **guidance rather than a gate**: a shorter line that is still a claim is
fine, and the operative ceiling is the two rendered lines, because that is what governs whether the
room reads it.

**Decided by** judgment (that it reads as a claim, per `assertion-headline`) · script (how many
lines it renders in, set in the deck's face at the headline's size and width; the cover's title is
not a headline) · **Threshold** `headline-lines-max = 2` (violation when a headline renders in more
than 2 lines)

### `ae-skeleton`: four zones on a content slide, and nothing else

```
assertion headline
evidence
locator · page number
```

The slide opens on the headline: nothing sits above the claim. The locator and the page number are
persistent chrome, sharing the footer, the locator at bottom left and the page number opposite it.
Nothing is drawn between the headline and the evidence: weight and whitespace separate the claim
from what proves it, and the evidence starts the same distance under the headline on every slide.
Everything a slide adds beyond these four zones is a candidate for `coherence`.

**Decided by** script (the layout supplies the zones)

### `no-section-dividers`: no slide is spent purely on navigation

The footer locator carries orientation, so the method ships no section-divider slide, no
single-word-emphasis slide, and no closing "thank you" slide. A slide whose only content is the name
of the next section is a slide that proves nothing. The close is `conclusion-stays-up`'s.

**Decided by** script (the deck offers no such layout; a slide whose body is a bare section name)

### `answer-first`: the talk opens on its answer

By about the second minute, the room has the result and the questions the talk answers: one slide
straight after the cover, its headline the result and its evidence the research questions, numbered
so the close can answer them by number. Everything after it is the case for that answer, and a
listener who drifts off at minute five already has what they came for. Background, related work and
the outline come after the answer, if at all; the footer's section map is the outline.

The opening also hands the slides over: the cover carries a QR code to the shared slides, so anyone
in the room can follow on their own screen from the first minute.

**Decided by** judgment (that the second slide states the result and the questions, and that the
room has them in time) · **Threshold** `answer-by-minute = 2`

### `conclusion-stays-up`: the last main slide answers the questions, and stays up through Q&A

The final slide of the talk, before any backup, is a conclusion: its headline is the talk's claim,
and its evidence answers each research question from `answer-first` one to one, by the same number.
It carries a QR code to the shared slides and the presenter's contact, and it stays on screen
through the questions, because that is when the room is reading it. A "thank you" or "questions?"
slide put there hides the answers for the whole of Q&A; say thank you aloud.

**Decided by** judgment (that each question gets its answer) · script (the last main slide has a
headline, the headline is not a closing label, and it does not read as a thank-you) · **Threshold**
`closing-labels = [Thank you, Thanks, Questions, Any questions, Q&A, The end, Conclusion, Conclusions, Summary]`,
`thank-you-words = [thank you, thanks]`, `conclusion-severity = warning` (a finding when the last
slide outside the backups has no headline, a headline that is one of `closing-labels`, or a headline
carrying one of `thank-you-words`)

### `section-locator`: the footer names the talk's sections, and the current one by weight too

The locator names the talk's few sections, not each slide's topic. A section is declared on its
first slide and carries forward until the next slide that declares one. By default the footer shows
the **section map**: every section in order, the current one marked by colour **and** weight
(`never-sole-channel`), the rest in the text neutral, never the softest one
(`decorative-neutral-never-text`). A deck may instead show the **single section label with a
count**, the current section and its position among them. Backup slides, held for questions after
the talk, sit outside the count: they show their own label and no position.

The map only works while it fits in one glance across the footer, so the deck keeps to a handful of
short section names. A deck that outgrows them is warned rather than failed: the label with a count
still fits, and whether the structure is right is the author's call.

The footer is a backup channel, not the only one. Every section change is also said aloud: the
first slide of each section carries a **signpost line** in its speaker notes: a line of its own,
opening `Signpost:`, with the sentence that tells the room the talk has moved on and where to.

**Decided by** script (how many sections, how long a label) · judgment (the signpost, said aloud) ·
**Threshold** `sections-max = 5`, `section-label-chars-max = 10`,
`section-locator-severity = warning` (a finding when a deck declares more than 5 sections, or a
section label longer than 10 characters)

### `evidence-is-visual`: the body proves the headline, visually

Evidence is a chart, a diagram, a photograph, or words and equations arranged visually. A wall of
prose is not evidence, and neither is a bullet list restating the headline. Bullets are the
**fallback** form, under the ceiling in `bullet-ceiling`, not the default.

**Decided by** judgment

### `equation-worked-example`: an equation arrives with a worked example

Real numbers pushed through the formula, on the same slide. An equation alone appears; an equation
with a worked example lands.

**Decided by** script (an equation is present) · judgment (whether the example is actually worked)

---

## 2. Authoring order

### `message-before-visual`: decide the message, then choose the visual

Pick the one thing the slide must land, then find the supporting material that earns it. Never reach
for a chart first and invent a caption for it afterwards.

**Decided by** judgment

### `established-terminology`: use the standard term as-is

If a term is already well established in the field, use it and do not rephrase it. An audience
should never have to guess what you mean, and a fresh synonym for a standard term buys nothing.
Define the term once, where the talk first leans on it, and use it from then on. A plain-words
gloss goes beside the term, never in its place: a room that hears the gloss and then reads the
paper meets the term cold.

The key terms are the paper's own, as its abstract and its title use them, or as a talk plan lists
them. A paraphrase standing in for one of them is the violation, however plain it reads.

This rule **wins over every rule in [§7](#7-voice)**. Plain words are for what the field has no
word for: a listed word that is genuinely the field's term is not a `no-inflated-register`
violation, and a standard term is not the abstraction `concrete-over-abstract` asks you to replace.

**Decided by** judgment

### `no-script-on-slide`: no sentences of script on the slide, but show the key terms

What you are about to say, written out in full sentences, does not belong on the slide: the room
reads it instead of listening, and you end up reading it to them. Speaker notes are where the
sentences go.

The key terms are a different matter, and they belong on the slide. Short labels next to a graphic
help people remember it (Mayer & Johnson 2008). Hearing the words while also seeing them in writing
helps most when the talk sets the pace and the audience is new to the topic (Adesope & Nesbit 2012,
a meta-analysis of 57 studies), and written words help listeners working in a second language
(Montero Perez et al. 2013). That describes most of a conference room. So the test is the
sentence, not the word: a term, a label or a number on screen is fine, and a sentence you are about
to say aloud is the script.

**Decided by** judgment

---

## 3. Density and noise

### `bullet-ceiling`: five bullets per slide, maximum

The ceiling is what physically prevents a slide from absorbing a second message.

**Decided by** script · **Threshold** `bullets-per-slide = 5` (violation when a slide's bullet count
exceeds 5)

### `word-ceiling`: twelve words per bullet, maximum

A bullet longer than this is a sentence, and a sentence belongs in the headline or the notes.

**Decided by** script · **Threshold** `words-per-bullet = 12` (violation when a bullet's word count
exceeds 12)

### `coherence`: cut anything that does not serve the one message

The top-level noise rule, and one of the best-evidenced in the method: that removing extraneous
material improves learning is well supported, though most of the tests come from Mayer's own lab.
Signal-to-noise, data-ink, restraint — all the same move.

**Decided by** judgment

### `signaling`: cue the one thing that matters

Point the eye at the part of the evidence that carries the claim. The attention roles are the
signalling channel; see `accent-is-attention`.

**Decided by** judgment

### `layout-discipline`: contrast, repetition, alignment, proximity

Make different things look clearly different. Reuse the same layouts and roles so the deck reads as
one system. Line everything up to the grid. Group what belongs together and separate what does not.
Leave empty space rather than filling it.

**Decided by** judgment

### `figure-noise`: figures spend ink on data

No chartjunk, no heavy gridlines, no 3-D, no ornamental fills. Treat this as a direction (reduce
noise), not a ratio to optimise: some redundant non-data ink genuinely helps.

**Decided by** judgment

### `element-ceiling`: about six visual groups on a slide

A visual group is one thing the eye lands on: a paragraph, a list, a table, an image, a figure, a
callout, a block of code or of markup. Working memory holds about four chunks at once (Kosslyn's
capacity principle), and a slide past about six groups is asking the room to hold more than that,
usually because it carries a second message. The count is taken at the top of the slide's body,
beneath the headline: a list is one group however many bullets it has (`bullet-ceiling` counts
those), and a block of markup is one group whatever it wraps. Footnotes cite rather than say, so
they are not a group (nor, under `on-slide-words`, words).

The point is balance, not minimalism. A slide that has to be dense passes review when its headline
says how to read it, which is why this rule warns rather than gates.

**Decided by** script (the count) · judgment (whether a dense slide's headline says how to read it)
· **Threshold** `elements-per-slide = 6`, `element-ceiling-severity = warning` (a finding when a
slide carries more than 6 visual groups)

### `on-slide-words`: about forty words on a slide, outside the headline and the figures

The words the room has to read while you talk: bullets, prose, callouts and tables. The headline is
not counted, and neither is a figure's own text, nor the footnotes that cite the sources: those are
attribution, set at the floor, and nobody reads them while you talk. Past about forty, the slide is
the script (`no-script-on-slide`) and the room reads instead of listening; the sentences go in the
speaker notes. The same balance holds as for `element-ceiling`: a dense slide passes review when its
headline says how to read it.

**Decided by** script (the count) · judgment (whether a dense slide's headline says how to read it)
· **Threshold** `words-per-slide = 40`, `on-slide-words-severity = warning` (a finding when a slide
carries more than 40 words outside its headline and figures)

### `signal-budget`: one emphasised span and one callout per slide

Signalling works because it is rare (Richter et al. 2016). A slide that bolds something in every
line has signalled nothing, and a second callout halves the first. One span set in bold or
highlighted, and one callout, per slide. Italics are for terms and titles and are not counted. The
attention roles are spent the same way, one locus per slide (`accent-is-attention`).

**Decided by** script · **Threshold** `emphasised-spans-per-slide = 1`, `callouts-per-slide = 1`,
`signal-budget-severity = warning` (a finding when a slide carries more than 1 emphasised span, or
more than 1 callout)

### `acronym-budget`: about five new abbreviations per talk, and the rest spelled out

Every abbreviation is a definition the room has to hold for the rest of the talk, and acronyms
measurably hinder understanding (Barnett and Doubleday 2020). Spend about five, on the terms the
talk keeps coming back to, and spell the rest out. An abbreviation is a word of two or more
capitals as the room reads it on a slide, and it is new on the first slide it appears on. Backup
slides are outside the talk and outside the count.

A script cannot know which abbreviations a room already owns, so it counts them all, and the
author decides whether one is already the field's word (`established-terminology`).

**Decided by** script (the count) · judgment (which abbreviations the room already owns) ·
**Threshold** `new-acronyms-per-talk = 5`, `acronym-budget-severity = warning` (a finding on the
slide where the talk's sixth new abbreviation appears)

### `pace-budget`: the slides' time budgets fill at most 85% of the slot

A talk planned to fill its slot runs over it: questions, a slow projector and a late start all come
out of the margin, and a talk planned without one has none. The slot is the `duration` the deck's
headmatter declares. A slide's budget is a line of its own in its speaker notes, opening `Time:`,
with a duration written as `90s`, `1min 30s` or `1:30`. Backup slides are not budgeted into the
slot. A slot or a budget the script cannot read is reported rather than skipped, because a budget
left out of the sum is a talk that only looks as if it fits.

**Decided by** script (where the deck declares its slot and its notes state budgets) ·
**Threshold** `pace-share-max = 0.85`, `pace-budget-severity = warning` (a finding on the slide
where the budgets so far pass 85% of the slot)

---

## 4. Legibility

### `type-scale`: type is sized for the room, and nothing goes below the floor

Fixed by the method, not by the palette and not per slide. On the logical canvas the headline and
the body each have one size, and every other piece of text the template sets (a caption, a table
header, a legend, a figure's axis and tick labels, the locator, the page number) sits at or above
the floor. A generated figure is held to the floor at the size it lands on the slide, not at the
size it was drawn. There is nothing smaller, and the floor is not a knob for fitting more onto a
slide: a slide that only fits below it is carrying too much.

Slides size text only through the template's classes, never with an inline size in px, so the floor
can be checked on every slide a deck writes and not only on the classes the theme ships. The floor
holds wherever a deck sets type: in a component it draws a diagram with and in its own stylesheet
too, because that text lands on the slide just the same.

**The room it suits.** The canvas is scaled to the screen, so a size is a share of the image
height, and what decides legibility is how many image heights away the farthest viewer sits. By
the AV industry's sizing rule ([AVIXA DISCAS](https://www.avixa.org/standards/discas-calculators/discas/learn-more-about-display-size)),
body type reads to about 4.5 image heights and the floor to about 3.5. That is a seminar
room or a typical conference session room, roughly 30 to 150 seats. A lecture hall or a plenary is
planned to about 6 image heights, and for one of those:

1. **Raise the body** to 26–28px, with the headline at about 40–42px. It is one variable in the
   theme, and it costs about 15–30% of each slide's text, so check the densest slides after.
2. **Cut what the slide carries** rather than shrinking it: detail moves to the spoken track, a
   backup slide or the shared PDF.
3. **Share the slides** with a QR code on the first and last slide (`answer-first`,
   `conclusion-stays-up`), so people can follow on their own screen.
4. **Ask the organisers** for a second screen or a confidence monitor for the rear.

Before any talk, whatever the room: view the deck from about six screen heights away (about 1.1 m
for a 13-inch laptop) and read the smallest text on every slide.

**Floor** · **Decided by** script (an inline px size, a size below the floor, figure text) · judgment (the
room) · **Threshold** `canvas-width-px = 1280`, `canvas-aspect-ratio = 16:9`, `body-px = 23`,
`headline-px = 37`, `floor-px = 18`, `body-reach-image-heights = 4.5` (violation when a slide sets
a font size in px inline, or sets text below `floor-px`)

### `fonts`: one text family, one mono family, both bundled

Inter for headings and body. JetBrains Mono for the locator and nothing else. Both are bundled and
registered with the figure toolchain, so a machine that lacks them cannot silently substitute a
fallback and leave the figures mismatched against the slides.

**Floor** · **Decided by** script · **Threshold** `font-text = Inter`, `font-mono = JetBrains Mono`

### `light-ground`: the colour scheme is light, and locked

Not a preference and not a per-viewer choice. Following the viewer's OS setting sets an ink-on-white
figure set against near-black and destroys the contrast the rest of the method depends on. A
validated dark ground would need every colour rule re-verified on it.

**Floor** · **Decided by** script · **Threshold** `color-scheme = light`

---

## 5. Colour

### `never-sole-channel`: colour never carries meaning alone

Every line series carries a distinct dash pattern and marker; bars carry direct labels. This is what
survives a grayscale photocopy, a bad projector, and the dichromacies the floor cannot fully cover.

**Floor** · **Decided by** script (generated figures, where the redundancy is structural) · judgment (hand-made
visuals and pasted images)

### `accent-is-attention`: the accent role marks attention, never data

An arrow, a highlight, "ours". Never a data series.

Attention is one hue doing two jobs, and no single tone of it clears contrast in both on a light
ground, so it comes as two roles. `accent` is a **fill**: a callout, a pill, a badge, always with
ink text on top of it and never light text. `accent-strong` is for **text and strokes**: an arrow, a
ring, a highlighted numeral. The fill colour is never text and never a thin stroke. A stroke in
either role is at least the stroke floor wide on the canvas, because a hairline in a warm hue is the
first thing a washed-out projector loses.

**One attention locus per slide:** one pill, or one arrow and the ring it points to, or one
highlighted numeral. Isolation is what makes a highlight work, and a second one dilutes both. Pair it
with a second cue (weight, shape or position), as `never-sole-channel` asks of all colour.

**Floor** · **Decided by** script (the contrast pairings, generated figures) · judgment (hand-made visuals, the
one locus) · **Threshold**
`attention-contrast-pairs = [ink on accent, accent-strong on surface, accent-strong on surface-alt]`,
`attention-contrast-min = 4.5`, `attention-stroke-px-min = 3` (violation when a pairing's WCAG
contrast ratio is below `attention-contrast-min`)

### `spend-colour-on-discrimination`: two groups by default, the full ramp only when earned

The default chart is a de-emphasised comparison group plus one highlight. Reach for the full
categorical ramp only when the message genuinely is a per-series comparison. Colour is spent where
the message needs discrimination, not by default.

**Decided by** judgment

### `decorative-neutral-never-text`: the softest neutral is not a text colour

It exists for rules, gridlines and ghost edges. Text on it fails contrast.

The same test governs every other role used for text: it clears WCAG contrast at the size it is set,
or it does not carry text at that size. A mid-contrast chrome colour such as `brand-strong` clears it
only at large sizes.

The roles the template sets as text are `ink`, `neutral` and `brand`, and the grounds they sit on
are `surface` and `surface-alt`, so every one of those pairings is measured, whatever the palette.
A palette that makes `neutral` unreadable fails here, however well its data colours separate.

**Floor** · **Decided by** script (role usage) · **Threshold** `text-contrast-min = 4.5`,
`text-contrast-pairs = [ink on surface, ink on surface-alt, neutral on surface, neutral on surface-alt, brand on surface, brand on surface-alt]`
(violation when a pairing's WCAG contrast ratio is below `text-contrast-min`)

### `separation-floor`: data colours stay perceptually separated under colour-vision deficiency

Every pair of data colours that can share one chart axis stays above the floor under normal vision
and all three dichromacies, simulated at full severity because that is the worst case. Grayscale is
measured the same way but is **advisory**: a grayscale pair below the floor is a warning, never a
failure, because `never-sole-channel` is the fix the method already mandates for it.

The floor is a **tunable design parameter**, grounded in the just-noticeable-difference literature,
not a physical constant. Comparison is inclusive, so a pair landing exactly on it passes. A palette
sitting exactly on the floor is at capacity: one more series will fail without retuning.

**Floor** · **Decided by** script · **Threshold** `delta-e-floor = 15.0`, `delta-e-metric = CAM02-UCS`,
`cvd-simulation = Machado 2009`, `cvd-severity = 100`,
`cvd-conditions = [normal, deuteranomaly, protanomaly, tritanomaly]`,
`grayscale = advisory` (violation when a pair's ΔE is below `delta-e-floor`)

---

## 6. Motion

### `motion-purpose`: motion adds evidence or depicts change, and does nothing else

Two uses earn motion. **A click reveal where each step adds evidence:** the next piece of the
argument arrives when you get to it. A reveal never hides a conclusion the headline already states,
because then the click holds back the answer the room has already read. **Process depiction:** the
change over time *is* the content. Both must be **apprehensible** (the eye can extract the structure
in the time it is on screen) and **congruent** (the motion's structure matches the idea's).
Decorative motion and entrance effects earn nothing, and a deck sets **no slide transition**.
Animated graphics are not better than well-designed static graphics (Tversky et al. 2002); a reveal
that splits a label from its referent in time is worse than either.

The segmenting research (Rey et al. 2019) does not back speaker-paced reveals: it is about narrated
multimedia split into coherent segments, not about hiding a callout until a click. The case for a
reveal is only the one above.

The **final build state is the exported page**: a PDF or a handout shows each slide with every step
revealed, so a slide has to read on its own once everything is showing.

**Decided by** judgment

### `motion-ceiling`: fifteen seconds, maximum

**Floor** · **Decided by** script (where a duration is declared) · **Threshold** `animation-seconds-max = 15`
(violation when a declared animation runs longer than 15 seconds)

---

## 7. Voice

**Say it the way you would say it out loud.** Slides and prose written to sound impressive read as
machine-written, and they date fast. The durable tells are structural and rhythmic rather than a
word blacklist, so the rules below are split by who can decide them. This set is a **seed**,
deliberately extensible. Every rule in it gives way to `established-terminology`: saying it out
loud means saying the field's term, not a paraphrase of it.

### 7a. Script-decided

#### `no-em-dash-headline`: no em-dashes in a headline

Rewrite the sentence, or use a colon. Prose outside headlines may use one where it is genuinely the
right mark, sparingly.

**Decided by** script · **Threshold** `em-dashes-per-headline-max = 0`

#### `no-inflated-register`: no words that inflate register without adding information

The wordlist below is a seed; extend it as tells accumulate. `established-terminology` wins over this
rule, which is why a hit is reported as a **warning** rather than a hard failure: "a robust
estimator" is the field's term, not inflation.

**Decided by** script · **Threshold**
`inflated-register-words = [crucial, pivotal, seamless, robust, leverage, elevate, delve, tapestry, testament to]`,
`inflated-register-severity = warning`

#### `opener-variety`: no more than half the sentences open the same way

Counted over a passage of prose or notes, not over one sentence.

**Decided by** script · **Threshold** `opener-words = [The, This, It, In]`, `opener-share-max = 0.5`
(violation when more than half a passage's sentences open with a listed word)

### 7b. Judgment

Every rule in this subsection is **Decided by** judgment, and none carries a threshold. These are the
tells a wordlist cannot catch.

#### `no-contrast-for-emphasis`: no foil invented to make a claim sound bigger

The tell is "not just X, it's Y", where X is a position nobody held and the negation exists only to
set up the reveal. State the claim on its own.

A contrast that names a **real alternative** the audience might otherwise choose is not this rule's
target: "the headline is the claim, not a label" earns its second clause, because labels are what
most decks actually put there.

#### `no-reflexive-tricolon`: three items because the claim has three

Not because three sounds complete. A padded third item is noise under `coherence`.

#### `no-hedging-or-boilerplate`: start at the claim, stop when it is proved

Cut the warm-up sentence that announces what you are about to say, and the closer that summarises
what you just said. This applies to a slide, a passage and its notes. A talk's **opening** and its
**conclusion** are exempt: there, saying what is coming and summing up what was said are structural
signals the room uses to follow along, and `answer-first` and `conclusion-stays-up` ask for exactly
that.

#### `rhythm-variety`: vary sentence length deliberately

Read it aloud. Fix anything you would not actually say.

#### `concrete-over-abstract`: prefer a number or a name to an abstraction

"Three series pass, and a fourth would fail" beats "demonstrates strong accessibility
characteristics".

---

## The flagship deck: 14 beats

The flagship deck is the **primary teaching artifact**: it teaches the method by being the method.
Each beat's headline is an assertion, and the slide self-demonstrates the rule it teaches. The
load-bearing rules get a beat of their own; the rest the deck obeys visibly, and this file states in
full.

| # | Beat (assertion headline) | Evidence / self-demonstration | Teaches |
|---|---|---|---|
| 1 | **legible-slides** · _Readable from the back row, and for every pair of eyes._ | Cover; the type scale and the palette from slide one, and a QR code to the slides | `type-scale`, `answer-first` |
| 2 | _A method decides what each slide is for, and two commands hold every slide to it._ | The result first, and the three questions the talk answers, numbered | `answer-first` |
| 3 | _Most templates hand you files and leave the hard part to you: deciding what a slide is for._ | A busy stock-template slide | — |
| 4 | _Every template quietly fails two audiences you can measure: the back row, and 1-in-12 eyes._ | Projector-distance sketch beside a CVD-muddy 5-line chart | `type-scale`, `separation-floor` |
| 5 | _A method first, files second._ | The pivot; the thesis of the whole deck | — |
| 6 | _Every slide answers one question. If you can't state it, the slide is wrong._ | This slide answers exactly one | `one-message` |
| 7 | _The headline is the claim, not a label._ | The headline is a claim; label versus claim side by side | `assertion-headline`, `headline-shape` |
| 8 | _Decide the message before you reach for the chart._ | Message-before-visual, shown as an ordering | `message-before-visual` |
| 9 | _Cut everything that isn't the message._ | Signal-to-noise; a purposeful reveal doubles as the motion guardrail | `coherence`, `motion-purpose` |
| 10 | _Body type is sized for the back row, not your laptop._ | The body size as a share of the image height, worked through to the room it reads in | `type-scale` |
| 11 | _If a colour dies under colour-blindness or grayscale, it's not in the palette._ | The 5-line chart under deuteranopia and grayscale, with dash and marker redundancy | `separation-floor`, `never-sole-channel` |
| 12 | _The validator reads any palette file, yours included, and names the pair that fails._ | This deck's palette measured, at capacity, the command that measures yours, plus the not-affiliated note | `separation-floor` |
| 13 | _One file is what you present, hand out and have reviewed._ | Slidev on screen, a PDF from the same file, plus the coding-agent skill | — |
| 14 | _Everything you just watched was built to the rules it was teaching you._ | Each question answered by its number, a QR code to the slides and the presenter's contact, left up through Q&A | `conclusion-stays-up` |

Beats 3, 5 and 13 teach no rule: they carry the argument for why the rules exist. The anti-slop
rules in [§7](#7-voice) get **no beat** — the deck obeys them silently, because a slide dated to
"don't sound like AI" would age badly and pull focus from the timeless part of the method.

The outline commits to no layout: which beat lands on which layout is the reference implementation's
call ([`slidev-reference-impl.md`](slidev-reference-impl.md) §2). What the outline does commit to is
that no beat needs a layout `no-section-dividers` forbids, the close included.

---

## Where these rules came from

Pointers only. Each records where a rule came from or how it is measured; none of them is
authoritative over this file, and the research documents carry values as they were proposed at the
time.

- [`design-provenance.md`](design-provenance.md) — the decisions as they were argued out in the
  CAiSE 2026 deck this method was extracted from, with the issue trail and the author's own words.
- [`research/presentation-methods.md`](research/presentation-methods.md) — the evidence base: Alley
  and Neeley on assertion-evidence, Mayer on coherence, redundancy and segmenting, Tversky on
  animation, Tufte on chartjunk, Williams on layout, plus the sources later corrections cite:
  Adesope & Nesbit, Mayer & Johnson and Montero Perez et al. on key terms on screen, and Rey et
  al. on segmenting.
- [`cvd-validator-contract.md`](cvd-validator-contract.md) — how `separation-floor` is measured, why
  the floor is where it is, and the retired `≥39` claim it replaces.
- [`token-contract.md`](token-contract.md) — the palette schema the colour rules are addressed to,
  and the split between what a palette may change and what the method fixes.
- [`agent-skill-contract.md`](agent-skill-contract.md) — how an agent turns these rules into a
  review, and which of them gate a build.
