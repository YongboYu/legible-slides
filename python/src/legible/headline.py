"""A headline, set the way the slide sets it.

`headline-shape` counts a headline in rendered lines, and a word count cannot say how many lines a
headline takes: a number, a capital or a long word moves the break. So this sets the headline the
way the browser does, from the face the deck is set in. Each line is as wide as the advances of its
glyphs, plus the pairs the face kerns, plus the theme's tracking after every character, at the
theme's headline size. Lines are filled greedily, breaking at a space or after a hyphen, which is
how a browser fills a block of ``text-wrap: wrap`` text. ``python/tests/test_headline.py`` holds the
widths to Chromium's.

The size is the canon's. The width, the weight and the tracking are the theme's, from
``theme/styles/layout.css``: a stylesheet cannot be read here the way the canon can, so the numbers
are written down below and ``python/tests/test_theme.py`` fails if they drift from the stylesheet.
"""

from __future__ import annotations

import re
from collections.abc import Callable, Iterator
from functools import cache

from fontTools.ttLib import TTFont

from legible.fonts import BUNDLE
from legible.method import CANVAS_WIDTH_PX, FONT_TEXT, HEADLINE_PX

__all__ = [
    "EDGE_X_PX",
    "HEADLINE_TRACKING_EM",
    "HEADLINE_WEIGHT",
    "HEADLINE_WIDTH_PX",
    "rendered_width",
    "wrap",
]

#: The theme's `--edge-x`: how far in from each side of the canvas a content slide's text starts.
EDGE_X_PX = 72

#: What a content slide's ``h1`` is set in: its weight, the bundle's file for that weight, and its
#: ``letter-spacing`` in em. The cover's title is heavier, and is a title rather than a headline.
HEADLINE_WEIGHT = 600
HEADLINE_FACE = f"{FONT_TEXT}-SemiBold.ttf"
HEADLINE_TRACKING_EM = -0.01

#: The width a headline wraps in: the canvas, less an edge on each side.
HEADLINE_WIDTH_PX = CANVAS_WIDTH_PX - 2 * EDGE_X_PX

#: Where a line may break inside a word: after a hyphen or a dash, before a letter.
_AFTER_HYPHEN = re.compile(r"(?<=[-–—])(?=[^\W\d_])")

#: The lookup types that position a pair of glyphs: a pair adjustment, or an extension wrapping one.
_PAIR_ADJUSTMENT, _EXTENSION = 2, 9


def wrap(headline: str) -> tuple[str, ...]:
    """The lines a headline is set in, in order. Nothing takes no lines.

    A newline is a break the author forced with ``<br>``, so the next line starts there whatever
    room is left. Each part between two breaks fills its lines on its own. A part with no words is
    the empty line two breaks in a row set, and it takes a line too.
    """
    lines: list[str] = []
    for part in headline.split("\n"):
        line = ""
        for piece, joint in _pieces(part):
            candidate = f"{line}{joint}{piece}" if line else piece
            if not line or rendered_width(candidate) <= HEADLINE_WIDTH_PX:
                line = candidate
            else:
                lines.append(line)
                line = piece
        lines.append(line)
    return tuple(lines) if any(lines) else ()


def rendered_width(text: str) -> float:
    """How wide one line of headline is on the canvas, in its px."""
    return _measure()(text)


def _pieces(headline: str) -> Iterator[tuple[str, str]]:
    """Every run of the headline between two places a line may break, and what joins it to the run
    before: a space between words, nothing after a hyphen."""
    for word in headline.split():
        for index, piece in enumerate(_AFTER_HYPHEN.split(word)):
            yield piece, "" if index else " "


@cache
def _measure() -> Callable[[str], float]:
    """A function giving one line's width, read once from the bundled face."""
    face = TTFont(BUNDLE / HEADLINE_FACE)
    glyphs = face.getBestCmap()
    advances = face["hmtx"].metrics
    per_unit = HEADLINE_PX / face["head"].unitsPerEm
    tracking = HEADLINE_TRACKING_EM * HEADLINE_PX
    kern = _kerning(face)

    def width(text: str) -> float:
        names = [glyphs.get(ord(character), ".notdef") for character in text]
        units = sum(advances[name][0] for name in names)
        units += sum(kern(left, right) for left, right in zip(names, names[1:], strict=False))
        return units * per_unit + tracking * len(text)

    return width


def _kerning(face: TTFont) -> Callable[[str, str], int]:
    """The face's ``kern`` feature, as a function of a pair of glyph names.

    Each lookup adjusts a pair once, by the first of its subtables that covers it, and the lookups
    add up, as a shaper applies them.
    """
    gpos = face["GPOS"].table
    indices = sorted(
        {
            index
            for record in gpos.FeatureList.FeatureRecord
            if record.FeatureTag == "kern"
            for index in record.Feature.LookupListIndex
        }
    )
    lookups = []
    for index in indices:
        lookup = gpos.LookupList.Lookup[index]
        subtables = [
            subtable.ExtSubTable if lookup.LookupType == _EXTENSION else subtable
            for subtable in lookup.SubTable
        ]
        lookups.append(
            [subtable for subtable in subtables if subtable.LookupType == _PAIR_ADJUSTMENT]
        )

    @cache
    def kern(left: str, right: str) -> int:
        return sum(_adjust(subtables, left, right) for subtables in lookups)

    return kern


def _adjust(subtables: list, left: str, right: str) -> int:
    """What one lookup does to a pair's advance, in font units."""
    for subtable in subtables:
        covered = subtable.Coverage.glyphs
        if left not in covered:
            continue
        if subtable.Format == 1:
            for record in subtable.PairSet[covered.index(left)].PairValueRecord:
                if record.SecondGlyph == right:
                    return _x_advance(record.Value1)
            # A first glyph with no record for this second one leaves the pair to the next subtable.
            continue
        first = subtable.ClassDef1.classDefs.get(left, 0)
        second = subtable.ClassDef2.classDefs.get(right, 0)
        return _x_advance(subtable.Class1Record[first].Class2Record[second].Value1)
    return 0


def _x_advance(value: object) -> int:
    """A value record's change to the advance, which a record that moves nothing leaves out."""
    return getattr(value, "XAdvance", 0) or 0
