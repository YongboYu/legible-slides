"""The theme this repo ships, and the marks it does not.

Two claims about the palette: it passes, and it passes by the amounts published in
docs/cvd-validator-contract.md §3. The second is the dependency-bump guard — a colorspacious
version that shifted the simulation or the distance would move these numbers, and this is where
that surfaces rather than in a palette someone already trusted.
"""

import subprocess
from pathlib import Path

import pytest

from legible import load_palette, validate

REPO = Path(__file__).resolve().parents[2]

# Collection-time, so a theme added beside it fails `test_exactly_one_theme_ships` by name.
SHIPPED = sorted(path.name for path in (REPO / "themes").glob("*.json"))

#: The one theme, by name. Everything downstream — the deck, the scaffold, CI — is built around it.
THEME = "leuven-blue.json"


def test_exactly_one_theme_ships():
    assert SHIPPED == [THEME]


@pytest.mark.parametrize("theme", SHIPPED)
def test_every_shipped_theme_loads_and_passes(themes_dir, theme):
    report = validate(load_palette(themes_dir / theme))

    assert report.failures == ()
    assert report.passed


@pytest.mark.parametrize("theme", SHIPPED)
def test_a_shipped_theme_that_declares_a_logo_ships_the_file(themes_dir, theme):
    """The key is optional, and the shipped theme leaves it out; one that names a mark must not
    point at nothing."""
    palette = load_palette(themes_dir / theme)

    if palette.logo is not None:
        assert (themes_dir / palette.logo).is_file()


def test_the_theme_achieves_its_documented_minima(themes_dir):
    report = validate(load_palette(themes_dir / "leuven-blue.json"))

    per_series, two_group = report.groups["G1"], report.groups["G2"]

    assert min(per_series.min_delta_e.values()) == 15.0
    assert per_series.grayscale_min == 10.9
    assert min(two_group.min_delta_e.values()) == 30.0
    assert two_group.grayscale_min == 18.5


def test_no_university_mark_ships():
    """The palette is inspired by a university's colours; its marks are the university's, and an
    author points a deck at the real ones in their own copy. Asked of the files git tracks, so a
    mark dropped anywhere in the tree fails here, whatever it is called beside the university."""
    tracked = subprocess.run(
        ["git", "ls-files"], cwd=REPO, capture_output=True, text=True, check=True
    ).stdout.splitlines()

    assert [path for path in tracked if "kuleuven" in path.lower()] == []
