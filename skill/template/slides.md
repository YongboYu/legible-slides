---
# The theme is the npm package slidev-theme-legible, which Slidev finds under the name `legible`.
# package.json pins it to the release that bin/legible installs the checks from, so the deck is
# checked against the rules it was built to.
theme: legible
title: Your title
author: You
info: |
  What this talk is, in a line. Slidev shows it in the presenter view and nowhere else.
# The cover's two marks: the venue's above the title, the affiliation's bottom left. Left unset,
# each shows a placeholder the theme bundles. Drop your own mark into this deck's public/ and name
# it here, or set a slot to '' for no mark. The footer maps the talk's sections; `locator: label`
# shows only the current one, with its position, instead.
# The slides, handed over on the cover and on the conclusion (`answer-first`,
# `conclusion-stays-up`): a QR code to the link you share them at, generated into public/ by any QR
# tool (`uvx segno <link> --no-size --output public/share-qr.svg`), the link itself, and on the
# conclusion how to reach you. The QR slot shows a placeholder until you name a code.
# themeConfig:
#   venueLogo: /venue-logo.png
#   affiliationLogo: /affiliation-logo.png
#   locator: label
#   shareQr: /share-qr.svg
#   shareUrl: https://example.org/your-slides
#   contact: you@example.org
# The first frontmatter block is the deck's headmatter and the cover's own frontmatter at once,
# which is why the cover's props sit here. The cover takes `speaker` when a talk is given by someone
# other than the `author` above; `venue` and `date` are yours to fill in or to delete.
layout: cover
venue: Where you are speaking
date: When
---

# Your title

## The one sentence you want the room to leave with.

---
layout: answer
# Straight after the cover. What goes on it, and why here: `legible rules answer-first`.
---

# The result of the whole talk, written as a sentence.

::questions::

1. The first question the talk answers?
2. The second?

<!--
What you say out loud while the room reads the result.
-->

---
layout: assertion-evidence
# The part of the talk this slide opens. It carries forward until another slide sets one, and
# `section: ''` clears it. The footer names every section, and this one is marked; this is what
# `no-section-dividers` leans on, so set it when the section changes rather than spending a slide on
# saying so. `legible rules section-locator` says how many sections, and how short, still fit.
section: Findings
---

# The claim this slide proves.

<!-- Point src at a figure of your own and delete public/placeholder.svg. `legible.figures`
     draws charts from data in this deck's palette, so changing the palette recolors them too.
     See public/README.md. -->

<Figure
  src="/placeholder.svg"
  caption="What the evidence shows, in a line."
  :cite="1"
/>

<Footnotes>
  <Footnote :number="1">Where that evidence came from.</Footnote>
</Footnotes>

<!--
Signpost: the sentence that tells the room a new part of the talk has started, and which.

Write what you'll say out loud here. `legible rules no-script-on-slide` explains why it goes in the
notes. The review reads these notes too.
-->

---
layout: two-col-evidence
# Equal panes by default. Give the evidence the wider half when it needs it.
ratio: 3fr 2fr
---

# The claim whose evidence needs two panes.

::left::

<Figure
  src="/placeholder.svg"
  caption="What the left pane shows."
/>

::right::

<Callout title="A label for the box">

The one thing on this slide that has to stand out. It might be a definition the slide relies on,
or the number the evidence turns on.

</Callout>

<!--
Both panes support the headline above them. If a slide starts doing two jobs, read `legible rules
one-message`. Splitting it now is easier than splitting it in front of the room.
-->

---
layout: conclusion
# The last slide of the talk; the QR code and your contact come from themeConfig above. What goes
# on it, and why: `legible rules conclusion-stays-up`.
---

# The claim the whole talk proved.

::answers::

1. The answer to the first question
2. The answer to the second

<!--
What you say out loud while this slide is up.
-->

---
layout: references
# Optional. In a talk the room rarely has time to read this slide, so delete it if the footnotes
# and your shared slides are enough. After the talk, so outside its sections: the footer names this
# one alone, with no position.
section: Sources
backup: true
# Numbered in this order, so a Footnote marker earlier in the deck lines up with an entry here.
indexEntries:
  - title: 'How the source is cited: author, year, title'
    uri: https://example.org/where-to-find-it
---

# Optional: references for the claims above.
