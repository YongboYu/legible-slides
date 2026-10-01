"""A Slidev deck, read as slides.

The linter decides rules; this module decides what a rule is looking at. Both halves are needed
and only one of them is interesting, so they are separate: a finding about a bullet ceiling is only
as trustworthy as the answer to "what is a bullet", and that answer belongs somewhere it can be
tested on its own.

The review surface is Slidev markdown (``docs/agent-skill-contract.md`` §3), so the split follows
Slidev's own: a line of three dashes ends a slide, and what follows it is that slide's frontmatter
when the next line is not blank and a closing line of three dashes arrives. Slidev asks nothing
else of the block — not that it read as ``key: value``, not that it parse as YAML — so neither does
this. The deck's headmatter falls out of the same rule, being the frontmatter of a slide that has
not started yet.

What comes back per slide is what the canon's script-decided rules ask about — the headline, the
bullets, the prose and the speaker notes, every font size the slide's own markup sets, and from
the frontmatter only the section the slide declares — plus the name of its layout, which no rule
reads but which is how a test finds a deck's opening and its close. Nothing else: what a layout
renders, components and code blocks are evidence, and no rule about them is a script's to decide.
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

#: Where a slide's markup can set a size: a style attribute (Vue's bound one included), a style
#: block, and a class list. A size anywhere else — a sentence about CSS, a code block — is not one.
_STYLE_ATTRIBUTE = re.compile(r"\bstyle\s*=\s*(?:\"(?P<double>[^\"]*)\"|'(?P<single>[^']*)')")
_STYLE_BLOCK = re.compile(r"<style\b[^>]*>(?P<css>.*?)</style>", re.DOTALL | re.IGNORECASE)
_CLASS_ATTRIBUTE = re.compile(r"\bclass\s*=\s*(?:\"(?P<double>[^\"]*)\"|'(?P<single>[^']*)')")

#: A font size inside a style: the CSS property, or the camel-cased key a Vue style object uses.
_FONT_SIZE = re.compile(r"font-?size['\"]?\s*:\s*['\"]?(?P<value>[^;'\",}]+)", re.IGNORECASE)

#: A UnoCSS class that sets a font size: a named step of its scale, or an arbitrary value.
_TEXT_SIZE_CLASS = re.compile(r"^text-(?:xs|sm|base|lg|\d?xl|\[[^\]]+\])$")

#: A top-level frontmatter key the rules read, and its value up to a trailing comment. Read by line
#: rather than as YAML, for the reason the module gives for the split: Slidev does not require the
#: block to parse, so neither does this, and the keys asked for are scalars at column 0.
_KEY = re.compile(
    r"""^(?P<key>section|backup|layout):[ \t]*"""
    r"""(?:(?P<quote>["'])(?P<quoted>.*?)(?P=quote)|(?P<plain>.*?))"""
    r"""[ \t]*(?:[ \t]\#.*)?$"""
)

#: How YAML 1.1, which Slidev reads frontmatter with, spells a true boolean. A quoted value is a
#: string whatever it says, so the theme would not take it for one and neither does this.
_TRUE = frozenset({"true", "True", "TRUE"})


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
    #: The section this slide declares, ``""`` for one that clears it, and ``None`` where the slide
    #: declares none and so carries the one before it. Carrying it forward is the theme's job.
    section: str | None = None
    #: Whether the section this slide declares is a backup, held for questions after the talk.
    backup: bool = False
    #: The layout the slide names, or ``None`` where it names none and the theme picks the default.
    layout: str | None = None
    #: Every font size the slide's markup sets, as written: ``font-size: 14px`` for a style,
    #: ``text-sm`` for a class. Which of them break the floor is the linter's call.
    font_sizes: tuple[str, ...] = ()


def read_deck(path: str | Path) -> tuple[Slide, ...]:
    """The slides of a deck on disk. Unreadable files raise ``OSError`` for the caller to report."""
    return parse_deck(Path(path).read_text(encoding="utf-8"))


def parse_deck(text: str) -> tuple[Slide, ...]:
    """The slides of a Slidev deck, in order."""
    return tuple(
        _slide(number, frontmatter, lines)
        for number, (frontmatter, lines) in enumerate(
            _split(text.replace("\r\n", "\n").split("\n")), start=1
        )
    )


def _split(lines: Sequence[str]) -> Iterator[tuple[list[str], list[str]]]:
    """Every slide's frontmatter and its lines, with the separators taken out.

    A slide of nothing but blank lines is not yielded unless it has frontmatter: the commonest
    source of one is the deck's own headmatter, which belongs to the slide after it, and an empty
    slide in the middle of a deck is a slide with nothing to check. A slide of frontmatter alone is
    one Slidev renders, a full-bleed image say, and the section it declares is on the footer.
    """
    start = 0
    index = 0
    frontmatter: list[str] = []
    while index < len(lines):
        line = lines[index].rstrip()

        if _FENCE.match(line):
            index = _fence_end(lines, index)
        elif _SEPARATOR.match(line):
            if frontmatter or any(text.strip() for text in lines[start:index]):
                yield frontmatter, list(lines[start:index])
            closing = _frontmatter_end(lines, index)
            frontmatter = [] if closing is None else list(lines[index + 1 : closing])
            index = index if closing is None else closing
            start = index + 1

        index += 1

    if frontmatter or any(text.strip() for text in lines[start:]):
        yield frontmatter, list(lines[start:])


def _fence_end(lines: Sequence[str], opened: int) -> int:
    """The line the code block closes on, or its last line if the author never closed it."""
    for index in range(opened + 1, len(lines)):
        if _FENCE.match(lines[index].rstrip()):
            return index
    return len(lines) - 1


def _frontmatter_end(lines: Sequence[str], separator: int) -> int | None:
    """The line closing the frontmatter block this separator opens, if it opens one at all.

    Two conditions, both Slidev's. The line after the separator has to carry something — the blank
    line every slide starts with is what tells the two apart — and the block has to close, because
    a block that never closes is a slide Slidev renders rather than frontmatter it strips. What the
    block *says* decides nothing: a comment before the first key opens a frontmatter block, and a
    heading written where a key belongs is swallowed by one.
    """
    if separator + 1 >= len(lines) or not lines[separator + 1].strip():
        return None
    for index in range(separator + 2, len(lines)):
        if _SEPARATOR.match(lines[index].rstrip()):
            return index
    return None


def _slide(number: int, frontmatter: Sequence[str], lines: Sequence[str]) -> Slide:
    body, notes = _body_and_notes(_without_code(lines))
    keys = _keys(frontmatter)

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
        section=keys.get("section"),
        backup=keys.get("backup") in _TRUE,
        layout=keys.get("layout") or None,
        font_sizes=_font_sizes("\n".join(body)),
    )


def _font_sizes(body: str) -> tuple[str, ...]:
    """Every size the slide's markup sets, in the order it sets them."""
    found: list[tuple[int, str]] = []
    for attribute in _STYLE_ATTRIBUTE.finditer(body):
        style = attribute.group("double") or attribute.group("single") or ""
        found.extend(
            (attribute.start(), f"font-size: {size.group('value').strip()}")
            for size in _FONT_SIZE.finditer(style)
        )
    for block in _STYLE_BLOCK.finditer(body):
        found.extend(
            (block.start(), f"font-size: {size.group('value').strip()}")
            for size in _FONT_SIZE.finditer(block.group("css"))
        )
    for attribute in _CLASS_ATTRIBUTE.finditer(body):
        classes = (attribute.group("double") or attribute.group("single") or "").split()
        found.extend((attribute.start(), name) for name in classes if _TEXT_SIZE_CLASS.match(name))
    return tuple(size for _, size in sorted(found, key=lambda at: at[0]))


def _keys(frontmatter: Sequence[str]) -> dict[str, str]:
    """The frontmatter keys the rules read. Absent keys are absent, not empty.

    A quoted section or layout comes back unquoted. A quoted backup is a string to YAML, so it comes
    back empty: only a plain value can be one of the spellings in ``_TRUE``.
    """
    keys: dict[str, str] = {}
    for line in frontmatter:
        found = _KEY.match(line.rstrip())
        if not found:
            continue
        key = found.group("key")
        if found.group("quote"):
            keys[key] = found.group("quoted") if key != "backup" else ""
        else:
            keys[key] = found.group("plain")
    return keys


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
