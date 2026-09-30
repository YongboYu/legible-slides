# The section locator: does it help, and where does it go

**Research question.** The method bans divider slides (`no-section-dividers`) and puts a persistent
locator on every content slide instead. Does that help an audience, and what form and placement
should it take?

> **Research input, dated 2026-09-30.** The rules this feeds (`ae-skeleton`, `no-section-dividers`,
> `signaling`, `type-scale`) live in [`docs/method.md`](../method.md), which is authoritative.

## Options compared (prototype, 2026-09-30)

- **Original:** navy filled pill, white uppercase mono, above the headline.
- **A · quiet top:** the same label as plain grey uppercase mono text above the headline.
- **B · footer:** the label in the footer, bottom left, opposite the page number.
- **C · section map:** `PROBLEM · APPROACH · EVALUATION · OUTLOOK` above the headline, the current
  section in navy and bold.

## Findings

**Structure cues help, most when the structure is complex or unfamiliar.** Headings and previews
improve recall of the content they cue (Lorch 1989), and the effect appears when the topic
structure is complex and unfamiliar (Lorch & Lorch 1996), which is the case for a research talk to
a mixed audience. In spoken multimedia lessons, section headings plus pointer words improved
transfer in all three experiments of Mautone & Mayer (2001). A meta-analysis of 103 studies
(N = 12,201) found signalling improves retention and transfer and lowers cognitive load, with no
moderation by prior knowledge (Schneider et al. 2018).

**Non-native listeners gain most from structure cues.** Discourse-structure signals significantly
help L2 lecture comprehension (Jung 2003). A visible label backs up a spoken signpost they may miss.

**The gap.** No controlled study was found on per-slide section labels, Beamer navigation bars or
progress bars in live talks. The case rests on signalling research in text and multimedia, so it
is an inference, not a measured result.

**The footer is where cues get lost.** Viewers start top-left and learn to skip regions that
usually carry nothing useful ("banner blindness",
[Nielsen Norman Group](https://www.nngroup.com/articles/banner-blindness-old-and-new-findings/)).
A footer next to the page number reads as boilerplate within a few slides. On a projected slide
the bottom edge is also the part most often hidden by heads or cut by a low screen, and older
adults have a narrower useful field of view (Ball et al. 1993). B's gain is aesthetic; its cost is
the navigation that replaces divider slides.

**The top costs little.** A quiet label directly above the headline is read in the same sweep as
the headline. The navy pill competes with the headline for the first look; the quiet form does not.

**Practice.** Alley recommends a mapping slide and signalled transitions; Beamer's metropolis
theme has an optional (off by default) progress bar and divider slides; Schwabish's *Better
Presentations* has a chapter on scaffolding slides; Duarte, Reynolds and TED-style talks rely on
verbal signposting. Across these, a structure cue is either repeated on screen or given as
dividers. None drops it entirely for technical audiences.

## Recommendation from the research

| Option | Verdict |
|---|---|
| A · quiet top label | adopt |
| B · footer | reject |
| C · section map | optional mode for talks with at most 5 short sections |
| thin progress bar with ticks | reject: "how much is left" without "where am I" |
| label only at section starts | reject: a late arriver has no cue |
| verbal signposting only | necessary, not sufficient; keep it in the speaker notes anyway |

Settings: 16px (the smallest size `type-scale` sanctions; A at 15px and B at 14px fall below it),
`--neutral` (6.1:1), never `--neutral-soft` (2.6:1). The section map allows at most 5 sections of
at most 10 characters, and marks the current one by weight **and** colour. A variant worth
considering is the single label with a position count: `RESULTS · 3/4`.

## Sources

- Lorch, R. F. (1989). *Educational Psychology Review* 1:209–234.
- Lorch, R. F., & Lorch, E. P. (1996). *Journal of Educational Psychology* 88:38–48.
- Mautone, P. D., & Mayer, R. E. (2001). *Journal of Educational Psychology* 93(2):377–389.
- Schneider, S., Beege, M., Nebel, S., & Rey, G. D. (2018). *Educational Research Review* 23:1–24.
- Jung, E. H. (2003). *Modern Language Journal* 87:562–577.
- Ball, K., Owsley, C., et al. (1993). The useful field of view test. *Optometry and Vision Science*.
- Alley, M., *The Craft of Scientific Presentations*, 2nd ed. (Springer, 2013).
- Schwabish, J. (2016). *Better Presentations*. Columbia University Press.
- Metropolis Beamer theme: <https://github.com/matze/mtheme>.
