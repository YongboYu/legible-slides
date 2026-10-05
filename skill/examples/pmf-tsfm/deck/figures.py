"""The worked example's figures, drawn from its data and its palette by the shipped archetypes.

Build mode draws every chart a plan entry calls for here, rather than pasting one in, so a recolour
reaches it and `separation-floor` has measured it. The numbers come from two places, and each says
which: the paper's tables, typed in below with the table each came from, and the two files in
``data/`` that ``data/extract.py`` read out of the pmf-tsfm codebase.

Run it from the stamped deck, and commit what it writes. It reads the deck's own palette by
default; from this checkout, where the deck is only the files build mode wrote over the template,
name the template's:

    uv run --project ../../../../python python figures.py ../../../template/themes/palette.json
"""

from __future__ import annotations

import csv
import sys
from functools import partial
from pathlib import Path

from legible import load_palette
from legible.figures import Series, multi_series, save, two_group

HERE = Path(__file__).resolve().parent

#: The palette a stamped deck wears, and keeps here.
PALETTE = HERE / "themes" / "palette.json"

#: Where the deck serves its figures from, under public/.
FIGURES = "figures"

#: One pane of a two-column evidence slide: its size in canvas px, and type at the floor rather than
#: the body size, because a pane this narrow has no room for body type on an axis (`type-scale`).
COLUMN = {"size_px": (540, 350), "tight_panel": True}

#: Zero-shot mean absolute error, Table 4 of the paper. The best baseline on every log is the
#: seasonal naive forecast, and the best model is the lowest error in that log's column.
BEST_BASELINE = {"BPI 2017": 8.30, "BPI 2019": 14.47, "Sepsis": 0.117, "Billing": 1.77}
BEST_MODEL = {"BPI 2017": 6.87, "BPI 2019": 10.75, "Sepsis": 0.084, "Billing": 1.39}

#: Zero-shot root mean squared error, Table 5. The best baseline is XGBoost on the two BPI logs and
#: the seasonal naive forecast on the other two; the best model is again the lowest in each column.
BEST_BASELINE_RMSE = {"BPI 2017": 11.91, "BPI 2019": 23.87, "Sepsis": 0.187, "Billing": 2.21}
BEST_MODEL_RMSE = {"BPI 2017": 9.32, "BPI 2019": 18.12, "Sepsis": 0.125, "Billing": 1.70}

#: The tuned XGBoost baseline's mean absolute error, Table 4, beside the seasonal naive's above.
XGBOOST = {"BPI 2017": 8.50, "BPI 2019": 14.70, "Sepsis": 0.169, "Billing": 2.67}

#: Entropic relevance of the forecast graphs, Table 7, on the three logs where every model fits at
#: least 98% of traces: the best baseline (XGBoost on all three) and the best pre-trained model.
#: Lower is better.
RELEVANCE_BASELINE = {"BPI 2017": 1.01, "BPI 2019": 2.39, "Billing": 2.12}
RELEVANCE_MODEL = {"BPI 2017": 1.09, "BPI 2019": 2.54, "Billing": 2.39}

#: MOIRAI on BPI 2017, Table 4, by generation and size (Table 1).
MOIRAI_PREVIOUS = {"1.1 small\n14M": 10.24, "1.1 large\n311M": 9.29}
MOIRAI_NEWEST = {"2.0\n11M": 6.87}

#: The share of Sepsis test traces each forecast process model can replay, in percent, Table 7.
SEPSIS_BASELINES = {"Seasonal\nnaive": 39.4, "XGBoost": 74.6}
SEPSIS_MODELS = {"Chronos-2": 13.2, "MOIRAI\n2.0": 4.1, "TimesFM\n2.5": 17.5}


def weekly_series(palette):
    with (HERE / "data" / "bpi2017-weekly.csv").open(encoding="utf-8") as source:
        rows = list(csv.DictReader(source))
    labels = [key for key in rows[0] if key != "week"]
    return multi_series(
        palette,
        [Series(label, [int(row[label]) for row in rows]) for label in labels],
        x=[int(row["week"]) for row in rows],
        x_label="Week of the log",
        y_label="Times per week",
    )


def relative_to(palette, reference, values, baseline, y_label, **pane):
    """Each log's value as a share of its baseline's, beside the baseline itself at 1."""
    relative = {log: values[log] / baseline[log] for log in values}
    return two_group(palette, {reference: 1.0}, relative, y_label=y_label, **pane)


def against_the_baseline(palette, **pane):
    return relative_to(
        palette,
        "Best\nbaseline",
        BEST_MODEL,
        BEST_BASELINE,
        y_label="Error, relative to the best baseline",
        **pane,
    )


def against_the_baseline_rmse(palette):
    """Slide 8's chart on the other error measure, for the backup that answers whether it agrees."""
    return relative_to(
        palette,
        "Best\nbaseline",
        BEST_MODEL_RMSE,
        BEST_BASELINE_RMSE,
        y_label="RMSE, relative to the best baseline",
    )


def xgboost_against_naive(palette):
    """The best baseline on every log is the seasonal naive, so it is the reference here."""
    return relative_to(
        palette,
        "Seasonal\nnaive",
        XGBOOST,
        BEST_BASELINE,
        y_label="XGBoost's error, relative to seasonal naive",
    )


def process_model_relevance(palette):
    """One pane of a two-column slide, beside the error figure it is read against."""
    return relative_to(
        palette,
        "Best\nbaseline",
        RELEVANCE_MODEL,
        RELEVANCE_BASELINE,
        y_label="Entropic relevance, relative",
        **COLUMN,
    )


def moirai_generations(palette):
    return two_group(palette, MOIRAI_PREVIOUS, MOIRAI_NEWEST, y_label="Mean absolute error")


def sepsis_fit(palette):
    return two_group(
        palette,
        SEPSIS_BASELINES,
        SEPSIS_MODELS,
        value_format="{:.0f}%",
        y_label="Sepsis traces that fit",
    )


#: Each figure the deck shows, by the path it is served at. A figure that returns on a later slide
#: is the same chart, drawn again for the pane it returns to.
CHARTS = {
    "bpi2017-weekly.png": weekly_series,
    "xgboost-against-naive.png": xgboost_against_naive,
    "against-the-baseline.png": against_the_baseline,
    "moirai-generations.png": moirai_generations,
    "process-model-relevance.png": process_model_relevance,
    "against-the-baseline-beside.png": partial(against_the_baseline, **COLUMN),
    "sepsis-fit.png": sepsis_fit,
    "against-the-baseline-rmse.png": against_the_baseline_rmse,
}


def draw(palette_path: str | Path, public: str | Path) -> list[Path]:
    """Draw every chart from the palette at ``palette_path`` into ``public``, and say where."""
    palette = load_palette(palette_path)
    out = Path(public) / FIGURES
    out.mkdir(parents=True, exist_ok=True)
    return [save(chart(palette), out / name) for name, chart in CHARTS.items()]


if __name__ == "__main__":
    for path in draw(sys.argv[1] if len(sys.argv) > 1 else PALETTE, HERE / "public"):
        print(path.relative_to(HERE))
