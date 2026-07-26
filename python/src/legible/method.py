"""The canon, quoted.

`docs/method.md` states every rule of the method and every number it turns on, once. This module is
how Python reads a number out of it, so the package quotes the canon rather than keeping a second
copy that can drift. Every rule carries a stable ID and a ``**Threshold**`` footer of
``key = value`` pairs; ``rule_thresholds`` returns one rule's pairs.

The constants below are grouped by the rule that owns them — `separation-floor` for the colour
numbers, `type-scale` and `fonts` for what a generated figure is set in. Change a rule and they
change here.
"""

from __future__ import annotations

import re
from pathlib import Path

#: A rule heading: `### \`rule-id\`: statement`. Any depth from `###` down, because the voice rules
#: sit one level deeper under a subsection heading and a rule is a rule wherever it is stated.
_RULE = re.compile(r"^#{3,6}\s+`(?P<rule>[a-z0-9-]+)`", re.MULTILINE)

#: One `key = value` pair inside a **Threshold** footer.
_THRESHOLD = re.compile(r"`(?P<key>[a-z0-9-]+)\s*=\s*(?P<value>[^`]+)`")


class MethodError(LookupError):
    """The canon could not be read, or does not carry what was asked of it."""


#: Where the canon may live, in preference order: `docs/method.md` in a checkout of this repo,
#: then the copy the build vendors beside this module for an author who installed the package and
#: has no checkout to read. The checkout wins, so editing the canon takes effect immediately; the
#: vendored copy is written from that same file at build time, so it is a build artifact rather
#: than a second version anyone maintains.
_CANON_CANDIDATES = (
    Path(__file__).resolve().parents[3] / "docs" / "method.md",
    Path(__file__).resolve().parent / "method.md",
)

#: The canon this install reads. Falls back to the checkout path so a failure names where the
#: canon was expected.
CANON = next(
    (path for path in _CANON_CANDIDATES if path.is_file()),
    _CANON_CANDIDATES[0],
)


def read_canon() -> str:
    """The text of `docs/method.md`."""
    try:
        return CANON.read_text(encoding="utf-8")
    except OSError as error:
        looked_in = " or ".join(str(path) for path in _CANON_CANDIDATES)
        raise MethodError(
            f"cannot read the canon to quote its thresholds; looked for {looked_in}"
        ) from error


def rule_thresholds(rule_id: str, canon: str | None = None) -> dict[str, str]:
    """The ``key = value`` thresholds one rule declares, as written in the canon.

    Values come back as the strings the canon wrote, because the canon is the authority on both
    the number and its units; callers convert to whatever type they need.
    """
    text = read_canon() if canon is None else canon

    starts = {match.group("rule"): match.span()[0] for match in _RULE.finditer(text)}
    if rule_id not in starts:
        raise MethodError(f"the canon carries no rule `{rule_id}`")

    start = starts[rule_id]
    following = [pos for pos in starts.values() if pos > start]
    body = text[start : min(following)] if following else text[start:]

    _, marker, footer = body.partition("**Threshold**")
    if not marker:
        raise MethodError(f"rule `{rule_id}` declares no threshold")

    # The footer is one paragraph, however many lines the canon wraps it over. Stopping at the
    # blank line keeps prose that merely follows a rule from being read as one of its thresholds.
    footer, _, _ = footer.partition("\n\n")

    return {
        match.group("key"): match.group("value").strip() for match in _THRESHOLD.finditer(footer)
    }


def _listed(value: str) -> tuple[str, ...]:
    """A threshold the canon writes as a list — ``[The, This, It, In]`` — as its items."""
    return tuple(item.strip() for item in value.strip("[]").split(","))


_SEPARATION_FLOOR = rule_thresholds("separation-floor")

#: The perceptual floor every pair of data colours must clear. The canon owns the number and the
#: reasoning behind it; `docs/cvd-validator-contract.md` §3 records how it was arrived at.
DELTA_E_FLOOR = float(_SEPARATION_FLOOR["delta-e-floor"])

#: The uniform space distances are measured in.
DELTA_E_METRIC = _SEPARATION_FLOOR["delta-e-metric"]

#: Simulation severity. The canon picks full dichromacy: the worst case.
SEVERITY = int(_SEPARATION_FLOOR["cvd-severity"])

#: Every condition a palette is checked under, normal vision first.
CVD_CONDITIONS = _listed(_SEPARATION_FLOOR["cvd-conditions"])

#: The conditions that need simulating — everything but normal vision.
CVD_TYPES = tuple(condition for condition in CVD_CONDITIONS if condition != "normal")


_TYPE_SCALE = rule_thresholds("type-scale")

#: The logical canvas a deck's px values are written against. A figure is sized in these same
#: pixels, so a chart drawn 960 wide occupies 960 of the layout's own units when it lands.
CANVAS_WIDTH_PX = int(_TYPE_SCALE["canvas-width-px"])

#: The canvas' height, from the ratio the canon fixes rather than from a second number.
_ASPECT_W, _ASPECT_H = (int(part) for part in _TYPE_SCALE["canvas-aspect-ratio"].split(":"))
CANVAS_HEIGHT_PX = CANVAS_WIDTH_PX * _ASPECT_H // _ASPECT_W

#: Body type, which `type-scale` puts at the floor, and the two sizes it marks as exceptions
#: beneath. The canon owns which of them may be used where.
BODY_PX = int(_TYPE_SCALE["body-px"])
DENSE_PX = int(_TYPE_SCALE["dense-px"])
DENSE_XS_PX = int(_TYPE_SCALE["dense-xs-px"])


#: The family the deck's text is set in. `fonts` says where it has to be bundled and registered,
#: and why; ``legible.fonts`` is what does it.
FONT_TEXT = rule_thresholds("fonts")["font-text"]


#: The density ceilings, which are what physically stop a slide absorbing a second message. Both
#: are exceeded rather than merely reached: the canon's own wording, kept in the name.
BULLETS_PER_SLIDE = int(rule_thresholds("bullet-ceiling")["bullets-per-slide"])
WORDS_PER_BULLET = int(rule_thresholds("word-ceiling")["words-per-bullet"])


#: How many em-dashes a headline may carry. The canon says none, and says it as a number so the
#: linter has something to compare against rather than a sentence to interpret.
EM_DASHES_PER_HEADLINE = int(rule_thresholds("no-em-dash-headline")["em-dashes-per-headline-max"])


_INFLATED_REGISTER = rule_thresholds("no-inflated-register")

#: The seed wordlist, and how loudly a hit is reported. The severity is the canon's call, not the
#: linter's: `established-terminology` can legitimately override this rule, so a hit warns.
INFLATED_REGISTER_WORDS = _listed(_INFLATED_REGISTER["inflated-register-words"])
INFLATED_REGISTER_SEVERITY = _INFLATED_REGISTER["inflated-register-severity"]


_OPENER_VARIETY = rule_thresholds("opener-variety")

#: The openers counted, and the share of a passage's sentences that may share one of them.
OPENER_WORDS = _listed(_OPENER_VARIETY["opener-words"])
OPENER_SHARE_MAX = float(_OPENER_VARIETY["opener-share-max"])
