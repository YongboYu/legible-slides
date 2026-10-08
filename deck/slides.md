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

## Slides that everyone in the room can read, back row included.

---
layout: answer
---

# A short set of rules shapes each slide, and two commands check the deck against them.

::questions::

1. What is each slide for?
2. Can everyone in the room read it?
3. How can you use this in your own deck?

<!--
Here's the short version of the whole talk. We'll take these three questions in order, and the
last slide answers them with the same numbers. You'll find the QR code from the cover on the last
slide too, and the slides are already online.
-->

---
layout: two-col-evidence
ratio: 3fr 2fr
section: Problem
---

# Most templates set the colors and fonts, and leave you to decide what each slide says.

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

<p class="demo-caption">A typical conference slide, built the way its template suggests.</p>

::right::

<Callout title="What the template leaves to you">

You still decide which question the slide answers. Without one, a slide tends to keep growing.

</Callout>

<!--
Signpost: I'll start with the problem, then the method, then legibility, and last, how to use it.

You might ask the room what their last template gave them. Usually it's a master, a color theme and
a logo in the corner. Deciding what each slide is for is still up to you, and that's often the part
that takes the most time.
-->

---
layout: two-col-evidence
---

# Most templates don't check whether people at the back, or with color blindness, can read the slides.

::left::

<div class="demo-type">
  <div class="demo-type-row">
    <span class="demo-type-label">12 px: shrunk to fit</span>
    <span class="demo-type-shrunk">Shrinking the text makes everything fit.</span>
  </div>
  <div class="demo-type-row">
    <span class="demo-type-label">23 px: the body size</span>
    <span class="demo-type-body">Keeping the body size lets the back row read it.</span>
  </div>
</div>

Red-green color deficiency affects about one in twelve men of European ancestry<sup>1</sup>, and
templates rarely account for it.

<Footnotes>
  <Footnote :number="1">Birch (2012), on worldwide prevalence: about 8% of men and 0.4% of women of European ancestry.</Footnote>
  <Footnote :number="2">Machado, Oliveira and Fernandes (2009), the simulation used for this deck and its validator.</Footnote>
</Footnotes>

::right::

<Figure
  src="/colour-alone.png"
  caption="How far apart the palette's colors are, pair by pair, under four kinds of vision. The chart is shown as someone with deuteranomaly sees it, and only color tells its lines apart."
  :cite="2"
/>

<!--
Both problems can be measured, and in my experience templates leave both to the author. The two
text samples are on the screen right now. Anyone at the back can check whether they can read the
small one. On the right is this deck's own palette, simulated at full severity. Its lines have no
dashes or markers yet, and a later slide adds them.
-->

---
section: Method
---

# The method decides what goes on each slide, and the tools check the result.

| What the method covers | What checks it |
|---|---|
| what each slide is for | a reviewer, human or agent |
| how distinct the data colors stay | `cvd-validate`, on any palette |
| how much fits on one slide | `legible lint`, on every push |
| what text size the back row can read | the theme's fixed type scale |
| how a figure is colored | the figure helper, from the palette file |

<Callout accent title="Why that order">

A theme sets how the slides look. The method shapes what they say, and the two commands catch
slides that break its rules.

</Callout>

<!--
Signpost: That covers the problem, so now the method, one rule per slide.

From here on, each slide shows one rule and tries to follow it. Every row in this table would
still hold with a different palette, and that's why the method comes first.
-->

---

# Each slide should answer one question, and you should be able to say what it is.

<Callout title="The question this slide answers">

What is each slide for?

</Callout>

Assertion-evidence slides pair one claim with the evidence for it<sup>3</sup>. Fitting three
messages onto one slide saves a little preparation, but usually takes longer to explain<sup>4</sup>.

<Footnotes>
  <Footnote :number="3">Alley and Neeley (2005), on sentence headlines and visual evidence.</Footnote>
  <Footnote :number="4">Mayer, on coherence: material that doesn't support the message gets in its way.</Footnote>
</Footnotes>

<!--
Try saying the question out loud before you show the slide, and then let the slide answer it. When
three messages share one slide, the audience often falls behind while you explain them. This slide
tries to follow its own advice: one claim and a couple of sentences of evidence.
-->

---
layout: two-col-evidence
---

# A headline works better as a short claim than as a topic label.

::left::

<Callout title="A label">

Results

</Callout>

Read on its own, this only tells you the topic.

::right::

<Callout accent title="A claim">

Three series pass, and a fourth would fail without retuning.

</Callout>

Read on its own, this tells you the finding. The rest of the slide shows the evidence for
it<sup>5</sup>.

<Footnotes>
  <Footnote :number="5">Alley, Schreiber, Ramsdell and Muffo (2006): audiences remembered more from sentence headlines than from topic phrases.</Footnote>
</Footnotes>

<!--
Read the two boxes and pause for a moment. Only one of them tells you something. A full sentence
that fits on two lines is usually enough. Someone who reads only the headlines of a good deck should
still be able to follow the argument.
-->

---
layout: two-col-evidence
---

# Writing the message before choosing the chart keeps each slide to one point.

::left::

1. Write down the one question the slide answers
2. Find the evidence that answers it
3. Turn the answer into the headline

::right::

<Callout accent title="What this order helps avoid">

A chart comes first, a caption gets written around it, and the point of the slide is unclear.

</Callout>

<!--
Most of us have worked the other way around at some point. You have a figure from the paper, it
feels like a slide's worth of material, and you write a heading for it afterward. Slides made like
that are often the hardest ones to cut later. Starting with a sentence you can say out loud makes
the rest easier.
-->

---

# Anything that doesn't support the main message makes it harder to follow.

Removing extra material helps people learn<sup>4</sup>, and the same idea applies to
figures: spend the ink on the data<sup>6</sup>.

<v-click>

<Callout accent title="Why that box appeared on a click">

Animation helps in two cases: adding evidence one step at a time, or showing a change over
time<sup>7</sup>.

</Callout>

</v-click>

<Footnotes>
  <Footnote :number="4">Mayer, on coherence.</Footnote>
  <Footnote :number="6">Tufte, on data ink and chartjunk.</Footnote>
  <Footnote :number="7">Tversky, Morrison and Bétrancourt (2002): animation helps when it is easy to follow and matches the idea it shows.</Footnote>
</Footnotes>

<!--
Pause before the click and ask the room what the box might add. It shows that the same idea
applies to time: a reveal should add evidence. It's the only reveal in this deck. This rule has
some of the best research behind it, though most of it comes from one lab. Use a click when each
step adds something, and don't use one to hold back a point the headline already made. This deck
uses no slide transitions either.
-->

---
layout: two-col-evidence
section: Legibility
---

# Body text is sized so that people at the back of the room can read it.

::left::

<ViewingDistance reach="4.5" caption="Body type reads to about 4.5 image heights, by the AV industry's sizing guideline." />

::right::

1. Body text is fixed at 23 px on a 1280 × 720 canvas
2. 23 ÷ 720 = 3.2% of the height, on any screen
3. A screen 2 m tall: 2 × 4.5 = 9 m, a session room

Nothing goes below 18 px.

<!--
Signpost: So far we've looked at what goes on a slide. Next is whether people can see it.

Walk through the three lines in order. The canvas is 1280 by 720, and it scales to fill whatever
screen it's on. So a font size is a share of the image height, the same on a projector as on a
laptop. The AV industry's sizing guideline says body text at that share reads to about four and a
half image heights. On a screen two meters tall, that's nine meters, about a seminar or conference
session room. Captions, legends and page numbers are all eighteen pixels or more.

The method fixes the type size once for the whole deck. When each slide can change it, it's tempting
to shrink whatever runs long, and the people at the back pay for that. This scale isn't designed for
a lecture hall. There, sharing the slides by QR code or asking for a second screen helps. In any
room, do the distance check from the method before the talk.
-->

---
layout: two-col-evidence
---

# A color only goes in the palette if it stays distinct for color-blind viewers.

::left::

<Figure
  src="/redundant-deuteranomaly.png"
  caption="The same ten pairs under deuteranomaly, the hardest condition for this palette: the closest pair lands on 15.0, exactly the floor."
  :cite="2"
/>

::right::

<Figure
  src="/redundant-grayscale.png"
  caption="The same chart in grayscale, where the closest pair drops to 10.9. The dashes and markers keep it readable."
/>

<!--
Here's the same chart from earlier, with the same palette and simulation (source 2). What's
different is that each line now has its own dash pattern and marker. The figure helper assigns
them by position, so they're always there. Grayscale is only a warning for that reason: the dashes
and markers already cover it.
-->

---

# The validator works on any palette file, including yours, and shows which pair fails.

| Theme | closest pair, ΔE | in grayscale | result |
|---|---|---|---|
| `leuven-blue` | 15.0 | 10.9 | passes, at capacity |

To check yours, run `cvd-validate your-palette.json`.

<Callout title="Not an endorsement">

This palette is inspired by KU Leuven's colors. It isn't affiliated with or endorsed by the
university.

</Callout>

<!--
These numbers come from the per-series colors, under normal vision and three types of color
blindness at full severity. No slide in this deck names a color directly. "At capacity" means a
fourth series would fail, and the validator would name the pair that's too close. Run it on your
own palette before a talk. A pass means it clears the floor, and a fail tells you which color to
change. The theme file carries the same not-affiliated note in its description.
-->

---
section: Delivery
---

# The same markdown file gives you the slides, a PDF and a deck an agent can review.

| What you get | Status |
|---|---|
| the Slidev theme and this deck | in use now: Slidev turns markdown into a web page, so a slide can hold HTML, video or live code |
| a PDF to present or share | `slidev export`, from the same file |
| a skill for coding agents | starts a deck and reviews it |

<Callout accent title="Why one file">

The slides, the PDF and the review all read the same markdown, so one fix reaches all three.

</Callout>

<!--
Signpost: The last part is how you can use this in your own deck.

You might wonder why there's no PowerPoint master. Slidev's PowerPoint export puts one screenshot on
each slide, so you can't edit it. A master kept by hand would drift from the theme as soon as either
one changed.
-->

---
layout: conclusion
---

# This deck was built with the same rules it has been describing.

::answers::

1. Each slide answers one question, and the headline gives the answer
2. Text is sized for the room, and colors are checked for color-blindness
3. One markdown file, checked by `legible lint` and `cvd-validate` on every push

<!--
Leave this slide up during questions, since it's what people will look at while they ask. Each
answer matches the question with the same number on the second slide. Thank the room out loud.
Mention that the code is on GitHub, and that the rules are in docs/method.md.
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
# docs/research/presentation-methods.md, the prevalence figure among them.
indexEntries:
  - title: 'Birch, J. (2012) — Worldwide prevalence of red-green color deficiency, JOSA A 29(3)'
  - title: 'Machado, Oliveira and Fernandes (2009) — Simulation of color vision deficiency, IEEE TVCG'
  - title: 'Alley, M. and Neeley, K. A. (2005) — Rethinking the design of presentation slides'
  - title: 'Mayer, R. E. — Multimedia Learning, Cambridge University Press'
  - title: 'Alley, Schreiber, Ramsdell and Muffo (2006) — How headline design affects retention'
  - title: 'Tufte, E. R. — The Visual Display of Quantitative Information, Graphics Press'
  - title: 'Tversky, Morrison and Bétrancourt (2002) — Animation: can it facilitate?'
---

# These are the sources behind the claims in this talk.
