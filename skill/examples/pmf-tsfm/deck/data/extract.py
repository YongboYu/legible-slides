"""Pull the worked example's data out of a pmf-tsfm checkout, into the two small files beside this.

Draft mode reads the paper for the argument and the codebase for the numbers, and this is the
codebase half written down: the paper's tables are typed into ``figures.py`` with the table each
came from, but a per-day series is not in the paper at all, so it is read from the code's own
outputs. What it writes is committed, so the deck builds and its figures redraw with no checkout of
pmf-tsfm and nothing on a GPU.

    uv run --with numpy --with pandas --with pyarrow python data/extract.py ../../pmf-tsfm

The argument is the checkout's path (https://github.com/YongboYu/pmf-tsfm).
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent

#: The relations the problem slide shows, as the processed BPI2017 series names them.
RELATIONS = {
    "Offer created": "O_Create Offer -> O_Created",
    "Offer sent, then canceled": "O_Sent (mail and online) -> O_Cancelled",
    "Offer sent, then returned": "O_Sent (mail and online) -> O_Returned",
}

#: The relation the paper's drift figure plots, by its column in the forecast arrays, and the
#: forecast day it plots: the last of the seven.
DRIFT_RELATION, LAST_DAY = 3, -1

#: The seasonal-naive baseline's lag, in days: next week is this week again.
SEASON = 7


def weekly_series(checkout: Path) -> None:
    """Three directly-follows relations of BPI2017, summed per week so a marker per point reads."""
    daily = pd.read_parquet(checkout / "data" / "time_series" / "bpi2017.parquet")
    weekly = daily[list(RELATIONS.values())].resample("W").sum().iloc[1:-1]
    with (HERE / "bpi2017-weekly.csv").open("w", newline="", encoding="utf-8") as out:
        writer = csv.writer(out, lineterminator="\n")
        writer.writerow(["week", *RELATIONS])
        for week, row in enumerate(weekly.itertuples(index=False), start=1):
            writer.writerow([week, *(int(value) for value in row)])


def drift_window(checkout: Path) -> None:
    """The relation the paper's drift figure shows, with what each forecaster said a week ahead.

    XGBoost's per-window forecasts are not in the checkout, so the comparison here is the other
    baseline the paper reports: the seasonal naive, which is this week's count again next week.
    """
    root = checkout / "outputs" / "zero_shot" / "BPI2017"
    actual = np.load(root / "chronos_2" / "BPI2017_chronos_2_targets.npy")
    chronos = np.load(root / "chronos_2" / "BPI2017_chronos_2_predictions.npy")
    moirai = np.load(root / "moirai_2_0_small" / "BPI2017_moirai_2_0_small_predictions.npy")
    actual = actual[:, LAST_DAY, DRIFT_RELATION]
    with (HERE / "bpi2017-drift.csv").open("w", newline="", encoding="utf-8") as out:
        writer = csv.writer(out, lineterminator="\n")
        writer.writerow(["window", "actual", "Chronos-2", "MOIRAI-2.0", "seasonal naive"])
        for window in range(SEASON, len(actual)):
            writer.writerow(
                [
                    window,
                    int(actual[window]),
                    round(float(chronos[window, LAST_DAY, DRIFT_RELATION]), 2),
                    round(float(moirai[window, LAST_DAY, DRIFT_RELATION]), 2),
                    int(actual[window - SEASON]),
                ]
            )


def main() -> None:
    checkout = Path(sys.argv[1]).resolve()
    weekly_series(checkout)
    drift_window(checkout)


if __name__ == "__main__":
    main()
