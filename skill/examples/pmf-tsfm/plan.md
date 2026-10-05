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

1. Can a pre-trained forecaster, used as it is, beat the best methods?
   - **Stated in:** Section 1, the contributions: "off-the-shelf models already outperform strong statistical and learning-based baselines in terms of MAE and RMSE". Section 4.1's questions on model size, iteration and family are the evidence under it.
2. Does fine-tuning make it better still?
   - **Stated in:** Section 1, the contributions: "identify when fine-tuning yields reliable gains and when it mainly introduces overfitting". Section 4.1 asks it again, as its third question.
3. Does a better forecast give a better process model?
   - **Stated in:** Section 1, the contributions: "combine time-series accuracy metrics with process-aware evaluation of the forecasted models".

## Slides

### 1. Time series foundation models for process model forecasting

- **Layout:** cover
- **Evidence:** subtitle. Pre-trained forecasters, used as they are, can predict how a process changes.
- **Time:** 30s

### 2. Used as they are, pre-trained forecasters cut the error by 17 to 28%, but the process models they forecast are no better.

- **Layout:** answer
- **Evidence:** questions. The three questions above.
- **Time:** 1min

This is the whole talk in one slide. First, why the problem is worth a new kind of model. Then the
three questions in order, and the last slide answers them with the same numbers.

### 3. How often one step follows another changes week to week, so last month's process model is already out of date.

- **Section:** Problem
- **Setup:** stakes
- **Layout:** assertion-evidence
- **Evidence:** figure. Weekly counts of three directly-follows relations in the BPI 2017 loan log, which rise and fall on their own schedules.
- **Source:** Section 1 of the paper; the BPI Challenge 2017 log, as processed in `data/time_series/bpi2017.parquet` of the code.
- **Terms:** directly-follows
- **Time:** 1min
- **Notes:**
  - **Question:** Why forecast a process model at all?
  - **Out:** Forecasting a few hundred counts sounds easy. Here's why it isn't.

Signpost: first the problem, then our approach, then three findings.

A process model here is a directly-follows graph: how often one activity is followed straight away
by another. Discover it from last month's events and it describes last month. These three counts
come from a loan application process, and each one moves on its own schedule. Count each arrow per
day, and it becomes a time series. Forecast every series, and you have next week's graph. That's
process model forecasting.

### 4. Each log is short and sparse: at most two years of days, and about two new Sepsis cases a day.

- **Section:** Problem
- **Setup:** difficulty
- **Layout:** assertion-evidence
- **Evidence:** table. The four logs: how many cases, how many relations get forecast, and how many days they span.
- **Source:** Table 2 of the paper.
- **Time:** 1min

These are the four public logs we forecast. A forecaster gets a few hundred days per series to learn
from, and in Sepsis most relations are zero on most days. The same log also mixes weekly patterns,
slow trends and sudden drops, so one setting rarely suits every series in it.

### 5. A tuned XGBoost model, trained on each log, forecasts no better than repeating last week.

- **Section:** Problem
- **Setup:** gap
- **Layout:** assertion-evidence
- **Evidence:** figure. XGBoost's error on each log, as a share of the seasonal naive forecast's, with the naive forecast at 1.
- **Source:** Table 4 of the paper; Section 1 for the earlier benchmark.
- **Terms:** seasonal naive
- **Time:** 1min
- **Notes:**
  - **Question:** Don't the methods we have already handle this?
  - **In:** So the data is small and noisy. Here's what a tuned model makes of it.
  - **Out:** Training from scratch doesn't pay on data this small. What if the model needed no training at all?
  - **Q&A:** Were the baselines tuned? Yes: they're two of the strongest from our earlier benchmark, and XGBoost's hyperparameters were optimized (Section 4.1).

In our earlier benchmark, machine learning and deep learning models gave only modest gains over
simple statistical ones. These are two of the strongest from it: a seasonal naive forecast, which says
next week looks like this week, and an XGBoost model with its hyperparameters tuned. XGBoost loses
on all four logs, by 2% on the two BPI logs and by about half on Sepsis and Hospital Billing. On
data this small, a model trained from scratch mostly learns the noise.

### 6. A time series foundation model is pre-trained the way a language model is, on series instead of text.

- **Section:** Approach
- **Setup:** approach
- **Load-bearing:** Without it, half the room thinks we fine-tuned GPT.
- **Layout:** assertion-evidence
- **Evidence:** table. A language model beside a time series foundation model: what each is trained on, what it reads and writes, and how it is used on data it has never seen.
- **Source:** Section 3.2 and Table 1 of the paper.
- **Terms:** time series foundation model, zero-shot
- **Time:** 1min
- **Notes:**
  - **Question:** Is this just a language model?
  - **Out:** So why should a model trained on other data help with ours?
  - **Q&A:** Did you fine-tune GPT? No: these are forecasters pre-trained on time series, not language models (Section 3.2).

Signpost: that's the problem. Here is what we tried.

The current direction in forecasting is foundation models. A language model learns from a huge
amount of text and then works on text it has never seen. A time series foundation model does the
same with numbers over time. So we're not using a language model here. We use these forecasters
zero-shot: we run the pre-trained model on a new log, with no training at all. Fine-tuning means
training it further on the log.

### 7. Every pre-training corpus the paper states holds over 400,000 times more observations than our largest log.

- **Section:** Approach
- **Setup:** approach
- **Layout:** assertion-evidence
- **Evidence:** table. The smallest and largest pre-training corpus the paper states, beside the largest of the four logs.
- **Source:** Tables 1 and 2 of the paper: 27 and 296 billion observations; Sepsis has 135 series over 459 days.
- **Time:** 1min

Why should that help? A model trained from scratch has only the log to learn from. A pre-trained one
brings patterns it learned elsewhere, like weekly cycles and trends, and used zero-shot, it never
sees our small log in training, so it has nothing to overfit.

We tested twelve of them, from three families: Chronos, MOIRAI and TimesFM. Each forecasts every
series a week ahead, over the last fifth of each log, against the two baselines from the last slide
but one. The error is the mean absolute error.

### 8. On every log, the best pre-trained model beats the best baseline by 17 to 28%.

- **Section:** Findings
- **Answers:** 1
- **Layout:** assertion-evidence
- **Evidence:** figure. The best model's error on each log, as a share of the best baseline's, with the baseline at 1.
- **Source:** Table 4 of the paper.
- **Time:** 1min 15s
- **Notes:**
  - **Question:** Used as they are, do they beat the best methods?
  - **Out:** There are twelve of them, so which one should you pick?
  - **Q&A:** Does RMSE tell the same story? Yes: it agrees with the mean absolute error everywhere the talk makes a claim (Table 5).

Signpost: now the three findings, one question at a time.

The first question, and the answer is yes. For each log, the baseline is whichever of the two did
better, and that was the seasonal naive forecast every time. Sepsis and BPI 2019 have the most
irregular series, and that's where the gap is largest. The best result on every log comes from one
of the three newest models: Chronos-2, MOIRAI 2.0 or TimesFM 2.5.

### 9. MOIRAI 2.0 beats MOIRAI 1.1 with a model 27 times smaller.

- **Section:** Findings
- **Answers:** 1
- **Layout:** assertion-evidence
- **Evidence:** figure. Zero-shot error on BPI 2017 for two sizes of MOIRAI 1.1 and for MOIRAI 2.0, labeled with their sizes.
- **Source:** Table 1 and Table 4 of the paper.
- **Time:** 45s
- **Notes:**
  - **Question:** Does a bigger model help?
  - **In:** Here are two generations of one family, on one log.
  - **Out:** They're strong as they are. Can training them on the log make them stronger?
  - **Q&A:** Which model should I use? No family wins every log, and the three newest models hold the best result on all four between them (Table 4).

A newer generation helped more than a bigger model did. MOIRAI 2.0 was trained on about ten times as
many observations as 1.1, which is our best guess at why. Within a generation, larger models do
help, but most on logs with a regular pattern to learn.

### 10. Fine-tuning helps a little on some logs, and full fine-tuning can nearly double the error.

- **Section:** Findings
- **Answers:** 2
- **Layout:** assertion-evidence
- **Evidence:** table. Error for three models with no tuning, with LoRA, and with full fine-tuning.
- **Source:** Table 6 of the paper.
- **Callout:** Full fine-tuning on BPI 2019: from 12.3 to 23.1
- **Terms:** fine-tuning, LoRA
- **Time:** 1min
- **Notes:**
  - **Question:** Does fine-tuning make it better still?
  - **In:** Now the second question: training them further on each log.
  - **Out:** So far, every number is the error on each series. Now the process model they add up to.

LoRA trains a small add-on and leaves the model itself alone, and it moved the error by up to about
a tenth, in either direction. Full fine-tuning retrains everything, and on BPI 2019 it took one
model from 12.3 to 23.1. With logs this small, the model mostly learns the noise, the same thing
that held XGBoost back.

### 11. Yet on three logs, the process models they forecast score 6 to 13% worse than the baselines' on entropic relevance.

- **Section:** Findings
- **Answers:** 3
- **Layout:** two-col-evidence
- **Evidence:** figure. Entropic relevance of the best pre-trained model's forecast graphs on BPI 2017, BPI 2019 and Hospital Billing, as a share of the best baseline's, with the baseline at 1. Lower is better. Beside it, slide 8's error figure, where lower is better too.
- **Source:** Table 7 of the paper; Table 4 for slide 8's figure.
- **Returns:** Slide 8, beside the relevance figure: the error of the same forecasts, each against its best baseline.
- **Reveal:** slide 8's figure, after the relevance figure
- **Terms:** entropic relevance
- **Time:** 1min 15s
- **Notes:**
  - **Question:** Does a better forecast give a better process model?
  - **In:** Now the third question: what those forecasts add up to.
  - **Out:** And on the fourth log, Sepsis, the graphs do much worse.

We find this one the most interesting. We rebuild the forecast counts into a directly-follows graph
for each week and replay the real traces on it. Entropic relevance is how many bits that graph needs
to describe them, so lower is better. The pre-trained models' graphs come out slightly worse than
the baselines', even though their counts were more accurate. All of them do better than reusing the
graph from the training data, which scores 1.15, 3.89 and 5.83 on these three logs. So forecasting
the graph is worth it, but a lower error per series doesn't add up to a better graph.

### 12. On the sparse Sepsis log, process models forecast by pre-trained models fit fewer than one trace in five.

- **Section:** Findings
- **Answers:** 3
- **Layout:** assertion-evidence
- **Evidence:** figure. The share of Sepsis traces each forecast process model can replay, for the two baselines and the three newest models.
- **Source:** Table 7 of the paper.
- **Time:** 45s
- **Notes:**
  - **Question:** What happens on the sparsest log?
  - **In:** Now the fourth log, the one the last slide left out.
  - **Out:** So, to answer the three questions.
  - **Q&A:** Why does Sepsis fail? Its cases are spread thin over many days, and its series carry the weakest temporal signal (Tables 2 and 3).

On the other three logs, at least 98% of traces fit for every model. Sepsis has few cases spread
over many days, and there the pre-trained models' graphs miss most traces.

### 13. Used as they are, pre-trained forecasters beat both baselines on all four logs, so they make a strong default to build on.

- **Layout:** conclusion
- **Evidence:** answers.
  1. Yes: 17 to 28% less error than the best baseline
  2. Barely: full fine-tuning can nearly double the error
  3. Not yet: no better process models, and much worse on Sepsis
- **Time:** 1min

The next step is to make a better forecast give a better process model. The slides, the code and
the data are all linked from the QR code. Thank you, and I'm happy to take questions.

## Challenges

Taken from the author's speaker notes and backup slides in the CAiSE deck, which stand in here for
asking them.

- **Did you fine-tune GPT?** Slide 6: these are forecasters pre-trained on time series, not language
  models.
- **Were the baselines tuned, and are they the strongest you had?** Slide 5's notes, and in Q&A
  from Section 4.1: they are two of the strongest from the earlier benchmark, and XGBoost's
  hyperparameters were optimized.
- **Does RMSE tell the same story?** Slide 8's notes, from Table 5: it agrees with the mean absolute error
  everywhere the talk makes a claim.
- **Why does Sepsis fail?** Slide 12, and in Q&A from Tables 2 and 3: its cases are spread thin
  over many days, and its series carry the weakest temporal signal.
- **Which model should I use?** Slide 9's notes, from Table 4: no family wins every log,
  and the three newest models hold the best result on all four between them.

## Cut

- **Model size, as its own slide.** Within Chronos-Bolt, the larger models cut the error on BPI 2017
  by a third, but on Hospital Billing all four sizes land within a hundredth of each other. It's
  Section 4.1's first question, and evidence under the talk's first. Slide 9 makes the stronger
  point, that a newer generation beats a bigger model, and its notes say the rest.
- **Model families, as their own slide.** The best zero-shot model on each log is a different
  family's, but always one of the newest three. It's Section 4.1's fourth question; slide 8's notes
  and the challenges carry it.
- **The drift figure.** The paper shows four series where the pre-trained models recover from a
  sudden drop and XGBoost does not. XGBoost's per-day forecasts are not in the codebase, only its
  averages. Against the seasonal naive baseline, which can be rebuilt from the data, the
  pre-trained models do worse on that relation after the drop (mean absolute error about 21 to 22,
  against 10; `deck/data/bpi2017-drift.csv`). Showing it would need the XGBoost forecasts first.
- **The RMSE table.** It agrees with the MAE results everywhere the talk makes a claim, so it stays
  in the paper, and in the challenges.
- **Time series characteristics.** The paper's Table 3 explains why the logs differ, and relating
  the results to it is the other half of the contribution question 3 quotes. Slide 4 says it in
  words, and the table stays in the paper for Q&A.
- **How LoRA works.** The equation is in the paper. The talk needs only that LoRA trains a small
  add-on and full fine-tuning trains everything.
