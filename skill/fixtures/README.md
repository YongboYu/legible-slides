# The non-compliant fixture

[`non-compliant.md`](non-compliant.md) is a deck built to fail its review, and this table is what
the review is expected to find in it. It exists so the skill's two halves can be exercised on
something whose answer is known: run the review over it and the report should name these, on these
slides.

Half of them a script settles, and `python/tests/test_skill.py` holds the linter to exactly the
rows below — no fewer, and none the table does not claim. The other half needs reading, so nothing
asserts them; they are here to be judged, and the fixture is where a change to the review procedure
can be tried against a known answer.

| Slide | Rule | Found by | Severity | What is planted |
|---|---|---|---|---|
| 1 | `no-em-dash-headline` | linter | error | An em-dash splitting the headline. |
| 1 | `assertion-headline` | reading | warning | "Results — an overview of the work" names the slide's topic and claims nothing. |
| 2 | `bullet-ceiling` | linter | error | Six bullets. |
| 2 | `word-ceiling` | linter | error | A first bullet that is a sentence. |
| 3 | `one-message` | reading | warning | Cost and index size, two questions, one slide, with a pane of evidence for each. |
| 4 | `never-sole-channel` | reading | warning | A hand-drawn SVG whose two series are told apart by colour and by nothing else, with a swatch legend to match. |
| 5 | `no-inflated-register` | linter | warning | "crucial" and "leverage" in the speaker notes. |
| 5 | `opener-variety` | linter | error | Both passages lean on one opener: "It" in the prose, "The" in the notes. |
| 5 | `no-contrast-for-emphasis` | reading | warning | "not just an optimisation, it is a rethinking", against a position nobody held. |
| 5 | `no-reflexive-tricolon` | reading | warning | "faster, cheaper, and more elegant", where the third item is padding. |
| 5 | `no-hedging-or-boilerplate` | reading | warning | The notes open by announcing what the slide is about to show. |
| 5 | `rhythm-variety` | reading | warning | Three notes sentences of the same shape and length in a row. |
| 5 | `concrete-over-abstract` | reading | warning | "demonstrates strong performance characteristics" where a number belongs. |

Slide 6 breaks nothing. A fixture that fired on every slide would not tell you whether the review
reads a deck or merely dislikes it.

**Found by** is the seam, not the canon's `**Decided by**`, and the two part company on one row.
`never-sole-channel` is marked both in the canon, because a generated figure carries the redundancy
structurally — but this deck's visual is hand-drawn, and no script decides that one. It is a reading.

The deck names no theme, so a review of it reports the palette as unchecked rather than as passing —
which is the other thing worth seeing here. What a palette below the floor produces is settled in
the linter's own tests, against a theme built to collide.

Run the mechanical half yourself:

```bash
legible lint skill/fixtures/non-compliant.md
```
