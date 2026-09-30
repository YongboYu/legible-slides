# The attention colour: keep the orange, split it by job

**Research question.** Should `#dd8a2e` stay the template's single highlight (attention) colour, or
is there a better choice for an academic talk seen by a mixed-age audience, some with colour-vision
deficiency (CVD), on a projector?

> **Research input, dated 2026-09-30.** The rules this feeds (`signaling`, `accent-is-attention`,
> `never-sole-channel`, `separation-floor`) live in [`docs/method.md`](../method.md), which is
> authoritative. Read the values here as what the research found, not as the rule.

## Verdict

Keep `#dd8a2e` as the only attention hue, but give it two tokens, because no single orange can
do both jobs on a white ground:

| Token | Hex | Job | Contrast |
|---|---|---|---|
| `accent` | `#dd8a2e` | **fills only**, with ink text on top (callout pills, badges) | ink on it 5.40:1 |
| `accent-strong` | `#b3541e` | **text and strokes** (arrows, circles, a highlighted numeral) | 5.00:1 on white, 4.65:1 on `surface-alt` |

`#dd8a2e` as text or a thin stroke is 2.71:1 on white. That fails WCAG AA even for large text
(3:1), fails WCAG 1.4.11 for graphics, and is the first thing a washed-out projector loses.
Contrast values were rechecked with the WCAG 2.x luminance formula.

## Why not change the hue

- **It is KU Leuven's own accent.** The house-style colour page lists `#DD8A2E` as the one warm
  colour ("Links:hover / accentkleur"); everything else there is blue: logo `#00407A`, `#52BDEC`;
  grid `#1FABD5`, `#1D8DB0`, `#116E8A`
  ([KU Leuven huisstijl — kleuren](https://associatie.kuleuven.be/huisstijl/kleuren); checked
  2026-09-30). Navy plus amber is the institution's pairing, not a generic "AI" choice.
- **Orange is the best pop-out against blue.** Hue is a pre-attentive feature, and pop-out grows
  with the target's distance from its distractors and shrinks as the distractors vary
  (Treisman & Gelade 1980; Duncan & Humphreys 1989; Healey & Enns 2012). On a blue slide, orange
  sits opposite every distractor at once. A second blue or the teal as the highlight would join
  the distractor set.
- **The CVD separation is wide.** Under Machado 2009 simulation at full severity, in CAM02-UCS ΔE,
  `#dd8a2e` stays at least 27 from every palette colour (floor 15). The tightest pair is teal
  `#57c0ae` under protanopia. `#b3541e` does better (min 33.7).
- **Older eyes.** Lens yellowing produces a tritan-like loss of blue/yellow discrimination
  (Pokorny, Smith & Lutze 1987). Orange against navy separates by lightness and the red–green
  difference, so it survives (tritan ΔE vs navy 59.7). Pale orange or yellow on white does not.

## Candidates considered

| Hex | Text on white | Ink on it | Worst CVD ΔE | Verdict |
|---|---|---|---|---|
| `#dd8a2e` | 2.71 | **5.40** | 27.0 | keep, fills only |
| `#b3541e` | **5.00** | 2.93 | 33.7 | add, text and strokes |
| `#c8551b` | 4.40 | 3.33 | 33.2 | strokes and large text only; just misses 4.5 for body |
| `#d55e00` (Okabe-Ito vermilion) | 3.87 | 3.79 | 34.0 | works fully in neither role; off-brand |
| `#b06400` (same hue, darkened) | 4.50 | — | — | reads as brown, not "attention" |
| no hue (weight, size, ink on grey) | — | — | — | safest in grayscale, but gives up the fastest pop-out; keep as the fallback cue |

## How the highlight works, and when it stops working

- **Signalling works, but the effect is modest.** Meta-analyses find r ≈ .17
  (Richter, Scheiter & Eitel 2016, *Educ. Res. Rev.* 17) and benefits for retention and transfer
  (Schneider et al. 2018, *Educ. Res. Rev.* 23), largest for learners new to the topic.
- **Isolation is the mechanism.** The von Restorff effect holds only while the item stays isolated
  (Hunt 1995). Two or three orange items per slide already dilute it; a colour on every slide (the
  old headline bar) teaches the audience to ignore it.
- **Grayscale.** The accent's lightness (L\* 65) sits near muted, brand-strong and teal, so in a
  grayscale printout it is just mid-grey. The shape or weight has to carry it too.
- **Practitioners agree:** grey by default and one saturated hue for "the thing"
  ([Datawrapper](https://www.datawrapper.de/blog/emphasize-with-color-in-data-visualizations));
  small spots of intense colour on a muted field (Tufte, *Envisioning Information*, 1990); orange
  or vermilion against blue as the canonical CVD-safe contrast
  ([Okabe & Ito](https://jfly.uni-koeln.de/color/), [Paul Tol](https://personal.sron.nl/~pault/)).

## Proposed usage

1. `accent` is a fill with ink text on it; `accent-strong` is for text and strokes. Raw `#dd8a2e`
   is never text or a thin stroke.
2. One attention locus per slide: one pill, or one arrow plus the circle it points to, or one
   highlighted numeral.
3. Strokes at least 3px on the 1280×720 canvas.
4. Always paired with a second cue: weight, shape or position (`never-sole-channel`).
5. Never a data series (`accent-is-attention`).
6. Orange body text is the rarest use; prefer a pill or a bold ink numeral.

## Sources

- Treisman & Gelade (1980), *Cognitive Psychology* 12:97–136.
- Duncan & Humphreys (1989), *Psychological Review* 96:433.
- Healey & Enns (2012), *IEEE TVCG* 18(7):1170–1188.
- Hunt (1995), *Psychonomic Bulletin & Review* 2:105.
- Pokorny, Smith & Lutze (1987), *Applied Optics* 26:1437.
- Richter, Scheiter & Eitel (2016), *Educational Research Review* 17:19–36.
- Schneider, Beege, Nebel & Rey (2018), *Educational Research Review* 23:1–24.
- Alley, *The Craft of Scientific Presentations*, 2nd ed. (Springer, 2013).
