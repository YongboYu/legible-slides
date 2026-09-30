"""The flagship deck, against the canon and the palette it quotes.

The deck teaches the method, so it does what no other file in this repo may: it writes the method's
numbers down, on screen, in words a room can read. `type-scale`'s arithmetic *is* beat 9's evidence,
and the achieved minima *are* beat 11's. That is sanctioned — the canon's own outline asks for "the
projection arithmetic on screen" — but it leaves the exposure ``test_theme.py`` was written for: a
hand-typed number is exactly where a copy drifts in silence, and a flagship quoting a threshold the
canon no longer carries is worse than a flagship quoting none.

So the copies are held to their originals, in both directions. Change a number in ``docs/method.md``
or a colour in ``themes/*.json`` without changing the slide that states it, or edit the slide's own
copy of one, and these fail naming which.
"""

import re
from pathlib import Path

import pytest

from legible import load_palette, validate
from legible.deck import read_deck
from legible.method import DELTA_E_FLOOR, rule_thresholds

DECK = Path(__file__).resolve().parents[2] / "deck" / "slides.md"

#: The thirteen beats of the canon's outline, then the sources they cite. Counted so that deleting a
#: beat is a failure rather than a quiet edit — the outline is the deck's contract.
BEATS = 13
SLIDES = BEATS + 1

#: The theme beat 11 tabulates, and the group it measures it over. `separation-floor` forms the
#: per-series ramp as G1, which is what "closest pair" on that slide means.
TABULATED = ("leuven-blue",)
PER_SERIES = "G1"


@pytest.fixture(scope="module")
def deck() -> str:
    """The deck as one line, so a finding never turns on where an author's editor wrapped."""
    return " ".join(DECK.read_text(encoding="utf-8").split())


def test_the_deck_carries_every_beat_and_its_sources():
    """One slide per beat, one for the sources, and a headline on each: the outline's shape."""
    slides = read_deck(DECK)

    assert len(slides) == SLIDES
    assert [slide.number for slide in slides if not slide.headline] == []


def test_beat_nine_is_set_in_the_canon_s_type_scale(deck):
    """The two sizes the slide names as fixed are the canon's body size and its logical canvas."""
    type_scale = rule_thresholds("type-scale")
    stated = re.search(r"fixed at (\d+) px on this deck's (\d+) px canvas", deck)
    assert stated, "beat 9 no longer states the body size and the canvas it is written against"

    assert stated.group(1) == type_scale["body-px"]
    assert stated.group(2) == type_scale["canvas-width-px"]


def test_beat_nine_s_worked_example_is_arithmetic_that_holds(deck):
    """`equation-worked-example` asks for real numbers pushed through the formula, so the numbers
    have to come out. Truncated rather than rounded, which is the conservative direction: the claim
    is what the back row can read, and promising a pixel the projector does not draw is the one
    error worth ruling out."""
    worked = re.search(r"(\d+) × (\d+) ÷ (\d+) = (\d+) px", deck)
    assert worked, "beat 9 no longer works the projection through on screen"
    body, screen, canvas, projected = (int(group) for group in worked.groups())

    assert body == int(rule_thresholds("type-scale")["body-px"])
    assert projected == body * screen // canvas


def test_beat_nine_names_the_canon_s_two_dense_exceptions(deck):
    """Named as exceptions on the slide, and they are the canon's exceptions, in its order."""
    type_scale = rule_thresholds("type-scale")
    named = re.search(r"Two smaller sizes exist, (\d+) px and (\d+) px", deck)
    assert named, "beat 9 no longer names the two sizes the canon marks as exceptions"

    assert named.groups() == (type_scale["dense-px"], type_scale["dense-xs-px"])


@pytest.mark.parametrize("theme", TABULATED)
def test_beat_eleven_tabulates_the_minima_the_validator_measures(deck, themes_dir, theme):
    """The slide's whole argument is that a palette is checked rather than trusted, so its row has
    to be what ``cvd-validate`` says today — not what it said when it was typed."""
    row = re.search(rf"\| `{theme}` \| ([\d.]+) \| ([\d.]+) \|", deck)
    assert row, f"beat 11 no longer tabulates the `{theme}` theme"
    group = validate(load_palette(themes_dir / f"{theme}.json")).groups[PER_SERIES]

    assert float(row.group(1)) == min(group.min_delta_e.values())
    assert float(row.group(2)) == group.grayscale_min


def test_beat_ten_s_caption_puts_the_binding_pair_on_the_floor(deck, themes_dir):
    """The caption's "exactly the floor" is the claim the demonstration turns on: the ramp is at
    capacity, and one more series would fail. It stops being true the moment either number moves."""
    caption = re.search(r"the closest pair lands on ([\d.]+), exactly the floor", deck)
    assert caption, "beat 10 no longer states where the binding pair lands"
    measured = validate(load_palette(themes_dir / "leuven-blue.json")).groups[PER_SERIES]

    assert float(caption.group(1)) == min(measured.min_delta_e.values()) == DELTA_E_FLOOR
