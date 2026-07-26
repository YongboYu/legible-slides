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

## Development

```bash
uv sync --extra dev
uv run pytest
uv run ruff check . && uv run ruff format --check .
```

The canon is read from `docs/method.md` in this repo, so the package expects to run from a checkout.
Packaging it for authors outside this repo belongs to the `cvd-validate` CLI ticket.
