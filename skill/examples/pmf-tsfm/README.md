# Worked example: a paper, its plan, its deck, its review

The skill's draft and build modes, run end to end on one real paper:
[_Time series foundation models for process model forecasting_](https://arxiv.org/abs/2512.07624)
and [its codebase](https://github.com/YongboYu/pmf-tsfm).

| File | What it is | Made by |
|---|---|---|
| [`plan.md`](plan.md) | The talk plan, in the format [`docs/talk-plan.md`](../../../docs/talk-plan.md) sets out | draft mode, from the paper and the code |
| [`deck/data/`](deck/data) | Two series read out of the codebase, and the script that read them | draft mode |
| [`deck/slides.md`](deck/slides.md) | The deck, one slide per plan entry | build mode |
| [`deck/figures.py`](deck/figures.py), [`deck/public/`](deck/public) | The figure script and the images it draws | build mode |
| [`review.md`](review.md) | Review mode's report on the deck | build mode's last step |

The plan was redrafted under [#38](https://github.com/YongboYu/legible-slides/issues/38), after a
comparison with the author's own CAiSE deck showed the first draft had the right shape and the wrong
story. Its questions now come from the paper's stated contributions (Section 1), each quoting the
sentence it's taken from, rather than from the axes of its tables. Five setup slides make the case
for the problem and the approach before any result, and the third question, whether a better forecast
gives a better process model, gets two slides instead of one. The slide the talk rests on and the
challenges the author expects were taken from the speaker notes and backup slides of that CAiSE deck,
which stand in for asking the author; the plan says so.

The plan's cuts are worth a look. The paper's drift figure didn't make it into the talk: the
codebase has no per-day XGBoost forecasts to redraw it from, and against the baseline that can be
rebuilt, the figure doesn't show what the paper's caption says. Draft mode is where that came up,
and the plan is where it was written down.

## What is here, and what isn't

`deck/` holds only the files build mode wrote. Everything else in a built deck, like the palette,
its stylesheet, the checks and `package.json`, is [`skill/template/`](../../template) stamped
unchanged, so it isn't copied here, where it could drift from the template. To build it:

```bash
cp -R skill/template/. /tmp/pmf-tsfm-deck/
cp -R skill/examples/pmf-tsfm/deck/. /tmp/pmf-tsfm-deck/
rm /tmp/pmf-tsfm-deck/public/placeholder.svg
# point `theme:` in /tmp/pmf-tsfm-deck/slides.md at this checkout's theme/, then:
cd /tmp/pmf-tsfm-deck && pnpm install && pnpm build
```

CI does exactly that on every push, and lints the result.
[`python/tests/test_plan.py`](../../../python/tests/test_plan.py) holds the rest: the plan is
complete, the deck matches it slide for slide, the deck passes the mechanical checks, every image
is drawn by the figure script, and the review reports the linter's verdict and every one of its
findings.

## Redrawing

```bash
cd skill/examples/pmf-tsfm/deck
uv run --project ../../../../python python figures.py ../../../template/themes/palette.json
uv run --with numpy --with pandas --with pyarrow python data/extract.py path/to/pmf-tsfm
```

The first redraws the figures. The second re-reads the data, and needs a checkout of pmf-tsfm with
its outputs.
