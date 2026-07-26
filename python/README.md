# `legible`

The mechanical half of [`legible-slides`](../README.md): the deck linter, and everything that reads
a theme file — the validator, the CSS emitter, and the figure archetypes.

A theme is one JSON palette with named roles ([`docs/token-contract.md`](../docs/token-contract.md)).
This package is the single reader of that schema, so nothing downstream re-implements it and drifts.

```python
from legible import load_palette, validate

report = validate(load_palette("themes/kuleuven.json"))
report.passed          # True
report.min_delta_e     # {'normal': …, 'deuteranomaly': …, 'protanomaly': …, 'tritanomaly': …}
report.failures        # pairs below the floor, named by role — never by hex
report.warnings        # grayscale collisions; advisory, never a failure
```

## What `validate()` checks

The rule is **`separation-floor`** in [`docs/method.md`](../docs/method.md), which owns the floor,
the metric, the conditions and the grayscale carve-out. This package quotes those numbers out of
the canon at import — change the rule and the validator changes with it, because there is no second
copy here to update:

```python
from legible import DELTA_E_FLOOR, rule_thresholds

rule_thresholds("separation-floor")   # {'delta-e-floor': …, 'delta-e-metric': …, 'cvd-severity': …}
```

What the package adds on top of the rule is fixed by
[`docs/cvd-validator-contract.md`](../docs/cvd-validator-contract.md): the palette is checked as
**two co-occurrence groups** — `G1 = {reference, muted, series…}` (the per-series ramp) and
`G2 = {reference, muted, brand}` (the two-group highlight). They live on mutually exclusive slides,
so `brand ↔ series` is never compared: those roles cannot share an axis.

Pass your own floor to move the boundary:

```python
validate(palette, threshold=20.0)
```

## `cvd-validate`

The same check as a command, so an accessibility claim about your palette is something you can run
rather than something you assert:

```bash
cvd-validate my-theme.json
```

```
FAIL  my-theme.json — min ΔE … (floor …)

  min ΔE per condition
    normal          …
    deuteranomaly   …
    protanomaly     …
    tritanomaly     …
    grayscale       …  advisory

  fail  deuteranomaly   …  series-1 ↔ series-2
  warn  grayscale       …  muted ↔ series-1
```

Pairs are named by **role**, never by hex, so the output says which colour in your theme file to
change. The achieved minimum prints on a pass too — headroom, or the lack of it, is the thing worth
seeing when you are deciding whether the ramp has room for one more series.

`--json` emits the report verbatim, one object per theme in the order given.

**Exit code** — `0` on pass, `1` if any pair falls below the floor, `2` if a theme file cannot be
read. Grayscale collisions are warnings and never change it.

### Installing it without this repo

```bash
uv tool install "git+https://github.com/YongboYu/legible-slides#subdirectory=python"
```

The build copies `docs/method.md` in beside the module, so an install with no checkout still reads
its thresholds out of the canon instead of a hardcoded copy (see `hatch_build.py`). Only the themes
*this* repo ships are gated by its CI; your palette is yours.

## `legible gen-css`

The same palette, emitted as the deck's CSS custom properties — every scalar role a property of the
same name, `series` expanded to `--series-1 … --series-n`. The mapping is
[`docs/token-contract.md`](../docs/token-contract.md) §5's:

```bash
legible gen-css themes/kuleuven.json --output theme/styles/tokens.css
```

```python
from legible import gen_css, load_palette

gen_css(load_palette("themes/kuleuven.json"))    # '/* Generated … */\n\n:root {\n  --ink: …;\n}\n'
```

Python emits the CSS because Python already reads this schema to validate a palette and to draw a
figure: the token contract is understood in exactly one language, so there is no JavaScript copy of
it to drift. The output is **committed and regenerated when the palette changes, like a lockfile**,
which is what lets a deck build import it and never invoke Python.

`--check` writes nothing and exits `1` when the file is not what the theme emits today — the gate
that keeps that lockfile honest, and what CI runs here:

```bash
legible gen-css themes/kuleuven.json --output theme/styles/tokens.css --check
```

Without `--output` the stylesheet goes to stdout. **Exit code** — `0` written or already current,
`1` stale under `--check`, `2` if the theme file cannot be read.

## `legible lint`

The rules the canon marks **decided by script**, as a command with an exit code — so the objective
half of a review is something CI runs rather than something a reader has to remember:

```bash
legible lint deck/slides.md --theme themes/kuleuven.json
```

```
FAIL  deck/slides.md — 2 errors, 1 warning

  slide 4
    error    bullet-ceiling        … bullets, ceiling …
    warning  no-inflated-register  '…' inflates register without adding information
  deck
    error    separation-floor      FAIL  themes/mine.json — min ΔE … (floor …); …
```

Findings are grouped by slide and named by the rule they enforce, so a finding is something you can
look up in [`docs/method.md`](../docs/method.md) and disagree with. Five rules are decided per
slide — `bullet-ceiling`, `word-ceiling`, `no-em-dash-headline`, `no-inflated-register` and
`opener-variety` — and `separation-floor` is decided per theme, for each `--theme` named. A deck
does not record which palette it wears, so naming none checks the slides alone.

```python
from legible import lint

report = lint("deck/slides.md", themes=["themes/kuleuven.json"])
report.passed      # False if any finding is an error
report.findings    # (Finding(rule=…, severity=…, slide=…, message=…), …)
report.unchecked   # themes cvd-validate could not measure; neither a pass nor a violation
```

**Exit code** — `0` clean, `1` on any violation, `2` if the deck or a theme could not be read.
Severity is the canon's call rather than the linter's: a rule whose threshold sets
`… -severity = warning` reports without ever changing the exit code, because
`established-terminology` can legitimately override the inflated-register wordlist. `--json` emits
the report verbatim.

### What it refuses to decide

- **The rules the canon marks `judgment`.** Whether a slide carries one message, whether a headline
  is a claim. Those are the review skill's, and they are advisory because they are fallible; this is
  a gate, and a gate may only hold what is decidable.
- **Colour.** `separation-floor` is checked by **running `cvd-validate` and reading its exit code**
  — which is what that exit code is for. There is one implementation of Machado (2009) in this
  package, so a linter saying a palette collapses and a report saying it holds cannot disagree.
- **Its own thresholds.** Every number and wordlist above is quoted from the rule that owns it in
  the canon. Change `bullets-per-slide` there and this command enforces the new one.

## The figure helper

Result charts are **regenerated from data, never redrawn** — which is the whole reason a palette
swap propagates. Two archetypes, because two is what the method prescribes
([`docs/slidev-reference-impl.md`](../docs/slidev-reference-impl.md) §4). This is not a charting
library, and a third shape belongs in a ticket rather than a keyword argument.

```python
from legible import load_palette
from legible.figures import Series, multi_series, two_group, save

palette = load_palette("themes/kuleuven.json")

save(
    multi_series(
        palette,
        [
            Series("Chronos", chronos_mae),
            Series("MOIRAI", moirai_mae),
            Series("Ground truth", truth_mae, role="reference"),
            Series("XGBoost", xgb_mae, role="muted"),
        ],
        x=windows,
        x_label="forecast window",
        y_label="MAE",
    ),
    "deck/public/figures/mae-by-window.png",
)
```

A `Series` carries **no dash and no marker**. Both are assigned by position, so `never-sole-channel`
holds by construction and there is nowhere to opt out of it — and a chart asking for more series
than there are distinct dashes is refused rather than quietly repeating one. Leave `role` unset and
a line takes the next colour off the theme's ramp; set it to pin the anchors.

The two-group archetype is the default headline chart — the de-emphasised comparison against one
highlight, every bar labelled where it stands, so it needs no legend and no value axis:

```python
two_group(palette, {"ARIMA": 0.51, "XGBoost": 0.44}, {"Ours": 0.29}, y_label="MAE")
```

### What the archetypes will not draw

- **Colour comes only from palette roles.** Nothing here takes a hex, which is what keeps the theme
  file the single authority the deck's CSS and the validator already read.
- **Only roles the validator measured may encode data** — the anchors and the ramp for a
  multi-series chart, the de-emphasised role plus one highlight for a two-group one. That puts the
  attention role out of reach (`accent-is-attention`) along with every structural neutral, because
  a pair nobody checked is a pair nobody can vouch for.
- **The deck's typeface is registered before anything is drawn**, and a resolution landing outside
  the bundle is an error. See [`theme/assets/fonts/`](../theme/assets/fonts/).

### Rendering under a colour-vision deficiency

Any chart can render as one pair of eyes receives it — the demonstration two of the flagship's
beats are built on, and the reason a hand-drawn approximation would not do:

```python
multi_series(palette, series, condition="deuteranomaly")
multi_series(palette, series, condition="grayscale")
```

The simulation is the validator's own. There is one implementation of Machado (2009) in this
package, so a chart showing a palette collapse and a report saying it holds cannot disagree.

### Sizes, and why the same figure comes back twice

Sizes are in the canon's **canvas pixels** — the units a slide layout is written in — so a chart
asked for at 640 wide occupies 640 of them when it lands. `save` writes PNG at twice that by
default, for the projector.

Type is set at the **body** size, which `type-scale` puts at the floor. The two dense sizes it
marks as exceptions for tight figure panels are reachable as exactly that, and not as a
preference:

```python
multi_series(palette, series, size_px=(420, 300), tight_panel=True)
```

```python
save(figure, path, scale=2)          # a 960 × 540 chart → a 1920 × 1080 file
```

`save` is deterministic: an unchanged palette and unchanged data produce a byte-identical file, so
rerunning the generation rewrites without churning and the one figure that did change is the one
you see in the diff.

## Development

```bash
uv sync --extra dev
uv run pytest
uv run ruff check . && uv run ruff format --check .
```

An editable install reads `docs/method.md` from the checkout directly, so a canon edit takes effect
with no rebuild.
