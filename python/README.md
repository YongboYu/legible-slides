# `legible`

The mechanical half of [`legible-slides`](../README.md): everything that reads a theme file.

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

## Development

```bash
uv sync --extra dev
uv run pytest
uv run ruff check . && uv run ruff format --check .
```

An editable install reads `docs/method.md` from the checkout directly, so a canon edit takes effect
with no rebuild.
