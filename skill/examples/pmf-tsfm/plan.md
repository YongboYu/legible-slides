---
title: Time series foundation models for process model forecasting
speaker: Yongbo Yu
venue: CAiSE 2026
duration: 15min
paper: https://arxiv.org/abs/2512.07624
code: https://github.com/YongboYu/pmf-tsfm
---

# Time series foundation models for process model forecasting

## Questions

1. Does a larger model forecast better?
2. Does a newer model forecast better?
3. Does fine-tuning help?
4. Is there one model family to pick?

## Slides

### 1. Time series foundation models for process model forecasting

- **Layout:** cover
- **Evidence:** subtitle. Pre-trained forecasters, used as they are, can predict how a process changes.
- **Time:** 30s

### 2. Used as they are, pre-trained forecasters predict directly-follows counts with 17 to 28% less error than the best baseline.

- **Layout:** answer
- **Evidence:** questions. The four questions above.
- **Time:** 1min 30s

This is the whole talk in one slide. The rest goes through the four questions in order, and the
last slide answers them with the same numbers.

### 3. Forecasting a process model means forecasting how often each pair of activities follows one another.

- **Section:** Problem
- **Layout:** assertion-evidence
- **Evidence:** figure. Weekly counts of three directly-follows relations in the BPI 2017 loan log, which rise and fall on their own schedules.
- **Source:** the BPI Challenge 2017 log, as processed in `data/time_series/bpi2017.parquet` of the code.
- **Time:** 1min 15s

Signpost: first the problem, then the setup, then what we found, and last where it falls short.

A process model here is a directly-follows graph: how often one activity is followed straight away
by another. Count that per day, and each arrow in the graph becomes a time series. Forecast every
series and you have the graph for next week. These three are from a loan application process, and
each one moves on its own schedule.

### 4. Twelve pre-trained models forecast four public event logs a week ahead, with no training on them.

- **Section:** Setup
- **Layout:** assertion-evidence
- **Evidence:** table. The four logs: how many cases, how many relations get forecast, and how many days they span.
- **Source:** Table 2 of the paper.
- **Time:** 1min

Signpost: that's the problem. Here is how we tested it.

The twelve models come from three families: Chronos, MOIRAI and TimesFM. We compare them with the
two strongest baselines from our earlier benchmark, a seasonal naive forecast and a tuned XGBoost
model. Errors are mean absolute errors over the last fifth of each series.

### 5. On every log, the best pre-trained model beats the best baseline by 17 to 28%.

- **Section:** Findings
- **Layout:** assertion-evidence
- **Evidence:** figure. The best model's error on each log, as a share of the best baseline's, with the baseline at 1.
- **Source:** Table 4 of the paper.
- **Time:** 1min 15s

Signpost: now the findings, one question at a time.

For each log, the baseline is whichever of the two did better, and that was the seasonal naive
forecast every time. Sepsis and BPI 2019 have the most irregular series, and that's where the gap
is largest.

### 6. Within Chronos-Bolt, the larger models cut the error on BPI 2017 by a third.

- **Section:** Findings
- **Layout:** assertion-evidence
- **Evidence:** figure. Zero-shot error on BPI 2017 for the four sizes of Chronos-Bolt, the largest highlighted.
- **Source:** Table 4 of the paper.
- **Time:** 1min

That answers the first question with a yes, but a careful one. On Hospital Billing, all four sizes
land within a hundredth of each other, so size helps most where there is a regular pattern to learn.

### 7. MOIRAI 2.0 beats MOIRAI 1.1 with a model 27 times smaller.

- **Section:** Findings
- **Layout:** assertion-evidence
- **Evidence:** figure. Zero-shot error on BPI 2017 for two sizes of MOIRAI 1.1 and for MOIRAI 2.0, labeled with their sizes.
- **Source:** Table 1 and Table 4 of the paper.
- **Time:** 1min

The second question. A newer generation helped more than a bigger model did. MOIRAI 2.0 was
trained on about ten times as many observations as 1.1, which is our best guess at why.

### 8. Fine-tuning helps a little on some logs, and full fine-tuning can nearly double the error.

- **Section:** Findings
- **Layout:** assertion-evidence
- **Evidence:** table. Error for three models with no tuning, with LoRA, and with full fine-tuning.
- **Source:** Table 6 of the paper.
- **Time:** 1min 15s

The third question. LoRA trains a small add-on and leaves the model itself alone, and it moved the
error by up to about a tenth, in either direction. Full fine-tuning retrains everything, and on BPI 2019 it took one
model from 12.3 to 23.1. With logs this small, the model mostly learns the noise.

### 9. No single family wins every log, but the newest generation is best on all four.

- **Section:** Findings
- **Layout:** assertion-evidence
- **Evidence:** table. The best zero-shot model on each log, and its error.
- **Source:** Table 4 of the paper.
- **Time:** 1min

The fourth question. Chronos-2, MOIRAI 2.0 and TimesFM 2.5 all came out in the second half of
2025, and between them they hold the best result on every log. Which family you pick seems to matter less
than picking a recent one.

### 10. On the sparse Sepsis log, process models forecast by pre-trained models fit fewer than one trace in five.

- **Section:** Limits
- **Layout:** assertion-evidence
- **Evidence:** figure. The share of Sepsis traces each forecast process model can replay, for the two baselines and the three newest models.
- **Source:** Table 7 of the paper.
- **Time:** 1min 15s

Signpost: last, where this falls short.

Lower error per series doesn't always give a better process model. We replay the test traces on
each forecast graph. On the other three logs, at least 98% of traces fit for every model. Sepsis has few
cases spread over many days, and there the pre-trained models' graphs miss most traces.

### 11. Pre-trained forecasters, used as they are, make a strong default for process model forecasting.

- **Layout:** conclusion
- **Evidence:** answers.
  1. Somewhat: larger helps most on regular logs
  2. Yes: the newest models are best, or tied, on every log
  3. Only a little: full fine-tuning can nearly double the error
  4. No single family: pick a recent one
- **Time:** 1min 30s

The slides, the code and the data are all linked from the QR code. Thank you, and I'm happy to take
questions.

## Cut

- **The drift figure.** The paper shows four series where the pre-trained models recover from a
  sudden drop and XGBoost does not. XGBoost's per-day forecasts are not in the codebase, only its
  averages. Against the seasonal naive baseline, which can be rebuilt from the data, the
  pre-trained models do worse on that relation after the drop (mean absolute error about 21 to 22,
  against 10; `deck/data/bpi2017-drift.csv`). Showing it would need the XGBoost forecasts first.
- **The RMSE table.** It agrees with the MAE results everywhere the talk makes a claim, so it stays
  in the paper.
- **Time series characteristics.** The paper's Table 3 explains why the logs differ. It's a good
  answer to a question, so it stays in the paper for Q&A.
- **How LoRA works.** The equation is in the paper. The talk needs only that LoRA trains a small
  add-on and full fine-tuning trains everything.
