"""The method's objective rules, as findings.

A rule the canon marks **decided by script** is a rule nobody should have to remember, so this
module decides them: the bullet and word ceilings, em-dashes in a headline, the inflated-register
wordlist, the sentence-opener share, and whether the deck's palette clears the separation floor.
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
from legible.method import (
    BULLETS_PER_SLIDE,
    EM_DASHES_PER_HEADLINE,
    INFLATED_REGISTER_SEVERITY,
    INFLATED_REGISTER_WORDS,
    OPENER_SHARE_MAX,
    OPENER_WORDS,
    WORDS_PER_BULLET,
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

#: The mark the rule names, and no other. An en-dash is a different character with a different job.
_EM_DASH = "—"

#: A word of a bullet: anything carrying a letter or a digit, so a stray dash or bracket left by
#: the markup does not count against the ceiling.
_WORD = re.compile(r"[^\W_]", re.UNICODE)

#: The end of a sentence, for counting openers over a passage.
_SENTENCE_END = re.compile(r"(?<=[.!?])[\"')\]]*\s+")


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
    findings = [finding for slide in read_deck(deck) for finding in _slide_findings(slide)]
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
