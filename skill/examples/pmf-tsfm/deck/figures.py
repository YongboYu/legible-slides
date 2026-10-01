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
from pathlib import Path

from legible import load_palette
from legible.figures import Series, multi_series, save, two_group

HERE = Path(__file__).resolve().parent

#: The palette a stamped deck wears, and keeps here.
PALETTE = HERE / "themes" / "palette.json"

#: Where the deck serves its figures from, under public/.
FIGURES = "figures"

#: Zero-shot mean absolute error, Table 4 of the paper. The best baseline on every log is the
#: seasonal naive forecast, and the best model is the lowest error in that log's column.
BEST_BASELINE = {"BPI 2017": 8.30, "BPI 2019": 14.47, "Sepsis": 0.117, "Billing": 1.77}
BEST_MODEL = {"BPI 2017": 6.87, "BPI 2019": 10.75, "Sepsis": 0.084, "Billing": 1.39}

#: Chronos-Bolt on BPI 2017, Table 4, by size (Table 1).
CHRONOS_BOLT = {"tiny\n9M": 11.64, "mini\n21M": 9.70, "small\n48M": 7.72}
CHRONOS_BOLT_LARGEST = {"base\n205M": 7.62}

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


def against_the_baseline(palette):
    relative = {log: BEST_MODEL[log] / BEST_BASELINE[log] for log in BEST_MODEL}
    return two_group(
        palette,
        {"Best\nbaseline": 1.0},
        relative,
        y_label="Error, relative to the best baseline",
    )


def chronos_bolt_sizes(palette):
    return two_group(palette, CHRONOS_BOLT, CHRONOS_BOLT_LARGEST, y_label="Mean absolute error")


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


#: Each figure the deck shows, by the path it is served at.
CHARTS = {
    "bpi2017-weekly.png": weekly_series,
    "against-the-baseline.png": against_the_baseline,
    "chronos-bolt-sizes.png": chronos_bolt_sizes,
    "moirai-generations.png": moirai_generations,
    "sepsis-fit.png": sepsis_fit,
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
