# Bundled typefaces

The deck's two families, bundled rather than assumed. The rule is `fonts` in
[`docs/method.md`](../../../docs/method.md), which states the requirement and the reason for it.
The reason was not hypothetical: in the deck this project was extracted from, a machine without
Inter installed drew every generated figure in DejaVu Sans, and nothing said so until a figure and
a slide were put side by side.

Each family is here **twice, in the two formats its two consumers need** — woff2 for the browser,
which cannot read a TTF it would rather subset, and TrueType for matplotlib, which cannot read a
woff2 at all. Both copies come from the same release of the same typeface, so the figures and the
slides are set from one set of outlines.

| File | What it is |
|---|---|
| `Inter-Regular` · `Inter-Medium` · `Inter-SemiBold` · `Inter-Bold` (`.ttf` + `.woff2`) | Inter, the text family, at the four weights the theme is allowed to ask for. Inter 3.019, hinted-for-Windows build. |
| `JetBrainsMono-Regular` (`.ttf` + `.woff2`) | JetBrains Mono, the family the locator pill is set in and nothing else. One weight, because one thing is set in it. JetBrains Mono 2.304. |
| `Inter-OFL.txt` · `JetBrainsMono-OFL.txt` | The licences. Inter is © the Inter Project Authors and JetBrains Mono © the JetBrains Mono Project Authors, both under the SIL Open Font License 1.1. |

The regular weight of each family is the one that carries the **bare family name**. A
weight-suffixed face reports a family of its own — "JetBrains Mono Medium" rather than "JetBrains
Mono" — which a browser reading `@font-face` does not care about and matplotlib, which resolves a
family by name, does. Shipping the regular is what keeps `JetBrains Mono` resolvable inside this
directory.

`legible.fonts.register()` puts these in front of matplotlib before either figure archetype draws,
and **checks that they won**: the bundled copy is moved to the head of the font list so a locally
installed Inter of a different release cannot outrank it, and a resolution landing anywhere else is
an error rather than a picture. That is what makes the same palette and the same data render to the
same pixels on two machines.

It registers by extension rather than by name, so both families arrive without an edit in Python.
Nothing there draws in the mono one; the package's tests hold this directory to carrying it anyway,
because the deck is the other consumer and it has no way to say so.

The browser side is declared in [`../../styles/fonts.css`](../../styles/fonts.css), with no font
provider and no `@import`: a deck must render in the family it was designed in on a lecture-room
laptop with no network.
