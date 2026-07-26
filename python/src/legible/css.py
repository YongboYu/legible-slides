"""The palette as the deck's custom properties.

``docs/token-contract.md`` §5 fixes the mapping from role to property; this module performs it, and
is the only thing that does. Why Python and not the deck's own toolchain is settled by
``docs/slidev-reference-impl.md`` §5, along with what that buys and what it costs.

What it costs is the constraint this module is written under. The emitted stylesheet is committed
and diffed by CI, like a lockfile, so it has to be a function of its input alone: nothing here
varies with the clock or with the machine that ran the command, and the only thing that reaches the
file besides the palette's colours is the palette's own name.
"""

from __future__ import annotations

from legible.palette import Palette

#: Two spaces, the way the stylesheets beside it are written. A generated file that no one edits is
#: still a file people read in a diff.
_INDENT = "  "


def gen_css(palette: Palette) -> str:
    """The palette as a `:root` block: one custom property per role, in token-contract order."""
    properties = "\n".join(
        f"{_INDENT}--{role}: {colour};" for role, colour in palette.roles.items()
    )
    return f"{_banner(palette)}\n:root {{\n{properties}\n}}\n"


def _banner(palette: Palette) -> str:
    """Why this file must not be hand-edited, for whoever opens it intending to.

    It names the theme, never the path it was read from: a theme's name is part of what it is,
    while its path is the caller's business and would make one palette emit two different files.
    """
    return (
        f"/* Generated from the `{palette.name}` theme by `legible gen-css` — do not edit.\n"
        f" * Change the palette, regenerate, and commit the result; CI checks the two agree. */\n"
    )
