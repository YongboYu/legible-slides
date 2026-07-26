# Theme logos

A theme's `meta.logo` is a path relative to this `themes/` directory. `neutral.json` omits the key
entirely — that is what brand-free means. `kuleuven.json` points at the lockup below.

| File | What it is | Size |
|---|---|---|
| `kuleuven-liris.png` | KU Leuven + Research Centre for Information Systems Engineering (LIRIS), horizontal lockup. **The `kuleuven` theme's default.** | 3480 × 472, tight crop |
| `kuleuven.png` | The KU Leuven wordmark alone, for decks with no research-centre affiliation. | 600 × 300, with transparent padding |

Swapping between them is a one-line edit to `meta.logo` in `themes/kuleuven.json`. If you use the
wordmark alone, note its canvas carries padding the lockup does not, so it needs different sizing in
slide chrome rather than a drop-in swap.

These are KU Leuven's own marks, used here by a KU Leuven researcher for a KU Leuven-derived theme.
This project is not an official KU Leuven product and carries no endorsement — the same note the
theme itself carries in `meta.description`. Anyone reusing this repo under a different affiliation
should point `meta.logo` at their own mark or drop the key.
