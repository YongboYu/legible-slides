"""A slide's markdown, rendered to HTML the way Slidev renders it.

Slidev renders with markdown-it, which markdown-it-py ports to Python, set up with options and a
stack of plugins of its own. Most of the plugins change no word and no block a rule reads: they
highlight code, number footnotes, draw maths and the like. One changes what is a block, and so what
the deck reader takes for a paragraph, a passage or a visual group, so it is ported here: the
component plugin, ``@mdit-vue/plugin-component``.

- A line that opens with a tag HTML does not set inline, which is to say a component, opens a block
  of markup, even straight after a paragraph. CommonMark would have run it on as the paragraph's.
- A component opened and closed on one line is left raw, with no paragraph around it and its
  markdown unparsed.
- An attribute's name may open with ``@``, as Vue writes an event handler.

Ported from ``@slidev/cli`` 52.18 and ``@mdit-vue/plugin-component`` 3.0.2, the versions the deck
and the template build with. Its HTML block rule is markdown-it's own with the component kind added,
so the port follows markdown-it-py's ``html_block`` and reads alongside it.
"""

from __future__ import annotations

import re
from functools import cache

from markdown_it import MarkdownIt
from markdown_it.common.html_blocks import block_names
from markdown_it.rules_block import StateBlock
from markdown_it.rules_inline import StateInline

__all__ = ["INLINE_TAGS", "render"]

#: The tags the component plugin takes for HTML's inline elements, which are MDN's less the two Vue
#: reserves for itself. Any other tag is a block, a component included.
INLINE_TAGS = frozenset(
    {
        *("a", "abbr", "acronym", "audio", "b", "bdi", "bdo", "big", "br", "button", "canvas"),
        *("cite", "code", "data", "datalist", "del", "dfn", "em", "embed", "i", "iframe", "img"),
        *("input", "ins", "kbd", "label", "map", "mark", "meter", "noscript", "object", "output"),
        *("picture", "progress", "q", "ruby", "s", "samp", "script", "select", "small", "span"),
        *("strong", "sub", "sup", "svg", "textarea", "time", "u", "tt", "var", "video", "wbr"),
    }
)

#: An attribute as Vue writes one: CommonMark's, except that its name may open with ``@``.
_ATTRIBUTE = (
    r"""(?:\s+[a-zA-Z_:@][a-zA-Z0-9:._-]*(?:\s*=\s*(?:[^"'=<>`\x00-\x20]+|'[^']*'|"[^"]*"))?)"""
)
_OPEN_TAG = rf"<[A-Za-z][A-Za-z0-9\-]*{_ATTRIBUTE}*\s*/?>"
_CLOSE_TAG = r"</[A-Za-z][A-Za-z0-9\-]*\s*>"

#: Inline HTML: a tag, a comment, a processing instruction, a declaration or a CDATA section.
_INLINE_HTML = re.compile(
    rf"(?:{_OPEN_TAG}|{_CLOSE_TAG}|<!---->|<!--(?:-?[^>-])(?:-?[^-])*-->|<[?][\s\S]*?[?]>"
    r"|<![A-Z]+\s+[^>]*>|<!\[CDATA\[[\s\S]*?\]\]>)"
)

#: A component the author opened and closed on one line, by a self-closing tag or a pair.
_SELF_CLOSING = re.compile(rf"<[A-Za-z][A-Za-z0-9\-]*{_ATTRIBUTE}*\s*/>")
_OPEN_AND_CLOSE = re.compile(
    rf"<(?P<name>[A-Za-z][A-Za-z0-9\-]*){_ATTRIBUTE}*\s*>.*</(?P=name)\s*>"
)

_BLANK = re.compile(r"^$")

#: The kinds of HTML block, in the order they are tried: how the line opening one starts, the line
#: it closes on, and whether it may cut a paragraph short. They are CommonMark's, with the
#: component's added before the last.
_HTML_BLOCKS: tuple[tuple[re.Pattern[str], re.Pattern[str], bool], ...] = (
    (
        re.compile(r"^<(script|pre|style)(?=(\s|>|$))", re.IGNORECASE),
        re.compile(r"</(script|pre|style)>", re.IGNORECASE),
        True,
    ),
    (re.compile(r"^<!--"), re.compile(r"-->"), True),
    (re.compile(r"^<\?"), re.compile(r"\?>"), True),
    (re.compile(r"^<![A-Z]"), re.compile(r">"), True),
    (re.compile(r"^<!\[CDATA\["), re.compile(r"\]\]>"), True),
    (
        re.compile(rf"^</?({'|'.join(block_names)})(?=(\s|/?>|$))", re.IGNORECASE),
        _BLANK,
        True,
    ),
    (
        re.compile(
            rf"^</?(?!({'|'.join(sorted(INLINE_TAGS))})(?![\w-]))[A-Za-z][A-Za-z0-9\-]*"
            r"(?=(\s|/?>|$))"
        ),
        _BLANK,
        True,
    ),
    (re.compile(rf"^(?:{_OPEN_TAG}|{_CLOSE_TAG})\s*$"), _BLANK, False),
)
_COMPONENT = _HTML_BLOCKS[6]


def render(markdown: str) -> str:
    """The HTML Slidev hands the browser for a slide's markdown, as far as words and blocks go."""
    return _markdown().render(markdown)


@cache
def _markdown() -> MarkdownIt:
    """markdown-it as Slidev sets it up. The default preset is CommonMark with tables and
    strikethrough. Raw HTML is allowed, and the typographer is on (``--`` sets an en dash) with its
    quotes left straight. Slidev also turns a bare URL into a link, which changes no word the room
    reads, so that is left out."""
    markdown = MarkdownIt("js-default", {"html": True, "typographer": True, "quotes": "\"\"''"})
    markdown.block.ruler.at(
        "html_block", _html_block, {"alt": ["paragraph", "reference", "blockquote"]}
    )
    markdown.inline.ruler.at("html_inline", _html_inline)
    return markdown


def _html_block(state: StateBlock, start: int, end: int, silent: bool) -> bool:
    """markdown-it's HTML block, as the component plugin rewrites it."""
    position = state.bMarks[start] + state.tShift[start]
    if state.is_code_block(start) or not state.md.options.get("html"):
        return False
    if state.src[position : position + 1] != "<":
        return False
    line = state.src[position : state.eMarks[start]]
    kind = next((kind for kind in _HTML_BLOCKS if kind[0].search(line)), None)
    if kind is None:
        return False
    if silent:
        return kind[2]

    whole = (
        (_SELF_CLOSING.match(line) or _OPEN_AND_CLOSE.match(line)) if kind is _COMPONENT else None
    )
    if whole:
        state.line = start + 1
        token = state.push("html_inline", "", 0)
        token.content = whole.group()
        token.map = [start, state.line]
        token = state.push("inline", "", 0)
        token.content = line[whole.end() :]
        token.map = [start, state.line]
        token.children = []
        return True

    following = start + 1
    if not kind[1].search(line):
        while following < end:
            if state.sCount[following] < state.blkIndent:
                break
            begun = state.bMarks[following] + state.tShift[following]
            text = state.src[begun : state.eMarks[following]]
            if kind[1].search(text):
                if text:
                    following += 1
                break
            following += 1

    state.line = following
    token = state.push("html_block", "", 0)
    token.map = [start, following]
    token.content = state.getLines(start, following, state.blkIndent, True)
    return True


def _html_inline(state: StateInline, silent: bool) -> bool:
    """markdown-it's inline HTML, as the component plugin rewrites it."""
    position = state.pos
    if not state.md.options.get("html"):
        return False
    if state.src[position] != "<" or position + 2 >= state.posMax:
        return False
    second = state.src[position + 1]
    if second not in "!?/" and not ("a" <= second.lower() <= "z"):
        return False
    tag = _INLINE_HTML.match(state.src, position)
    if not tag:
        return False
    if not silent:
        token = state.push("html_inline", "", 0)
        token.content = tag.group()
    state.pos = tag.end()
    return True
