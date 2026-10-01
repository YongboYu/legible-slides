"""The flagship deck, against the canon and the palette it quotes.

The deck teaches the method, so it does what no other file in this repo may: it writes the method's
numbers down, on screen, in words a room can read. `type-scale`'s arithmetic *is* beat 9's evidence,
and the achieved minima *are* beat 11's. That is sanctioned — the canon's own outline asks for the
body size "worked through to the room it reads in" — but it leaves the exposure ``test_theme.py``
was written for: a hand-typed number is exactly where a copy drifts in silence, and a flagship
quoting a threshold the canon no longer carries is worse than a flagship quoting none.

So the copies are held to their originals, in both directions. Change a number in ``docs/method.md``
or a colour in ``themes/*.json`` without changing the slide that states it, or edit the slide's own
copy of one, and these fail naming which.
"""

import importlib.util
import re
from itertools import takewhile
from pathlib import Path

import pytest

from legible import load_palette, validate
from legible.deck import read_deck
from legible.figures import smallest_type_px
from legible.lint import lint
from legible.method import (
    BODY_PX,
    BODY_REACH_IMAGE_HEIGHTS,
    CANVAS_HEIGHT_PX,
    DELTA_E_FLOOR,
    FLOOR_PX,
    rule_thresholds,
)

DECK = Path(__file__).resolve().parents[2] / "deck" / "slides.md"

#: The fourteen beats of the canon's outline, then the sources they cite. Counted so that deleting a
#: beat is a failure rather than a quiet edit — the outline is the deck's contract.
BEATS = 14
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


def test_beat_ten_is_set_in_the_canon_s_type_scale(deck):
    """The two sizes the slide names as fixed are the canon's body size and its logical canvas."""
    type_scale = rule_thresholds("type-scale")
    stated = re.search(r"fixed at (\d+) px on this deck's (\d+) × (\d+) canvas", deck)
    assert stated, "beat 10 no longer states the body size and the canvas it is written against"

    assert stated.group(1) == type_scale["body-px"]
    assert stated.group(2) == type_scale["canvas-width-px"]
    assert int(stated.group(3)) == CANVAS_HEIGHT_PX


def test_beat_ten_s_worked_example_is_arithmetic_that_holds(deck):
    """`equation-worked-example` asks for real numbers pushed through the formula, so the numbers
    have to come out: the body's share of the image height, and how far that share reads in a room
    with a screen of a given height. The reach is the canon's, not the slide's."""
    share = re.search(r"(\d+) ÷ (\d+) = ([\d.]+)%", deck)
    reach = re.search(r"(\d+) × ([\d.]+) = (\d+) m", deck)
    assert share, "beat 10 no longer works the body's share of the image height on screen"
    assert reach, "beat 10 no longer works through how far the body size reads"

    body, height, percent = int(share.group(1)), int(share.group(2)), float(share.group(3))
    assert (body, height) == (BODY_PX, CANVAS_HEIGHT_PX)
    assert percent == round(100 * body / height, 1)

    screen, heights, metres = float(reach.group(1)), float(reach.group(2)), float(reach.group(3))
    assert heights == BODY_REACH_IMAGE_HEIGHTS
    assert metres == screen * heights


def test_beat_ten_names_the_canon_s_floor(deck):
    """One size under the body, and it is a floor rather than an exception."""
    named = re.search(r"Nothing goes below (\d+) px", deck)
    assert named, "beat 10 no longer names the floor"

    assert int(named.group(1)) == FLOOR_PX


@pytest.mark.parametrize("theme", TABULATED)
def test_beat_twelve_tabulates_the_minima_the_validator_measures(deck, themes_dir, theme):
    """The slide's whole argument is that a palette is checked rather than trusted, so its row has
    to be what ``cvd-validate`` says today — not what it said when it was typed."""
    row = re.search(rf"\| `{theme}` \| ([\d.]+) \| ([\d.]+) \|", deck)
    assert row, f"beat 12 no longer tabulates the `{theme}` theme"
    group = validate(load_palette(themes_dir / f"{theme}.json")).groups[PER_SERIES]

    assert float(row.group(1)) == min(group.min_delta_e.values())
    assert float(row.group(2)) == group.grayscale_min


def test_beat_eleven_s_caption_puts_the_binding_pair_on_the_floor(deck, themes_dir):
    """The caption's "exactly the floor" is the claim the demonstration turns on: the ramp is at
    capacity, and one more series would fail. It stops being true the moment either number moves."""
    caption = re.search(r"the closest pair lands on ([\d.]+), exactly the floor", deck)
    assert caption, "beat 11 no longer states where the binding pair lands"
    measured = validate(load_palette(themes_dir / "leuven-blue.json")).groups[PER_SERIES]

    assert float(caption.group(1)) == min(measured.min_delta_e.values()) == DELTA_E_FLOOR


#: The talk's sections, in order, as the footer's map names them.
SECTIONS = ["Problem", "Method", "Legibility", "Delivery"]


def test_the_deck_is_grouped_into_the_talk_s_sections():
    """`section-locator`: a handful of real sections, declared where each starts. The sources come
    after the close, as a backup outside them."""
    slides = read_deck(DECK)
    declared = [slide for slide in slides if slide.section]

    assert [slide.section for slide in declared if not slide.backup] == SECTIONS
    assert [slide.section for slide in declared if slide.backup] == ["Sources"]
    assert slides[-1].backup


def test_every_section_change_is_signposted_aloud():
    """The footer is the backup channel. The first slide of each of the talk's sections carries
    the spoken signpost in its notes, on a line of its own."""
    for slide in read_deck(DECK):
        if slide.section and not slide.backup:
            assert slide.notes and slide.notes.startswith("Signpost: "), (
                f"slide {slide.number} opens {slide.section!r} with no signpost"
            )


def test_the_deck_sets_no_retired_per_slide_locator():
    assert not re.search(r"^locator:", DECK.read_text(encoding="utf-8"), re.MULTILINE)


@pytest.fixture(scope="module")
def deck_figures():
    """The deck's own ``figures.py``: a script beside the deck rather than a module here."""
    spec = importlib.util.spec_from_file_location("deck_figures", DECK.parent / "figures.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize("condition", ["deuteranomaly", "grayscale"])
def test_the_deck_s_figures_hold_the_floor_in_the_pane_they_land_in(
    deck_figures, themes_dir, condition
):
    """`type-scale` measures figure text where it lands: here, half a two-column slide."""
    figure = deck_figures.separation_chart(load_palette(themes_dir / "leuven-blue.json"), condition)
    width, _ = deck_figures.PANE_PX

    assert smallest_type_px(figure, lands_at_px=width) >= FLOOR_PX


# ── the opening and the close ─────────────────────────────────────────────────

#: Where the deck serves its own files from, which is where a `themeConfig` image path points.
PUBLIC = DECK.parent / "public"


def _main(slides):
    """The talk's slides: everything before the first backup, which the flagship puts last."""
    return list(takewhile(lambda slide: not slide.backup, slides))


def test_the_answer_comes_straight_after_the_cover():
    """`answer-first`: the second slide is the result, with the questions it answers."""
    slides = read_deck(DECK)

    assert slides[1].layout == "answer"
    assert len(slides[1].bullets) >= 2, "the answer slide numbers no questions"


def test_the_close_answers_each_question_by_its_number():
    """`conclusion-stays-up`: the last main slide is the conclusion, and it answers as many
    questions as the opening asked, one to one."""
    slides = read_deck(DECK)
    close = _main(slides)[-1]

    assert close.layout == "conclusion"
    assert len(close.bullets) == len(slides[1].bullets)


def test_the_slides_are_handed_over_on_the_first_and_the_last_slide():
    """One QR code, set once for the deck: the cover and the conclusion both read it. It is a file
    the deck serves, and the link and the contact are written beside it."""
    headmatter = re.match(r"---\n(.*?)\n---\n", DECK.read_text(encoding="utf-8"), re.DOTALL)[1]
    qr = re.search(r"^  shareQr: (\S+)$", headmatter, re.MULTILINE)
    url = re.search(r"^  shareUrl: (\S+)$", headmatter, re.MULTILINE)

    assert qr and url, "the deck sets no QR code to its slides"
    assert re.search(r"^  contact: \S", headmatter, re.MULTILINE), "the close carries no contact"
    assert (PUBLIC / qr.group(1).lstrip("/")).is_file()
    assert url.group(1) in (PUBLIC / qr.group(1).lstrip("/")).read_text(encoding="utf-8")


# ── the review advisories ─────────────────────────────────────────────────────

#: Every advisory the flagship is left carrying, and why the author overrides it. The canon's own
#: balance clause is the ground for most of them: a dense slide passes review when its headline says
#: how to read it. Where the words were script, they were moved to the notes instead, so a new
#: advisory turning up here is a slide to review rather than one more line for this table.
OVERRIDDEN = {
    (3, "on-slide-words"): "the stock template's slide is a picture of one, and its words are it",
    (4, "on-slide-words"): "the two type samples are the evidence, set at the sizes they compare",
    (5, "on-slide-words"): "the table is the evidence: what the method decides, and what holds it",
    (7, "signal-budget"): "the label and the claim are compared side by side, and one is accented",
    (10, "on-slide-words"): "the arithmetic is `equation-worked-example`'s worked example",
    (13, "on-slide-words"): "the table is the evidence: one file, and each output it is shipped as",
}


def test_the_flagship_carries_only_the_advisories_its_author_overrides():
    """Advisories never gate, so nothing else would notice the flagship drifting into the density it
    teaches against."""
    report = lint(DECK)

    assert report.passed
    assert {(finding.slide, finding.rule) for finding in report.findings} == set(OVERRIDDEN)
    assert {finding.severity for finding in report.findings} == {"warning"}
