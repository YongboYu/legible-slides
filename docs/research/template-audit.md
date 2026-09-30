# Audit: the method and the CAiSE deck against presentation research

**Research question.** Judged against the template's purpose (academic talks that are clear and
efficient, work for audiences of diverse backgrounds and ages, stay content-driven and concise,
and respect cognitive load and the attention budget), what does the method get right, and what
should change?

> **Research input, dated 2026-09-30.** Audited: [`docs/method.md`](../method.md) and the CAiSE
> 2026 deck the template is distilled from (the `pmf-tsfm` slides). Slide numbers (S1–S20) refer to
> that deck. The method is authoritative; the proposals here are not rules until the canon adopts
> them.

## What the template already gets right

- `assertion-headline`, `headline-shape`: Alley's recipe, with trial evidence; Naegle's
  "Ten simple rules" say the same (Naegle 2021, *PLOS Comp Bio*).
- `one-message`: Naegle's rule 1.
- `coherence`, `figure-noise`: data-ink as a direction rather than a ratio to maximise.
- Mayer's pre-training principle in practice: terms are defined before the results that need them,
  and acronyms are spelled out on first use.
- `never-sole-channel` and `separation-floor` handle CVD well; alt text is on almost every image.
- Speaker notes that open with the slide's question, give a time budget, script the transitions and
  record what not to say. Worth making the template's standard.
- Backups are clearly marked and each answers a likely question.

## Gaps, ranked by impact

**G1. Type is too small for large halls and older eyes.** The `type-scale` rationale ("23px
renders at ~34px on a 1920 projector") does not measure legibility: scaling does not change a
letter's share of the image height. By the AV-industry sizing rule
([AVIXA DISCAS](https://www.avixa.org/standards/discas-calculators/discas/learn-more-about-display-size)),
23px body text is legible to about 4.6× the image height and 14px captions to about 2.8×, while
teaching rooms are planned to 6×. In visual angle at 6×, body x-height is about 0.17°, below the
~0.2° critical print size for full reading speed (Legge & Bigelow 2011), which rises with age
(Calabrèse et al. 2016). The deck also goes below its own dense floor (13–16px table headers,
captions, legends and axis labels). **Proposed:** state the scale as a share of image height; body
about 28px; no text under 20px, figure text included; check computed sizes, not class names.

**G2. The density ceilings never fire.** `bullet-ceiling` and `word-ceiling` count bullets; the
deck's slides are HTML blocks. S2 carries a table, two diagrams, two callouts and four defined
terms. Naegle advises at most about 6 elements per slide; Kosslyn's capacity principle puts working
limits near four chunks (Kosslyn et al. 2012). **Proposed:** an element ceiling (about 6 visual
groups) and an on-slide word budget (about 40 words outside figures and the headline), both
checkable against the rendered page.

**G3. No clear opening or close.** The research questions arrive at S10 (about minute 8), the first
result at S13. The takeaways skip one research question's answer; a "Thank you / Questions" slide
hides them through Q&A. Alley advises a conclusion slide with "Questions" at its foot, left up
during Q&A. **Proposed:** answer-first (the result and the questions by about minute 2) and a
conclusion that answers each question and stays up through Q&A.

**G4. Pace and acronyms.** The notes' time budgets add to about 19.2 minutes for a 20-minute slot.
By S16 the audience holds eleven acronyms; acronyms measurably hinder understanding (Barnett &
Doubleday 2020, *eLife*). **Proposed:** a pace budget (notes at most 85% of the slot) and an
acronym budget (about five new ones per talk).

**G5. Emphasis overuse.** Several slides bold something in nearly every line; there are 12 accent
callouts across 9 main slides. Signalling works when it is rare (Richter et al. 2016).
**Proposed:** a signal budget of one emphasised span and one callout per slide. See also
[`accent-colour.md`](accent-colour.md).

**G6. Motion.** A deck-wide `slide-left` transition breaks `motion-purpose`; 11 of 18 content
slides use click reveals, several of which only hide a conclusion the headline already states.
Segmenting evidence (Rey et al. 2019) supports splitting complex material, not hiding a punchline.
**Proposed:** no transition; a reveal only when each step adds evidence; the final build state is
the exported page.

**G7. Text in the forbidden grey.** Captions and the page number use `--neutral-soft` (2.6:1),
which `decorative-neutral-never-text` bans. **Proposed:** `--neutral` (6.1:1).

**G8. Accessibility beyond colour.** No shared slides or handout, no captions on the screencast, an
unlabelled SVG figure, and an untagged PDF export
([SIGACCESS guide](https://www.sigaccess.org/welcome-to-sigaccess/resources/accessible-presentation-guide/),
[W3C WAI](https://www.w3.org/WAI/teach-advocate/accessible-presentations/)).
**Proposed:** a QR code to the slides on the first and last slide; captioned media.

**G9. Smaller.** Prose lines run to about 95 characters (45–75 recommended); a 24-number table
whose claim has no comparison column on the slide; all-caps labels (Naegle rule 7); two backup
headlines with em-dashes; two headlines that are labels, not claims.

## Where the method overstates the evidence

1. **`no-script-on-slide`.** A meta-analysis of 57 studies found spoken plus written beats spoken
   alone for system-paced material and low-prior-knowledge audiences (Adesope & Nesbit 2012); short
   key-term labels next to a graphic improve retention (Mayer & Johnson 2008); captions help L2
   listeners (Montero Perez et al. 2013). Better: no full sentences of script, but do show key terms.
2. **The anti-summary voice rule.** Fine for prose, but a talk's recap and conclusion are
   structural signals. Exempt the opening and the close.
3. **The `type-scale` rationale.** See G1.
4. **`motion-purpose` citing segmenting for speaker-paced reveals.** The evidence is about narrated
   multimedia split into coherent segments, not hiding callouts.
5. **`coherence` "across every test".** The tally is from Mayer's own lab: well supported, not
   universal.

## Sources

- Naegle, K. M. (2021). Ten simple rules for effective presentation slides. *PLOS Computational
  Biology* 17(12): e1009554.
- Legge, G. E., & Bigelow, C. A. (2011). *Journal of Vision* 11(5):8.
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
- Alley, M., *The Craft of Scientific Presentations*, 2nd ed. (Springer, 2013).
