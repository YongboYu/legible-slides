"""The themes this repo ships.

Two claims: they pass, and they pass by the amounts published in
docs/cvd-validator-contract.md §3. The second is the dependency-bump guard — a colorspacious
version that shifted the simulation or the distance would move these numbers, and this is where
that surfaces rather than in a palette someone already trusted.
"""

from pathlib import Path

import pytest

from legible import load_palette, validate

# Collection-time, so every theme this repo ships gets its own test the moment it lands.
SHIPPED = sorted(
    path.name for path in (Path(__file__).resolve().parents[2] / "themes").glob("*.json")
)


@pytest.mark.parametrize("theme", SHIPPED)
def test_every_shipped_theme_loads_and_passes(themes_dir, theme):
    report = validate(load_palette(themes_dir / theme))

    assert report.failures == ()
    assert report.passed


def test_the_reference_theme_achieves_its_documented_minima(themes_dir):
    report = validate(load_palette(themes_dir / "kuleuven.json"))

    per_series, two_group = report.groups["G1"], report.groups["G2"]

    assert min(per_series.min_delta_e.values()) == 15.0
    assert per_series.grayscale_min == 10.9
    assert min(two_group.min_delta_e.values()) == 30.0
    assert two_group.grayscale_min == 18.5


def test_the_brand_free_theme_achieves_its_documented_minima(themes_dir):
    report = validate(load_palette(themes_dir / "neutral.json"))

    per_series, two_group = report.groups["G1"], report.groups["G2"]

    assert min(per_series.min_delta_e.values()) == 25.4
    assert per_series.grayscale_min == 11.8
    assert min(two_group.min_delta_e.values()) == 21.5
    assert two_group.grayscale_min == 13.2
