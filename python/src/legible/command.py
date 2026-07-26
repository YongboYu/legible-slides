"""`legible` — the commands an author of a deck runs.

Two console scripts, on purpose. `cvd-validate` stands alone because it is the artifact external
theme authors are pointed at, and a stranger's palette is all it needs. Everything else this
package does acts on a *deck* — emitting its tokens today, drawing its figures and linting its
slides in due course — and hangs off this one command instead.

Each subcommand stays a thin shell over the package's public functions: what a stylesheet contains
is ``gen_css``' business, and what follows here is only where the bytes go and what the exit code
says about them.
"""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path

from legible.css import gen_css
from legible.palette import PaletteError, load_palette

#: 0 says the stylesheet is current — just written, or already matching its palette. 1 says it is
#: stale, the shape `ruff format --check` has and the one the CI gate keys on. 2 keeps the meaning
#: it has in ``cli`` and in argparse: nothing was measured, because the arguments or the theme
#: behind them could not be read, and a file nobody generated makes no claim about being stale.
CURRENT, STALE, NOT_GENERATED = 0, 1, 2


def main(argv: Sequence[str] | None = None) -> int:
    """Run one subcommand. Returns the process exit code."""
    args = _parser().parse_args(argv)
    return args.run(args)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="legible",
        description="Build-time commands for a deck: the palette's tokens, and what follows them.",
    )
    subcommands = parser.add_subparsers(metavar="COMMAND", required=True)

    gen_css_parser = subcommands.add_parser(
        "gen-css",
        help="emit a theme's colours as CSS custom properties",
        description=(
            "Emit a theme's colours as the deck's CSS custom properties. The result is committed "
            "and regenerated when the palette changes, like a lockfile, so the deck build imports "
            "it rather than invoking Python."
        ),
    )
    gen_css_parser.add_argument("theme", metavar="THEME", type=Path, help="the theme JSON file")
    gen_css_parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="write the stylesheet here instead of to stdout, creating its directory if needed",
    )
    gen_css_parser.add_argument(
        "--check",
        action="store_true",
        help=(
            "write nothing; exit 1 if the file at --output is not what this theme emits today. "
            "This is the CI gate against a committed stylesheet going stale."
        ),
    )
    gen_css_parser.set_defaults(run=_gen_css, parser=gen_css_parser)

    return parser


def _gen_css(args: argparse.Namespace) -> int:
    if args.check and args.output is None:
        args.parser.error("--check needs --output: a stylesheet on stdout is nothing to compare")

    try:
        palette = load_palette(args.theme)
    except (OSError, PaletteError) as error:
        print(f"legible gen-css: {error}", file=sys.stderr)
        return NOT_GENERATED

    stylesheet = gen_css(palette)

    if args.output is None:
        print(stylesheet, end="")
        return CURRENT

    if args.check:
        return _report_if_stale(stylesheet, args.output, args.theme)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    # Newlines fixed rather than translated: the file is committed, and a diff that says only
    # "generated on Windows" is the one thing a lockfile must never produce.
    args.output.write_text(stylesheet, encoding="utf-8", newline="\n")
    print(f"legible gen-css: wrote {args.output}")
    return CURRENT


def _report_if_stale(stylesheet: str, output: Path, theme: Path) -> int:
    """Compare, and never write — a gate that repairs what it measures can only ever pass."""
    # Reading translates newlines back, so a checkout that materialised CRLF still compares equal:
    # this gate is a claim about the palette, not about how the file reached the disk.
    committed = output.read_text(encoding="utf-8") if output.is_file() else None
    if committed == stylesheet:
        print(f"legible gen-css: {output} is current")
        return CURRENT

    state = "is stale" if committed is not None else "has not been generated"
    print(
        f"legible gen-css: {output} {state}. Regenerate it and commit the result:\n"
        f"    legible gen-css {theme} --output {output}",
        file=sys.stderr,
    )
    return STALE
