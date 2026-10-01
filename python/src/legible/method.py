"""The canon, quoted.

`docs/method.md` states every rule of the method and every number it turns on, once. This module is
how Python reads one out of it, so the package quotes the canon rather than keeping a second copy
that can drift. Every rule carries a stable ID and, where it has a number, a ``**Threshold**``
footer of ``key = value`` pairs; ``rule_thresholds`` returns one rule's pairs, and ``rules`` returns
whole rules — the statement, the prose that qualifies it, and which side of the script/judgment
seam the canon puts it on.

Two callers, one reader. A linter needs a number; the review skill needs the rule itself, because a
reviewer handed a rule ID and nothing else would have to remember what it says. Neither of them may
hold a copy, which is what ``docs/agent-skill-contract.md`` §2 means by a thin pointer.

The constants below are grouped by the rule that owns them — `separation-floor` for the colour
numbers, `type-scale` and `fonts` for what a generated figure is set in. Change a rule and they
change here.
"""

from __future__ import annotations

import re
from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path

#: Any heading the canon states, from a section down to the deepest rule.
_HEADING = re.compile(r"^(?P<hashes>#{2,6})[ \t]+(?P<title>.+?)[ \t]*$", re.MULTILINE)

#: A fenced block, and what a heading inside one is: an example of a heading rather than one. The
#: canon fences a diagram today and documents markdown, so a rule invented inside a fence is a
#: reachable mistake rather than a hypothetical one.
_FENCED = re.compile(r"^(?P<fence>```|~~~).*?^(?P=fence)", re.MULTILINE | re.DOTALL)

#: What makes a heading a rule's: it opens with the rule's stable ID in backticks, and what follows
#: is the rule's statement. Any depth, because the voice rules sit one level deeper under a
#: subsection heading and a rule is a rule wherever it is stated. The colon the canon writes after
#: the ID is optional here: an ID in backticks at the head of a heading is the whole signal, and a
#: rule that stopped being one over a missing colon would be a rule nothing checks.
_RULE_TITLE = re.compile(r"^`(?P<rule>[a-z0-9-]+)`\s*:?\s*(?P<statement>.*)$")

#: One `key = value` pair inside a **Threshold** footer.
_THRESHOLD = re.compile(r"`(?P<key>[a-z0-9-]+)\s*=\s*(?P<value>[^`]+)`")

#: The footers a rule's own metadata lives in.
_DECIDED_BY, _THRESHOLD_MARKER = "**Decided by**", "**Threshold**"

#: The two sides of the seam, and the only words a `**Decided by**` footer may name. `script` is a
#: rule `legible lint` settles; `judgment` is one only a reader can.
DECIDERS = ("script", "judgment")

#: A section's number, which is navigation rather than part of its name: `## 7. Voice` is the voice
#: section whatever it is numbered next year.
_ENUMERATION = re.compile(r"^\d+[a-z]?\.\s*")

_NOT_IN_A_SLUG = re.compile(r"[^a-z0-9]+")

#: A separator line, which belongs to the canon's typography rather than to the rule above it.
_SEPARATOR = re.compile(r"^\s*---+\s*$")


class MethodError(LookupError):
    """The canon could not be read, or does not carry what was asked of it."""


@dataclass(frozen=True)
class Rule:
    """One rule of the method, as the canon states it.

    ``text`` is the rule's own markdown, verbatim, because a reviewer weighing a slide against a
    rule should read the canon's words and not a paraphrase of them. The rest is what a caller
    selects on: ``section`` and ``decided_by`` are how the review picks up a rule the canon added
    without anybody editing the reviewer.
    """

    id: str
    section: str
    statement: str
    decided_by: tuple[str, ...]
    text: str
    thresholds: Mapping[str, str] = field(default_factory=dict)


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


def rules(
    canon: str | None = None,
    *,
    decided_by: str | None = None,
    section: str | None = None,
) -> tuple[Rule, ...]:
    """Every rule the canon states, in the order it states them, narrowed by what is asked for.

    ``decided_by`` and ``section`` are filters rather than lookups: a caller after "the judgment
    rules of the voice section" is asking the canon which those are, so a rule added there is
    picked up with nothing edited here or in whatever loaded them.
    """
    selected = _parse(read_canon() if canon is None else canon)
    if decided_by is not None:
        selected = [rule_ for rule_ in selected if decided_by in rule_.decided_by]
    if section is not None:
        selected = [rule_ for rule_ in selected if rule_.section == section]
    return tuple(selected)


def rule(rule_id: str, canon: str | None = None) -> Rule:
    """One rule, by its stable ID."""
    for candidate in rules(canon):
        if candidate.id == rule_id:
            return candidate
    raise MethodError(f"the canon carries no rule `{rule_id}`")


def rule_thresholds(rule_id: str, canon: str | None = None) -> dict[str, str]:
    """The ``key = value`` thresholds one rule declares, as written in the canon.

    Values come back as the strings the canon wrote, because the canon is the authority on both
    the number and its units; callers convert to whatever type they need.
    """
    found = rule(rule_id, canon)
    if _THRESHOLD_MARKER not in found.text:
        raise MethodError(f"rule `{rule_id}` declares no threshold")
    return dict(found.thresholds)


def _parse(text: str) -> list[Rule]:
    """Walk the canon's headings, and make a rule of each one that names a rule.

    Order matters twice over. A rule belongs to the section heading above it, and — where the canon
    declares `**Decided by**` once for a whole subsection rather than on each rule under it — it is
    also decided by the nearest declaration above it. Both are the canon's own way of stating
    something once, so both are read rather than made up for here.
    """
    parsed: list[Rule] = []
    section = ""
    # What each depth of heading declares for the rules beneath it. A heading closes the headings
    # at or below its own depth and nothing above them, so a plain `#### Notes` written inside a
    # subsection cannot silently strip that subsection's declaration off the rules that follow —
    # which would drop them out of a review that asked for them and leave it reporting a pass.
    declared: dict[int, tuple[str, ...]] = {}

    headings = _headings(text)
    for position, heading in enumerate(headings):
        end = headings[position + 1].start() if position + 1 < len(headings) else len(text)
        block = text[heading.start() : end]
        body = text[heading.end() : end]
        depth = len(heading.group("hashes"))

        title = _RULE_TITLE.match(heading.group("title"))
        if title is None:
            # A section heading, whose prose may decide the rules beneath it.
            if depth == 2:
                section = _slug(heading.group("title"))
            declared = {level: at for level, at in declared.items() if level < depth}
            declared[depth] = _decided_by(body)
            continue

        inherited = next(
            (declared[level] for level in sorted(declared, reverse=True) if declared[level]),
            (),
        )

        parsed.append(
            Rule(
                id=title.group("rule"),
                section=section,
                statement=title.group("statement").strip(),
                decided_by=_decided_by(body) or inherited,
                text=_trimmed(block),
                thresholds=_thresholds(body),
            )
        )

    return parsed


def _headings(text: str) -> list[re.Match[str]]:
    """Every heading the canon states, and none of the ones it merely shows inside a fence."""
    fenced = [match.span() for match in _FENCED.finditer(text)]
    return [
        heading
        for heading in _HEADING.finditer(text)
        if not any(start <= heading.start() < end for start, end in fenced)
    ]


def _decided_by(body: str) -> tuple[str, ...]:
    """Which side of the seam a `**Decided by**` footer puts its rule on, in the order it says so.

    A mixed rule names both, and the canon states which half is which in prose the caller reads for
    itself: what is decidable here is that both words are present.
    """
    footer = _footer(body, _DECIDED_BY)
    found = [(footer.find(decider), decider) for decider in DECIDERS if _names(footer, decider)]
    return tuple(decider for _, decider in sorted(found))


def _thresholds(body: str) -> dict[str, str]:
    return {
        match.group("key"): match.group("value").strip()
        for match in _THRESHOLD.finditer(_footer(body, _THRESHOLD_MARKER))
    }


def _footer(body: str, marker: str) -> str:
    """One footer of a rule, from its marker to the end of its own paragraph.

    A footer is one paragraph, however many lines the canon wraps it over. Stopping at the blank
    line keeps prose that merely follows a rule from being read as one of its thresholds.
    """
    _, found, footer = body.partition(marker)
    if not found:
        return ""
    footer, _, _ = footer.partition("\n\n")
    return footer


def _names(footer: str, word: str) -> bool:
    return re.search(rf"\b{re.escape(word)}\b", footer) is not None


def _trimmed(block: str) -> str:
    """A rule's markdown without the blank lines and the separator that follow it on the page."""
    lines = block.rstrip().split("\n")
    while lines and (not lines[-1].strip() or _SEPARATOR.match(lines[-1])):
        lines.pop()
    return "\n".join(lines)


def _slug(title: str) -> str:
    """A section's name as something to pass on a command line: `## 7. Voice` is `voice`."""
    return _NOT_IN_A_SLUG.sub("-", _ENUMERATION.sub("", title).lower()).strip("-")


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


_FONTS = rule_thresholds("fonts")

#: The family the deck's text is set in. `fonts` says where it has to be bundled and registered,
#: and why; ``legible.fonts`` is what does it.
FONT_TEXT = _FONTS["font-text"]

#: The family the deck's locator is set in, and nothing else. Nothing here draws with it: it is here
#: so the bundle can be held to carrying both of the families the canon names.
FONT_MONO = _FONTS["font-mono"]


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


_SECTION_LOCATOR = rule_thresholds("section-locator")

#: How many sections the footer's map can name, and how long each name may run, before the map
#: stops fitting. Both are *exceeded* rather than reached, and a hit warns: the label with a count
#: still fits a deck that outgrew the map, so outgrowing it is a finding and never a gate.
SECTIONS_MAX = int(_SECTION_LOCATOR["sections-max"])
SECTION_LABEL_CHARS_MAX = int(_SECTION_LOCATOR["section-label-chars-max"])
SECTION_LOCATOR_SEVERITY = _SECTION_LOCATOR["section-locator-severity"]


_ACCENT_IS_ATTENTION = rule_thresholds("accent-is-attention")

#: The pairings attention is read in, as (foreground, background) roles: ink on the fill, and the
#: text-and-stroke role on each ground. The canon writes them `x on y`; this is that, split.
ATTENTION_CONTRAST_PAIRS = tuple(
    tuple(pair.split(" on ")) for pair in _listed(_ACCENT_IS_ATTENTION["attention-contrast-pairs"])
)

#: The WCAG contrast ratio each of those pairings has to clear.
ATTENTION_CONTRAST_MIN = float(_ACCENT_IS_ATTENTION["attention-contrast-min"])
