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

## Four layouts, four components, and a palette that had to pass the floor to get here.

---
locator: The skeleton
---

# The theme ships four layouts, and refuses the ones the method forbids.

- `cover` for the title, and for nothing else
- `assertion-evidence` for a claim and its one pane of evidence
- `two-col-evidence` when the evidence needs two panes
- `references` for the sources, from data

<!-- The blank lines are load-bearing: without them markdown-it takes the block for raw HTML and
     leaves the backticks as backticks. -->
<Callout title="Refused">

No `section`, no `intro`, no `end`, no one-word emphasis. A slide spent on navigation proves nothing,
so there is no layout that builds one.

</Callout>

---
layout: two-col-evidence
ratio: 3fr 2fr
locator: Evidence
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

The locator pill and the page number are one component, injected on every other slide in this
deck. No layout opts in, so none can forget. `chrome: false` in a slide's frontmatter takes both
off, and the `cover` layout is without them already.

This slide also names no layout. `default` is `assertion-evidence` under the name Slidev falls back
to, so the skeleton is what a slide gets by default rather than something it has to ask for.

---
layout: references
locator: Sources
indexEntries:
  - title: 'Alley, M. — The Craft of Scientific Presentations'
    uri: https://www.craftofscientificpresentations.com
  - title: 'Machado, G. M. et al. (2009) — A Physiologically-based Model for Simulation of Color Vision Deficiency'
    uri: https://doi.org/10.1109/TVCG.2009.113
  - title: 'legible-slides — the method, and the floor it is measured against'
    uri: https://github.com/YongboYu/legible-slides/blob/main/docs/method.md
---

# The sources are a slide, not a divider.
