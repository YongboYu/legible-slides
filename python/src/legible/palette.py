"""Reading a theme file.

A theme is one JSON palette of named roles — the single source of truth a deck's CSS, the figure
helper and the CVD validator all read, so that nothing downstream hardcodes a colour and drifts.
The schema is fixed by ``docs/token-contract.md``; this module is its only reader.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path

HEX_COLOUR = re.compile(r"^#[0-9a-fA-F]{6}$")

SCALAR_ROLES = (
    # structural neutrals
    "ink",
    "neutral",
    "neutral-soft",
    "surface",
    "surface-alt",
    "hairline",
    # brand & accent
    "brand",
    "brand-strong",
    "accent",
    "accent-strong",
    # data-encoding anchors
    "reference",
    "muted",
)


class PaletteError(ValueError):
    """A theme file that does not satisfy the token contract."""


@dataclass(frozen=True)
class Palette:
    """A loaded theme: its identity, and every role flattened to one ordered mapping.

    ``roles`` holds the scalar roles in token-contract order followed by the series ramp expanded
    to ``series-1 … series-n`` — the same 1-indexed names the validator reports failures under and
    the CSS emitter turns into custom properties.
    """

    name: str
    description: str | None
    logo: str | None
    roles: dict[str, str]
    series_roles: tuple[str, ...]

    def __getitem__(self, role: str) -> str:
        return self.roles[role]


def _is_hex_colour(value: object) -> bool:
    return isinstance(value, str) and bool(HEX_COLOUR.match(value))


def load_palette(path: str | Path) -> Palette:
    """Load and check a theme file, returning its roles flattened."""
    path = Path(path)
    try:
        raw = json.loads(path.read_text())
    except json.JSONDecodeError as error:
        # A file that is not JSON is a theme this loader cannot honour, so it comes back as the
        # same error type as a missing role. What the file *is* is this module's business; whether
        # it could be read at all stays the caller's.
        raise PaletteError(f"{path}: not valid JSON: {error}") from error
    if not isinstance(raw, dict):
        raise PaletteError(f"{path}: a theme is a JSON object of roles, not {type(raw).__name__}")

    meta = raw.get("meta", {})
    if not isinstance(meta, dict):
        raise PaletteError(f"{path}: 'meta' must be an object, not {type(meta).__name__}")

    missing = [role for role in (*SCALAR_ROLES, "series") if role not in raw]
    if missing:
        raise PaletteError(f"{path}: missing required role(s): {', '.join(missing)}")

    unknown = [key for key in raw if key not in (*SCALAR_ROLES, "series", "meta")]
    if unknown:
        raise PaletteError(f"{path}: unknown role(s): {', '.join(unknown)}")

    series = raw["series"]
    if not isinstance(series, list):
        raise PaletteError(f"{path}: 'series' must be a list of hex colours, ordered")

    roles = {role: raw[role] for role in SCALAR_ROLES}
    series_roles = tuple(f"series-{i}" for i in range(1, len(series) + 1))
    roles.update(zip(series_roles, series, strict=True))

    malformed = [
        f"{role} = {value!r}" for role, value in roles.items() if not _is_hex_colour(value)
    ]
    if malformed:
        raise PaletteError(
            f"{path}: role(s) must be a six-digit hex colour like '#1b6fb0': "
            + "; ".join(malformed)
        )

    return Palette(
        name=meta.get("name", path.stem),
        description=meta.get("description"),
        logo=meta.get("logo"),
        roles=roles,
        series_roles=series_roles,
    )
