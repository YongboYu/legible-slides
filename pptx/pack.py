"""Pack the hand-authored parts under `src/` into `legible-master.pptx`.

A `.pptx` is a zip of XML parts, and every one of this proof's is written by hand in `src/` — the
master, the four layouts, the theme's twelve colour slots, the four slides. **Nothing here derives
any of them.** `docs/pptx-static-proof.md` §6 is deliberate about that: the mapping from a palette
to a tool's theme is the artifact that has to survive being rerun in Keynote and Google Slides,
neither of which can read a PowerPoint theme, so the mapping is documented and hand-set once rather
than generated. This script only puts the pieces in a container.

What it does add is the parts a text editor cannot hold. The typefaces and the figure are binary,
and they are **taken from where the rest of the repo already keeps them** rather than copied in
beside the XML:

    ppt/fonts/*.fntdata   theme/assets/fonts/*.ttf     — the same outlines the figures are drawn in
    ppt/media/image1.png  themes/logos/…               — the palette's own mark
    ppt/media/image2.png  deck/public/…                — the flagship's generated, validated figure

That is what keeps "figures are regenerated, never redrawn" true of this delivery too: regenerate
the chart with `deck/figures.py`, repack, and the slide is current. There is no second copy of the
data anywhere in the package.

Run it from this directory:

    python pack.py            # write legible-master.pptx
    python pack.py --check    # fail if the shipped file is not what src/ packs to

The packed bytes are a function of the inputs alone — fixed timestamps, fixed order, fixed
compression — so `--check` is a real comparison rather than a diff of zip metadata. The shipped
`.pptx` is committed like `theme/styles/tokens.css` is: a build artifact people download without
running anything, held to its source by a test.
"""

from __future__ import annotations

import argparse
import sys
import zipfile
from collections.abc import Sequence
from io import BytesIO
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent

#: The hand-authored half: every file under here is a part, at the same path inside the package.
SOURCE = HERE / "src"

#: Where the packed file ships.
PACKAGE = HERE / "legible-master.pptx"

#: The binary half, as ``part inside the package`` → ``file in this repo``. One copy of each, where
#: its own delivery already keeps it.
BINARY_PARTS = {
    "ppt/media/image1.png": "themes/logos/kuleuven-liris.png",
    "ppt/media/image2.png": "deck/public/redundant-deuteranomaly.png",
    # `.fntdata` is a whole TrueType file under the extension PowerPoint expects; the bytes are the
    # TTF's, unchanged. Which face fills which slot is declared in ppt/presentation.xml.
    "ppt/fonts/font1.fntdata": "theme/assets/fonts/Inter-Regular.ttf",
    "ppt/fonts/font2.fntdata": "theme/assets/fonts/Inter-Bold.ttf",
    "ppt/fonts/font3.fntdata": "theme/assets/fonts/JetBrainsMono-Regular.ttf",
}

#: The part an OPC reader looks for first. Everything else is sorted, so the archive's order is a
#: function of the part names rather than of the order a filesystem happened to walk them.
CONTENT_TYPES = "[Content_Types].xml"

#: The one timestamp in the archive, and it is not a clock. Zip's own epoch, so packing the same
#: sources twice on two machines gives the same bytes and `--check` compares content.
FIXED_TIMESTAMP = (1980, 1, 1, 0, 0, 0)

#: The exit codes, in the shape `legible gen-css --check` already has: 0 says the shipped file is
#: current, 1 says it is stale and blocks, and 2 says nothing was compared because the sources could
#: not be assembled — a file nobody packed makes no claim about being stale.
CURRENT, STALE, NOT_PACKED = 0, 1, 2


class PackError(RuntimeError):
    """The sources could not be assembled into a package."""


def parts() -> dict[str, bytes]:
    """Every part of the package, by the path it takes inside it."""
    authored = {
        str(path.relative_to(SOURCE).as_posix()): path.read_bytes()
        for path in SOURCE.rglob("*")
        if path.is_file()
    }
    binary = {name: (REPO / source).read_bytes() for name, source in BINARY_PARTS.items()}

    clash = sorted(authored.keys() & binary.keys())
    if clash:
        raise PackError(f"src/ already holds a part pack.py supplies: {', '.join(clash)}")

    return {**authored, **binary}


def pack(contents: dict[str, bytes]) -> bytes:
    """The parts, as the bytes of a `.pptx`."""
    if CONTENT_TYPES not in contents:
        raise PackError(f"src/ is missing {CONTENT_TYPES}, which is what names every part's type")
    ordered = [CONTENT_TYPES, *sorted(name for name in contents if name != CONTENT_TYPES)]

    buffer = BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as archive:
        for name in ordered:
            entry = zipfile.ZipInfo(name, FIXED_TIMESTAMP)
            entry.compress_type = zipfile.ZIP_DEFLATED
            entry.external_attr = 0o600 << 16
            archive.writestr(entry, contents[name])
    return buffer.getvalue()


def main(argv: Sequence[str] | None = None) -> int:
    """Write the package, or check the shipped one. Returns the process exit code."""
    cli = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    cli.add_argument(
        "--check",
        action="store_true",
        help="exit non-zero if the shipped .pptx is not what src/ packs to, and write nothing",
    )
    arguments = cli.parse_args(argv)

    try:
        contents = parts()
        packed = pack(contents)
    except (OSError, PackError) as error:
        print(f"pack.py: {error}", file=sys.stderr)
        return NOT_PACKED

    if arguments.check:
        shipped = PACKAGE.read_bytes() if PACKAGE.is_file() else None
        if shipped == packed:
            print(f"{PACKAGE.name} is current")
            return CURRENT
        print(
            f"{PACKAGE.name} is not what src/ packs to; run `python pack.py` and commit it",
            file=sys.stderr,
        )
        return STALE

    PACKAGE.write_bytes(packed)
    print(f"{PACKAGE} ({len(packed):,} bytes, {len(contents)} parts)")
    return CURRENT


if __name__ == "__main__":
    raise SystemExit(main())
