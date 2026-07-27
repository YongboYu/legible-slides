---
# The theme by path, until the package is on npm. The canvas, the aspect ratio, the two bundled
# families and the locked light scheme all arrive with it, so this deck configures none of them.
theme: ../theme
title: legible-slides
author: Yongbo Yu
info: |
  The flagship deck. It teaches the method by being the method, and the thirteen beats it grows into
  are the outline in docs/method.md. What is here is the frame: the cover, one beat, and the sources.
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
locator: The method
---

# Every slide answers one question, and if you cannot state it the slide is wrong.

<Callout title="The question this slide answers">

What is a slide *for*?

</Callout>

Assertion-evidence gives a slide one claim and the evidence that proves it<sup>1</sup>. Compressing
three messages onto one saves building the other two, then spends longer than that in the
explaining, and the room is behind by the time you are done<sup>2</sup>.

<Footnotes>
  <Footnote :number="1">Alley and Neeley (2005), on sentence headlines and visual evidence.</Footnote>
  <Footnote :number="2">Mayer, on coherence: what does not serve the message costs the message.</Footnote>
</Footnotes>

<!--
Say the question out loud before the slide is on screen, then let the slide answer it. The beat is
the method's first rule and its own demonstration: one claim, two sentences of evidence, nothing
else on the canvas.
-->

---
layout: references
locator: Sources
# Numbered by position, which is what a `Footnote` marker earlier in the deck points at. A URI is
# optional because a book has none.
indexEntries:
  - title: 'Alley, M. and Neeley, K. A. (2005) — Rethinking the design of presentation slides: a case for sentence headlines and visual evidence'
    uri: http://writing.engr.psu.edu/2005_alley_neeley.pdf
  - title: 'Mayer, R. E. — Multimedia Learning, Cambridge University Press'
---

# Every claim these slides make came from somewhere, and here is where.
