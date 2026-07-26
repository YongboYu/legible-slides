# Bundled typefaces

The deck's text family, bundled rather than assumed. The rule is `fonts` in
[`docs/method.md`](../../../docs/method.md), which states the requirement and the reason for it.
The reason was not hypothetical: in the deck this project was extracted from, a machine without
Inter installed drew every generated figure in DejaVu Sans, and nothing said so until a figure and
a slide were put side by side.

| File | What it is |
|---|---|
| `Inter-Regular.ttf` · `Inter-Medium.ttf` · `Inter-SemiBold.ttf` · `Inter-Bold.ttf` | Inter, the text family, as static TrueType. All four report the family name `Inter`, so registering them makes that name resolve without an install. |
| `OFL.txt` | Inter's licence. Inter is © the Inter Project Authors, under the SIL Open Font License 1.1. |

`legible.fonts.register()` puts these in front of matplotlib before either figure archetype draws,
and **checks that they won**: the bundled copy is moved to the head of the font list so a locally
installed Inter of a different release cannot outrank it, and a resolution landing anywhere else is
an error rather than a picture. That is what makes the same palette and the same data render to the
same pixels on two machines.

It registers by extension, not by name, so the mono family the locator is set in is picked up by
the same call once the deck theme ships it — no edit in Python.

The deck itself wants woff2, which browsers can subset and matplotlib cannot read. Those land here
too when the Slidev theme lands; the two sets are the same typeface in the two formats its two
consumers need.
