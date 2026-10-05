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

# Used as they are, pre-trained forecasters cut the error by 17 to 28%, but the process models they forecast are no better.

::questions::

1. Can a pre-trained forecaster, used as it is, beat the best methods?
2. Does fine-tuning make it better still?
3. Does a better forecast give a better process model?

<!--
Time: 1min

This is the whole talk in one slide. First, why the problem is worth a new kind of model. Then the
three questions in order, and the last slide answers them with the same numbers.
-->

---
layout: assertion-evidence
section: Problem
---

# How often one step follows another changes week to week, so last month's process model is already out of date.

<Figure
  src="/figures/bpi2017-weekly.png"
  caption="Three directly-follows relations in the BPI 2017 loan log, counted per week."
  :cite="2"
/>

<Footnotes>
  <Footnote :number="2">BPI Challenge 2017, as processed for the paper's code.</Footnote>
</Footnotes>

<!--
Time: 1min

Signpost: first the problem, then our approach, then three findings.

Question: Why forecast a process model at all?

Out: Forecasting a few hundred counts sounds easy. Here's why it isn't.

A process model here is a directly-follows graph: how often one activity is followed straight away
by another. Discover it from last month's events and it describes last month. These three counts
come from a loan application process, and each one moves on its own schedule. Count each arrow per
day, and it becomes a time series. Forecast every series, and you have next week's graph. That's
process model forecasting.
-->

---
layout: assertion-evidence
---

# Each log is short and sparse: at most two years of days, and about two new Sepsis cases a day.

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

These are the four public logs we forecast. A forecaster gets a few hundred days per series to learn
from, and in Sepsis most relations are zero on most days. The same log also mixes weekly patterns,
slow trends and sudden drops, so one setting rarely suits every series in it.
-->

---
layout: assertion-evidence
---

# A tuned XGBoost model, trained on each log, forecasts no better than repeating last week.

<Figure
  src="/figures/xgboost-against-naive.png"
  caption="XGBoost's error on each log, as a share of the seasonal naive forecast's."
  :cite="1"
/>

<Footnotes>
  <Footnote :number="1">Yu et al. (2026), Table 4: mean absolute error.</Footnote>
</Footnotes>

<!--
Time: 1min

Question: Don't the methods we have already handle this?

In: So the data is small and noisy. Here's what a tuned model makes of it.

Out: Training from scratch doesn't pay on data this small. What if the model needed no training at all?

Q&A: Were the baselines tuned? Yes: they're two of the strongest from our earlier benchmark, and XGBoost's hyperparameters were optimized (Section 4.1).

In our earlier benchmark, machine learning and deep learning models gave only modest gains over
simple statistical ones. These are two of the strongest from it: a seasonal naive forecast, which says
next week looks like this week, and an XGBoost model with its hyperparameters tuned. XGBoost loses
on all four logs, by 2% on the two BPI logs and by about half on Sepsis and Hospital Billing. On
data this small, a model trained from scratch mostly learns the noise.
-->

---
layout: assertion-evidence
section: Approach
---

# A time series foundation model is pre-trained the way a language model is, on series instead of text.

| | Language model | Time series foundation model |
|---|---|---|
| Pre-trained on | Text | Series from many domains |
| Reads and writes | Words | Numbers over time |
| On data it has never seen | Used with no training | Used with no training: zero-shot |

<Footnotes>
  <Footnote :number="1">Yu et al. (2026), Section 3.2 and Table 1.</Footnote>
</Footnotes>

<!--
Time: 1min

Signpost: that's the problem. Here is what we tried.

Question: Is this just a language model?

Out: So why should a model trained on other data help with ours?

Q&A: Did you fine-tune GPT? No: these are forecasters pre-trained on time series, not language models (Section 3.2).

The current direction in forecasting is foundation models. A language model learns from a huge
amount of text and then works on text it has never seen. A time series foundation model does the
same with numbers over time. So we're not using a language model here. We use these forecasters
zero-shot: we run the pre-trained model on a new log, with no training at all. Fine-tuning means
training it further on the log.
-->

---
layout: assertion-evidence
---

# Every pre-training corpus the paper states holds over 400,000 times more observations than our largest log.

| Data | Observations |
|---|---:|
| MOIRAI 1.1's pre-training, the smallest stated | 27 billion |
| MOIRAI 2.0's pre-training, the largest | 296 billion |
| Sepsis, our largest log | 62 thousand |

<Footnotes>
  <Footnote :number="1">Yu et al. (2026), Tables 1 and 2. Sepsis is 135 series over 459 days.</Footnote>
</Footnotes>

<!--
Time: 1min

Why should that help? A model trained from scratch has only the log to learn from. A pre-trained one
brings patterns it learned elsewhere, like weekly cycles and trends, and used zero-shot, it never
sees our small log in training, so it has nothing to overfit.

We tested twelve of them, from three families: Chronos, MOIRAI and TimesFM. Each forecasts every
series a week ahead, over the last fifth of each log, against the two baselines from the last slide
but one. The error is the mean absolute error.
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

Signpost: now the three findings, one question at a time.

Question: Used as they are, do they beat the best methods?

Out: There are twelve of them, so which one should you pick?

Q&A: Does RMSE tell the same story? Yes: it agrees with the mean absolute error everywhere the talk makes a claim (Table 5).

The first question, and the answer is yes. For each log, the baseline is whichever of the two did
better, and that was the seasonal naive forecast every time. Sepsis and BPI 2019 have the most
irregular series, and that's where the gap is largest. The best result on every log comes from one
of the three newest models: Chronos-2, MOIRAI 2.0 or TimesFM 2.5.
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
Time: 45s

Question: Does a bigger model help?

In: Here are two generations of one family, on one log.

Out: They're strong as they are. Can training them on the log make them stronger?

Q&A: Which model should I use? No family wins every log, and the three newest models hold the best result on all four between them (Table 4).

A newer generation helped more than a bigger model did. MOIRAI 2.0 was trained on about ten times as
many observations as 1.1, which is our best guess at why. Within a generation, larger models do
help, but most on logs with a regular pattern to learn.
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

<Callout accent>

Full fine-tuning on BPI 2019: from 12.3 to 23.1

</Callout>

<Footnotes>
  <Footnote :number="1">Yu et al. (2026), Table 6: mean absolute error.</Footnote>
</Footnotes>

<!--
Time: 1min

Question: Does fine-tuning make it better still?

In: Now the second question: training them further on each log.

Out: So far, every number is the error on each series. Now the process model they add up to.

LoRA trains a small add-on and leaves the model itself alone, and it moved the error by up to about
a tenth, in either direction. Full fine-tuning retrains everything, and on BPI 2019 it took one
model from 12.3 to 23.1. With logs this small, the model mostly learns the noise, the same thing
that held XGBoost back.
-->

---
layout: two-col-evidence
---

# Yet on three logs, the process models they forecast score 6 to 13% worse than the baselines' on entropic relevance.

::left::

<Figure
  src="/figures/process-model-relevance.png"
  caption="Entropic relevance of the best model's forecast graphs, as a share of the best baseline's. Lower is better."
  :cite="1"
/>

::right::

<Figure
  v-click
  src="/figures/against-the-baseline-beside.png"
  caption="From slide 8: the error of the same forecasts, as a share of the best baseline's."
  :cite="2"
/>

<Footnotes>
  <Footnote :number="1">Yu et al. (2026), Table 7.</Footnote>
  <Footnote :number="2">Yu et al. (2026), Table 4.</Footnote>
</Footnotes>

<!--
Time: 1min 15s

Question: Does a better forecast give a better process model?

In: Now the third question: what those forecasts add up to.

Out: And on the fourth log, Sepsis, the graphs do much worse.

We find this one the most interesting. We rebuild the forecast counts into a directly-follows graph
for each week and replay the real traces on it. Entropic relevance is how many bits that graph needs
to describe them, so lower is better. The pre-trained models' graphs come out slightly worse than
the baselines', even though their counts were more accurate. All of them do better than reusing the
graph from the training data, which scores 1.15, 3.89 and 5.83 on these three logs. So forecasting
the graph is worth it, but a lower error per series doesn't add up to a better graph.
-->

---
layout: assertion-evidence
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
Time: 45s

Question: What happens on the sparsest log?

In: Now the fourth log, the one the last slide left out.

Out: So, to answer the three questions.

Q&A: Why does Sepsis fail? Its cases are spread thin over many days, and its series carry the weakest temporal signal (Tables 2 and 3).

On the other three logs, at least 98% of traces fit for every model. Sepsis has few cases spread
over many days, and there the pre-trained models' graphs miss most traces.
-->

---
layout: conclusion
---

# Used as they are, pre-trained forecasters beat both baselines on all four logs, so they make a strong default to build on.

::answers::

1. Yes: 17 to 28% less error than the best baseline
2. Barely: full fine-tuning can nearly double the error
3. Not yet: no better process models, and much worse on Sepsis

<!--
Time: 1min

The next step is to make a better forecast give a better process model. The slides, the code and
the data are all linked from the QR code. Thank you, and I'm happy to take questions.
-->

---
layout: assertion-evidence
section: Backup
backup: true
---

# Measured by RMSE, the best pre-trained model still beats the best baseline on every log, by 22 to 33%.

<Figure
  src="/figures/against-the-baseline-rmse.png"
  caption="The best model's root mean squared error on each log, as a share of the best baseline's."
  :cite="1"
/>

<Footnotes>
  <Footnote :number="1">Yu et al. (2026), Table 5: root mean squared error.</Footnote>
</Footnotes>

<!--
Time: 45s

Question: Does RMSE tell the same story?

The best baseline changes under this measure: XGBoost on the two BPI logs, seasonal naive on Sepsis
and Hospital Billing. Against whichever is better, the best pre-trained model still wins on all
four, by about as much as it does on the mean absolute error.
-->

---
layout: assertion-evidence
---

# A larger Chronos-Bolt cuts the error on BPI 2017 by a third, and on Hospital Billing barely moves it.

| Chronos-Bolt | Tiny, 9M | Mini, 21M | Small, 48M | Base, 205M |
|---|---:|---:|---:|---:|
| BPI 2017 | 11.64 | 9.70 | 7.72 | 7.62 |
| Hospital Billing | 1.39 | 1.40 | 1.40 | 1.40 |

<Footnotes>
  <Footnote :number="1">Yu et al. (2026), Table 4: mean absolute error; sizes from Table 1.</Footnote>
</Footnotes>

<!--
Time: 45s

Question: Within one family, do larger models do better?

Size helps where there's a regular pattern to learn. BPI 2017 has the strongest seasonality of the
four logs, and the error falls from 11.64 to 7.62 as the model grows. On Hospital Billing all four
sizes land within a hundredth of each other.
-->

---
layout: assertion-evidence
---

# The newest model of each family is best on at least one log, so no family wins them all.

| Log | Chronos-2 | MOIRAI 2.0 | TimesFM 2.5 |
|---|---:|---:|---:|
| BPI 2017 | 7.25 | 6.87 | 6.87 |
| BPI 2019 | 11.39 | 10.99 | 10.75 |
| Sepsis | 0.090 | 0.084 | 0.096 |
| Hospital Billing | 1.39 | 1.39 | 1.42 |

<Footnotes>
  <Footnote :number="1">Yu et al. (2026), Table 4: mean absolute error, zero-shot.</Footnote>
</Footnotes>

<!--
Time: 1min

Question: Which model should I use?

MOIRAI 2.0 is best or tied for it on three logs, TimesFM 2.5 on two, and Chronos-2 ties on Hospital
Billing. If you can run only one, start with the newest model of any family: within each family,
the newest generation is best or tied for best on every log.
-->

---
layout: assertion-evidence
---

# Sepsis's series have the weakest trend, the least stationarity and the most non-Gaussian values of the four logs.

| Log | Trend | Stationarity | Non-Gaussianity |
|---|---:|---:|---:|
| BPI 2017 | 0.255 | 0.222 | 0.334 |
| BPI 2019 | 0.154 | 0.094 | 0.465 |
| Sepsis | 0.087 | 0.003 | 0.585 |
| Hospital Billing | 0.260 | 0.137 | 0.457 |

<Footnotes>
  <Footnote :number="1">Yu et al. (2026), Table 3, three of its seven characteristics; Table 2 for the cases.</Footnote>
</Footnotes>

<!--
Time: 1min

Question: Why do the process models fail on Sepsis?

Sepsis has about two new cases a day over more than a year, so most relations are zero on most
days. What's left has little trend and little regularity to forecast a week ahead, and a graph
rebuilt from those forecasts misses most of the traces.
-->

---
layout: assertion-evidence
---

# LoRA trained a rank-2 add-on for three epochs, and full fine-tuning followed each model's own recipe.

| | LoRA | Full fine-tuning |
|---|---|---|
| What trains | A rank-2 add-on to the attention weights | Every weight |
| Schedule | AdamW, learning rate 1e-4, 3 epochs | Each model's original recipe |
| Patch, batch | 16, 32 | 16, 32 |

<Footnotes>
  <Footnote :number="1">Yu et al. (2026), Section 4.1.</Footnote>
</Footnotes>

<!--
Time: 45s

Question: How exactly did you fine-tune them?

We kept LoRA small on purpose: with logs this size, a larger add-on has more room to overfit. Both
kinds used the same patch size and batch size, so the two can be compared with each other fairly.
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
