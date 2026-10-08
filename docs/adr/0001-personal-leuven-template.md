# 0001 — A single-theme Slidev template for the author's KU Leuven talks

**Status:** accepted, 2026-09-30; amended 2026-10-08 (logos in git history, under Scope). Supersedes
the multi-brand, tool-plural scope of the v1 spec (#13) where the two disagree.

## Context

v1 shipped as a brand-neutral, tool-plural method: two themes (`kuleuven`, `neutral`), a Slidev
theme and a hand-authored PowerPoint master. Its only real user is the author, preparing
KU Leuven-affiliated academic talks. The template should distil the deck the author already likes,
the CAiSE 2026 talk ([HF Space](https://huggingface.co/spaces/YongboYu/pmf-tsfm-slides)), into
something reusable, and in time drive agent-generated decks from a talk plan.

The template's purpose, restated: academic talks that are (1) clear and efficient, (2) work for
audiences of diverse backgrounds and ages, (3) content-driven and concise, and (4) respect the
audience's cognitive load and attention budget. The research behind the decisions below is in
[`docs/research/accent-colour.md`](../research/accent-colour.md),
[`docs/research/section-locator.md`](../research/section-locator.md) and
[`docs/research/template-audit.md`](../research/template-audit.md). The decisions were made against
a prototype of the CAiSE deck with switchable chrome.

## Decisions

### Scope
- **One theme, `leuven-blue`.** The `neutral` theme and the "swappable brand" argument go. The
  palette keeps passing `cvd-validate`.
- **Slidev only.** The PowerPoint master (`pptx/`, `docs/pptx-static-proof.md`) goes.
- **No university marks in the repo.** Logo files are replaced by placeholders; the author points at
  the real lockup in their own deck. This resolves #8 without asking the university.
- **The logos stay in git history** (amended 2026-10-08). Earlier commits hold the university's
  logo files and the retired PowerPoint master that embeds one. Rewriting history was the original
  plan, but it is not a legal requirement: no current file carries a mark, the README disclaims
  any affiliation, and the license excludes those files. Rewriting would cost either the issue
  trail the docs link to, or a support request to purge the merged PR's refs. If the university
  asks for their removal, history is rewritten then.

### Chrome
- **No decorative accent.** The orange rule under every headline, the cover's orange bar and its
  radial glow are removed. Weight and whitespace separate headline from evidence.
- **Cover:** two logo slots, a venue logo above the title and an affiliation logo at bottom left,
  both shipped as placeholders.
- **Locator: the section map in the footer (C footer) by default; the single section label with a
  count in the footer (A′ footer, `EVALUATION · 3/4`) as an option.** The top of a content slide
  opens straight on the claim. The locator names the talk's 4–5 sections, not each slide's topic:
  a `section:` key on the first slide of a section, carried forward. The current section is marked
  by colour and weight, in `--neutral` otherwise, at no less than the type floor. The footer is a
  backup channel, so every section change is also signposted aloud (a line in the speaker-note
  template).

### Colour
- **Orange stays the only attention hue** (it is KU Leuven's own accent), split by job: `accent`
  `#dd8a2e` for fills with ink text on them, and `accent-strong` `#b3541e` for text and strokes.
  One attention locus per slide.

### Type
- **Body 23px and headline 37px on the 1280×720 canvas, unchanged.**
- **An 18px floor for every other piece of text:** captions, table headers, legends, the locator,
  the page number, and text inside generated figures. Slides size text only through the template's
  classes, never inline px, so the floor can be checked.
- **The scale is stated for the room it suits** (below), replacing the "renders at 34px on a
  projector" argument, which does not measure legibility.

## Which rooms the type scale suits

Slidev scales the whole canvas to the screen, so a size is a share of the image height, and what
decides legibility is the farthest viewer's distance relative to the image height. By the
AV-industry sizing rule ([AVIXA DISCAS](https://www.avixa.org/standards/discas-calculators/discas/learn-more-about-display-size)),
23px body text reads to about **4.5× the image height**, and the 18px floor to about 3.5×.

**Suits:** seminar rooms and typical conference session rooms (roughly 30–150 seats), where the
back row sits within about 4–5 image heights of the screen.

**For a larger room** (a lecture hall or plenary, planned to about 6× the image height):
1. **Raise the body size** to 26–28px (headline about 40–42px). It is one variable in the theme,
   and it costs about 15–30% of each slide's text capacity. Check the deck's densest slides after
   the change.
2. **Cut what the slide carries**, rather than shrinking it: move detail to the spoken track,
   backups, or the shared PDF.
3. **Share the slides** with a QR code on the first and last slide, so people can follow on their
   own device.
4. **Ask the organisers** about a second screen or a confidence monitor for the rear.

A quick check before any talk: view the deck from a distance of about six screen heights (about
1.1 m for a 13-inch laptop) and read the smallest text on every slide.

## Consequences

- `docs/method.md` changes first: `ae-skeleton` (no accent rule, the locator zone moves to the
  footer), `type-scale` (the floor and the room statement), `accent-is-attention` (two tokens).
  Everything downstream follows the canon.
- The theme, flagship deck, tests, README and docs lose `neutral`, `pptx/` and the brand-swap story.
- Further method and skill changes from the audit (answer-first opening, a conclusion that stays up
  through Q&A, density, signal, acronym and pace budgets, and allowing key terms on slides) are
  proposals, to be ticketed separately.
