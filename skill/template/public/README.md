# What this deck serves

Anything here is served from the deck's root, so `public/figure.png` is `/figure.png` on a slide.

`placeholder.svg` is the blank both skeleton slides currently point at. Replace those two `src`
values with figures of your own and delete it — a deck still serving it is a deck with a slide
nobody has filled in yet.

**Charts are regenerated from data, never redrawn** — that is what makes a palette swap reach them.
Draw them with the archetypes in the `legible` package, from this deck's own palette:

```bash
python -c "
from legible import load_palette
from legible.figures import save, two_group
palette = load_palette('themes/palette.json')
save(two_group(palette, {'baseline': 0.51}, {'ours': 0.29}, y_label='MAE'), 'public/figure.png')
"
```

See [`python/README.md`](https://github.com/YongboYu/legible-slides/blob/main/python/README.md#the-figure-helper)
for the two archetypes and what they refuse to draw. A figure drawn any other way is one a recolour
will leave behind, and one nothing has measured for separation.

A brand's mark belongs here too, beside the figures, and reaches the cover through `themeConfig.logo`
in the deck's headmatter.
