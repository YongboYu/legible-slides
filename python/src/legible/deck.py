"""A Slidev deck, read as slides.

The linter decides rules; this module decides what a rule is looking at. Both halves are needed
and only one of them is interesting, so they are separate: a finding about a bullet ceiling is only
as trustworthy as the answer to "what is a bullet", and that answer belongs somewhere it can be
tested on its own.

The review surface is Slidev markdown (``docs/agent-skill-contract.md`` §3), so the split follows
Slidev's own: a line of three dashes ends a slide, and the block after it is that slide's
frontmatter when it reads as ``key: value`` rather than as content. The deck's headmatter falls out
of the same rule, being the frontmatter of a slide that has not started yet.

What comes back per slide is what the canon's script-decided rules ask about — the headline, the
bullets, the prose and the speaker notes — and nothing else. Layouts, components and code blocks
are evidence: the method has rules about them, but none a script decides.
"""

from __future__ import annotations

import re
from collections.abc import Iterator, Sequence
from dataclasses import dataclass
from pathlib import Path

__all__ = ["Slide", "parse_deck", "read_deck"]

#: A slide separator: three dashes alone on a line. Four or more is a horizontal rule, which is
#: what Slidev's own parser makes of it too.
_SEPARATOR = re.compile(r"^---\s*$")

#: The opening line of a frontmatter block — `layout: cover`, `clicks: 3`. A block that does not
#: start this way is content, and a parser that swallowed it would hide a slide from every check.
_FRONTMATTER = re.compile(r"^[A-Za-z_][\w.-]*\s*:(\s|$)")

_FENCE = re.compile(r"^\s*(```|~~~)")
_HEADING = re.compile(r"^\s{0,3}#{1,6}\s+(?P<text>.*?)\s*#*\s*$")
_BULLET = re.compile(r"^\s*(?:[-*+]|\d+[.)])\s+(?P<text>.*)$")

#: A whole HTML comment. Slidev reads the last one on a slide as the speaker notes.
_COMMENT = re.compile(r"<!--(?P<text>.*?)-->", re.DOTALL)

#: Inline markup that is not what the room reads: an image is evidence rather than words, a link
#: shows its text and never its URL, and emphasis markers are punctuation for the renderer.
_IMAGE = re.compile(r"!\[[^\]]*\]\([^)]*\)")
_LINK = re.compile(r"\[(?P<text>[^\]]*)\]\([^)]*\)")
_TAG = re.compile(r"<[^>]+>")
_EMPHASIS = re.compile(r"[*`~]+")


@dataclass(frozen=True)
class Slide:
    """One slide, as the rules that are decided by script see it.

    ``number`` counts from 1, the way an author and a reviewer both count slides, so a finding can
    name a slide without anyone translating an index.
    """

    number: int
    headline: str | None
    bullets: tuple[str, ...]
    prose: tuple[str, ...]
    notes: str | None


def read_deck(path: str | Path) -> tuple[Slide, ...]:
    """The slides of a deck on disk. Unreadable files raise ``OSError`` for the caller to report."""
    return parse_deck(Path(path).read_text(encoding="utf-8"))


def parse_deck(text: str) -> tuple[Slide, ...]:
    """The slides of a Slidev deck, in order."""
    return tuple(
        _slide(number, lines)
        for number, lines in enumerate(_split(text.replace("\r\n", "\n").split("\n")), start=1)
    )


def _split(lines: Sequence[str]) -> Iterator[list[str]]:
    """Every slide's lines, with the separators and the frontmatter blocks taken out.

    A slide of nothing but blank lines is not yielded: the commonest source of one is the deck's
    own headmatter, and an empty slide in the middle of a deck is a slide with nothing to check.
    """
    start = 0
    index = 0
    while index < len(lines):
        line = lines[index].rstrip()

        if _FENCE.match(line):
            index = _fence_end(lines, index)
        elif _SEPARATOR.match(line):
            if any(text.strip() for text in lines[start:index]):
                yield list(lines[start:index])
            closing = _frontmatter_end(lines, index)
            index = index if closing is None else closing
            start = index + 1

        index += 1

    if any(text.strip() for text in lines[start:]):
        yield list(lines[start:])


def _fence_end(lines: Sequence[str], opened: int) -> int:
    """The line the code block closes on, or its last line if the author never closed it."""
    for index in range(opened + 1, len(lines)):
        if _FENCE.match(lines[index].rstrip()):
            return index
    return len(lines) - 1


def _frontmatter_end(lines: Sequence[str], separator: int) -> int | None:
    """The line closing the frontmatter block this separator opens, if it opens one at all."""
    if separator + 1 >= len(lines) or not _FRONTMATTER.match(lines[separator + 1]):
        return None
    for index in range(separator + 2, len(lines)):
        if _SEPARATOR.match(lines[index].rstrip()):
            return index
    return None


def _slide(number: int, lines: Sequence[str]) -> Slide:
    body, notes = _body_and_notes(_without_code(lines))

    headline: str | None = None
    bullets: list[str] = []
    prose: list[str] = []
    paragraph: list[str] = []
    # Whether the line being read continues the bullet above it. Only a blank line, a heading or
    # the next bullet ends one, so where an author's editor wrapped a long bullet cannot decide
    # its word count — markdown's own lazy continuation, and the ceiling depends on it.
    continuing = False

    for line in body:
        heading = _HEADING.match(line)
        bullet = _BULLET.match(line)

        if not line.strip() or heading or bullet:
            # Any of the three also ends the paragraph being gathered; a wrapped paragraph is
            # still one passage, so the line break inside it does not.
            _flush(paragraph, prose)
            continuing = False

        if heading:
            headline = headline or _plain(heading.group("text")) or None
        elif bullet:
            bullets.append(_plain(bullet.group("text")))
            continuing = True
        elif not line.strip():
            continue
        elif continuing:
            bullets[-1] = f"{bullets[-1]} {_plain(line)}".strip()
        else:
            paragraph.append(_plain(line))

    _flush(paragraph, prose)
    return Slide(
        number=number,
        headline=headline,
        bullets=tuple(bullet for bullet in bullets if bullet),
        prose=tuple(prose),
        notes=notes,
    )


def _flush(paragraph: list[str], prose: list[str]) -> None:
    """One gathered paragraph becomes one passage. Lines that were only markup are not a passage."""
    passage = " ".join(text for text in paragraph if text)
    paragraph.clear()
    if passage:
        prose.append(passage)


def _without_code(lines: Sequence[str]) -> list[str]:
    """The slide without its code blocks. Code is evidence: no rule decided by script reads it."""
    kept: list[str] = []
    index = 0
    while index < len(lines):
        if _FENCE.match(lines[index].rstrip()):
            index = _fence_end(lines, index) + 1
            continue
        kept.append(lines[index])
        index += 1
    return kept


def _body_and_notes(lines: Sequence[str]) -> tuple[list[str], str | None]:
    """The slide's body with every comment removed, and the last comment as its speaker notes."""
    text = "\n".join(lines)
    comments = _COMMENT.findall(text)
    notes = comments[-1].strip() if comments else None
    return _COMMENT.sub("", text).split("\n"), notes or None


def _plain(text: str) -> str:
    """One line as the room receives it: no markup, no components, no URLs."""
    text = _IMAGE.sub("", text)
    text = _LINK.sub(lambda match: match.group("text"), text)
    text = _TAG.sub("", text)
    return _EMPHASIS.sub("", text).strip()
