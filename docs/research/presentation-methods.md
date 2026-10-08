# Presentation-design methods: what should inform the method canon

**Research ticket.** Beyond Assertion-Evidence, what established presentation-design
methods should inform **v1** of the `legible-slides` method canon — and which should be
deferred to **v2**?

This document surveys the reputable literature (books, peer-reviewed papers, author
sites), confirms what the project already asserts, and closes with an explicit
**v1-adopt vs. v2-defer** recommendation. It is descriptive research feeding the
wayfinder map; nothing here is settled until its ticket is.

> **Research input, dated.** The rules this document set out to sharpen — and the rules it
> recommends — now live in the canon, [`docs/method.md`](../method.md), which is authoritative on
> every one of them and owns their numbers. Read the values quoted here as what was proposed when
> the research ran, not as the rule.

The canon it sharpens was, at the time, the practice recorded in
[`docs/design-provenance.md`](../design-provenance.md): one message per slide, Assertion-Evidence,
the bullet and word ceilings, message before visual, the animation ceiling, standard terminology.

---

## 1. Assertion-Evidence — the method we already run, and its evidence

**Primary sources:** Michael Alley, *The Craft of Scientific Presentations*, 2nd ed.
(Springer, 2013); Alley & Neeley, "Rethinking the design of presentation slides: A case
for sentence headlines and visual evidence," *Technical Communication* 52(4), 2005; the
research base curated at [assertion-evidence.com](https://www.assertion-evidence.com/).

### The exact recipe (confirms and refines ours)

From the Penn State
[Assertion-Evidence checklist](http://www.writing.engr.psu.edu/AE_checklist.pdf) and
[instruction set](https://cpb-us-e1.wpmucdn.com/sites.psu.edu/dist/7/13153/files/2008/10/Assertion-Evidence-Slides-Instruction_Set.pdf):

- Every body slide opens with a **sentence-assertion headline** — a complete claim, not a
  topic phrase.
- The headline is **left-justified, ≤2 lines, ~28-point type, 8–14 words**.
- The body **supports that claim with visual evidence** — photographs, drawings, graphs,
  film, or *words and equations arranged visually* — and **avoids bulleted text lists**.
- One assertion per slide. If the headline isn't the takeaway, the slide has no message.

> **Fit with our canon:** this is exactly our model. Our word ceiling governs bullets and
> Alley's band governs the *headline*, so the two are compatible, and the tighter headline
> discipline (full sentence, ≤2 lines) is worth adopting.

### The evidence (this is why it is the foundation, not a preference)

- **Retention.** Alley, Schreiber, Ramsdell & Muffo (2006), "How the design of headlines
  in presentation slides affects audience retention," *Technical Communication* 53(2):
  audiences retained significantly more when slides used **sentence** headlines than
  **phrase/topic** headlines.
- **Comprehension & recall of complex concepts.** Garner & Alley (ASEE 2011),
  [*Assertion-evidence slides appear to lead to better comprehension and recall of more
  complex concepts*](https://peer.asee.org/assertion-evidence-slides-appear-to-lead-to-better-comprehension-and-recall-of-more-complex-concepts.pdf):
  two audiences heard the **same recorded ~6-minute talk** (how MRI detects cancerous
  tumors); **55** saw topic-subtitle slides, **56** saw assertion-evidence slides, tested
  immediately and again ~1 week later. The AE group scored higher on the harder
  comprehension/retention questions.
- **Cognitive load.** A study of **110 engineering students'** essay responses found the
  AE group showed **superior comprehension, fewer misconceptions, lower perceived
  cognitive load, and stronger delayed recall** (Penn State; see
  [pure.psu.edu](https://pure.psu.edu/en/publications/assertion-evidence-slides-appear-to-lead-to-better-comprehension--2/)
  and [writing.engr.psu.edu](https://writing.engr.psu.edu/ae_comprehension.pdf)).

**Rationale:** Alley grounds the method in **working-memory / cognitive-load theory** —
a phrase headline plus a wall of bullets forces the audience to *reconstruct* the
argument, whereas a sentence claim plus a congruent visual delivers it. This dovetails
directly with Mayer (§3) and with Tufte's bullet-point critique (§2).

---

## 2. Layout & visual hierarchy — Tufte and Robin Williams' CRAP

### Edward Tufte — spend ink on data, not decoration

**Primary sources:** *The Visual Display of Quantitative Information* (1983/2001); *The
Cognitive Style of PowerPoint* (2003/2006).

- **Data-ink ratio.** Maximize the share of "ink" that encodes data; erase non-data ink
  (heavy gridlines, boxes, backgrounds, 3-D effects). See
  [InfoVis:Wiki](https://infovis-wiki.net/wiki/Data-Ink_Ratio).
- **Chartjunk.** Moiré patterns, ornamental hatching, false perspective and "self-
  promoting" graphics obscure rather than reveal
  ([EU data-viz guide](https://data.europa.eu/apps/data-visualisation-guide/chart-junk-and-data-ink-origins)).
- **Small multiples.** A grid of the *same* small chart repeated across a variable lets
  the eye compare directly — a high-density, low-noise pattern.
- **Bullets are low-resolution.** In *The Cognitive Style of PowerPoint* Tufte argues
  bullet lists **can't express logical relationships** and flatten reasoning; his case
  study is the **NASA Columbia** slides, where a fatal foam-strike risk was buried in
  nested bullets ([review](https://www.rightattitudes.com/2016/06/10/the-cognitive-style-of-powerpoint/)).
  This is independent corroboration of the AE move away from bullets.

> **Evidence vs. taste — a caveat to record.** Strict data-ink *minimalism* is contested.
> Bateman et al. (2010) and Borkin et al. found that some "chartjunk" can **improve
> memorability/engagement** without hurting accuracy, and a 1994 study found some
> redundant non-data ink (e.g., tick marks) *helped*. So Tufte's direction is sound —
> **reduce noise** — but "erase everything non-data" is a heuristic, not a law. Adopt the
> direction; don't over-fit the ratio. (See
> [Frank Elavsky's critique](https://www.frank.computer/blog/2025/04/data-to-ink.html).)

### Robin Williams — CRAP as a layout checklist

**Primary source:** *The Non-Designer's Design Book* (1994; 4th ed. 2015). CRAP =
**C**ontrast, **R**epetition, **A**lignment, **P**roximity
([Saylor](https://saylordotorg.github.io/text_business-information-systems-design-an-app-for-that/s07-01-c-r-a-p-principles-of-graphic-.html)).

- **Contrast** — make different things look *clearly* different (size, weight, colour) to
  build hierarchy. (Our `accent-is-attention` role is a contrast rule already.)
- **Repetition** — reuse fonts, colours, layouts so the deck reads as one system. (Our
  token architecture + fixed Slidev layouts already enforce this.)
- **Alignment** — put nothing arbitrarily; every element lines up to an invisible grid.
- **Proximity** — group related items; separate unrelated ones, so structure is visible
  before it is read.

CRAP is craft heuristics with strong practitioner consensus but little controlled-trial
evidence; it is cheap, low-risk, and complements AE's "one message" by governing *how the
evidence is arranged*. **Whitespace / grid discipline** (leave empty space; don't fill
it) is the same idea and is echoed by Reynolds (§4).

---

## 3. Cognitive load & multimedia learning — Mayer, and the animation question

**Primary source:** Richard E. Mayer, *Multimedia Learning*, 2nd/3rd ed. (Cambridge);
Mayer & Fiorella, *Cambridge Handbook of Multimedia Learning*. Mayer's principles are the
**best-evidenced** body here — each is backed by meta-analysed experiments with reported
effect sizes.

Principles that bear directly on slide design (numbers per Mayer/Fiorella):

| Principle | Rule | Evidence |
|---|---|---|
| **Coherence** | Exclude extraneous words/pictures/sounds. | Supported **23/23** tests, median **d ≈ 0.86**. |
| **Signaling** | Add cues that highlight the *organization* of essential material. | Positive; guides attention without adding content. |
| **Redundancy** | Graphics + **spoken** words beat graphics + spoken + **on-screen text**. | Reading identical text aloud off a slide *hurts* learning. |
| **Segmenting** | Present in **learner-paced segments**, not one continuous dump. | Supported **10/10** tests, median **d ≈ 0.79**. |
| **Temporal contiguity** | Present corresponding words & pictures **simultaneously**, not in sequence. | Meta-analysis of 13 experiments, **d ≈ 0.87** favouring simultaneous. |

Sources:
[Cambridge Handbook ch.12](https://www.cambridge.org/core/books/abs/cambridge-handbook-of-multimedia-learning/principles-for-reducing-extraneous-processing-in-multimedia-learning-coherence-signaling-redundancy-spatial-contiguity-and-temporal-contiguity-principles/CD5B7AE1279A9AB81F8EEBB53DBEC86E),
[ch.13 segmenting](https://www.cambridge.org/core/books/abs/cambridge-handbook-of-multimedia-learning/principles-for-managing-essential-processing-in-multimedia-learning-segmenting-pretraining-and-modality-principles/DD24C2F48B9B1277CE59F78276110258),
[FCLD summary](https://www.hartford.edu/faculty-staff/faculty/fcld/_files/12%20Principles%20of%20Multimedia%20Learning.pdf).

**Why this matters for us:** Coherence, signaling and redundancy are the *evidence base
underneath* Assertion-Evidence and Tufte's noise-cutting — they say, in controlled trials,
that removing clutter and not duplicating the speaker's script on the slide **measurably
improves learning**. They are cheap to state as rules.

### Animation: when motion helps, and when it just distracts

This is the part the ticket flags, and the literature is unusually clear.

**The disappointing news about animation.** Tversky, Morrison & Bétrancourt (2002),
[*Animation: can it facilitate?*](https://hci.stanford.edu/courses/cs448b/papers/Tversky_AnimationFacilitate_IJHCS02.pdf)
(*Int. J. Human-Computer Studies* 57(4):247–262) reviewed the empirical record and found
**animated graphics are generally not superior to well-designed static graphics.** Where
animation *seemed* to win, the animated and static versions weren't equivalent — the
animation smuggled in extra information or interactivity. They propose two conditions an
animation must meet to help at all:

- **Apprehension principle** — the animation must be **accurately perceivable**. Most are
  too fast or too complex; the eye can't extract the structure in real time.
- **Congruence principle** — the animation's structure must **match** the structure of
  the idea. Motion for its own sake (spins, flies, dissolves) violates this.

**The encouraging news — progressive disclosure is different.** Mayer's **segmenting**
principle (d ≈ 0.79) says breaking a complex message into **learner-paced steps** helps.
On a slide, that is exactly what a *build* / progressive reveal does: show one part, then
the next, at the speaker's pace. So the evidence splits cleanly:

- **Supported:** animation as **segmenting** — revealing a complex slide **one congruent
  chunk at a time**, speaker-paced, to manage cognitive load; or animation that
  **literally depicts a process** whose change over time *is* the content (congruence).
- **Not supported / discouraged:** decorative motion, transitions, "entrance effects,"
  anything the audience can't apprehend in the time it's on screen, and anything that
  **separates a label from its referent in time** (temporal contiguity warns against
  splitting corresponding words and pictures across successive reveals).

> This is a precise, evidence-backed sharpening of our existing animation ceiling:
> **purposeful = segmenting or process-depiction that is apprehensible and congruent;
> everything else is noise.**

---

## 4. Presentation Zen (Reynolds) & slide:ology (Duarte) — the craft synthesis

**Primary sources:** Garr Reynolds, *Presentation Zen* (2008; 2nd ed. 2011); Nancy
Duarte, *slide:ology* (2008).

- **Reynolds — restraint, simplicity, naturalness.** His operational idea is the
  **signal-to-noise ratio**: every element on a slide is either signal (the message) or
  noise (everything else); **maximize signal, delete noise**
  ([O'Reilly excerpt](https://www.oreilly.com/library/view/presentation-zen/9780132901529/ch06lev1sec3.html)).
  Supporting heuristics: **use empty space** deliberately, and **align to the rule of
  thirds** ([garrreynolds.com](https://www.garrreynolds.com/design-tips)).
- **Duarte — visual thinking, slides as a distinct medium.** *slide:ology* is the
  systematic "technical manual": decide the message first, **storyboard** before building,
  treat slides as glance-media (not documents), and design one clear idea per slide.

**Evidence vs. taste — record this honestly.** Reynolds and Duarte are **synthesists**,
not experimenters. "Signal-to-noise," "simplicity," and "empty space" are re-statements of
Mayer's coherence and Tufte's data-ink in accessible, quotable form — their *value* is the
memorable framing, not independent evidence. Their more stylistic advice (full-bleed
photos, particular aesthetics) is **taste**, and taste that can fight our accessibility
floor (a full-bleed photo behind text can wreck contrast). **Adopt the framings that
restate the evidence; treat the aesthetics as optional, subordinate to the a11y floor.**

---

## RECOMMENDATION — v1 adopt vs. v2 defer

> **Outcome.** The v1 list below was adopted into [`method.md`](../method.md) as `headline-shape`,
> `coherence`, `no-script-on-slide`, `signaling`, `layout-discipline`, `figure-noise`,
> `motion-purpose` and `established-terminology`. One deviation: Alley's **8–14 word headline band
> landed as guidance rather than a threshold**, because several of the flagship's resolved beat
> headlines are shorter claims and a hard word gate would fail them. The canon keeps the two-line
> ceiling as the operative limit instead.

### v1 — adopt into the method canon now

Cheap-to-state rules that **sharpen the existing one-message / Assertion-Evidence method**
and are backed by evidence or strong consensus:

1. **Tighten the AE headline recipe** (Alley): headline is a **full-sentence claim**,
   **left-justified, ≤2 lines, 8–14 words**; body is **visual evidence, not bullets**.
   Confirms our model; makes the headline rule sharper than the word ceiling alone.
2. **Coherence / signal-to-noise as the top-level rule** (Mayer d ≈ 0.86; Reynolds;
   Tufte): if an element doesn't serve the slide's one message, **delete it**. This is the
   evidence-backed generalization of "one message per slide."
3. **Redundancy rule** (Mayer): **don't put the speaker's script on the slide as text** —
   visual evidence + spoken words. Reinforces the no-bullets stance with trial evidence.
4. **Signaling rule** (Mayer): cue the eye to the one thing that matters (our accent =
   `accent-is-attention` is already this; state it as a general rule).
5. **CRAP as the layout checklist** (Williams): Contrast, Repetition, Alignment,
   Proximity — plus **whitespace/grid discipline** (Reynolds). Cheap, low-risk, governs
   *how* the evidence is arranged. Our tokens + fixed layouts already deliver Repetition.
6. **Figure-noise rules** (Tufte): cut chartjunk, heavy gridlines, 3-D, and decoration;
   **maximize data-ink** — *as a direction, not a literal ratio* (note the memorability
   caveat). Already partly lived in the figure pipeline.
7. **Animation guardrail** (Tversky/Mayer): animation is allowed **only** when it is
   **segmenting** (speaker-paced progressive disclosure of congruent chunks) or **directly
   depicts a process**, and is **apprehensible + congruent**. **No decorative motion or
   transitions.** This is the evidence-backed reading of our animation ceiling.
8. **Standard terminology** (already canon; keep).

### v2 — defer

Things needing **implementation**, or lower-priority / more taste-dependent:

1. **A real build/animation system** — timed, speaker-paced reveal engine for
   progressive disclosure. The *rule* is v1 (#7); the *tooling* is v2.
2. **Small multiples as a first-class figure/layout pattern** (Tufte) — high value but
   requires figure-pipeline and layout work.
3. **Temporal-contiguity tuning** (Mayer, d ≈ 0.87) — keeping each label adjacent to its
   referent and syncing reveals with narration is per-slide craft; codify once the build
   system exists.
4. **Duarte's storyboard/visual-thinking workflow** — a *process*, not a slide rule;
   valuable as authoring guidance later, not a canon rule now.
5. **Tufte's "high-resolution handout / narrative companion"** — a strong idea (a written
   doc carrying the reasoning slides can't), but a separate deliverable, not a slide rule.
6. **Redundancy/modality nuance for self-running or narrated decks** — the on-screen-text
   trade-offs change when there's no live speaker; revisit if we support that mode.

---

## Sources

- Michael Alley, *The Craft of Scientific Presentations*, 2nd ed., Springer, 2013 —
  <https://link.springer.com/book/10.1007/978-1-4419-8279-7>
- Alley & Neeley (2005), "A case for sentence headlines and visual evidence,"
  *Technical Communication* — <http://writing.engr.psu.edu/2005_alley_neeley.pdf>
- Garner & Alley (ASEE 2011), "Assertion-evidence slides appear to lead to better
  comprehension and recall of more complex concepts" —
  <https://peer.asee.org/assertion-evidence-slides-appear-to-lead-to-better-comprehension-and-recall-of-more-complex-concepts.pdf>
- "How the design of presentation slides affects audience comprehension" (Penn State) —
  <https://writing.engr.psu.edu/ae_comprehension.pdf> ·
  <https://pure.psu.edu/en/publications/assertion-evidence-slides-appear-to-lead-to-better-comprehension--2/>
- Assertion-Evidence approach + checklist —
  <https://www.assertion-evidence.com/> · <http://www.writing.engr.psu.edu/AE_checklist.pdf>
- Edward Tufte, *The Visual Display of Quantitative Information* (data-ink, chartjunk,
  small multiples) — <https://infovis-wiki.net/wiki/Data-Ink_Ratio> ·
  <https://data.europa.eu/apps/data-visualisation-guide/chart-junk-and-data-ink-origins>
- Edward Tufte, *The Cognitive Style of PowerPoint* (bullets, Columbia) —
  <https://www.rightattitudes.com/2016/06/10/the-cognitive-style-of-powerpoint/>
- Data-ink minimalism critique (Elavsky) —
  <https://www.frank.computer/blog/2025/04/data-to-ink.html>
- Robin Williams, *The Non-Designer's Design Book* (CRAP) —
  <https://saylordotorg.github.io/text_business-information-systems-design-an-app-for-that/s07-01-c-r-a-p-principles-of-graphic-.html>
- Richard Mayer, *Multimedia Learning* / *Cambridge Handbook* (coherence, signaling,
  redundancy, segmenting, temporal contiguity) —
  <https://www.cambridge.org/core/books/abs/cambridge-handbook-of-multimedia-learning/principles-for-reducing-extraneous-processing-in-multimedia-learning-coherence-signaling-redundancy-spatial-contiguity-and-temporal-contiguity-principles/CD5B7AE1279A9AB81F8EEBB53DBEC86E>
  · <https://www.cambridge.org/core/books/abs/cambridge-handbook-of-multimedia-learning/principles-for-managing-essential-processing-in-multimedia-learning-segmenting-pretraining-and-modality-principles/DD24C2F48B9B1277CE59F78276110258>
- Tversky, Morrison & Bétrancourt (2002), "Animation: can it facilitate?",
  *Int. J. Human-Computer Studies* 57(4):247–262 —
  <https://hci.stanford.edu/courses/cs448b/papers/Tversky_AnimationFacilitate_IJHCS02.pdf>
- Garr Reynolds, *Presentation Zen* (signal-to-noise, simplicity) —
  <https://www.oreilly.com/library/view/presentation-zen/9780132901529/ch06lev1sec3.html>
  · <https://www.garrreynolds.com/design-tips>
- Nancy Duarte, *slide:ology* — visual thinking / storyboarding (book).

### Added by the 2026-09-30 audit of the method

- Naegle, K. M. (2021). Ten simple rules for effective presentation slides. *PLOS Computational
  Biology* 17(12): e1009554.
- Legge, G. E., & Bigelow, C. A. (2011). Does print size matter for reading? *Journal of Vision*
  11(5):8.
- Calabrèse, A., et al. (2016). *Investigative Ophthalmology & Visual Science* 57(8).
- Kosslyn, S. M., et al. (2012). PowerPoint presentation flaws and failures. *Frontiers in
  Psychology* 3:230.
- Barnett, A., & Doubleday, Z. (2020). The growth of acronyms in the scientific literature. *eLife*
  9:e60080.
- Richter, J., Scheiter, K., & Eitel, A. (2016). *Educational Research Review* 17:19–36.
- Rey, G. D., et al. (2019). A meta-analysis of the segmenting effect. *Educational Psychology
  Review* 31.
- Adesope, O. O., & Nesbit, J. C. (2012). Verbal redundancy in multimedia learning environments.
  *Journal of Educational Psychology* 104(1).
- Mayer, R. E., & Johnson, C. I. (2008). *Journal of Educational Psychology* 100(2).
- Montero Perez, M., Van Den Noortgate, W., & Desmet, P. (2013). *System* 41(3).
- AVIXA, DISCAS display-size standard —
  <https://www.avixa.org/standards/discas-calculators/discas/learn-more-about-display-size>
- SIGACCESS accessible presentation guide —
  <https://www.sigaccess.org/welcome-to-sigaccess/resources/accessible-presentation-guide/> ·
  W3C WAI — <https://www.w3.org/WAI/teach-advocate/accessible-presentations/>

### Colour

- Birch, J. (2012). Worldwide prevalence of red-green color deficiency. *JOSA A* 29(3) —
  <https://doi.org/10.1364/JOSAA.29.000313>
- Machado, Oliveira & Fernandes (2009). A physiologically-based model for simulation of color vision
  deficiency. *IEEE TVCG* 15(6):1291–1298 —
  <https://www.inf.ufrgs.br/~oliveira/pubs_files/CVD_Simulation/Machado_Oliveira_Fernandes_CVD_Vis2009_final.pdf>
