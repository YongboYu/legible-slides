"""The deck's typeface, handed to the plotting backend.

`fonts` is the rule, and the canon owns both the requirement and the reason behind it. What this
module adds is the posture: it does not fall back. It puts the bundled files in front of the
backend and checks that the backend now resolves the canon's text family to one of them; if it
cannot, it raises. A figure that would not match the deck is worth more as an error than as a
picture. See ``theme/assets/fonts/README.md`` for the bundle itself.

"In front of" is literal. A machine that already has the family installed is the quieter half of
the same problem: two releases of a typeface have different metrics, so one palette and one set of
data would render to different pixels on two machines. The bundled copy therefore outranks anything
installed locally, and the check afterwards is what proves it did.
"""

from __future__ import annotations

from pathlib import Path

from matplotlib import font_manager

from legible.method import FONT_TEXT


class FontError(RuntimeError):
    """The bundled typeface could not be put in front of the plotting backend."""


#: Where the bundle may live, in preference order — the same two-step ``legible.method`` uses for
#: the canon, for the same reason. In a checkout the fonts are the deck theme's, at the path
#: ``docs/slidev-reference-impl.md`` §5 fixes, so the figures and the slides are set from one copy
#: of the files. In a wheel there is no checkout, so the build carries them in beside the module.
_BUNDLE_CANDIDATES = (
    Path(__file__).resolve().parents[3] / "theme" / "assets" / "fonts",
    Path(__file__).resolve().parent / "assets" / "fonts",
)

#: The bundle this install registers from. Falls back to the checkout path so a failure names where
#: the typeface was expected.
BUNDLE = next(
    (path for path in _BUNDLE_CANDIDATES if path.is_dir()),
    _BUNDLE_CANDIDATES[0],
)

#: What has already been handed to the backend. ``addfont`` appends unconditionally, so a second
#: call would grow the font list without changing what it resolves to.
_registered: set[Path] = set()


def register(bundle: Path | None = None) -> tuple[Path, ...]:
    """Register the bundled typefaces with the plotting backend, and return the files.

    Idempotent, because every archetype calls it before it draws. Every TrueType file in the
    bundle goes in, not only the text family: the mono family the locator is set in lands in the
    same directory when the deck theme ships it, and registering by extension means it arrives
    without an edit here.

    Raises ``FontError`` if the bundle is empty or if the canon's text family is still not
    resolvable afterwards.
    """
    bundle = BUNDLE if bundle is None else Path(bundle)

    typefaces = tuple(sorted(bundle.glob("*.ttf")))
    if not typefaces:
        raise FontError(
            f"no TrueType file in {bundle}: the deck's typeface is not bundled here, which "
            f"`fonts` requires it to be"
        )

    added = [typeface for typeface in typefaces if typeface not in _registered]
    for typeface in added:
        font_manager.fontManager.addfont(str(typeface))
        _registered.add(typeface)
    if added:
        _put_bundle_first(bundle)

    _check_resolves_to(bundle)
    return typefaces


def _put_bundle_first(bundle: Path) -> None:
    """Move the bundle to the head of the backend's font list.

    The backend keeps the first best-scoring match, and a locally installed copy of the same
    family scores identically — so without this the machine's copy wins purely for having been
    found first. Reordering is what makes the resolution a property of this repo rather than of
    the box it ran on.

    Worth being plain about the cost: matplotlib's font list is process-wide, so other code in the
    same interpreter asking for this family will also get the bundled copy. Registering at all has
    that reach, and the alternative is figures whose metrics depend on the machine.

    ``addfont`` above has already dropped the backend's resolution cache, so nothing needs
    invalidating here.
    """
    fontlist = font_manager.fontManager.ttflist
    bundled = [entry for entry in fontlist if Path(entry.fname).parent == bundle]
    elsewhere = [entry for entry in fontlist if Path(entry.fname).parent != bundle]
    fontlist[:] = bundled + elsewhere


def _check_resolves_to(bundle: Path) -> None:
    """Confirm the backend now answers with the bundle, rather than with something like it.

    Asking for the family by name is the same question every piece of text in a figure asks, so
    this is the claim the figures actually depend on — not merely that the files were read.
    """
    try:
        resolved = Path(font_manager.findfont(FONT_TEXT, fallback_to_default=False))
    except ValueError as error:
        raise FontError(
            f"{bundle} carries no `{FONT_TEXT}`, the family `fonts` sets the deck in"
        ) from error

    if resolved.parent != bundle:
        raise FontError(
            f"`{FONT_TEXT}` resolved to {resolved}, outside the bundle at {bundle}: a figure set "
            f"in a machine-local copy is a figure that can differ from the deck"
        )
