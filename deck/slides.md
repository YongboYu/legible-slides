---
# The theme by path, until the package is on npm. The canvas, the aspect ratio, the two bundled
# families and the locked light scheme all arrive with it, so this deck configures none of them.
theme: ../theme
title: legible-slides
author: Yongbo Yu
info: |
  The flagship deck. It teaches the method by being the method: fourteen beats, each one obeying the
  rule it is about, and the outline they follow is in docs/method.md.
# The slides, handed over on the cover and again on the close: a QR code to where they are shared,
# the link written out under it, and on the close how to reach the speaker. The code is generated for
# that link and committed, like the figures:
#   uvx segno https://github.com/YongboYu/legible-slides --error M --border 4 --light "#ffffff" \
#     --title "QR code to https://github.com/YongboYu/legible-slides" --no-xmldecl --no-size \
#     --output public/share-qr.svg
# No logos: the cover's two slots show the theme's placeholders, because this project ships nobody's
# mark. Presenting under a venue or an affiliation is dropping its mark into public/ and naming it
# here, as `venueLogo` or `affiliationLogo`. The footer shows the map of this talk's four sections,
# which is the theme's default; `locator: label` would show the current one with its position.
themeConfig:
  shareQr: /share-qr.svg
  shareUrl: https://github.com/YongboYu/legible-slides
  contact: Yongbo Yu · github.com/YongboYu
# The first frontmatter block is the cover's as well as the deck's, which is why the cover's own
# props sit here. `author` is not among them: Slidev keeps that word for the headmatter, so the
# layout reads `speaker`, and falls back to the author above when a deck omits it.
layout: cover
speaker: Yongbo Yu
venue: KU Leuven · Research Centre for Information Systems Engineering
# The palette every colour on these slides comes from, and the floor it cleared to get here:
#   uv run --project ../python cvd-validate ../themes/leuven-blue.json
---

# legible-slides

## Readable from the back row, and for every pair of eyes.

---
layout: answer
---

# A method decides what each slide is for, and two commands hold every slide to it.

::questions::

1. What is a slide for?
2. Can the back row, and every pair of eyes, read it?
3. How does the method reach your own deck?

<!--
That headline is the whole talk. Everything after it is the case for it, in the order of these three
questions, and the last slide answers them by the same numbers. Point at the QR code on the cover if
anyone missed it: the slides are already on their phones.
-->

---
layout: two-col-evidence
ratio: 3fr 2fr
section: Problem
---

# Most templates hand you files and leave the hard part to you: deciding what a slide is for.

::left::

<!-- A picture of a slide rather than a slide: it is evidence, and its markup and its scale both
     live in style.css. The bullets are `li` elements because they are part of the picture, not
     content this deck is making. -->
<div class="demo-stock" aria-hidden="true">
  <div class="demo-stock-head">
    <span class="demo-stock-logo">LOGO</span>
    <span class="demo-stock-deco"></span>
  </div>
  <div class="demo-stock-title">Background, Method and Results</div>
  <ul class="demo-stock-list">
    <li>Motivation and context</li>
    <li>Related work</li>
    <li>Research questions</li>
    <li>Datasets and preprocessing</li>
    <li>Model architecture</li>
    <li>Experimental setup</li>
    <li>Results and ablations</li>
    <li>Threats to validity</li>
    <li>Discussion</li>
    <li>Conclusions and future work</li>
  </ul>
  <div class="demo-stock-footer">
    <span>Author · Institution · 2026</span>
    <span>Slide 14 of 42</span>
  </div>
</div>

<p class="demo-caption">A conference slide, built exactly as its template allows.</p>

::right::

<Callout title="What the files cannot decide">

Which one question this slide answers. No master, colour theme or font stack settles it, and a slide
that has not settled it grows until it is three slides wearing one page number.

</Callout>

<!--
Signpost: first the problem, then the method, then what it does for legibility, then how it ships.

Ask the room what their template handed them last time. Masters, a colour theme, a logo in the
corner. Nobody has ever been given the decision about what a slide is for, and that is the decision
that costs you the evening.
-->

---
layout: two-col-evidence
---

# Every template quietly fails two audiences you can measure: the back row, and 1-in-12 eyes.

::left::

<div class="demo-type">
  <div class="demo-type-row">
    <span class="demo-type-label">12 px: shrunk until it fits</span>
    <span class="demo-type-shrunk">Shrink the body type and everything fits.</span>
  </div>
  <div class="demo-type-row">
    <span class="demo-type-label">23 px: the body size, held</span>
    <span class="demo-type-body">Hold the body size and the back row reads it.</span>
  </div>
</div>

Whatever is projecting these slides is projecting both samples, so the room settles this one rather
than the arithmetic. Red-green deficiency reaches about one man in twelve of European
ancestry<sup>1</sup>, and no template checks for that either.

<Footnotes>
  <Footnote :number="1">Birch (2012), on worldwide prevalence: about 8% of men and 0.4% of women of European ancestry.</Footnote>
  <Footnote :number="2">Machado, Oliveira and Fernandes (2009), the simulation this deck and its validator both use.</Footnote>
</Footnotes>

::right::

<Figure
  src="/colour-alone.png"
  caption="Ten pairs of data colours, measured under four conditions, as deuteranomaly receives them. Colour is the only thing telling the five lines apart."
  :cite="2"
/>

<!--
Two numbers, both measurable, both left to the author by every template I have used. Read the small
sample aloud from the back if anyone thinks it is fine. On the right is this deck's own palette,
simulated at full severity, with the dash and the marker taken off the chart it draws later.
-->

---
section: Method
---

# The method comes first, and the files are only what it ships as.

| The method decides | What holds it to that |
|---|---|
| what a slide is for | a reviewer, human or agent |
| how far apart data colours stay | `cvd-validate`, on any palette |
| how much may go on one slide | `legible lint`, on every push |
| what type the back row can read | the theme, which fixes the scale |
| what a figure is made of | the palette, regenerated and never redrawn |

<Callout accent title="Why that order">

Files without a method are a look. A method without files is advice.

</Callout>

<!--
Signpost: that was the problem, so now the method, one rule a slide.

Here is the pivot. Everything before it is the problem, and everything after it is one rule and its
demonstration. Swap the palette and every row above survives it, which is the test of which half was
load-bearing.
-->

---

# Every slide answers one question, and if you cannot state it the slide is wrong.

<Callout title="The question this slide answers">

What is a slide *for*?

</Callout>

Assertion-evidence gives a slide one claim and the evidence that proves it<sup>3</sup>. Compressing
three messages onto one saves building the other two, then spends longer than that in the
explaining, and the room is behind by the time you are done<sup>4</sup>.

<Footnotes>
  <Footnote :number="3">Alley and Neeley (2005), on sentence headlines and visual evidence.</Footnote>
  <Footnote :number="4">Mayer, on coherence: what does not serve the message costs the message.</Footnote>
</Footnotes>

<!--
Say the question out loud before the slide is on screen, then let the slide answer it. The beat is
the method's first rule and its own demonstration: one claim, two sentences of evidence, nothing
else on the canvas.
-->

---
layout: two-col-evidence
---

# The headline is the claim, not a label.

::left::

<Callout title="A label">

Results

</Callout>

Someone who reads only this knows the slide is about results, and knows nothing.

::right::

<Callout accent title="A claim">

Three series pass, and a fourth would fail without retuning.

</Callout>

Someone who reads only this already has the finding, and the slide has only to prove
it<sup>5</sup>. Eight to fourteen words is the band, and two rendered lines is the ceiling this
headline is sitting inside.

<Footnotes>
  <Footnote :number="5">Alley, Schreiber, Ramsdell and Muffo (2006): audiences retained more from sentence headlines than from topic phrases.</Footnote>
</Footnotes>

<!--
Read the two boxes in order and stop. One of them told you something. A deck whose headlines read as
a paragraph on their own has an argument; a deck whose headlines read as a table of contents has a
filing system.
-->

---
layout: two-col-evidence
---

# A slide's message is chosen before its chart, never the other way round.

::left::

1. State the one question the slide answers
2. Find the evidence that answers it
3. Write the claim it proves, as the headline

::right::

<Callout accent title="The failure this order prevents">

A chart turns up first, a caption gets invented to justify it, and the slide ends up being about
whatever the chart happened to show.

</Callout>

Reaching for the visual first is how a deck acquires slides nobody can state the point of, and they
are the hardest ones to cut later.

<!--
Everyone has done the other order. You have a figure from the paper, it looks like a slide's worth
of work, and a heading gets written to cover it. Three steps, and the first one is a sentence you
say out loud before anything gets drawn.
-->

---

# Whatever does not serve the one message is costing you the message.

Removing extraneous material improves learning in every test of it, which is what makes this the
best-evidenced rule in the method<sup>4</sup>. Spending ink on data rather than on decoration is the
same move, applied to a figure<sup>6</sup>.

<v-click>

<Callout accent title="Why that box arrived on a click">

Motion earns a place two ways and no others: it segments what you would otherwise have to hold all
at once, or the change over time is itself the content<sup>7</sup>. Decoration is neither, and this
one reveal is the whole animation budget of the deck.

</Callout>

</v-click>

<Footnotes>
  <Footnote :number="4">Mayer, on coherence and on segmenting a reveal to the speaker's pace.</Footnote>
  <Footnote :number="6">Tufte, on data ink and chartjunk.</Footnote>
  <Footnote :number="7">Tversky, Morrison and Bétrancourt (2002): animation helps when it is apprehensible and congruent, and not otherwise.</Footnote>
</Footnotes>

<!--
Pause before the click. Ask what a second box could be for, then let it answer: it is here because
the rule about cutting applies to time as well as to space. Segment what the room has to hold, and
depict a process that genuinely changes. Nothing else.
-->

---
section: Legibility
---

# Body type is sized for the back row, not for your laptop.

<Callout title="The arithmetic, worked">

Body type is fixed at 23 px on this deck's 1280 × 720 canvas, and the canvas is scaled to fill the
screen, so what matters is its share of the image height: 23 ÷ 720 = 3.2%, on any projector. By the
AV industry's sizing rule that reads to about 4.5 image heights, so a screen 2 m tall carries it
2 × 4.5 = 9 m: a seminar room or a conference session.

</Callout>

Nothing goes below 18 px: not a caption, a legend or the page number. A bigger room raises the
body size rather than lowering anything, and cuts what the slide carries.

<!--
Signpost: those were the rules about what goes on a slide, and next is whether the room can see it.

Fixed by the method, not by the palette and not per slide. Once type becomes a knob, every slide that
runs one line long gets solved the same way, and the room pays for it at the back. A lecture hall
sits past where this scale reaches: share the slides by QR code, ask for a second screen. Whatever
the room, do the distance check in the method before the talk.
-->

---
layout: two-col-evidence
---

# If a colour dies under colour-blindness or in grayscale, it is not in the palette.

::left::

<Figure
  src="/redundant-deuteranomaly.png"
  caption="The same ten pairs under deuteranomaly, which is the binding condition here: the closest pair lands on 15.0, exactly the floor."
  :cite="2"
/>

::right::

<Figure
  src="/redundant-grayscale.png"
  caption="The same chart in black and white, where the closest pair falls to 10.9. Dash and marker are what keep it readable."
/>

<!--
Same chart as the third slide, same palette, same simulation, and source 2 again for it. What changed
is that every line got a dash and a marker of its own, and the archetype assigns both by position so
an author cannot decline them. Grayscale stays advisory for exactly that reason: redundant encoding
is already the fix.
-->

---

# The validator reads any palette file, yours included, and names the pair that fails.

| Theme | closest pair, ΔE | in grayscale | verdict |
|---|---|---|---|
| `leuven-blue` | 15.0 | 10.9 | passes, and is at capacity |

Measured over the per-series ramp, under normal vision and all three dichromacies at full severity.
Yours is `cvd-validate your-palette.json`, and no slide in this deck names a colour.

<Callout title="Not an endorsement">

This palette is inspired by KU Leuven's house colours. It is not affiliated with or endorsed by the
university, and the theme file carries that sentence in its own description.

</Callout>

<!--
Read the last column. At capacity means a fourth series in this ramp fails, and the validator says
so by role rather than quietly reusing a colour. Run it on your own palette file before a talk: a
pass is the floor cleared, and a fail tells you which colour to move.
-->

---
section: Delivery
---

# One file is the slides on screen, the PDF you hand out and the deck an agent reviews.

| Delivery | Where it stands |
|---|---|
| this Slidev theme, and this deck | shipped, and on the screen |
| a PDF to present from | `slidev export`, from the same file |
| a skill for coding agents | shipped: it scaffolds a deck and reviews one |

<Callout accent title="Why only one">

Every output reads the same markdown, so none of them can fall out of step with the others.

</Callout>

<!--
Signpost: last part, which is how all of this reaches your own deck.

Say why there is no PowerPoint master. An export is one screenshot per slide, and a hand-kept twin
drifts from the deck it copies the first time either one changes.
-->

---
layout: conclusion
---

# Everything you just watched was built to the rules it was teaching you.

::answers::

1. One question per slide, and its answer is the headline
2. Type sized for the room, colours measured under colour-vision deficiency
3. One markdown file, with `legible lint` and `cvd-validate` on every push

<!--
Leave this slide up through the questions: it is the one the room reads while they ask. Each answer
closes the question with the same number on the second slide. Say thank you aloud rather than on a
slide, and point at the code for the slides and the rules, which all live in docs/method.md.
-->

---
layout: references
# After the close and outside the talk's four sections, so the footer shows this section's own name
# and no position among them.
section: Sources
backup: true
# Numbered by position, which is what a `Footnote` marker earlier in the deck points at.
#
# No URI on any of them, though the layout takes one. A sources slide is for attribution; retrieval
# is what a search box is for, and seven of these with a link under each runs past the slide's bottom
# edge. The links for the presentation-method and colour-simulation sources are in
# docs/research/presentation-methods.md and docs/research/cvd-validator.md; the prevalence figure is
# Birch (2012), https://doi.org/10.1364/JOSAA.29.000313.
indexEntries:
  - title: 'Birch, J. (2012) — Worldwide prevalence of red-green colour deficiency, JOSA A 29(3)'
  - title: 'Machado, Oliveira and Fernandes (2009) — Simulation of colour vision deficiency, IEEE TVCG'
  - title: 'Alley, M. and Neeley, K. A. (2005) — Rethinking the design of presentation slides'
  - title: 'Mayer, R. E. — Multimedia Learning, Cambridge University Press'
  - title: 'Alley, Schreiber, Ramsdell and Muffo (2006) — How headline design affects retention'
  - title: 'Tufte, E. R. — The Visual Display of Quantitative Information, Graphics Press'
  - title: 'Tversky, Morrison and Bétrancourt (2002) — Animation: can it facilitate?'
---

# Every claim these slides make came from somewhere, and here is where.
