from textwrap import dedent

import pytest

from legible import DELTA_E_FLOOR, load_palette, validate
from legible.method import (
    BULLETS_PER_SLIDE,
    EM_DASHES_PER_HEADLINE,
    INFLATED_REGISTER_SEVERITY,
    INFLATED_REGISTER_WORDS,
    OPENER_SHARE_MAX,
    OPENER_WORDS,
    WORDS_PER_BULLET,
    MethodError,
    rule_thresholds,
)

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

SUBSECTION_EXCERPT = dedent(
    """\
    ### 7a. Script-decided

    #### `opener-variety`: no more than half the sentences open the same way

    **Decided by** script · **Threshold** `opener-words = [The, This, It, In]`,
    `opener-share-max = 0.5`

    ### 7b. Judgment

    Every rule in this subsection carries no threshold, but this prose does: `not-a-rule = 99`.
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


def test_a_rule_stated_under_a_subsection_is_read_like_any_other():
    """The voice rules sit a heading level deeper than the rest. A reader does not care, and
    neither may the parser — a rule the canon states is a rule the linter can quote."""
    thresholds = rule_thresholds("opener-variety", canon=SUBSECTION_EXCERPT)

    assert thresholds["opener-share-max"] == "0.5"


def test_a_threshold_footer_stops_at_the_end_of_its_own_paragraph():
    """The last rule of a subsection runs on into prose that is nobody's threshold."""
    thresholds = rule_thresholds("opener-variety", canon=SUBSECTION_EXCERPT)

    assert "not-a-rule" not in thresholds


def test_the_shipped_canon_carries_the_separation_floor():
    thresholds = rule_thresholds("separation-floor")

    assert thresholds["delta-e-floor"] == "15.0"
    assert thresholds["cvd-severity"] == "100"


def test_the_default_threshold_is_the_canons_floor(themes_dir):
    report = validate(load_palette(themes_dir / "kuleuven.json"))

    assert report.threshold == DELTA_E_FLOOR == 15.0


def test_the_shipped_canon_carries_the_numbers_the_linter_enforces():
    """Every ceiling the linter decides, read out of the canon rather than kept beside it."""
    assert BULLETS_PER_SLIDE == 5
    assert WORDS_PER_BULLET == 12
    assert EM_DASHES_PER_HEADLINE == 0
    assert OPENER_SHARE_MAX == 0.5


def test_the_shipped_canon_carries_the_wordlists_the_linter_enforces():
    assert "crucial" in INFLATED_REGISTER_WORDS
    # Multi-word entries survive the list: the canon writes one of them.
    assert "testament to" in INFLATED_REGISTER_WORDS
    assert OPENER_WORDS == ("The", "This", "It", "In")


def test_the_canon_decides_how_loudly_an_inflated_word_is_reported():
    """`established-terminology` wins over the wordlist, which is why the canon sets this to
    `warning` — and why the severity is quoted rather than chosen here."""
    assert INFLATED_REGISTER_SEVERITY == "warning"
