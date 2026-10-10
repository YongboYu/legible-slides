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
bullets, the prose and the speaker notes, every font size the slide's own markup sets, the visual
groups it is built from, the spans it emphasises and the callouts it carries, the time budget its
notes state, and from the frontmatter only the section the slide declares and the slot the deck's
headmatter does — plus the name of its layout, which no rule reads but which is how a test finds a
deck's opening and its close. Nothing else: what a layout renders, what a component draws and what
a code block says are evidence, and no rule about them is a script's to decide.
"""

from __future__ import annotations

import re
from collections.abc import Iterable, Iterator, Sequence
from dataclasses import dataclass
from pathlib import Path

__all__ = ["DeckError", "Slide", "font_sizes", "parse_deck", "read_deck"]

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

#: A run of the whitespace the browser sets as one space. A no-break space is not part of one.
_SPACES = re.compile(r"[ \t\r\f]+")

#: An HTML list's tags, opening or closing: the list's own, and each item's.
_LIST_TAG = re.compile(r"<(?P<closing>/?)(?P<name>ul|ol|li)\b", re.IGNORECASE)

#: The tags of an element the browser sets as a block, which part the words on either side of
#: them however close they sit. An inline element's parts nothing: ``re<b>read</b>`` is one word.
_BLOCK_TAG = re.compile(
    r"</?(?:address|article|aside|blockquote|caption|dd|details|dialog|div|dl|dt|fieldset"
    r"|figcaption|figure|footer|form|h[1-6]|header|hgroup|hr|main|nav|p|pre|section|summary"
    r"|table|td|th|tr)\b",
    re.IGNORECASE,
)

#: How a list's tag stands while the slide is read: this, then ``ul``, ``/li`` and the like, on a
#: line of its own.
_LIST_MARK = ""

#: A line break the author forced, and the character it stands as while tags are taken out. A
#: forced break shapes a headline, so the headline keeps it; elsewhere it only separates words. The
#: character is no space, so a heading's trim leaves a break at either end of it in place.
_BREAK_TAG = re.compile(r"<br\b[^>]*>", re.IGNORECASE)
_BREAK = "\ue000"
_EMPHASIS = re.compile(r"[*`~]+")

#: Inline code, which the slide shows as written: a ``<br>`` in backticks is text, and breaks no
#: line. Markdown closes a span on a run of as many backticks as opened it, within one paragraph.
_CODE_SPAN = re.compile(
    r"(?<!`)(?P<ticks>`+)(?!`)(?:(?!\n[ \t]*\n).)+?(?<!`)(?P=ticks)(?!`)", re.DOTALL
)

#: The characters a code span's angle brackets stand as while tags are read, so no reader of tags
#: takes one for a tag. ``_plain`` turns them back into what the span shows.
_SHOWN = str.maketrans("<>", "\ue001\ue002")
_UNSHOWN = str.maketrans("\ue001\ue002", "<>")

#: Where a slide's markup can set a size: a style attribute (Vue's bound one included), a style
#: block, and a class list. A size anywhere else — a sentence about CSS, a code block — is not one.
_STYLE_ATTRIBUTE = re.compile(r"\bstyle\s*=\s*(?:\"(?P<double>[^\"]*)\"|'(?P<single>[^']*)')")
_STYLE_BLOCK = re.compile(r"<style\b[^>]*>(?P<css>.*?)</style>", re.DOTALL | re.IGNORECASE)
_CLASS_ATTRIBUTE = re.compile(r"\bclass\s*=\s*(?:\"(?P<double>[^\"]*)\"|'(?P<single>[^']*)')")

#: A font size inside a style: the CSS property, or the camel-cased key a Vue style object uses.
_FONT_SIZE = re.compile(r"font-?size['\"]?\s*:\s*['\"]?(?P<value>[^;'\",}]+)", re.IGNORECASE)

#: An SVG text element's size as a presentation attribute, ``font-size="8"``. Unitless, it is in the
#: SVG's user units, which are canvas px when the SVG is drawn at the size it lands.
_SVG_FONT_SIZE = re.compile(
    r"\bfont-size\s*=\s*(?:\"(?P<double>[^\"]*)\"|'(?P<single>[^']*)')", re.IGNORECASE
)

#: A UnoCSS class that sets a font size: a named step of its scale, or an arbitrary value.
_TEXT_SIZE_CLASS = re.compile(r"^text-(?:xs|sm|base|lg|\d?xl|\[[^\]]+\])$")

#: An element's opening tag at the start of a line, which makes the block it opens one visual group.
#: Only a name opens one: a closing tag or a stray ``<`` in prose does not.
_ELEMENT = re.compile(r"^\s*<(?P<name>[A-Za-z][\w-]*)")

#: Any tag of a given element, opening or closing, wherever the author wrapped its attributes. A
#: quoted attribute may carry a ``>``, which is why quotes are skipped whole.
_TAG_OF = r"""<(?P<closing>/?){name}\b(?:[^>"']|"[^"]*"|'[^']*')*?(?P<empty>/?)>"""

#: The elements HTML never closes, so their opening tag is the whole of them.
_VOID = frozenset({"br", "hr", "img", "input", "source", "wbr"})

#: A run of a table, a picture alone on its line, and the slot marker a two-column layout splits on.
_TABLE_ROW = re.compile(r"^\s*\|")
_IMAGE_ALONE = re.compile(r"^\s*!\[[^\]]*\]\([^)]*\)\s*$")
_SLOT = re.compile(r"^\s*::[\w-]+::\s*$")

#: What a slide emphasises: a span in bold, either spelling, or a strong or highlighting element.
#: Italics are for terms and titles and are not counted, and neither is anything in inline code.
#: Markdown's own spellings open after a non-word character and close before one, so neither a
#: ``snake__case`` name nor a stray pair of stars across a paragraph break reads as one.
_EMPHASISED = re.compile(
    r"(?<![\w*])\*\*(?P<stars>[^*\s](?:(?!\n\s*\n)[^*])*?)\*\*(?![\w*])"
    r"|(?<!\w)__(?P<unders>[^_\s](?:(?!\n\s*\n)[^_])*?)__(?!\w)"
    r"|<(?P<tag>strong|b|mark)\b[^>]*>(?P<inner>.*?)</(?P=tag)\s*>",
    re.DOTALL | re.IGNORECASE,
)

#: The tags that emphasise, which are kept while every other tag is blanked out of the way.
_EMPHASIS_TAG = re.compile(r"</?(?:strong|b|mark)\b", re.IGNORECASE)
_INLINE_CODE = re.compile(r"`[^`]*`")

#: The line a code block is folded to while the slide's groups are counted: it is one group, and
#: nothing inside it is markup.
_CODE = "\x00code"

#: The elements that are not a group the eye lands on: a stylesheet and a script draw nothing, a
#: line break only spaces what does, and the footnotes cite rather than say (below).
_NOT_A_GROUP = frozenset({"style", "script", "br", "footnotes", "footnote"})

#: The theme's footnotes, which cite rather than say: attribution set at the floor, which the room
#: is not reading while the speaker talks. Their text is left out of what the slide says.
_FOOTNOTES = re.compile(
    r"""<(?P<name>Footnotes?)\b(?:[^>"']|"[^"]*"|'[^']*')*?(?:/>|>.*?</(?P=name)\s*>)""",
    re.DOTALL,
)

#: A callout, by the component the theme ships for one.
_CALLOUT = re.compile(r"<Callout\b")

#: The line of a slide's notes that states its time budget, as the canon asks for it to be written.
_TIME = re.compile(r"^\s*Time:[ \t]*(?P<budget>.+?)\s*$", re.MULTILINE)

#: An exception the author takes to one of the method's defaults on this slide: a line of the notes
#: opening ``Exception:``, then the rule's ID, then the reason, which is the part that matters.
_EXCEPTION = re.compile(
    r"^\s*Exception:[ \t]*`?(?P<rule>[a-z0-9-]+)`?[ \t:,—–-]*(?P<reason>.*?)\s*$", re.MULTILINE
)

#: A top-level frontmatter key the rules read, and its value up to a trailing comment. Read by line
#: rather than as YAML, for the reason the module gives for the split: Slidev does not require the
#: block to parse, so neither does this, and the keys asked for are scalars at column 0.
_KEY = re.compile(
    r"""^(?P<key>section|backup|layout|duration|src):[ \t]*"""
    r"""(?:(?P<quote>["'])(?P<quoted>.*?)(?P=quote)|(?P<plain>.*?))"""
    r"""[ \t]*(?:[ \t]\#.*)?$"""
)

#: One part of the range an import takes from a file, ``2``, ``4-`` or ``2-3``, as Slidev reads it.
_RANGE_PART = re.compile(r"^\s*(?P<start>\d+)\s*(?:(?P<dash>-)\s*(?P<end>\d*))?\s*$")

#: How YAML 1.1, which Slidev reads frontmatter with, spells a true boolean. A quoted value is a
#: string whatever it says, so the theme would not take it for one and neither does this.
_TRUE = frozenset({"true", "True", "TRUE"})


class DeckError(ValueError):
    """A deck that cannot be read as slides, though every file it names could be opened."""


@dataclass(frozen=True)
class Slide:
    """One slide, as the rules that are decided by script see it.

    ``number`` counts from 1, the way an author and a reviewer both count slides, so a finding can
    name a slide without anyone translating an index.
    """

    number: int
    #: The slide's first heading, its lines joined by newlines. A ``<br>`` the author wrote starts a
    #: line, so two in a row leave an empty one between.
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
    #: The visual groups the slide is built from, beneath its headline, each named by its kind: a
    #: ``paragraph``, a ``list``, a ``table``, an ``image``, ``code``, or the element a block of
    #: markup opens with. A block is counted at the top of the body, so what it wraps is part of it.
    groups: tuple[str, ...] = ()
    #: The text of every span the slide sets in bold or highlights, its headline's included.
    emphasis: tuple[str, ...] = ()
    #: How many callouts the slide carries, wherever in its markup they sit.
    callouts: int = 0
    #: The slot the deck is planned for, as its headmatter writes it. Only the first slide carries
    #: headmatter, so only it can say; ``None`` everywhere else.
    duration: str | None = None
    #: The time budget the slide's notes state, as written, or ``None`` where they state none.
    time: str | None = None
    #: The exceptions the notes take, as (rule ID, reason) pairs; a reason may be empty.
    exceptions: tuple[tuple[str, str], ...] = ()


def read_deck(path: str | Path) -> tuple[Slide, ...]:
    """The slides of a deck on disk, as Slidev shows them.

    A slide whose frontmatter names a ``src`` stands for the slides of the file it names, which are
    read in its place, the way Slidev's own loader reads them. The import's frontmatter overrides
    each imported slide's, and numbering runs on through them, so a finding names the slide the
    room sees. Unreadable files raise ``OSError`` for the caller to report, and a file that imports
    itself, directly or by way of another, raises ``DeckError``.
    """
    path = Path(path).resolve()
    return _numbered(_imported(path, path.parent, "", {}, ()))


def parse_deck(text: str) -> tuple[Slide, ...]:
    """The slides of a Slidev deck, in order. With no file to resolve it from, an import is read
    as the slide it is written as."""
    return _numbered(_parts(text))


def _numbered(parts: Iterable[tuple[dict[str, str], list[str]]]) -> tuple[Slide, ...]:
    return tuple(_slide(number, keys, lines) for number, (keys, lines) in enumerate(parts, start=1))


def _parts(text: str) -> Iterator[tuple[dict[str, str], list[str]]]:
    """Every slide of one file: the frontmatter keys the rules read, and its lines."""
    for frontmatter, lines in _split(text.replace("\r\n", "\n").split("\n")):
        yield _keys(frontmatter), lines


def _imported(
    path: Path,
    root: Path,
    wanted: str,
    override: dict[str, str],
    chain: tuple[Path, ...],
) -> Iterator[tuple[dict[str, str], list[str]]]:
    """The slides ``wanted`` of one file, each import in it read in its place.

    Slidev's rules, from its loader: a ``src`` starting with ``/`` is from the deck's folder, and
    any other from the file it is written in. An import's frontmatter, less its ``src``, overrides
    every slide it brings in, and an outer import overrides an inner one.
    """
    if path in chain:
        loop = " -> ".join(str(step) for step in (*chain[chain.index(path) :], path))
        raise DeckError(f"{path} imports itself: {loop}")
    parts = list(_parts(path.read_text(encoding="utf-8")))
    for index in _range(wanted, len(parts)):
        keys, lines = parts[index - 1]
        if not keys.get("src"):
            yield {**keys, **override}, lines
            continue
        target, _, inner = keys["src"].partition("#")
        found = root / target[1:] if target.startswith("/") else path.parent / target
        outer = {key: value for key, value in keys.items() if key != "src"}
        yield from _imported(found.resolve(), root, inner, {**outer, **override}, (*chain, path))


def _range(wanted: str, total: int) -> list[int]:
    """The slides of a file an import's range takes, numbered from 1, in order, each once."""
    if wanted.strip() in ("", "all", "*"):
        return list(range(1, total + 1))
    if wanted.strip() == "none":
        return []
    taken: set[int] = set()
    for part in re.split(r"[,;]", wanted):
        found = _RANGE_PART.match(part)
        if not found:
            raise DeckError(f"slide range {wanted!r}: {part!r} is not a number or a run of them")
        start = int(found.group("start"))
        end = int(found.group("end")) if found.group("end") else total
        taken.update(range(start, end + 1) if found.group("dash") else (start,))
    return sorted(index for index in taken if 1 <= index <= total)


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


def _slide(number: int, keys: dict[str, str], lines: Sequence[str]) -> Slide:
    body, notes = _body_and_notes(_without_code(lines))
    markup = "\n".join(body)
    # What the slide says, as opposed to what it cites.
    said = _FOOTNOTES.sub(_line_breaks, markup)
    time = _TIME.search(notes) if notes else None

    headline: str | None = None
    bullets: list[str] = []
    prose: list[str] = []
    paragraph: list[str] = []
    # Whether the line being read continues the bullet above it. Only a blank line, a heading or
    # the next bullet ends one, so where an author's editor wrapped a long bullet cannot decide
    # its word count — markdown's own lazy continuation, and the ceiling depends on it.
    continuing = False
    # The HTML lists open around the line being read, the innermost last. Each holds the bullet of
    # its open item, or None between items. Text inside an item is that item's own, whatever blank
    # lines or child lists come between, as the browser groups it.
    lists: list[int | None] = []

    for line in _without_tags(_BREAK_TAG.sub(_BREAK, _code_shown(said))).split("\n"):
        if line.startswith(_LIST_MARK):
            _flush(paragraph, prose)
            continuing = False
            _follow(line.removeprefix(_LIST_MARK), lists, bullets)
            continue
        # A slot marker is where a layout splits the slide, which is layout rather than words.
        line = "" if _SLOT.match(line) else line
        heading = _HEADING.match(line)
        bullet = _BULLET.match(line)

        if not line.strip() or heading or bullet:
            # Any of the three also ends the paragraph being gathered; a wrapped paragraph is
            # still one passage, so the line break inside it does not.
            _flush(paragraph, prose)
            continuing = False

        if heading:
            headline = headline or _headline(heading.group("text")) or None
        elif bullet:
            bullets.append(_plain(bullet.group("text")))
            continuing = True
        elif not line.strip():
            continue
        elif continuing:
            bullets[-1] = f"{bullets[-1]} {_plain(line)}".strip()
        elif (item := _open_item(lists)) is not None:
            bullets[item] = f"{bullets[item]} {_plain(line)}".strip()
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
        font_sizes=_font_sizes(markup),
        groups=_groups(lines),
        emphasis=_emphasis(said),
        callouts=len(_CALLOUT.findall(markup)),
        duration=keys.get("duration") or None,
        time=time.group("budget") if time else None,
        exceptions=tuple(
            (match.group("rule"), match.group("reason"))
            for match in _EXCEPTION.finditer(notes or "")
        ),
    )


def _without_tags(markup: str) -> str:
    """The slide with its tags taken out, a line break inside one kept as a line break.

    A tag the author wrapped over several lines is still one tag: its attributes are the
    component's, a figure's caption say, and not prose the room reads beside it. A list's tags each
    leave a mark on a line of their own. The reader follows the lists by those marks, and reads an
    HTML list the way it reads the same list in markdown.
    """
    return _TAG.sub(_tag_left, markup)


def _tag_left(match: re.Match[str]) -> str:
    """What a tag leaves behind: the line breaks it spanned, a list's tag as its mark, and a
    block's tag as a space between the words it parts."""
    breaks = _line_breaks(match)
    tag = _LIST_TAG.match(match.group())
    if tag:
        return f"{breaks}\n{_LIST_MARK}{tag.group('closing')}{tag.group('name').lower()}\n"
    if _BLOCK_TAG.match(match.group()):
        return f" {breaks}"
    return breaks


def _follow(tag: str, lists: list[int | None], bullets: list[str]) -> None:
    """Move the reader's place in the HTML lists past one of their tags.

    Each item opens a bullet, and its own closing tag or its list's closes it. An item outside any
    list is read as a list of its own.
    """
    if tag in {"ul", "ol"}:
        lists.append(None)
    elif tag in {"/ul", "/ol"}:
        if lists:
            lists.pop()
    elif tag == "li":
        bullets.append("")
        if lists:
            lists[-1] = len(bullets) - 1
        else:
            lists.append(len(bullets) - 1)
    elif lists:
        lists[-1] = None


def _open_item(lists: Sequence[int | None]) -> int | None:
    """The bullet of the innermost HTML list item open, or None outside every item."""
    return next((item for item in reversed(lists) if item is not None), None)


def _line_breaks(match: re.Match[str]) -> str:
    """What a match leaves behind: only the line breaks it spanned."""
    return "\n" * match.group().count("\n")


def _groups(lines: Sequence[str]) -> tuple[str, ...]:
    """Each block at the top of the slide's body, beneath its headline, named by its kind.

    A block is a run of lines between blank ones, or an element from its opening tag to the tag
    that closes it, blank lines and all. What is inside an element is not counted again: a click
    reveal wrapping a callout is one thing on the slide, and it is the thing the eye lands on.
    Within a run, a change of kind starts a new block, except that a line running on from a bullet
    is still that bullet's, as markdown's lazy continuation has it.
    """
    text = _COMMENT.sub("", "\n".join(_code_as_one_line(lines)))
    rows = text.split("\n")
    starts = [0]
    for row in rows:
        starts.append(starts[-1] + len(row) + 1)

    groups: list[str] = []
    headline = False
    block: str | None = None
    index = 0
    while index < len(rows):
        line = rows[index]
        element = _ELEMENT.match(line)
        heading = _HEADING.match(line)
        if not line.strip() or _SLOT.match(line):
            block = None
        elif element:
            name = element.group("name")
            closed = _element_end(text, starts[index] + element.start("name") - 1, name)
            if name.lower() not in _NOT_A_GROUP:
                groups.append(name)
            block = None
            # Resume on the line after the one the element closes on.
            while index + 1 < len(rows) and starts[index + 1] < closed:
                index += 1
        elif line == _CODE:
            groups.append("code")
            block = None
        elif heading and not headline:
            headline = True
            block = None
        else:
            kind = _block_kind(line, heading is not None)
            if block is None or (kind != block and not (block == "list" and kind == "paragraph")):
                groups.append(kind)
                block = kind
        index += 1
    return tuple(groups)


def _block_kind(line: str, heading: bool) -> str:
    """What kind of markdown block a line of the slide's body opens, or carries on."""
    if heading:
        return "heading"
    if _TABLE_ROW.match(line):
        return "table"
    if _BULLET.match(line):
        return "list"
    if _IMAGE_ALONE.match(line):
        return "image"
    return "paragraph"


def _element_end(text: str, opened: int, name: str) -> int:
    """Where the element opening at ``opened`` closes: the end of the tag that brings its depth back
    to nothing, or the end of the slide if the author never closed it."""
    depth = 0
    for tag in re.finditer(_TAG_OF.format(name=re.escape(name)), text[opened:]):
        if tag.group("closing"):
            depth -= 1
        elif not tag.group("empty") and name.lower() not in _VOID:
            depth += 1
        if depth <= 0:
            return opened + tag.end()
    return len(text)


def _code_as_one_line(lines: Sequence[str]) -> list[str]:
    """The slide with each code block folded to one line, which marks where it was."""
    kept: list[str] = []
    index = 0
    while index < len(lines):
        if _FENCE.match(lines[index].rstrip()):
            kept.append(_CODE)
            index = _fence_end(lines, index) + 1
            continue
        kept.append(lines[index])
        index += 1
    return kept


def _attributes_blanked(markup: str) -> str:
    """The slide with every tag but the emphasising ones blanked to spaces, so no attribute can be
    read as emphasis and a match still sits where it did."""
    return _TAG.sub(
        lambda tag: (
            tag.group() if _EMPHASIS_TAG.match(tag.group()) else re.sub(r"\S", " ", tag.group())
        ),
        markup,
    )


def _emphasis(markup: str) -> tuple[str, ...]:
    """The text of every span the slide emphasises, in the order it sets them."""
    return tuple(
        _plain(next(group for group in match.group("stars", "unders", "inner") if group))
        for match in _EMPHASISED.finditer(_INLINE_CODE.sub("", _attributes_blanked(markup)))
    )


def font_sizes(text: str, *, css: bool = False) -> tuple[str, ...]:
    """Every size a deck's own component or stylesheet sets, as ``Slide.font_sizes`` writes them.

    ``css`` reads the whole of ``text`` as a stylesheet; otherwise it is markup, a Vue component
    with its ``<style>`` block, its style attributes, its classes and any SVG it draws.
    """
    if css:
        return tuple(
            f"font-size: {size.group('value').strip()}" for size in _FONT_SIZE.finditer(text)
        )
    return _font_sizes(text)


def _font_sizes(body: str) -> tuple[str, ...]:
    """Every size the slide's markup sets, in the order it sets them."""
    found: list[tuple[int, str]] = []
    for attribute in _SVG_FONT_SIZE.finditer(body):
        value = (attribute.group("double") or attribute.group("single") or "").strip()
        # A bare number is user units; spelled with px, it is the same size said the CSS way.
        unit = "px" if re.fullmatch(r"\d*\.?\d+", value) else ""
        found.append((attribute.start(), f"font-size: {value}{unit}"))
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


def _headline(text: str) -> str:
    """The headline as the room receives it, each line the author's breaks set ending at a newline.

    A break starts a line, an empty one too when the next break follows it, as the browser sets
    them. A break at the very end only closes the last line. A headline of breaks alone is empty.
    """
    lines = [_plain(part) for part in text.split(_BREAK)]
    if len(lines) > 1 and not lines[-1]:
        lines.pop()
    return "\n".join(lines) if any(lines) else ""


def _code_shown(markup: str) -> str:
    """The markup with each inline code span's angle brackets standing as other characters."""
    return _CODE_SPAN.sub(lambda span: span.group().translate(_SHOWN), markup)


def _plain(text: str) -> str:
    """One line as the room receives it: no markup, no components, no URLs."""
    text = text.replace(_BREAK, " ")
    text = _IMAGE.sub("", text)
    text = _LINK.sub(lambda match: match.group("text"), text)
    text = _TAG.sub("", text)
    return _SPACES.sub(" ", _EMPHASIS.sub("", text).translate(_UNSHOWN)).strip()
