---
# Built from ../plan.md by the skill's build mode: the template stamped, then each slide filled from
# its entry. The theme is consumed by path, as the template stamps it; point it at your checkout.
theme: ../legible-slides/theme
title: Time series foundation models for process model forecasting
author: Yongbo Yu
info: |
  A fifteen-minute talk on the paper, built from a talk plan as the legible-slides worked example.
duration: 15min
# The slides and the code, handed over on the cover and on the conclusion. The QR code was generated
# for the link it encodes:
#   uvx segno https://github.com/YongboYu/pmf-tsfm --error M --border 4 --light "#ffffff" \
#     --title "QR code to https://github.com/YongboYu/pmf-tsfm" --no-xmldecl --no-size \
#     --output public/share-qr.svg
# No logos: the cover's two slots show the theme's placeholders.
themeConfig:
  shareQr: /share-qr.svg
  shareUrl: https://github.com/YongboYu/pmf-tsfm
  contact: Yongbo Yu · github.com/YongboYu
layout: cover
venue: CAiSE 2026
---

# Time series foundation models for process model forecasting

## Pre-trained forecasters, used as they are, can predict how a process changes.

<!--
Time: 30s
-->

---
layout: answer
---

# Used as they are, pre-trained forecasters predict directly-follows counts with 17 to 28% less error than the best baseline.

::questions::

1. Does a larger model forecast better?
2. Does a newer model forecast better?
3. Does fine-tuning help?
4. Is there one model family to pick?

<!--
Time: 1min 30s

This is the whole talk in one slide. The rest goes through the four questions in order, and the
last slide answers them with the same numbers.
-->

---
layout: assertion-evidence
section: Problem
---

# Forecasting a process model means forecasting how often each pair of activities follows one another.

<Figure
  src="/figures/bpi2017-weekly.png"
  caption="Three directly-follows relations in the BPI 2017 loan log, counted per week."
  :cite="2"
/>

<Footnotes>
  <Footnote :number="2">BPI Challenge 2017, as processed for the paper's code.</Footnote>
</Footnotes>

<!--
Time: 1min 15s

Signpost: first the problem, then the setup, then what we found, and last where it falls short.

A process model here is a directly-follows graph: how often one activity is followed straight away
by another. Count that per day, and each arrow in the graph becomes a time series. Forecast every
series and you have the graph for next week. These three are from a loan application process, and
each one moves on its own schedule.
-->

---
layout: assertion-evidence
section: Setup
---

# Twelve pre-trained models forecast four public event logs a week ahead, with no training on them.

| Event log | Cases | Relations forecast | Days |
|---|---:|---:|---:|
| BPI 2017 | 40,229 | 21 | 319 |
| BPI 2019 | 197,521 | 149 | 307 |
| Sepsis | 999 | 135 | 459 |
| Hospital Billing | 78,828 | 73 | 726 |

<Footnotes>
  <Footnote :number="1">Yu et al. (2026), Table 2.</Footnote>
</Footnotes>

<!--
Time: 1min

Signpost: that's the problem. Here is how we tested it.

The twelve models come from three families: Chronos, MOIRAI and TimesFM. We compare them with the
two strongest baselines from our earlier benchmark, a seasonal naive forecast and a tuned XGBoost
model. Errors are mean absolute errors over the last fifth of each series.
-->

---
layout: assertion-evidence
section: Findings
---

# On every log, the best pre-trained model beats the best baseline by 17 to 28%.

<Figure
  src="/figures/against-the-baseline.png"
  caption="The best model's error on each log, as a share of the best baseline's."
  :cite="1"
/>

<Footnotes>
  <Footnote :number="1">Yu et al. (2026), Table 4.</Footnote>
</Footnotes>

<!--
Time: 1min 15s

Signpost: now the findings, one question at a time.

For each log, the baseline is whichever of the two did better, and that was the seasonal naive
forecast every time. Sepsis and BPI 2019 have the most irregular series, and that's where the gap
is largest.
-->

---
layout: assertion-evidence
---

# Within Chronos-Bolt, the larger models cut the error on BPI 2017 by a third.

<Figure
  src="/figures/chronos-bolt-sizes.png"
  caption="Zero-shot error on BPI 2017, for the four sizes of Chronos-Bolt."
  :cite="1"
/>

<Footnotes>
  <Footnote :number="1">Yu et al. (2026), Table 4.</Footnote>
</Footnotes>

<!--
Time: 1min

That answers the first question with a yes, but a careful one. On Hospital Billing, all four sizes
land within a hundredth of each other, so size helps most where there is a regular pattern to learn.
-->

---
layout: assertion-evidence
---

# MOIRAI 2.0 beats MOIRAI 1.1 with a model 27 times smaller.

<Figure
  src="/figures/moirai-generations.png"
  caption="Zero-shot error on BPI 2017, for two sizes of MOIRAI 1.1 and for MOIRAI 2.0."
  :cite="1"
/>

<Footnotes>
  <Footnote :number="1">Yu et al. (2026), Tables 1 and 4.</Footnote>
</Footnotes>

<!--
Time: 1min

The second question. A newer generation helped more than a bigger model did. MOIRAI 2.0 was
trained on about ten times as many observations as 1.1, which is our best guess at why.
-->

---
layout: assertion-evidence
---

# Fine-tuning helps a little on some logs, and full fine-tuning can nearly double the error.

| Model, on one log | No tuning | LoRA | Full fine-tuning |
|---|---:|---:|---:|
| Chronos-Bolt base, BPI 2017 | 7.62 | 7.39 | 7.52 |
| Chronos-2, BPI 2017 | 7.25 | not run | 7.89 |
| MOIRAI 1.1 large, BPI 2019 | 12.30 | 12.27 | 23.06 |

<Footnotes>
  <Footnote :number="1">Yu et al. (2026), Table 6: mean absolute error.</Footnote>
</Footnotes>

<!--
Time: 1min 15s

The third question. LoRA trains a small add-on and leaves the model itself alone, and it moved the
error by up to about a tenth, in either direction. Full fine-tuning retrains everything, and on BPI
2019 it took one model from 12.3 to 23.1. With logs this small, the model mostly learns the noise.
-->

---
layout: assertion-evidence
---

# No single family wins every log, but the newest generation is best on all four.

| Event log | Best zero-shot model | Error |
|---|---|---:|
| BPI 2017 | MOIRAI 2.0, TimesFM 2.5 | 6.87 |
| BPI 2019 | TimesFM 2.5 | 10.75 |
| Sepsis | MOIRAI 2.0 | 0.084 |
| Hospital Billing | Chronos-2, MOIRAI 2.0 | 1.39 |

<Footnotes>
  <Footnote :number="1">Yu et al. (2026), Table 4: mean absolute error. Chronos-Bolt tiny ties on Hospital Billing.</Footnote>
</Footnotes>

<!--
Time: 1min

The fourth question. Chronos-2, MOIRAI 2.0 and TimesFM 2.5 all came out in the second half of
2025, and between them they hold the best result on every log. Which family you pick seems to matter
less than picking a recent one.
-->

---
layout: assertion-evidence
section: Limits
---

# On the sparse Sepsis log, process models forecast by pre-trained models fit fewer than one trace in five.

<Figure
  src="/figures/sepsis-fit.png"
  caption="The share of Sepsis test traces each forecast process model can replay."
  :cite="1"
/>

<Footnotes>
  <Footnote :number="1">Yu et al. (2026), Table 7.</Footnote>
</Footnotes>

<!--
Time: 1min 15s

Signpost: last, where this falls short.

Lower error per series doesn't always give a better process model. We replay the test traces on
each forecast graph. On the other three logs, at least 98% of traces fit for every model. Sepsis
has few cases spread over many days, and there the pre-trained models' graphs miss most traces.
-->

---
layout: conclusion
---

# Pre-trained forecasters, used as they are, make a strong default for process model forecasting.

::answers::

1. Somewhat: larger helps most on regular logs
2. Yes: the newest models are best, or tied, on every log
3. Only a little: full fine-tuning can nearly double the error
4. No single family: pick a recent one

<!--
Time: 1min 30s

The slides, the code and the data are all linked from the QR code. Thank you, and I'm happy to take
questions.
-->

---
layout: references
section: Sources
backup: true
indexEntries:
  - title: 'Yu, Peeperkorn, De Smedt and De Weerdt (2026), Time series foundation models for process model forecasting'
    uri: https://arxiv.org/abs/2512.07624
  - title: 'van Dongen (2017), BPI Challenge 2017, 4TU.ResearchData'
    uri: https://doi.org/10.4121/uuid:5f3067df-f10b-45da-b98b-86ae4c7a310b
  - title: 'Yu (2026), Process model forecasting datasets, Zenodo'
    uri: https://doi.org/10.5281/zenodo.18327515
  - title: 'The code and results behind every figure'
    uri: https://github.com/YongboYu/pmf-tsfm
---

# Every number in this talk comes from the paper, its data or its code.
