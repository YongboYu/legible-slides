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

Rules are grouped: [structure](#1-structure), [authoring order](#2-authoring-order),
[density and noise](#3-density-and-noise), [legibility](#4-legibility), [colour](#5-colour),
[motion](#6-motion), [voice](#7-voice). The [13-beat flagship outline](#the-flagship-deck-13-beats)
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

**Decided by** judgment (that it reads as a claim, per `assertion-headline`, and that it fits) ·
script where the build can measure rendered lines · **Threshold** `headline-lines-max = 2`

### `ae-skeleton`: five zones on a content slide, and nothing else

```
locator  →  assertion headline  →  accent rule  →  evidence  →  page number
```

The locator and the page number are persistent chrome. Everything a slide adds beyond these five
zones is a candidate for `coherence`.

**Decided by** script (the layout supplies the zones)

### `no-section-dividers`: no slide is spent purely on navigation

The persistent locator carries orientation, so the method ships no section-divider slide, no
single-word-emphasis slide, and no closing "thank you" slide. A slide whose only content is the name
of the next section is a slide that proves nothing.

**Decided by** script (the deck offers no such layout; a slide whose body is a bare section name)

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
should never have to guess what you mean, and a fresh synonym for a standard term buys nothing. This
rule **wins over** `no-inflated-register`: a listed word that is genuinely the field's term is not a
violation.

**Decided by** judgment

### `no-script-on-slide`: do not put what you are about to say on the slide

Visual evidence plus spoken words beats visual evidence plus spoken words plus the same words on
screen. Reading your slide aloud measurably hurts what the audience retains (Mayer's redundancy
principle). Speaker notes are where the sentences go.

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

The top-level noise rule, and the best-evidenced one in the method: removing extraneous material
improves learning across every test of it. Signal-to-noise, data-ink, restraint — all the same move.

**Decided by** judgment

### `signaling`: cue the one thing that matters

Point the eye at the part of the evidence that carries the claim. The `accent` role is the signalling
channel; see `accent-is-attention`.

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

---

## 4. Legibility

### `type-scale`: type is sized for the back row, not the laptop

Fixed by the method, not by the brand and not per slide. On the logical canvas, body type sits at the
floor: it projects to roughly 34px at 1920, which is what the back row of a lecture hall can read.
The two dense sizes exist for tight figure panels and are marked exceptions, not knobs.

**Decided by** script · **Threshold** `canvas-width-px = 1280`, `body-px = 23`, `headline-px = 37`,
`dense-px = 18`, `dense-xs-px = 16`

### `fonts`: one text family, one mono family, both bundled

Inter for headings and body. JetBrains Mono for the locator and nothing else. Both are bundled and
registered with the figure toolchain, so a machine that lacks them cannot silently substitute a
fallback and leave the figures mismatched against the slides.

**Decided by** script · **Threshold** `font-text = Inter`, `font-mono = JetBrains Mono`

### `light-ground`: the colour scheme is light, and locked

Not a preference and not a per-viewer choice. Following the viewer's OS setting sets an ink-on-white
figure set against near-black and destroys the contrast the rest of the method depends on. A
validated dark ground would need every colour rule re-verified on it.

**Decided by** script · **Threshold** `color-scheme = light`

---

## 5. Colour

### `never-sole-channel`: colour never carries meaning alone

Every line series carries a distinct dash pattern and marker; bars carry direct labels. This is what
survives a grayscale photocopy, a bad projector, and the dichromacies the floor cannot fully cover.

**Decided by** script (generated figures, where the redundancy is structural) · judgment (hand-made
visuals and pasted images)

### `accent-is-attention`: the accent role marks attention, never data

An arrow, a highlight, "ours". Never a data series, and always with ink text on top of it rather than
light text.

**Decided by** script (generated figures) · judgment (hand-made visuals)

### `spend-colour-on-discrimination`: two groups by default, the full ramp only when earned

The default chart is a de-emphasised comparison group plus one highlight. Reach for the full
categorical ramp only when the message genuinely is a per-series comparison. Colour is spent where
the message needs discrimination, not by default.

**Decided by** judgment

### `decorative-neutral-never-text`: the softest neutral is not a text colour

It exists for rules, gridlines and ghost edges. Text on it fails contrast.

**Decided by** script (role usage)

### `separation-floor`: data colours stay perceptually separated under colour-vision deficiency

Every pair of data colours that can share one chart axis stays above the floor under normal vision
and all three dichromacies, simulated at full severity because that is the worst case. Grayscale is
measured the same way but is **advisory**: a grayscale pair below the floor is a warning, never a
failure, because `never-sole-channel` is the fix the method already mandates for it.

The floor is a **tunable design parameter**, grounded in the just-noticeable-difference literature,
not a physical constant. Comparison is inclusive, so a pair landing exactly on it passes. A palette
sitting exactly on the floor is at capacity: one more series will fail without retuning.

**Decided by** script · **Threshold** `delta-e-floor = 15.0`, `delta-e-metric = CAM02-UCS`,
`cvd-simulation = Machado 2009`, `cvd-severity = 100`,
`cvd-conditions = [normal, deuteranomaly, protanomaly, tritanomaly]`,
`grayscale = advisory` (violation when a pair's ΔE is below `delta-e-floor`)

---

## 6. Motion

### `motion-purpose`: motion segments or depicts, and does nothing else

Two uses earn motion. **Segmenting:** a speaker-paced reveal of one congruent chunk at a time, to
manage what the audience has to hold at once. **Process depiction:** the change over time *is* the
content. Both must be **apprehensible** (the eye can extract the structure in the time it is on
screen) and **congruent** (the motion's structure matches the idea's). Decorative motion, slide
transitions and entrance effects earn nothing. Animated graphics are not better than well-designed
static graphics; a reveal that splits a label from its referent in time is worse than either.

**Decided by** judgment

### `motion-ceiling`: fifteen seconds, maximum

**Decided by** script (where a duration is declared) · **Threshold** `animation-seconds-max = 15`
(violation when a declared animation runs longer than 15 seconds)

---

## 7. Voice

**Say it the way you would say it out loud.** Slides and prose written to sound impressive read as
machine-written, and they date fast. The durable tells are structural and rhythmic rather than a
word blacklist, so the rules below are split by who can decide them. This set is a **seed**,
deliberately extensible.

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

#### `no-contrast-for-emphasis`: no "not X, it's Y"

The construction manufactures emphasis by inventing a foil. State the claim.

#### `no-reflexive-tricolon`: three items because the claim has three

Not because three sounds complete. A padded third item is noise under `coherence`.

#### `no-hedging-or-boilerplate`: start at the claim, stop when it is proved

Cut the warm-up sentence that announces what you are about to say, and the closer that summarises
what you just said.

#### `rhythm-variety`: vary sentence length deliberately

Read it aloud. Fix anything you would not actually say.

#### `concrete-over-abstract`: prefer a number or a name to an abstraction

"Three series pass, and a fourth would fail" beats "demonstrates strong accessibility
characteristics".

---

## The flagship deck: 13 beats

The flagship deck is the **primary teaching artifact**: it teaches the method by being the method.
Each beat's headline is an assertion, and the slide self-demonstrates the rule it teaches. The
load-bearing rules get a beat of their own; the rest the deck obeys visibly, and this file states in
full.

| # | Beat (assertion headline) | Evidence / self-demonstration | Teaches |
|---|---|---|---|
| 1 | **legible-slides** · _Readable from the back row, and for every pair of eyes._ | Cover; the type scale and the brand from slide one | `type-scale` |
| 2 | _Most templates hand you files and leave the hard part to you: deciding what a slide is for._ | A busy stock-template slide | — |
| 3 | _Every template quietly fails two audiences you can measure: the back row, and 1-in-12 eyes._ | Projector-distance sketch beside a CVD-muddy 5-line chart | `type-scale`, `separation-floor` |
| 4 | _A method first, files second._ | The pivot; the thesis of the whole deck | — |
| 5 | _Every slide answers one question. If you can't state it, the slide is wrong._ | This slide answers exactly one | `one-message` |
| 6 | _The headline is the claim, not a label._ | The headline is a claim; label versus claim side by side | `assertion-headline`, `headline-shape` |
| 7 | _Decide the message before you reach for the chart._ | Message-before-visual, shown as an ordering | `message-before-visual` |
| 8 | _Cut everything that isn't the message._ | Signal-to-noise; a purposeful reveal doubles as the motion guardrail | `coherence`, `motion-purpose` |
| 9 | _Body type is sized for the back row, not your laptop._ | Body sits at the floor; the projection arithmetic on screen | `type-scale` |
| 10 | _If a colour dies under colour-blindness or grayscale, it's not in the palette._ | The 5-line chart under deuteranopia and grayscale, with dash and marker redundancy | `separation-floor`, `never-sole-channel` |
| 11 | _Your brand is a swappable layer that must pass the validator._ | The worked KU Leuven example plus the non-endorsement note | `separation-floor` |
| 12 | _Present in the tool you already use._ | Slidev and PowerPoint now, Keynote and Google Slides next, plus the coding-agent skill | — |
| 13 | _Everything you just watched was built to these rules._ | The close; a pointer to this file and a call to action | all of them |

Beats 2, 4 and 12 teach no rule: they carry the argument for why the rules exist. The anti-slop
rules in [§7](#7-voice) get **no beat** — the deck obeys them silently, because a slide dated to
"don't sound like AI" would age badly and pull focus from the timeless part of the method.

Structural notes the outline commits to: beat 13 reuses the cover layout rather than introducing a
closing layout (`no-section-dividers`), and beats 3, 6 and 10 are the two-column evidence slides.

---

## Where these rules came from

Pointers only. Each records where a rule came from or how it is measured; none of them is
authoritative over this file, and the research documents carry values as they were proposed at the
time.

- [`design-provenance.md`](design-provenance.md) — the decisions as they were argued out in the
  CAiSE 2026 deck this method was extracted from, with the issue trail and the author's own words.
- [`research/presentation-methods.md`](research/presentation-methods.md) — the evidence base: Alley
  and Neeley on assertion-evidence, Mayer on coherence, redundancy and segmenting, Tversky on
  animation, Tufte on chartjunk, Williams on layout.
- [`cvd-validator-contract.md`](cvd-validator-contract.md) — how `separation-floor` is measured, why
  the floor is where it is, and the retired `≥39` claim it replaces.
- [`token-contract.md`](token-contract.md) — the palette schema the colour rules are addressed to,
  and the split between what a brand may swap and what the method fixes.
- [`agent-skill-contract.md`](agent-skill-contract.md) — how an agent turns these rules into a
  review, and which of them gate a build.
