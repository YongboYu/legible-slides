"""Carry the repo's shared files into the built package.

Two things this package reads live outside it, because two other parts of the repo own them:
`docs/method.md` is the canon every threshold is quoted from, and `theme/assets/fonts/` is the
typeface the deck itself is set in. Reading them in place is what stops either from being copied
and drifting — but a wheel installed elsewhere has no repo to read, so the build carries them in.
Written from the authority itself on every build, so they are artifacts rather than second copies
anyone maintains.

The paths differ by target because a source distribution is where the wheel is built *from*: the
sdist carries each file at its own repo-relative path, which is exactly where a wheel built inside
that sdist then finds it.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from hatchling.builders.hooks.plugin.interface import BuildHookInterface

CANON = Path("docs") / "method.md"
FONTS = Path("theme") / "assets" / "fonts"

#: Where each one lands, per target: importable beside the module in a wheel, at its own
#: repo-relative path in an sdist.
DESTINATIONS = {
    "wheel": {CANON: Path("legible") / "method.md", FONTS: Path("legible") / "assets" / "fonts"},
    "sdist": {CANON: CANON, FONTS: FONTS},
}


class SharedFilesBuildHook(BuildHookInterface):
    PLUGIN_NAME = "custom"

    def initialize(self, version: str, build_data: dict[str, Any]) -> None:
        # An editable install imports from the checkout, which already has both in place.
        if version == "editable":
            return

        for source, destination in DESTINATIONS.get(self.target_name, {}).items():
            build_data["force_include"][str(self._locate(source))] = str(destination)

    def _locate(self, relative: Path) -> Path:
        """One shared file, from the repo root above this package or from an unpacked sdist."""
        root = Path(self.root)
        for candidate in (root.parent / relative, root / relative):
            if candidate.exists():
                return candidate
        raise FileNotFoundError(
            f"cannot find {root.parent / relative} to build the package around it"
        )
