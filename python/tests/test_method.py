from textwrap import dedent

import pytest

from legible import DELTA_E_FLOOR, load_palette, validate
from legible.method import MethodError, rule_thresholds

CANON_EXCERPT = dedent(
    """\
    ### `separation-floor`: data colours stay perceptually separated

    Every pair of data colours that can share one chart axis stays above the floor.

    **Decided by** script · **Threshold** `delta-e-floor = 22.5`,
    `delta-e-metric = CAM02-UCS`, `cvd-severity = 80`,
    `cvd-conditions = [normal, deuteranomaly, protanomaly, tritanomaly]`,
    `grayscale = advisory` (violation when a pair's ΔE is below `delta-e-floor`)

    ---

    ### `motion-purpose`: motion segments or depicts

    **Decided by** judgment · **Threshold** `animation-seconds-max = 15`
    """
)


def test_a_threshold_is_quoted_from_the_canon_rather_than_re_derived():
    """Change the canon and the number changes — that is what "quote it" has to mean."""
    thresholds = rule_thresholds("separation-floor", canon=CANON_EXCERPT)

    assert thresholds["delta-e-floor"] == "22.5"
    assert thresholds["cvd-severity"] == "80"
    assert thresholds["delta-e-metric"] == "CAM02-UCS"


def test_thresholds_stop_at_the_rule_they_belong_to():
    thresholds = rule_thresholds("separation-floor", canon=CANON_EXCERPT)

    assert "animation-seconds-max" not in thresholds


def test_a_rule_the_canon_does_not_carry_is_an_error():
    with pytest.raises(MethodError, match="no-such-rule"):
        rule_thresholds("no-such-rule", canon=CANON_EXCERPT)


def test_the_shipped_canon_carries_the_separation_floor():
    thresholds = rule_thresholds("separation-floor")

    assert thresholds["delta-e-floor"] == "15.0"
    assert thresholds["cvd-severity"] == "100"


def test_the_default_threshold_is_the_canons_floor(themes_dir):
    report = validate(load_palette(themes_dir / "kuleuven.json"))

    assert report.threshold == DELTA_E_FLOOR == 15.0
