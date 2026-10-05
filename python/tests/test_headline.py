"""A headline, set the way the slide sets it.

The expected numbers here were read off Chromium, rendering the bundled face at the theme's headline
size, weight, tracking and width: what the room sees is the reference, and the wrap is held to it.
"""

import pytest

from legible.headline import HEADLINE_WIDTH_PX, rendered_width, wrap
from legible.method import CANVAS_WIDTH_PX

#: A headline from the worked example, which fills most of two lines and goes no further.
TWO_LINES = (
    "Used as they are, pre-trained forecasters cut the error by 17 to 28%, but the process models "
    "they forecast are no better."
)

#: The same claim, grown until it cannot fit in two.
THREE_LINES = (
    "Used as they are, pre-trained forecasters cut the error by 17 to 28%, but the process models "
    "they forecast are no better, and on Sepsis they are much worse than last week."
)


def test_the_headline_is_as_wide_as_the_canvas_less_its_edges():
    assert 0 < HEADLINE_WIDTH_PX < CANVAS_WIDTH_PX


@pytest.mark.parametrize(
    ("headline", "chromium_px"),
    [
        ("A headline works better as a short claim than as a topic label.", 1069.5),
        ("The sources are a slide, not a divider.", 647.5),
        # Pairs the face kerns, digits and capitals among them: an unkerned sum is 8 px wider.
        ("MOIRAI 2.0 beats MOIRAI 1.1 with a model 27 times smaller.", 1029.3),
    ],
)
def test_a_line_is_as_wide_as_chromium_sets_it(headline, chromium_px):
    assert rendered_width(headline) == pytest.approx(chromium_px, abs=0.1)


def test_a_short_claim_takes_one_line():
    assert wrap("The sources are a slide, not a divider.") == (
        "The sources are a slide, not a divider.",
    )


def test_a_long_claim_takes_two():
    assert len(wrap(TWO_LINES)) == 2


def test_a_claim_past_two_lines_takes_three():
    assert len(wrap(THREE_LINES)) == 3


def test_every_line_fits_the_width_it_is_set_in():
    for line in wrap(THREE_LINES):
        assert rendered_width(line) <= HEADLINE_WIDTH_PX


def test_a_line_may_break_after_a_hyphen():
    """Chromium breaks a hyphenated word after its hyphen when the whole of it will not fit, so a
    wrap that only broke at spaces would count a line too many on the boundary."""
    words = TWO_LINES.split()
    # Grow a run of words until "pre-" still fits after it, and "pre-trained" does not.
    for count in range(1, 60):
        lead = " ".join((words * 3)[:count])
        if (
            rendered_width(f"{lead} pre-")
            <= HEADLINE_WIDTH_PX
            < rendered_width(f"{lead} pre-trained")
        ):
            break
    else:
        pytest.fail("no run of words puts the hyphen on the edge")

    assert wrap(f"{lead} pre-trained") == (f"{lead} pre-", "trained")


def test_a_word_wider_than_the_line_still_takes_one_line():
    """It overflows rather than vanishing, which is what the browser does with it too."""
    assert len(wrap("x" * 200)) == 1


def test_nothing_takes_no_lines():
    assert wrap("") == ()
