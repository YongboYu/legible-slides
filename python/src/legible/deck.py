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

A slide's body is read the way Slidev renders it. markdown-it, the parser Slidev renders with, turns
the markdown into the HTML the browser is handed, raw HTML and all (``slidev_markdown``), and the
standard library's HTML parser builds that into a tree. What is a bullet, a paragraph, a code span
or a tag is then the renderer's answer, read off the tree, rather than a regex's guess at it.

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
from dataclasses import dataclass, field
from html.parser import HTMLParser
from pathlib import Path

from legible.slidev_markdown import INLINE_TAGS, render

__all__ = ["DeckError", "Slide", "font_sizes", "parse_deck", "read_deck"]

#: A slide separator: three dashes alone on a line. Four or more is a horizontal rule, which is
#: what Slidev's own parser makes of it too.
_SEPARATOR = re.compile(r"^---\s*$")

_FENCE = re.compile(r"^\s*(```|~~~)")

#: A whole HTML comment. Slidev reads the last one on a slide as the speaker notes.
_COMMENT = re.compile(r"<!--(?P<text>.*?)-->", re.DOTALL)

#: A run of the whitespace the browser sets as one space. A no-break space is not part of one.
_SPACES = re.compile(r"[ \t\n\r\f]+")

#: An element's name as the author wrote it. The HTML parser lowercases every name, and a component
#: is told apart by its capitals: ``Figure`` is the theme's, ``figure`` the browser's.
_TAG_NAME = re.compile(r"<(?P<name>[A-Za-z][^\t\n\r\f />\x00]*)")

_HEADINGS = frozenset({"h1", "h2", "h3", "h4", "h5", "h6"})

#: The elements whose text the room does not read off the slide: a stylesheet and a script draw no
#: words, and a code block is evidence that no rule decided by script reads. The theme's footnotes
#: cite rather than say: attribution set at the floor, which the room is not reading while the
#: speaker talks.
_UNSAID = frozenset({"style", "script", "pre", "footnotes", "footnote"})

#: A font size inside a style: the CSS property, or the camel-cased key a Vue style object uses.
_FONT_SIZE = re.compile(r"font-?size['\"]?\s*:\s*['\"]?(?P<value>[^;'\",}]+)", re.IGNORECASE)

#: A UnoCSS class that sets a font size: a named step of its scale, or an arbitrary value.
_TEXT_SIZE_CLASS = re.compile(r"^text-(?:xs|sm|base|lg|\d?xl|\[[^\]]+\])$")

#: The elements HTML never closes, so their opening tag is the whole of them.
_VOID = frozenset(
    {
        *("area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source"),
        *("track", "wbr"),
    }
)

#: The elements that emphasise: bold, as markdown writes it or as HTML does, and a highlight.
#: Italics are for terms and titles and are not counted.
_EMPHASISING = frozenset({"strong", "b", "mark"})

#: The elements that are not a group the eye lands on: a stylesheet and a script draw nothing, a
#: line break or a rule only spaces what does, and the footnotes cite rather than say (above).
_NOT_A_GROUP = frozenset({"style", "script", "br", "hr", "footnotes", "footnote"})

#: A callout, by the component the theme ships for one.
_CALLOUT = "Callout"

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
    #: markup opens with. A block is counted at the top of the body, so what it wraps is part of it,
    #: and each of a layout's slots is counted as the top of the body it holds.
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
    notes = _notes(lines)
    time = _TIME.search(notes) if notes else None
    tree = _rendered("\n".join(lines))
    words = _Words(tree)
    return Slide(
        number=number,
        headline=words.headline,
        bullets=words.bullets,
        prose=words.prose,
        notes=notes,
        section=keys.get("section"),
        backup=keys.get("backup") in _TRUE,
        layout=keys.get("layout") or None,
        font_sizes=_font_sizes(tree),
        groups=_groups(tree),
        emphasis=tuple(_emphasis(tree)),
        callouts=sum(1 for element in _elements(tree) if element.name == _CALLOUT),
        duration=keys.get("duration") or None,
        time=time.group("budget") if time else None,
        exceptions=tuple(
            (match.group("rule"), match.group("reason"))
            for match in _EXCEPTION.finditer(notes or "")
        ),
    )


@dataclass
class _Element:
    """One element of a rendered slide: its name as the author wrote it, its attributes in the
    order they were written, and what it holds, text and elements in turn."""

    name: str
    attributes: list[tuple[str, str | None]]
    children: list[_Element | str] = field(default_factory=list)

    @property
    def tag(self) -> str:
        """The name as HTML compares it, which is without regard to case."""
        return self.name.lower()


class _Tree(HTMLParser):
    """HTML built into a tree of elements, as forgiving of it as a browser.

    An element HTML never closes holds nothing, a closing tag closes the innermost element it names
    and everything opened inside that, a closing tag that names no open element is dropped, and an
    element still open at the end is closed there. A comment is nothing on the slide.
    """

    def __init__(self) -> None:
        super().__init__()
        self.root = _Element("", [])
        self._open = [self.root]

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        written = _TAG_NAME.match(self.get_starttag_text() or "")
        element = _Element(written.group("name") if written else tag, attrs)
        self._open[-1].children.append(element)
        if tag not in _VOID:
            self._open.append(element)

    def handle_endtag(self, tag: str) -> None:
        for depth in range(len(self._open) - 1, 0, -1):
            if self._open[depth].tag == tag:
                del self._open[depth:]
                return

    def handle_data(self, data: str) -> None:
        self._open[-1].children.append(data)


def _rendered(markdown: str) -> _Element:
    """The slide as the browser is handed it: its markdown rendered as Slidev renders it, raw HTML
    and all, and built into a tree. What is a tag, a paragraph or a code span is the renderer's
    answer, and markdown's text arrives escaped, so nothing it left as text is read as a tag."""
    return _parsed(render(markdown))


def _parsed(html: str) -> _Element:
    """HTML as a tree."""
    tree = _Tree()
    tree.feed(html)
    tree.close()
    return tree.root


class _Words:
    """What a slide says, read off its rendered tree: its headline, its bullets and its prose.

    Text belongs to the innermost of three things around it. A heading's is the headline, if it is
    the slide's first heading with words in it, and is nobody's otherwise. A list item's is that
    item's bullet, whatever blocks and blank lines come between its parts, since the browser sets
    them all inside it; a list inside the item holds bullets of its own. Any other text is prose,
    one passage to a block.

    A block is any element HTML does not set inline, and it parts the words on either side of it
    however close they sit, where an inline one parts nothing: ``re<b>read</b>`` is one word. A
    component is a block, as Slidev's renderer reads one, since what it draws is its own business.
    """

    def __init__(self, tree: _Element) -> None:
        self.headline: str | None = None
        self._items: list[list[str]] = []
        self._passages: list[str] = []
        self._passage: list[str] = []
        self._read(tree, self._passage)
        self._end(self._passage)
        self.bullets = tuple(text for item in self._items if (text := _collapsed("".join(item))))
        self.prose = tuple(self._passages)

    def _read(self, element: _Element, into: list[str]) -> None:
        for child in element.children:
            if isinstance(child, str):
                into.append(child)
            elif child.tag in _UNSAID:
                continue
            elif child.tag in _HEADINGS:
                self._end(into)
                self.headline = self.headline or _headline(child)
            elif child.tag == "li":
                self._end(into)
                self._items.append(item := [])
                self._read(child, item)
            elif child.tag == "br":
                into.append(" ")
            elif child.tag in INLINE_TAGS:
                self._read(child, into)
            else:
                self._end(into)
                into.append(" ")
                self._read(child, into)
                into.append(" ")
                self._end(into)

    def _end(self, into: list[str]) -> None:
        """End the passage being gathered, if ``into`` is a passage rather than a bullet."""
        if into is not self._passage:
            return
        passage = _collapsed("".join(into))
        into.clear()
        if passage:
            self._passages.append(passage)


def _headline(heading: _Element) -> str | None:
    """The headline as the room receives it, each line the author's breaks set ending at a newline.

    A break starts a line, an empty one too when the next break follows it, as the browser sets
    them. A break at the very end only closes the last line. A headline of breaks alone is none.
    """
    lines = [_collapsed("".join(line)) for line in _lines(heading, [[]])]
    if len(lines) > 1 and not lines[-1]:
        lines.pop()
    return "\n".join(lines) if any(lines) else None


def _lines(element: _Element, lines: list[list[str]]) -> list[list[str]]:
    """An element's text, in the lines its ``<br>`` tags start."""
    for child in element.children:
        if isinstance(child, str):
            lines[-1].append(child)
        elif child.tag == "br":
            lines.append([])
        elif child.tag not in _UNSAID:
            _lines(child, lines)
    return lines


def _text(element: _Element) -> str:
    """An element's text on one line, a break in it a space between words."""
    return _collapsed(" ".join("".join(line) for line in _lines(element, [[]])))


def _collapsed(text: str) -> str:
    """Text as the browser sets it: each run of whitespace one space, and none at either end."""
    return _SPACES.sub(" ", text).strip()


def _groups(tree: _Element) -> tuple[str, ...]:
    """Each block at the top of the slide's body, beneath its headline, named by its kind.

    What is inside a block is not counted again: a click reveal wrapping a callout is one thing on
    the slide, and it is the thing the eye lands on. The slide's first heading is its headline,
    which the groups sit beneath rather than one of them.
    """
    groups: list[str] = []
    headline = False
    for block in _top(tree):
        kind = _kind(block)
        if kind == "heading" and not headline:
            headline = True
        elif kind:
            groups.append(kind)
    return tuple(groups)


def _top(element: _Element) -> Iterator[_Element]:
    """The blocks at the top of a slide's body. A slot's template draws nothing of its own, so each
    of a layout's slots is looked through to the top of the body it holds. Text there is what a
    component on a line of its own leaves after it, and is not a block."""
    for child in element.children:
        if isinstance(child, str):
            continue
        if child.tag == "template":
            yield from _top(child)
        else:
            yield child


def _kind(block: _Element) -> str | None:
    """What kind of group a block is, or None for one the eye does not land on."""
    if block.tag in _NOT_A_GROUP:
        return None
    if block.tag in _HEADINGS:
        return "heading"
    if block.tag in {"ul", "ol"}:
        return "list"
    if block.tag == "pre":
        return "code"
    if block.tag == "img":
        return "image"
    if block.tag == "p":
        held = [child for child in block.children if not isinstance(child, str) or child.strip()]
        alone = len(held) == 1 and isinstance(held[0], _Element) and held[0].tag == "img"
        return "image" if alone else "paragraph"
    return block.name


def _emphasis(element: _Element) -> Iterator[str]:
    """The text of every span the slide emphasises, in the order it sets them. A span inside one is
    part of it, and is not counted again."""
    for child in element.children:
        if isinstance(child, str) or child.tag in _UNSAID:
            continue
        if child.tag in _EMPHASISING:
            if text := _text(child):
                yield text
        else:
            yield from _emphasis(child)


def _elements(element: _Element) -> Iterator[_Element]:
    """Every element inside this one, in the order they open."""
    for child in element.children:
        if isinstance(child, _Element):
            yield child
            yield from _elements(child)


def font_sizes(text: str, *, css: bool = False) -> tuple[str, ...]:
    """Every size a deck's own component or stylesheet sets, as ``Slide.font_sizes`` writes them.

    ``css`` reads the whole of ``text`` as a stylesheet; otherwise it is markup, a Vue component
    with its ``<style>`` block, its style attributes, its classes and any SVG it draws.
    """
    return tuple(_css_sizes(text)) if css else _font_sizes(_parsed(text))


def _font_sizes(tree: _Element) -> tuple[str, ...]:
    """Every size the markup sets, in the order it sets them: in an attribute, a style attribute
    (Vue's bound one included), a class list or a style block. A size anywhere else, in a sentence
    about CSS or a code block, is text and sets nothing."""
    sizes: list[str] = []
    for element in _elements(tree):
        for name, value in element.attributes:
            name = name.removeprefix("v-bind").removeprefix(":")
            if value is None:
                continue
            if name == "font-size":
                # A bare number is user units; with px, it is the same size said the CSS way.
                unit = "px" if re.fullmatch(r"\d*\.?\d+", value.strip()) else ""
                sizes.append(f"font-size: {value.strip()}{unit}")
            elif name == "style":
                sizes.extend(_css_sizes(value))
            elif name == "class":
                sizes.extend(word for word in value.split() if _TEXT_SIZE_CLASS.match(word))
        if element.tag == "style":
            sizes.extend(_css_sizes("".join(c for c in element.children if isinstance(c, str))))
    return tuple(sizes)


def _css_sizes(css: str) -> Iterator[str]:
    """Every size a stylesheet or a style attribute sets."""
    for size in _FONT_SIZE.finditer(css):
        yield f"font-size: {size.group('value').strip()}"


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


def _notes(lines: Sequence[str]) -> str | None:
    """The slide's speaker notes: its last comment, a code block's left out."""
    comments = _COMMENT.findall("\n".join(_without_code(lines)))
    return (comments[-1].strip() or None) if comments else None
