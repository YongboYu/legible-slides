# The CVD-validator contract

_Resolves [#9](https://github.com/YongboYu/legible-slides/issues/9). Depends on the
library/metric research ([#4](https://github.com/YongboYu/legible-slides/issues/4)) and the token roles
([#2](https://github.com/YongboYu/legible-slides/issues/2),
[`docs/token-contract.md`](token-contract.md))._

The validator turns pmf's *one-time, unrecorded* accessibility assertion ("the colours are ≥39
apart") into a **reproducible check anyone can run on any palette** — pinned library, named metric,
stated floor. The provenance calls this "the single most transferable artifact in the whole
project" ([`design-provenance.md`](design-provenance.md) §2).

The rule it enforces is `separation-floor` in [`method.md`](method.md), which owns the floor, the
metric and the conditions. This document fixes the **library, the report shape and the gate** — and
records how that floor was arrived at.

---

## 1. What is checked — two co-occurrence groups

The validator enforces **pairwise perceptual separation** among the data-encoding roles that can
actually share one chart axis. Per the token contract's *hybrid strategy* (§4), the ramp and the
brand highlight appear on **mutually exclusive** slides, so they form two groups — both anchored on
the two lines that appear in every chart (`reference`, `muted`):

| Group | Members | Chart context |
|---|---|---|
| **G1** per-series | `{reference, muted, series[0..n]}` | family / per-series comparison — the full ramp |
| **G2** two-group | `{reference, muted, brand}` | headline "highlight vs the rest" |

- **`brand ↔ series` is *not* checked** — they never co-occur on one axis, and requiring it is both
  wrong on the merits and empirically impossible for the reference palette (brand `#00407a` vs
  series-3 `#4c3a78` collapse to ΔE ≈ 0.7 under protanopia, because both are dark blue-purples).
- **Excluded roles:** `accent` and `accent-strong` (`accent-is-attention` keeps them off every data
  axis, and they carry shape and position redundancy of their own) and all structural neutrals (`ink`, `neutral`, `neutral-soft`, `surface*`,
  `hairline`) — those are governed by WCAG *contrast*, not categorical ΔE.

A theme with fewer series still works: the groups are formed pairwise over whatever roles are
present.

### The attention pairings — contrast, not ΔE

`accent-is-attention` names a short list of pairings the attention roles are read in, and the WCAG
contrast ratio they clear. Those are a
legibility question, not a separation one, so they are measured with the WCAG 2.x luminance ratio
rather than ΔE, at two decimal places, and compared inclusively against the canon's minimum. A
pairing below it fails the palette and exits `1`, exactly like a pair below the floor; the canon
owns the list and the number, so a pairing added there is checked with nothing edited here.

`decorative-neutral-never-text` does the same for the roles the template sets as text, on the grounds
they sit on, against its own minimum. Without it a palette could pass with captions and the footer
painted in the ground colour, because nothing about its data colours would have moved.

## 2. Metric

The canon names the simulation, the conditions, the severity and the distance space
(`separation-floor`). Standardize on **`colorspacious`** (MIT, **pinned** — last release 2018) to
implement all of it in one dependency:

- **Simulation** — the canon's Machado, Oliveira & Fernandes (2009) simulation via the `sRGB1+CVD`
  space, passing each `cvd_type` and the canon's severity straight through. Full dichromacy is the
  worst case, so passing there implies passing milder anomalous CVD.
- **Distance** — `colorspacious.deltaE`, whose default uniform space is the canon's CAM02-UCS
  (perceptually uniform, so equal numbers mean roughly equal perceived difference).
- **Grayscale** — chroma drop in a uniform appearance space (`JCh`, set `C = 0`), since grayscale is
  not a Machado CVD type.
- **Backup** — keep `daltonlens` (MIT, actively maintained) as a drop-in for the *simulation* step if
  `colorspacious`' staleness ever bites; keep `colorspacious.deltaE` for the distance.

### Why "≥39" is retired

pmf asserted the five-line set stays "≥39 apart," and research [#4] *inferred* (explicitly, as an
unrecorded guess) that this was a min pairwise CAM02-UCS ΔE. **That inference is wrong on units.**
Measured on the exact palette:

| Ruler | min across normal + 3 CVD + grayscale |
|---|---|
| raw sRGB (0–255) Euclidean | **~46** |
| CIE76 (Lab Euclidean) | ~10.5 |
| CIEDE2000 | ~10.5 |
| **CAM02-UCS ΔE** (this validator) | **~11** |

"39" belongs to the *raw, non-perceptual* distance family (~46 in raw sRGB) — not a perceptual ΔE.
The palette is genuinely well-separated; "39" and the canon's floor are the **same colours measured
with different rulers**. Do **not** treat 39 as "headroom above the floor" — that compares two
scales. The honest statement is below.

## 3. Threshold — where the canon's floor came from

The pass condition is `separation-floor`: the canon owns the number, the metric, the conditions, the
inclusive comparison and the grayscale carve-out. What this section records is the derivation.

- **The floor is grounded in the JND literature** (≈6–15× the just-noticeable difference; above every
  perceptibility and acceptability figure in [#4](https://github.com/YongboYu/legible-slides/issues/4)),
  **not** reverse-engineered to the palette. That is why the canon documents it as a tunable design
  parameter rather than a physical constant.
- **The inclusive comparison is safe because the numbers are deterministic.** With `colorspacious`
  pinned, a value that lands exactly on the floor is a reproducible pass rather than a coin flip.
- **ΔE is measured, reported and compared at one decimal place.** One precision throughout, so the
  verdict can never disagree with the figure printed beside it: the reference palette's binding pair
  measures 14.9609 and is published below at one decimal, and "published at the floor" therefore
  means "passes the floor". That precision is far finer than the floor's own derivation warrants —
  the canon settles a design parameter, not a constant known to a hundredth.
- **Grayscale is advisory because the method already mandates the fix** (`never-sole-channel`).
  Grayscale is precisely the condition redundant encoding exists to cover, so it produces a warning
  and leaves the exit code alone.

### Verified against the shipped palette (`themes/leuven-blue.json`)

| | min ΔE (normal + CVD) | grayscale min | verdict |
|---|---|---|---|
| **G1** `{reference, muted, series[]}` | **15.0** | 10.9 | **pass** — at capacity |
| **G2** `{reference, muted, brand}` | **30.0** | 18.5 | pass |

G1's 15.0 is the binding pair (`series-1` ↔ `series-3` under deuteranomaly). It passes at exactly the
floor: the validator is correctly signalling the 3-series ramp is **at capacity for this palette** — a
4th series would fail without retuning, which is exactly the behaviour token contract §4 asks for
("the validator tells you when you've added one too many"). The grayscale 10.9 is a lightness clash
(`muted` J′ 57 vs `series-1` J′ 46) — warned, covered by redundant encoding.

The table is asserted by the package tests. It is the **dependency-bump guard**: a
`colorspacious` release that shifted the simulation or the distance would move these numbers and
turn the suite red, rather than quietly re-rating a palette someone already trusted.

## 4. Interface

A single Python core with two faces, shipped as an installable package (`pyproject.toml`, pinned
`colorspacious`, `cvd-validate` console script):

```python
def validate(palette, threshold: float = DELTA_E_FLOOR) -> Report: ...
```

`DELTA_E_FLOOR` is quoted from the canon (`separation-floor`); the package reads the number from
there rather than carrying its own copy, and the same name is used throughout this document.

```
Report:
  passed:       bool          # every CVD pair ≥ threshold in both groups (grayscale excluded),
                              # and every attention pairing ≥ contrast_threshold
                              # and every text pairing ≥ text_contrast_threshold
  threshold:    float         # the canon's floor unless the caller overrides it
  groups:       {G1: {...}, G2: {...}}
  min_delta_e:  {normal, deuteranomaly, protanomaly, tritanomaly}
  grayscale_min: float        # advisory
  failures:     [(condition, role_a, role_b, delta_e)]   # CVD pairs < threshold
  warnings:     [(role_a, role_b, delta_e)]              # grayscale pairs < threshold
  contrast_threshold: float                              # the canon's `attention-contrast-min`
  contrast:     [(foreground, background, ratio)]        # every pairing the canon names
  contrast_failures: [(foreground, background, ratio)]   # pairings < contrast_threshold
  text_contrast_threshold: float                         # the canon's `text-contrast-min`
  text_contrast: [(foreground, background, ratio)]       # every text pairing the canon names
  text_contrast_failures: [(foreground, background, ratio)]
```

**CLI** — `cvd-validate themes/leuven-blue.json`:

- **Human-readable text by default:** a `PASS`/`FAIL` line, per-condition min ΔE, and each failing /
  warning pair named **by role** (`muted ↔ series-1`), never by hex — so an author knows which colour
  to fix. The **achieved min prints even on pass**, so headroom (or the lack of it) is visible.
- **`--json`** emits the `Report` verbatim for CI logs / tooling.
- **Exit code** `0` on pass, `1` on any CVD or attention-contrast failure. **Warnings never change the exit code.**

The command takes **one or more** theme paths, so the CI gate and the pre-commit hook are one
invocation over whatever they were handed. Three consequences of that, settled in implementation:

- **`2`, not `1`, for a theme that cannot be read** (missing file, malformed JSON, a role the token
  contract requires). `1` is a measurement — *these two colours are this far apart, and that is too
  close*. A file that was never measured must not make that claim. `2` is also argparse's code for a
  malformed command line, which is the same statement about a different mistake: the check did not
  run. Consumers that only gate on "did it pass" are unaffected — both are non-zero.
- **An unreadable theme does not stop the run.** Every other theme is still checked and reported. If
  any palette came back below the floor the exit is `1` — the more actionable verdict — and `2` only
  when nothing was measured as failing.
- **`--json` emits one report per line**, in argument order, so a report's shape never depends on how
  many themes were asked for. One theme — the documented call — is therefore one JSON object.

The importable `validate()` is what tests, CI, and the (optional) figure helper [#10] call; they can
share one palette-loader that reads the token-contract schema.

## 5. What it gates

- **Scope** — the one theme shipped in this repo, `themes/leuven-blue.json` (`*.dark.json` is a v2
  concern). External authors get the CLI to self-check their own palettes but are not blocked.
- **Hard gate — a GitHub Actions job** (`.github/workflows/ci.yml`) runs `cvd-validate` over the
  shipped theme on push/PR; a non-zero exit turns the check red and blocks merge. Enforcement lives
  in CI, not a skippable hook. *Blocking* is the one half a workflow file cannot grant itself, and
  the branch ruleset on `main` now grants it
  ([#26](https://github.com/YongboYu/legible-slides/issues/26)): `palette floor` is a required
  status check there, so a red check holds the merge instead of decorating it. Repo admins are a
  bypass actor — this repo is authored by direct push to `main` — so the gate binds what arrives by
  pull request and is discipline for the author.
- **Package test** — the suite asserts the shipped palette passes, so a future
  `colorspacious` version bump that shifts the numbers is caught by tests, not silently in prod.
- **No deck-build coupling** — the Slidev (JS) build does **not** invoke the validator; it trusts CI.
  The validator stays a Python authoring/CI tool, never a deck-runtime dependency.
- **Optional pre-commit hook** — `.pre-commit-config.yaml`, opt-in for fast local feedback; the CI
  job is the gate.
- **Installable without a checkout** — the build carries `method.md` into the package, so an external
  author's `cvd-validate` quotes the same canon rather than a hardcoded floor. CI proves it by
  installing the built wheel and checking a palette outside the repo.

## 6. Reference recipe

```python
import itertools, math
from colorspacious import cspace_convert, deltaE

# The canon owns the conditions, the severity and the floor; the package quotes
# method.md `separation-floor` rather than keeping a second copy of any of them.
from legible.method import CVD_TYPES, SEVERITY, DELTA_E_FLOOR

def _simulate(rgb1, *, cvd_type=None, grayscale=False):
    if grayscale:                                   # drop chroma in a uniform space
        out = []
        for c in rgb1:
            J, C, h = cspace_convert(c, "sRGB1", "JCh")
            out.append(cspace_convert([J, 0.0, h], "JCh", "sRGB1"))
        return out
    if cvd_type:
        space = {"name": "sRGB1+CVD", "cvd_type": cvd_type, "severity": SEVERITY}
        return [cspace_convert(c, space, "sRGB1") for c in rgb1]
    return rgb1                                      # normal vision

def _min_pairwise(colours):                          # colours: list of sRGB1
    return min(
        deltaE(a, b, input_space="sRGB1", uniform_space="CAM02-UCS")
        for a, b in itertools.combinations(colours, 2)
    )

def validate(palette, threshold=DELTA_E_FLOOR):
    # groups built from token-contract roles present in the palette
    g1 = ["reference", "muted", *palette["series"]-roles]     # per-series ramp + anchors
    g2 = ["reference", "muted", "brand"]                      # two-group highlight + anchors
    hard_conditions = [("normal", {})] + [(t, {"cvd_type": t}) for t in CVD_TYPES]

    failures, warnings, mins = [], [], {}
    for group in (g1, g2):
        for name, kw in hard_conditions:
            sim = _simulate(role_rgb(group), **kw)
            for (i, a), (j, b) in itertools.combinations(enumerate(sim), 2):
                d = deltaE(a, b, input_space="sRGB1", uniform_space="CAM02-UCS")
                mins[name] = min(mins.get(name, math.inf), d)
                if d < threshold:
                    failures.append((name, group[i], group[j], round(d, 1)))
        # grayscale → advisory only
        gs = _simulate(role_rgb(group), grayscale=True)
        for (i, a), (j, b) in itertools.combinations(enumerate(gs), 2):
            d = deltaE(a, b, input_space="sRGB1", uniform_space="CAM02-UCS")
            if d < threshold:
                warnings.append((group[i], group[j], round(d, 1)))

    return Report(passed=not failures, threshold=threshold,
                  min_delta_e=mins, failures=failures, warnings=warnings)
```

*(`role_rgb` / the exact group construction are implementation detail; the contract is: two groups,
the canon's floor on the four hard conditions, grayscale advisory.)*

## 7. Open dependencies

- The **shared palette-loader** and whether a **Python figure helper** is a third consumer of the
  theme file is decided in [#10](https://github.com/YongboYu/legible-slides/issues/10).
- The review skill [#12] enforces "palette failing the validator" by invoking `cvd-validate` — this
  contract fixes the tool and the exit code it keys on.
- A **validated dark variant** (validator run on both grounds) is **v2**, per the token contract's
  light-only lock.
