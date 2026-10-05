"""The method's objective rules, as findings.

A rule the canon marks **decided by script** is a rule nobody should have to remember, so this
module decides them: the bullet and word ceilings, how many lines a headline takes on the slide,
em-dashes in a headline, the inflated-register wordlist, the sentence-opener share, whether the
footer's section map still fits, a font size a slide sets inline or below the type floor, whether
the talk closes on a conclusion rather than a thank-you, and whether the deck's palette clears the
separation floor. It also counts what the review advisories budget — visual groups and words on a
slide, emphasis and callouts, new abbreviations over the talk, and the notes' time budgets against
the slot — and reports each at the severity the canon gives it, which is a warning: an advisory is
the review's to weigh, never a gate.
``docs/agent-skill-contract.md`` §4a fixes the set; the canon fixes every number in it, and this
module quotes those numbers through ``legible.method`` rather than keeping a second copy.

Two things it deliberately does not do.

It does not decide the rules the canon marks **judgment** — whether a slide carries one message,
whether a headline is a claim. Those belong to the review skill, which is fallible and advisory;
what is here is a gate, and a gate may only hold things that are decidable.

It does not measure colour. `separation-floor` is checked by running ``cvd-validate`` and reading
its exit code, which is what that exit code is for: one implementation of Machado (2009) in this
package means a linter that says a palette collapses and a report that says it holds cannot
disagree, because there is only ever one of them speaking.
"""

from __future__ import annotations

import re
import shutil
import subprocess
import sys
from collections.abc import Iterable, Iterator, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import NamedTuple

from legible.deck import Slide, read_deck
from legible.headline import HEADLINE_WIDTH_PX, wrap
from legible.method import (
    ACRONYM_BUDGET_SEVERITY,
    BULLETS_PER_SLIDE,
    CALLOUTS_PER_SLIDE,
    CLOSING_LABELS,
    CONCLUSION_SEVERITY,
    ELEMENT_CEILING_SEVERITY,
    ELEMENTS_PER_SLIDE,
    EM_DASHES_PER_HEADLINE,
    EMPHASISED_SPANS_PER_SLIDE,
    FLOOR_PX,
    HEADLINE_LINES_MAX,
    HEADLINE_PX,
    INFLATED_REGISTER_SEVERITY,
    INFLATED_REGISTER_WORDS,
    NEW_ACRONYMS_PER_TALK,
    ON_SLIDE_WORDS_SEVERITY,
    OPENER_SHARE_MAX,
    OPENER_WORDS,
    PACE_BUDGET_SEVERITY,
    PACE_SHARE_MAX,
    SECTION_LABEL_CHARS_MAX,
    SECTION_LOCATOR_SEVERITY,
    SECTIONS_MAX,
    SIGNAL_BUDGET_SEVERITY,
    THANK_YOU_WORDS,
    WORDS_PER_BULLET,
    WORDS_PER_SLIDE,
)

__all__ = ["ERROR", "WARNING", "Finding", "LintReport", "Unchecked", "lint"]

#: The two severities the review contract fixes. An error is an objective violation and gates; a
#: warning reports and never does. Which rules may only warn is the canon's call, not this
#: module's — `no-inflated-register` sets its own severity, because `established-terminology`
#: legitimately overrides it.
ERROR, WARNING = "error", "warning"

#: The command the palette check runs. Never imported, always run: the exit code is the interface.
VALIDATOR = "cvd-validate"

#: The exit codes ``cvd-validate`` publishes. 1 is a palette measured below the floor; anything
#: else non-zero is a theme that was never measured, which is a different thing to report.
_FLOOR_FAILED = 1

#: The layout whose ``#`` is the talk's title rather than a headline: set heavier, and with no
#: headline zone under it for a third line to run into.
_COVER = "cover"

#: The mark the rule names, and no other. An en-dash is a different character with a different job.
_EM_DASH = "—"

#: A word of a bullet: anything carrying a letter or a digit, so a stray dash or bracket left by
#: the markup does not count against the ceiling.
_WORD = re.compile(r"[^\W_]", re.UNICODE)

#: The end of a sentence, for counting openers over a passage.
_SENTENCE_END = re.compile(r"(?<=[.!?])[\"')\]]*\s+")

#: A size in a style, split into its number and its unit.
_CSS_SIZE = re.compile(
    r"^font-size:\s*(?P<number>\d*\.?\d+)\s*(?P<unit>px|pt|rem)\b", re.IGNORECASE
)

#: A UnoCSS arbitrary size in px, which is an inline px size spelled as a class.
_ARBITRARY_PX = re.compile(r"^text-\[(?P<number>\d*\.?\d+)px\]$")

#: How many canvas px one of each absolute unit is. A rem is the browser's 16 px root: Slidev scales
#: the canvas as a whole rather than the root size, so a rem is 16 of the canvas' own px.
_PX_PER = {"px": 1.0, "pt": 96 / 72, "rem": 16.0}

#: What UnoCSS's named text sizes set, in px, at that same root. Only the steps the floor can catch
#: are needed, and they are UnoCSS's numbers rather than the method's: the canon fixes the floor,
#: and these are what a class resolves to under it.
_TEXT_CLASS_PX = {"text-xs": 12.0, "text-sm": 14.0, "text-base": 16.0, "text-lg": 18.0}

#: An abbreviation as the room reads one: a run of two or more capitals, with a plural ``s`` after
#: it at most. The run is the abbreviation, so ``BPIs`` and ``BPI2017`` are both ``BPI``; a word
#: that merely opens on a capital, or a name in mixed case, is not one.
_ACRONYM = re.compile(r"(?<![A-Za-z])(?P<capitals>[A-Z]{2,})s?(?![A-Za-z])")

#: A duration as the canon writes one: a clock (``1:30``), or a run of numbers with units.
_CLOCK = re.compile(r"^(?:(?P<h>\d+):)?(?P<m>\d+):(?P<s>\d{2})$")
_DURATION_PART = re.compile(
    r"(?P<number>\d*\.?\d+)\s*"
    r"(?P<unit>h|hr|hours?|min|mins|minutes?|m|s|sec|secs|seconds?)(?![a-z])"
)
_SECONDS_PER = {"h": 3600, "m": 60, "s": 1}


class Finding(NamedTuple):
    """One rule, broken in one place.

    ``slide`` is the slide's number as an author counts them, or ``None`` when the finding is
    against the deck rather than any one slide — which is what a palette below the floor is.
    """

    rule: str
    severity: str
    slide: int | None
    message: str


class Unchecked(NamedTuple):
    """A theme the validator could not measure. Not a violation, and not a pass either."""

    theme: str
    detail: str


@dataclass(frozen=True)
class LintReport:
    """What the deck broke.

    ``passed`` is about violations alone, the way ``validate()``'s is: a theme that could not be
    measured lands in ``unchecked``, and turning that into an exit code is the command's job.
    """

    passed: bool
    findings: tuple[Finding, ...] = ()
    unchecked: tuple[Unchecked, ...] = ()


def lint(deck: str | Path, themes: Iterable[str | Path] = ()) -> LintReport:
    """Check a Slidev deck, and the themes it is presented in, against the canon's script rules.

    ``themes`` is empty by default because a deck does not say which palette it wears — the theme
    is the caller's to name, and naming none checks the slides alone.
    """
    slides = read_deck(deck)
    findings = [finding for slide in slides for finding in _slide_findings(slide)]
    findings.extend(_section_findings(slides))
    findings.extend(_conclusion_findings(slides))
    findings.extend(_acronym_findings(slides))
    findings.extend(_pace_findings(slides))
    # In slide order, the deck's own findings after them, so a report reads the way the deck runs.
    findings.sort(key=lambda finding: (finding.slide is None, finding.slide or 0))
    palette, unchecked = _palette_findings(themes)

    return LintReport(
        # Only the severity the canon spells `warning` is allowed not to block, which is what
        # ``docs/agent-skill-contract.md`` §5 carves out and the whole of it. A severity nobody
        # here recognises gates, because a gate that fails open is not one.
        passed=all(finding.severity == WARNING for finding in (*findings, *palette)),
        findings=(*findings, *palette),
        unchecked=tuple(unchecked),
    )


def _slide_findings(slide: Slide) -> Iterator[Finding]:
    """Every rule this slide breaks, in the order a reader meets them on it."""
    if len(slide.bullets) > BULLETS_PER_SLIDE:
        yield _finding(
            "bullet-ceiling",
            slide,
            f"{len(slide.bullets)} bullets, ceiling {BULLETS_PER_SLIDE}",
        )

    for bullet in slide.bullets:
        words = _words(bullet)
        if words > WORDS_PER_BULLET:
            yield _finding(
                "word-ceiling",
                slide,
                f"{words} words, ceiling {WORDS_PER_BULLET}: {bullet!r}",
            )

    if slide.headline and slide.layout != _COVER:
        lines = wrap(slide.headline)
        if len(lines) > HEADLINE_LINES_MAX:
            yield _finding(
                "headline-shape",
                slide,
                f"{len(lines)} lines at {HEADLINE_PX} px across {HEADLINE_WIDTH_PX} px, ceiling "
                f"{HEADLINE_LINES_MAX}; past it: {' '.join(lines[HEADLINE_LINES_MAX:])!r}",
            )

    em_dashes = (slide.headline or "").count(_EM_DASH)
    if em_dashes > EM_DASHES_PER_HEADLINE:
        yield _finding(
            "no-em-dash-headline",
            slide,
            f"{em_dashes} em-dash in the headline: {slide.headline!r}",
        )

    for word in _inflated(slide):
        yield _finding(
            "no-inflated-register",
            slide,
            f"{word!r} inflates register without adding information",
            severity=INFLATED_REGISTER_SEVERITY,
        )

    for opener, shared, total in _monotonous(slide):
        yield _finding(
            "opener-variety",
            slide,
            f"{shared} of {total} sentences open with {opener!r}",
        )

    for size in slide.font_sizes:
        problem = _off_scale(size)
        if problem:
            yield _finding("type-scale", slide, f"{size!r}: {problem}")

    if len(slide.groups) > ELEMENTS_PER_SLIDE:
        yield _finding(
            "element-ceiling",
            slide,
            f"{len(slide.groups)} visual groups ({', '.join(slide.groups)}), "
            f"ceiling {ELEMENTS_PER_SLIDE}",
            severity=ELEMENT_CEILING_SEVERITY,
        )

    words = sum(_words(text) for text in (*slide.bullets, *slide.prose))
    if words > WORDS_PER_SLIDE:
        yield _finding(
            "on-slide-words",
            slide,
            f"{words} words outside the headline and figures, ceiling {WORDS_PER_SLIDE}",
            severity=ON_SLIDE_WORDS_SEVERITY,
        )

    if len(slide.emphasis) > EMPHASISED_SPANS_PER_SLIDE:
        spans = ", ".join(repr(span) for span in slide.emphasis)
        yield _finding(
            "signal-budget",
            slide,
            f"{len(slide.emphasis)} emphasised spans ({spans}), "
            f"ceiling {EMPHASISED_SPANS_PER_SLIDE}",
            severity=SIGNAL_BUDGET_SEVERITY,
        )
    if slide.callouts > CALLOUTS_PER_SLIDE:
        yield _finding(
            "signal-budget",
            slide,
            f"{slide.callouts} callouts, ceiling {CALLOUTS_PER_SLIDE}",
            severity=SIGNAL_BUDGET_SEVERITY,
        )


def _off_scale(size: str) -> str | None:
    """What is wrong with one size a slide sets, or ``None`` if nothing is.

    An inline px size is wrong whatever it says, because the floor can only be checked on slides
    that size text through the template's classes. A size below the floor is wrong in any unit that
    resolves to canvas px. A relative size (``em``, ``%``, a custom property) resolves only against
    the page, so it is the theme's scale that sizes it and nothing here can say it is too small.
    """
    css, arbitrary = _CSS_SIZE.match(size), _ARBITRARY_PX.match(size)
    if css:
        unit = css.group("unit").lower()
        px, inline = float(css.group("number")) * _PX_PER[unit], unit == "px"
    elif arbitrary:
        px, inline = float(arbitrary.group("number")), True
    elif size in _TEXT_CLASS_PX:
        px, inline = _TEXT_CLASS_PX[size], False
    else:
        return None

    problems = ["inline px size; size text through the template's classes"] if inline else []
    if px < FLOOR_PX:
        problems.append(f"{px:.3g} px, below the {FLOOR_PX} px floor")
    return ", and ".join(problems) or None


def _section_findings(slides: Sequence[Slide]) -> Iterator[Finding]:
    """Whether the footer's map still fits the sections the deck declares.

    Over the deck rather than per slide, because a section is a run of slides. Only the sections the
    map names are counted: a backup shows its own label and no position, so it takes no place in the
    map and its label has no map to fit. A name declared again is the same section, and is judged
    where it was first declared.
    """
    named: list[str] = []
    for slide in slides:
        if not slide.section or slide.backup or slide.section in named:
            continue
        named.append(slide.section)

        if len(slide.section) > SECTION_LABEL_CHARS_MAX:
            yield _finding(
                "section-locator",
                slide,
                f"section {slide.section!r} is {len(slide.section)} characters, "
                f"ceiling {SECTION_LABEL_CHARS_MAX}",
                severity=SECTION_LOCATOR_SEVERITY,
            )
        if len(named) == SECTIONS_MAX + 1:
            yield _finding(
                "section-locator",
                slide,
                f"section {slide.section!r} is one more than the map holds, ceiling {SECTIONS_MAX}",
                severity=SECTION_LOCATOR_SEVERITY,
            )


def _conclusion_findings(slides: Sequence[Slide]) -> Iterator[Finding]:
    """Whether the slide left up through Q&A is a conclusion rather than a thank-you.

    That slide is the last one outside the backups.
    """
    talk = list(_main(slides))
    if not talk:
        return
    last = talk[-1]

    problem = _not_a_conclusion(last.headline)
    if problem:
        yield _finding(
            "conclusion-stays-up",
            last,
            f"the last main slide {problem}; it stays up through Q&A, so make it the answers",
            severity=CONCLUSION_SEVERITY,
        )


def _main(slides: Sequence[Slide]) -> Iterator[Slide]:
    """The talk's slides, without its backups.

    A backup is declared where its section starts and carries forward with it, so it runs until a
    slide declares a section of the talk again.
    """
    in_backup = False
    for slide in slides:
        if slide.section is not None:
            in_backup = slide.backup
        if not in_backup:
            yield slide


def _acronym_findings(slides: Sequence[Slide]) -> Iterator[Finding]:
    """The slide where the talk introduces one abbreviation more than its budget.

    Once, on that slide: the abbreviations past it are the same advice again, and the finding names
    every one the talk had introduced by then, which is the list to choose the budget from.
    """
    introduced: list[str] = []
    for slide in _main(slides):
        text = " ".join(part for part in (slide.headline, *slide.bullets, *slide.prose) if part)
        for acronym in (match.group("capitals") for match in _ACRONYM.finditer(text)):
            if acronym in introduced:
                continue
            introduced.append(acronym)
            if len(introduced) == NEW_ACRONYMS_PER_TALK + 1:
                yield _finding(
                    "acronym-budget",
                    slide,
                    f"{acronym!r} is new abbreviation {len(introduced)} of the talk, ceiling "
                    f"{NEW_ACRONYMS_PER_TALK} (so far: {', '.join(introduced)}); "
                    "spell the rest out",
                    severity=ACRONYM_BUDGET_SEVERITY,
                )


def _pace_findings(slides: Sequence[Slide]) -> Iterator[Finding]:
    """The slide where the notes' time budgets, summed, pass their share of the slot.

    Silent unless the deck declares a slot: a deck that plans none has made no claim to check. A
    slot or a budget this cannot read is reported where it is written, never skipped, because a
    budget left out of the sum is a talk that reads as fitting when it may not.
    """
    if not slides or not slides[0].duration:
        return
    slot = _seconds(slides[0].duration)
    if not slot:
        yield _unreadable(slides[0], "slot", slides[0].duration)
        return

    spent = 0.0
    for slide in _main(slides):
        if not slide.time:
            continue
        budget = _seconds(slide.time)
        if budget is None:
            yield _unreadable(slide, "time budget", slide.time)
            continue
        spent += budget
        if spent > PACE_SHARE_MAX * slot:
            yield _finding(
                "pace-budget",
                slide,
                f"the budgets reach {_clock(spent)} by this slide, {spent / slot:.0%} of the "
                f"{slides[0].duration} slot, ceiling {PACE_SHARE_MAX:.0%}",
                severity=PACE_BUDGET_SEVERITY,
            )
            return


def _unreadable(slide: Slide, what: str, written: str) -> Finding:
    return _finding(
        "pace-budget",
        slide,
        f"cannot read the {what} {written!r}; write a duration such as 90s, 1min 30s or 1:30",
        severity=PACE_BUDGET_SEVERITY,
    )


def _seconds(duration: str) -> float | None:
    """A duration in seconds, or ``None`` when it is written in no form this can read.

    The canon's own forms, and the unit spellings around them a speaker is likely to type.
    """
    text = duration.strip().lower()
    clock = _CLOCK.match(text)
    if clock:
        hours, minutes, seconds = (int(clock.group(unit) or 0) for unit in "hms")
        return 3600 * hours + 60 * minutes + seconds
    parts = list(_DURATION_PART.finditer(text))
    if not parts or _DURATION_PART.sub("", text).strip():
        return None
    return sum(float(part.group("number")) * _SECONDS_PER[part.group("unit")[0]] for part in parts)


def _clock(seconds: float) -> str:
    """A number of seconds as a speaker reads a clock: ``18:00``."""
    minutes, rest = divmod(round(seconds), 60)
    return f"{minutes}:{rest:02d}"


def _not_a_conclusion(headline: str | None) -> str | None:
    """What keeps a headline from being a conclusion's, or ``None`` if nothing a script can see.

    A label is matched whole, so a claim that names the questions it answers is not one; a thank-you
    is matched anywhere in the headline, which can catch a claim that opens "thanks to", and is one
    reason the canon has this rule warn rather than gate.
    """
    if not headline:
        return "has no headline"
    spoken = " ".join(headline.split()).strip(" .!?:;,").casefold()
    if spoken in {label.casefold() for label in CLOSING_LABELS}:
        return f"is headed {headline!r}, a label rather than a claim"
    for words in THANK_YOU_WORDS:
        if re.search(rf"\b{re.escape(words.casefold())}\b", spoken):
            return f"reads as a thank-you: {headline!r}"
    return None


def _finding(rule: str, slide: Slide, message: str, severity: str = ERROR) -> Finding:
    return Finding(rule=rule, severity=severity, slide=slide.number, message=message)


def _words(text: str) -> int:
    return sum(1 for token in text.split() if _WORD.search(token))


def _inflated(slide: Slide) -> Iterator[str]:
    """Every listed word the slide uses anywhere, once each, in the order the canon lists them.

    Matched whole and as written: the canon's list is a seed to extend there rather than a stem to
    inflect here, so a form it does not carry is not a hit and `established-terminology` keeps the
    benefit of the doubt.
    """
    text = " ".join(
        part for part in (slide.headline, *slide.bullets, *slide.prose, slide.notes) if part
    ).lower()
    for word in INFLATED_REGISTER_WORDS:
        if re.search(rf"\b{re.escape(word.lower())}\b", text):
            yield word


def _monotonous(slide: Slide) -> Iterator[tuple[str, int, int]]:
    """Every listed opener that carries more than its share of one of the slide's passages.

    A passage is the slide's prose, or its speaker notes — the two places sentences run on into
    each other. The canon counts openers over a passage and says so twice, which is what keeps a
    lone sentence out of it: one sentence is a share of 1.0 and no evidence of anything.
    """
    for passage in _passages(slide):
        sentences = _sentences(passage)
        if len(sentences) < 2:
            continue
        for opener in OPENER_WORDS:
            shared = sum(1 for sentence in sentences if _opens_with(sentence, opener))
            if shared / len(sentences) > OPENER_SHARE_MAX:
                yield opener, shared, len(sentences)


def _passages(slide: Slide) -> tuple[str, ...]:
    """The slide's runs of prose: each paragraph, and the speaker notes.

    One paragraph is one passage. Counting the slide's prose as a single passage would let a long
    second paragraph carry a monotonous first one under the ceiling, which is the wrong way for a
    gate to fail. A headline is one sentence by rule and a bullet is under the word ceiling, so
    neither is a passage anything could be counted over.
    """
    return tuple(passage for passage in (*slide.prose, slide.notes) if passage)


def _sentences(passage: str) -> list[str]:
    return [sentence for sentence in _SENTENCE_END.split(passage) if sentence.strip()]


def _opens_with(sentence: str, opener: str) -> bool:
    words = sentence.split(maxsplit=1)
    first = words[0].strip("\"'([") if words else ""
    return first.casefold() == opener.casefold()


def _palette_findings(
    themes: Iterable[str | Path],
) -> tuple[list[Finding], list[Unchecked]]:
    """Run the validator over each theme and read its verdict off the exit code."""
    findings: list[Finding] = []
    unchecked: list[Unchecked] = []

    paths = [str(theme) for theme in themes]
    command = _validator()
    if command is None and paths:
        return findings, [
            Unchecked(theme, f"{theme}: {VALIDATOR} is not installed on this machine")
            for theme in paths
        ]

    for theme in paths:
        result = subprocess.run([str(command), theme], capture_output=True, text=True, check=False)
        if result.returncode == 0:
            continue
        if result.returncode == _FLOOR_FAILED:
            findings.append(
                Finding(
                    rule="separation-floor",
                    severity=ERROR,
                    slide=None,
                    message=(
                        f"{_verdict(result.stdout, theme)}; `{VALIDATOR} {theme}` names the pairs"
                    ),
                )
            )
        else:
            unchecked.append(Unchecked(theme, _verdict(result.stderr, theme)))

    return findings, unchecked


def _validator() -> str | None:
    """Where ``cvd-validate`` is, preferring the one installed beside the interpreter running us.

    An environment where the package is importable but its console script is not on ``PATH`` is
    ordinary — a virtualenv nobody activated — and looking there first means the linter and the
    validator are the same install, checking against the same pin.
    """
    return shutil.which(VALIDATOR, path=str(Path(sys.executable).parent)) or shutil.which(VALIDATOR)


def _verdict(output: str, theme: str) -> str:
    """The validator's own first line, so its wording reaches the author rather than a paraphrase.

    Which is also why nothing here parses that line: what it *means* arrived in the exit code.
    """
    lines: Sequence[str] = [line.strip() for line in output.splitlines() if line.strip()]
    return lines[0] if lines else f"{theme}: {VALIDATOR} said nothing"
