# CVD validator — tooling & metric research

*Research ticket: what Python tooling and metric should `legible-slides`' colour-vision-deficiency
(CVD) validator standardize on?*

> **Research input, dated.** The floor, the metric and the conditions this document proposes are now
> the canon's `separation-floor` ([`docs/method.md`](../method.md)), which is authoritative and owns
> the numbers. Read the values below as what the research recommended, not as the rule.

**Context.** The source deck (`pmf-tsfm`, CAiSE 2026) asserts that its 5-line categorical colour
set stays **"≥39 apart"** under deuteranopia / protanopia / tritanopia *and* grayscale, using
[Machado (2009)](https://www.inf.ufrgs.br/~oliveira/pubs_files/CVD_Simulation/Machado_Oliveira_Fernandes_CVD_Vis2009_final.pdf)
CVD simulation. This document works out which library and metric make that check reproducible, and
what "≥39 apart" most plausibly means. See `docs/design-provenance.md` §2 for the accessibility
background and `pmf-tsfm/slides/palette.json` for the concrete palette.

**TL;DR recommendation.** Standardize on **`colorspacious`** for the simulation *and* the distance
in one MIT-licensed dependency: Machado (2009) via the `sRGB1+CVD` space, and **ΔE in CAM02-UCS**
via `colorspacious.deltaE` (its default uniform space). That pairing is almost certainly the origin
of the deck's "≥39". Treat 39 as the *achieved* margin and set the **pass floor at ΔE ≥ 15
(CAM02-UCS)** — a large, defensible multiple of the just-noticeable difference. The one caveat:
`colorspacious` is unmaintained (last release 2018), so pin it and keep the actively-maintained
`daltonlens` as a drop-in for the simulation step.

> **Correction ([#9](https://github.com/YongboYu/legible-slides/issues/9), resolved).** The inference
> below that "≥39" *is* a min pairwise CAM02-UCS ΔE — and the framing "treat 39 as headroom above the
> 15 floor" — is **wrong on units** and is retired. Measured on the actual palette, CAM02-UCS ΔE tops
> out at ~15 (CVD) / ~11 (grayscale); "39" belongs to the *raw, non-perceptual* distance family
> (~46 in raw sRGB). "39" and "15" are the same colours on two different rulers — do not compare them.
> The library + metric recommendation (`colorspacious`, CAM02-UCS, floor 15) stands; only the "39"
> interpretation is corrected. See [`docs/cvd-validator-contract.md`](../cvd-validator-contract.md) §2.

---

## 1. CVD simulation library

Machado, Oliveira & Fernandes (2009), *A physiologically-based model for simulation of color vision
deficiency*, IEEE TVCG 15(6):1291–1298
([paper PDF](https://www.inf.ufrgs.br/~oliveira/pubs_files/CVD_Simulation/Machado_Oliveira_Fernandes_CVD_Vis2009_final.pdf)),
is the standard model. It maps colours into an LMS-based physiological space, applies a
severity-parameterised transform, and maps back — supporting both dichromacy (severity = 100%) and
anomalous trichromacy (partial). Most Python libraries ship the paper's **precomputed 3×3 matrices**.

| Library | Machado 2009? | API shape | License | Last release / maintenance |
|---|---|---|---|---|
| **`colorspacious`** | **Yes** (precomputed matrices) | `cspace_convert(c, {"name":"sRGB1+CVD","cvd_type":...,"severity":...}, "sRGB1")`; also `machado_et_al_2009_matrix(cvd_type, severity)` | MIT | **v1.1.2, Apr 2018 — inactive** ([Snyk](https://snyk.io/advisor/python/colorspacious), [libraries.io](https://libraries.io/pypi/colorspacious)) |
| **`daltonlens`** | **Yes** (+ Viénot 1999, Brettel 1997) | `simulator.simulate_cvd(im, Deficiency.PROTAN, severity=0.8)`; CLI `--model machado` | MIT | **Actively maintained** (CI, recent commits) ([repo](https://github.com/DaltonLens/DaltonLens-Python)) |
| **`coloraide`** | **Yes** (as a filter; not the default) | `Color(...).filter('deutan', 0.5, method='machado')` — *also* provides ΔE | MIT | **Actively maintained** ([filters docs](https://facelessuser.github.io/coloraide/filters/)) |
| **`colour-science`** | **Yes** (low-level) | `colour.matrix_anomalous_trichromacy_Machado2009(cmfs, primaries, d_LMS)` — needs cone fundamentals + display primaries; *also* provides ΔE | BSD-3-Clause | **Actively maintained** (0.4.x) ([repo](https://github.com/colour-science/colour)) |

**Notes on each:**

- **`colorspacious`** — the only candidate that gives Machado 2009 **and** a clean perceptual
  distance (`deltaE`, CAM02-UCS) in a single import. `cvd_type` accepts `"deuteranomaly"`,
  `"protanomaly"`, `"tritanomaly"`; `severity` is 0–100 (100 = full dichromacy). This is the
  reference implementation behind matplotlib's colormap analysis and `viscm`. Downside: no release
  since 2018 — usable but frozen, so pin the version.
- **`daltonlens`** — purpose-built for CVD research; cleanest, best-documented simulation API and
  actively maintained; also implements Viénot/Brettel for cross-checking. It is image/array-oriented
  and does **not** provide a perceptual ΔE, so you'd pair it with a distance library.
- **`coloraide`** — the most ergonomic single-library option: `filter()` for simulation *and*
  `delta_e(..., method='2000')` for distance. But its **default** protan/deutan method is Viénot
  1999 and tritan is Brettel 1997; Machado is opt-in via `method='machado'`. Good "batteries
  included" fallback if you want one dependency and are willing to pass `method='machado'` explicitly.
- **`colour-science`** — the most rigorous/complete colour library, but its Machado entry point is
  low-level (you assemble the matrix from cone fundamentals and display primaries), which is more
  ceremony than a validator needs.

**Accuracy caveat (all Machado implementations).** DaltonLens' review notes that Machado 2009 is
theoretically strongest for **anomalous trichromacy** (mild/partial CVD) and less reliable as a
*full-dichromacy* model, and that some implementations mishandle sRGB gamma decoding
([Review of Open-Source CVD Simulations](https://daltonlens.org/opensource-cvd-simulation/)). For a
pass/fail *screening* validator this is acceptable — we want a conservative "are these robustly
separated" signal, not a perceptually exact rendering — but it's why the threshold should carry
margin rather than sit at the JND.

---

## 2. Perceptual distance metric

"How far apart" two colours look should be measured in a **perceptually uniform** space, so that
equal numeric distances mean roughly equal perceived difference. Two mainstream choices:

- **CIEDE2000 (ΔE₀₀)** — the CIE/ISO-standard colour-difference formula on CIELAB. The most
  *citable* metric; available in `coloraide` (`delta_e(other, method="2000")`), `colour-science`
  (`colour.delta_E(a, b, method="CIE 2000")`), and `colormath`. ISO/CIE 11664-6.
- **ΔE in CAM02-UCS** — Euclidean distance in the CAM02-UCS uniform space (Luo, Cui & Li 2006). This
  is `colorspacious.deltaE`'s **default** (`uniform_space="CAM02-UCS"`), e.g.
  `deltaE([255,127,127],[127,255,127], input_space="sRGB255") ≈ 55`
  ([colorspacious tutorial](https://colorspacious.readthedocs.io/en/latest/tutorial.html)). It is
  the metric Nathaniel Smith's colormap tooling uses to reason about perceptual spacing.

Both are legitimate. **For this validator, use CAM02-UCS ΔE** — not because it's "better" than
CIEDE2000, but because it is what the source deck almost certainly used (see §3) and it comes free
with the recommended simulation library, avoiding a second dependency. Optionally also compute
CIEDE2000 as a citable cross-check in reports.

---

## 3. What "≥39 apart" means, and a defensible threshold

### Which colour space is "39"?

The deck used **Machado 2009**, and the one library that couples Machado 2009 with a perceptual
distance is `colorspacious`, whose `deltaE` defaults to **CAM02-UCS**. So "≥39 apart" is, with high
confidence, the **minimum pairwise ΔE in CAM02-UCS** across all simulated conditions. Sanity check:
`colorspacious`' own example gives ΔE ≈ 55 between two strongly different colours, so 39 is a large,
comfortably-separated *minimum* for a 5-colour categorical set — consistent with a set that was
deliberately tuned. (It is **not** CIEDE2000 by construction: CIEDE2000 requires a separate library
and would be an odd choice next to a Machado simulation done in `colorspacious`.) This inference
should be recorded as such — the deck did not write the space down explicitly.

### Citable reference points for "distinguishable"

There is **no single canonical ΔE threshold for "categorical colours are distinguishable."** The
literature anchors the *small* end (perceptibility), and distinguishability for data-viz is a design
choice some multiples above it:

- **Just-noticeable difference (JND):** ≈ 1.0 ΔE by common convention; Mahy et al. (1994) measured a
  mean JND of ≈ **2.3** ΔE*ab in CIELAB
  ([Color difference — Wikipedia](https://en.wikipedia.org/wiki/Color_difference)).
- **Perceptibility / acceptability thresholds (Paravina et al. 2015, dentistry — the most-cited
  primary source for ΔE₀₀ thresholds):** 50:50 **perceptibility ≈ ΔE₀₀ 0.8–1.2**, **acceptability ≈
  ΔE₀₀ 1.8–2.7**
  ([J Esthet Restor Dent](https://onlinelibrary.wiley.com/doi/abs/10.1111/jerd.12149),
  [PubMed](https://pubmed.ncbi.nlm.nih.gov/25886208/)).
- **Engineering rules of thumb (heuristics, not standards):** ΔE > 5 "easily noticeable"; industry
  guides treat ΔE ≈ 10 as "clearly different" and ≈ 20 as "unambiguously different"
  ([ColorFYI](https://colorfyi.com/blog/what-is-delta-e/),
  [Zschuessler DeltaE 101](http://zschuessler.github.io/DeltaE/learn/)).

### Recommended pass threshold

For *series that must never be confused* — a stricter bar than "just perceptible" — use a large
multiple of the JND:

> **Pass if every simulated pair has ΔE (CAM02-UCS) ≥ 15**, checked under normal vision + the three
> Machado dichromacies + grayscale.

Rationale: 15 is roughly **6–15× the JND** and well above every perceptibility/acceptability figure,
so it encodes "unambiguously distinct," while the deck's **achieved ≥ 39** shows the actual set clears
the bar with wide headroom. Document 15 as a tunable design parameter, not a physical constant. If
you prefer the citable metric, an equivalent CIEDE2000 floor of ~10–12 carries similar meaning; keep
the two thresholds separate since the scales differ slightly.

**Belt-and-braces (from the deck's own practice):** colour is never the *sole* channel — multi-line
plots add redundant dash/marker cues and bars carry direct labels. The validator screens the colour
channel; it does not replace redundant encoding.

---

## 4. Reference recipe — `validate(palette) -> pass/fail`

Minimal pseudocode using `colorspacious`. Grayscale is handled as a **desaturation** (drop chroma in
a uniform space), since it is not a Machado CVD type.

```python
import itertools, math
from colorspacious import cspace_convert, deltaE

CVD_TYPES = ["deuteranomaly", "protanomaly", "tritanomaly"]
THRESHOLD = 15.0          # CAM02-UCS ΔE floor for "distinguishable"
SEVERITY  = 100           # full dichromacy = worst case

def _simulate(rgb1, *, cvd_type=None, grayscale=False):
    """rgb1: list of sRGB colours in [0,1]. Returns simulated sRGB1 colours."""
    if grayscale:
        # drop chroma in a uniform appearance space, then back to sRGB1
        out = []
        for c in rgb1:
            J, C, h = cspace_convert(c, "sRGB1", "JCh")
            out.append(cspace_convert([J, 0.0, h], "JCh", "sRGB1"))
        return out
    if cvd_type:
        space = {"name": "sRGB1+CVD", "cvd_type": cvd_type, "severity": SEVERITY}
        return [cspace_convert(c, space, "sRGB1") for c in rgb1]
    return rgb1  # normal vision

def validate(palette_hex, threshold=THRESHOLD):
    rgb1 = [hex_to_srgb1(h) for h in palette_hex]          # '#00407a' -> [0..1]^3
    conditions  = [("normal", {})]
    conditions += [(t, {"cvd_type": t}) for t in CVD_TYPES]
    conditions += [("grayscale", {"grayscale": True})]

    worst, failures = math.inf, []
    for name, kw in conditions:
        sim = _simulate(rgb1, **kw)
        for (i, a), (j, b) in itertools.combinations(enumerate(sim), 2):
            d = deltaE(a, b, input_space="sRGB1", uniform_space="CAM02-UCS")
            worst = min(worst, d)
            if d < threshold:
                failures.append((name, palette_hex[i], palette_hex[j], round(d, 1)))

    return {"pass": not failures, "min_delta_e": round(worst, 1), "failures": failures}
```

`hex_to_srgb1` is a trivial `#rrggbb → [r/255, g/255, b/255]` helper (or use `colorspacious`
`cspace_convert(..., "sRGB255", "sRGB1")`). To reproduce the deck's headline number, run `validate`
on the truth + baseline + 3 family hues and read `min_delta_e` (expected ≈ 39 against a low
threshold).

**Swap-in for the simulation step** (if `colorspacious`' staleness ever bites): replace `_simulate`'s
CVD branch with `daltonlens` (`simulator.simulate_cvd(arr, Deficiency.DEUTAN, severity=1.0)`) and keep
`colorspacious.deltaE` for the distance — or move wholesale to `coloraide`
(`Color(hex).filter('deutan', 1, method='machado')` + `.delta_e(other, method='2000')`, noting the
metric then becomes CIEDE2000).

---

## Sources

- Machado, Oliveira & Fernandes (2009), *A physiologically-based model for simulation of color vision
  deficiency*, IEEE TVCG — [paper PDF](https://www.inf.ufrgs.br/~oliveira/pubs_files/CVD_Simulation/Machado_Oliveira_Fernandes_CVD_Vis2009_final.pdf)
- colorspacious — [GitHub](https://github.com/njsmith/colorspacious) ·
  [tutorial](https://colorspacious.readthedocs.io/en/latest/tutorial.html) ·
  [PyPI](https://pypi.org/project/colorspacious/) ·
  [maintenance (Snyk)](https://snyk.io/advisor/python/colorspacious) ·
  [libraries.io](https://libraries.io/pypi/colorspacious)
- DaltonLens-Python — [GitHub](https://github.com/DaltonLens/DaltonLens-Python) ·
  [Review of Open-Source CVD Simulations](https://daltonlens.org/opensource-cvd-simulation/) ·
  [Understanding LMS-based CVD simulations](https://daltonlens.org/understanding-cvd-simulation/)
- ColorAide — [CVD filters](https://facelessuser.github.io/coloraide/filters/) ·
  [distance / ΔE](https://facelessuser.github.io/coloraide/distance/)
- colour-science — [GitHub](https://github.com/colour-science/colour) ·
  [`colour.delta_E`](https://colour.readthedocs.io/en/latest/generated/colour.delta_E.html)
- Thresholds — [Paravina et al. 2015, *Color Difference Thresholds in Dentistry*](https://onlinelibrary.wiley.com/doi/abs/10.1111/jerd.12149)
  ([PubMed](https://pubmed.ncbi.nlm.nih.gov/25886208/)) ·
  [Color difference — Wikipedia (JND, Mahy 1994)](https://en.wikipedia.org/wiki/Color_difference) ·
  [ColorFYI — What is Delta E](https://colorfyi.com/blog/what-is-delta-e/) ·
  [Zschuessler — Delta E 101](http://zschuessler.github.io/DeltaE/learn/)
