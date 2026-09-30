---
# The theme, by path: slidev-theme-legible is not on npm yet, so a deck consumes it from a checkout
# of legible-slides. Point this at that checkout's theme/ directory.
theme: ../legible-slides/theme
title: Your title
author: You
info: |
  What this talk is, in a line. Slidev shows it in the presenter view and nowhere else.
themeConfig:
  # Your affiliation's mark, served from this deck's own public/. The file below is a placeholder:
  # drop your own mark into public/ and point this line at it, or set it to '' for no mark.
  logo: /affiliation-logo.svg
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
layout: assertion-evidence
# The pill that says where the talk has got to. It carries forward until another slide sets one,
# and `locator: ''` clears it. This is the mechanism `no-section-dividers` leans on, so set it when
# the section changes rather than spending a slide on saying so.
locator: Where the talk has got to
---

# The claim this slide proves, written as a sentence.

<!-- Point src at a figure of your own and delete public/placeholder.svg. Charts are regenerated
     from data rather than redrawn — `legible.figures` draws the archetypes from this deck's
     palette, which is what makes a recolour reach them. See public/README.md. -->

<Figure
  src="/placeholder.svg"
  caption="What the evidence shows, in a line."
  :cite="1"
/>

<Footnotes>
  <Footnote :number="1">Where that evidence came from.</Footnote>
</Footnotes>

<!--
Everything you say out loud goes here. `legible rules no-script-on-slide` is why there is a place
for it, and a review reads these notes like everything else in this file.
-->

---
layout: two-col-evidence
# Equal panes by default. Give the evidence the wider half when it needs it.
ratio: 3fr 2fr
---

# The claim whose evidence needs two panes, written as a sentence.

::left::

<Figure
  src="/placeholder.svg"
  caption="What the left pane shows."
/>

::right::

<Callout title="A label for the box">

The one thing on this slide that has to read as set apart: a definition the rest of it leans on, or
the number the evidence turns on.

</Callout>

<!--
Both panes serve the headline above them. Read `legible rules one-message` when a slide starts to
feel like it is doing two jobs, because splitting it here is cheaper than splitting it in the room.
-->

---
layout: references
locator: Sources
# Numbered in this order, so a Footnote marker earlier in the deck lines up with an entry here.
indexEntries:
  - title: 'How the source is cited: author, year, title'
    uri: https://example.org/where-to-find-it
---

# Where every claim above came from.
