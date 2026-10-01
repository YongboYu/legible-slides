---
# The theme, from its own directory. A deck outside this repo consumes it the same way, by path.
theme: ./
author: legible-slides
info: |
  The theme package's own example deck: every layout it ships, exercised once, so a build proves the
  machinery rather than a screenshot. The teaching artifact is the flagship deck, not this file.
# The palette every colour on these slides comes from, and the floor it passed to get here:
#   uv run --project ../python cvd-validate ../themes/leuven-blue.json
---

# slidev-theme-legible

## Six layouts, five components, and a palette that had to pass the floor to get here.

---
layout: answer
---

# The theme opens a talk on its answer and closes on one that stays up.

::questions::

1. Which layouts does it ship, and which does it refuse?
2. What does the palette have to clear?

---
section: Skeleton
---

# The theme ships six layouts, and refuses the ones the method forbids.

| Layout | For |
|---|---|
| `cover` | the title, and the QR code to the slides |
| `answer` | the result, and the questions the talk answers |
| `assertion-evidence` | a claim and its one pane of evidence |
| `two-col-evidence` | evidence that needs two panes |
| `conclusion` | each question answered, left up through Q&A |
| `references` | the sources, from data |

<!-- Six rows at body size is as much as this slide holds, so what the theme refuses is said here
     instead: no `section`, `intro`, `end` or one-word emphasis layout. A slide spent on navigation
     proves nothing, so there is no layout that builds one. -->

---
layout: two-col-evidence
ratio: 3fr 2fr
section: Evidence
---

# Deuteranomaly is the binding condition for this palette, at exactly the floor.

::left::

<Figure
  src="/example-figure.png"
  caption="Closest pair in the KU Leuven ramp, per condition, simulated at full severity."
  :cite="1"
/>

::right::

<Callout accent title="At capacity">

Three series pass. A fourth fails without retuning the ramp, and the validator says so rather than
quietly repeating a colour.

</Callout>

The chart is regenerated from the same theme file this slide is coloured from, so a palette swap
reaches both.

<Footnotes>
  <Footnote :number="1">Achieved minima for <code>themes/leuven-blue.json</code>, group G1.</Footnote>
</Footnotes>

---
chrome: false
---

# A slide can drop the chrome, and this one has.

The section locator and the page number are one component, injected on every other slide in
this deck. No layout opts in, so none can forget. `chrome: false` in a slide's frontmatter takes both
off, and the `cover` layout is without them already.

This slide also names no layout. `default` is `assertion-evidence` under the name Slidev falls back
to, so the skeleton is what a slide gets by default rather than something it has to ask for.

---
layout: conclusion
---

# Every layout here is one the method asks for, and none is a divider.

::answers::

1. Six layouts, and no section, intro, end or thank-you slide
2. The separation floor, under all three dichromacies

---
layout: references
section: Sources
backup: true
indexEntries:
  - title: 'Alley, M. — The Craft of Scientific Presentations'
    uri: https://www.craftofscientificpresentations.com
  - title: 'Machado, G. M. et al. (2009) — A Physiologically-based Model for Simulation of Color Vision Deficiency'
    uri: https://doi.org/10.1109/TVCG.2009.113
  - title: 'legible-slides — the method, and the floor it is measured against'
    uri: https://github.com/YongboYu/legible-slides/blob/main/docs/method.md
---

# The sources are a slide, not a divider.
