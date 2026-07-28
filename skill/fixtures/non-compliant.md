---
# A deck built to fail its review. What each slide plants, and where, is in README.md — and the
# linter is held to that table by python/tests/test_skill.py, so this deck cannot quietly heal.
theme: ../../theme
title: A deck that breaks the method on purpose
colorSchema: light
layout: cover
---

# Results — an overview of the work

## What we found, and what it means

<!--
Say hello and thank the organisers.
-->

---
layout: default
---

# Twelve sources feed one pipeline that trains in eighteen hours

- we collected the data from twelve separate sources over a period of eighteen months in total
- preprocessing
- training
- evaluation
- ablations
- deployment

---
layout: two-col-evidence
---

# Retrieval halves the cost, and a smaller index would have served just as well

::left::

| window | baseline | retrieval |
|---|---|---|
| 1h | 0.51 | 0.29 |
| 6h | 0.55 | 0.31 |

::right::

| index | recall |
|---|---|
| full | 0.94 |
| half | 0.93 |

---
layout: default
---

# The green line beats the red line at every horizon

<div class="chart">
  <span style="color: #2f8f2f">■</span> ours
  <span style="color: #cc3333">■</span> baseline
  <svg viewBox="0 0 240 120" role="img" aria-label="Error against horizon">
    <polyline points="10,90 80,70 150,55 230,40" stroke="#2f8f2f" fill="none" stroke-width="3" />
    <polyline points="10,60 80,45 150,35 230,25" stroke="#cc3333" fill="none" stroke-width="3" />
  </svg>
</div>

---
layout: default
---

# Retrieval is not just faster, it is a different way to answer a query

This system is not just an optimisation, it is a rethinking of the retrieval stack. It is faster,
cheaper, and more elegant. It demonstrates strong performance characteristics across the board.

<!--
Before we get to the numbers, let me walk you through what we are about to see. The pipeline was
rebuilt from scratch. The index was rebuilt with it. The evaluation was rerun on the same hardware.
This is the crucial part of the talk, and the part where we leverage the new index.
-->

---
layout: default
---

# Every number above comes from the run in commit 4f2c1e

- the evaluation harness is in `bench/`
- the raw logs ship with the release

Both are in the repository the paper links to.
