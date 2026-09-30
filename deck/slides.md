---
# The theme by path, until the package is on npm. The canvas, the aspect ratio, the two bundled
# families and the locked light scheme all arrive with it, so this deck configures none of them.
theme: ../theme
title: legible-slides
author: Yongbo Yu
info: |
  The flagship deck. It teaches the method by being the method: thirteen beats, each one obeying the
  rule it is about, and the outline they follow is in docs/method.md.
themeConfig:
  # A brand's mark is the deck's to serve, from its own public/, so the file below is a copy of
  # themes/logos/kuleuven-liris.png rather than a reference to it. Nothing wires the two together:
  # a deck that changes its mark changes this line and that file, and the theme file's meta.logo
  # records which mark the palette considers its own.
  logo: /kuleuven-liris.png
# The first frontmatter block is the cover's as well as the deck's, which is why the cover's own
# props sit here. `author` is not among them: Slidev keeps that word for the headmatter, so the
# layout reads `speaker`, and falls back to the author above when a deck omits it.
layout: cover
speaker: Yongbo Yu
venue: KU Leuven · Research Centre for Information Systems Engineering
# The palette every colour on these slides comes from, and the floor it cleared to get here:
#   uv run --project ../python cvd-validate ../themes/kuleuven.json
---

# legible-slides

## Readable from the back row, and for every pair of eyes.

---
layout: two-col-evidence
ratio: 3fr 2fr
locator: The problem
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
    <span class="demo-type-label">12 px on the canvas → 18 px projected at 1920</span>
    <span class="demo-type-shrunk">Shrink the body type and everything fits.</span>
  </div>
  <div class="demo-type-row">
    <span class="demo-type-label">23 px on the canvas → 34 px projected at 1920</span>
    <span class="demo-type-floor">Hold the floor and the back row reads it.</span>
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
locator: The method
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
Here is the pivot. Everything before it is the problem, and everything after it is one rule and its
demonstration. Swap the palette and every row above survives it, which is the test of which half was
load-bearing.
-->

---
locator: The rules
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
locator: The floor
---

# Body type is sized for the back row, not for your laptop.

<Callout title="The arithmetic, worked">

Body type is fixed at 23 px on this deck's 1280 px canvas. A projector running at 1920 renders it at
23 × 1920 ÷ 1280 = 34 px, which is what the back row of a lecture hall can read.

</Callout>

Two smaller sizes exist, 18 px and 16 px, and both are marked exceptions for a figure panel too
narrow for body type. Neither is a knob for fitting more onto a slide. This paragraph is set at the
floor, which is how you can check the claim without taking my word for it.

<!--
Fixed by the method, not by the brand and not per slide. Once type becomes a knob, every slide that
runs one line long gets solved the same way, and the room pays for it at the back.
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
locator: Your brand
---

# Your brand is a swappable layer, and it has to pass the validator to ship.

| Theme | closest pair, ΔE | in grayscale | verdict |
|---|---|---|---|
| `kuleuven` | 15.0 | 10.9 | passes, and is at capacity |
| `neutral` | 25.4 | 11.8 | passes, with room to spare |

Measured over the per-series ramp, under normal vision and all three dichromacies at full severity.
Swapping is one theme file and one command, and no slide in this deck names a colour.

<Callout title="Not an endorsement">

These slides wear a palette derived from KU Leuven's house style. Nothing here is an official KU
Leuven product, and the theme file carries that sentence in its own description.

</Callout>

<!--
Read the last column. At capacity means a fourth series in the KU Leuven ramp fails, and the
validator says so rather than quietly reusing a colour. That is the number to hand someone who asks
whether they can add one more.
-->

---
locator: Deliveries
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
Say why there is no PowerPoint master. An export is one screenshot per slide, and a hand-kept twin
drifts from the deck it copies the first time either one changes.
-->

---
locator: The close
---

# Everything you just watched was built to the rules it was teaching you.

Every rule sits in one file, `docs/method.md`, and every number it turns on is quoted from there
rather than copied. Both commands below run on every push, and a finding either of them calls an
error turns the build red.

```bash
legible lint slides.md --theme ../themes/kuleuven.json
cvd-validate ../themes/kuleuven.json
```

<Callout accent title="Take it">

Point a deck at the theme, run those two lines against your own palette, and when you disagree with a
rule, change the one file the rule lives in: [github.com/YongboYu/legible-slides](https://github.com/YongboYu/legible-slides)

</Callout>

<!--
Close on the commands rather than on thanks. What you have just watched is lint-green, and its
palette is measured in the same pipeline: nothing on any of these slides was exempt.
-->

---
layout: references
locator: Sources
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
