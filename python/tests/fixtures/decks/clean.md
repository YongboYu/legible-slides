---
theme: ./theme
title: A deck that breaks no rule a script decides
colorSchema: light
---

# Retrieval beats fine-tuning at a tenth of the cost

<!--
Open on the number. Nobody argues with a tenth.
-->

---
layout: assertion-evidence
---

# Cost falls with retrieval and accuracy holds

![Mean absolute error by forecast window](/figures/mae-by-window.png)

<!--
Walk the room along the highlighted line, then stop talking.
-->

---
layout: two-col-evidence
---

# Cost tracks the index rather than the model

- error falls at the short windows
- the gap narrows past twelve hours
- retrieval carries the long tail

Evidence sits beside the claim rather than under it.

```python
save(multi_series(palette, series), "public/figures/mae-by-window.png")
```

---
layout: references
---

# Sources

- Alley and Neeley, Rethinking the design of presentation slides
- Mayer, Multimedia Learning
