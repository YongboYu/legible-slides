"""Carry the canon into the built package.

`docs/method.md` is the single source of truth for every threshold the validator enforces, and
``legible.method`` reads it in place rather than keeping a copy. A wheel installed outside this
repo has no repo to read, so the build copies the canon in beside the module — written from the
authority itself on every build, so it cannot drift the way a committed copy would.

The path differs by target because a source distribution is where the wheel is built *from*: the
sdist carries the canon at `docs/method.md`, which is exactly where a wheel built inside that
sdist then finds it.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from hatchling.builders.hooks.plugin.interface import BuildHookInterface

CANON = Path("docs") / "method.md"

#: Where the canon lands, per target: importable beside the module in a wheel, and at its own
#: repo-relative path in an sdist.
DESTINATION = {"wheel": Path("legible") / "method.md", "sdist": CANON}


class CanonBuildHook(BuildHookInterface):
    PLUGIN_NAME = "custom"

    def initialize(self, version: str, build_data: dict[str, Any]) -> None:
        # An editable install imports from the checkout, which already has the canon in place.
        if version == "editable":
            return

        destination = DESTINATION.get(self.target_name)
        if destination is None:
            return

        build_data["force_include"][str(self._canon())] = str(destination)

    def _canon(self) -> Path:
        """The canon, found from the repo root above this package or from an unpacked sdist."""
        root = Path(self.root)
        for candidate in (root.parent / CANON, root / CANON):
            if candidate.is_file():
                return candidate
        raise FileNotFoundError(
            f"cannot find the canon at {root.parent / CANON} to build the package around it"
        )
