"""Colour-vision simulation and perceptual distance.

One implementation, one pinned dependency. The validator measures with these; the figure helper
renders its "under deuteranopia" panel with the *same* ``simulate`` rather than a second
implementation that could disagree with the numbers a theme was validated against.

`separation-floor` names the simulation, the conditions, the severity and the distance space;
they arrive here from ``legible.method``, and ``docs/cvd-validator-contract.md`` §2 records why
``colorspacious`` implements all of it in one dependency.
"""

from __future__ import annotations

import warnings
from collections.abc import Sequence

from legible.method import CVD_CONDITIONS, CVD_TYPES, DELTA_E_METRIC, SEVERITY

# A docstring in colorspacious 1.1.2, the release pinned, holds an escape Python 3.12 calls invalid.
# Python warns when it compiles the module, which happens on an author's first check after
# stamping, so the warning would print above their report.
with warnings.catch_warnings():
    warnings.simplefilter("ignore", SyntaxWarning)
    from colorspacious import cspace_convert, deltaE

__all__ = [
    "CVD_CONDITIONS",
    "CVD_TYPES",
    "GRAYSCALE",
    "NORMAL",
    "delta_e",
    "hex_to_rgb1",
    "rgb1_to_hex",
    "simulate",
]

RGB1 = Sequence[float]

#: Normal vision, as the canon names it.
NORMAL = "normal"

#: Not a CVD type — a projector in black and white, a photocopied handout.
GRAYSCALE = "grayscale"


def hex_to_rgb1(value: str) -> tuple[float, float, float]:
    """``'#1b6fb0'`` → sRGB1 floats in [0, 1]."""
    value = value.lstrip("#")
    return tuple(int(value[i : i + 2], 16) / 255 for i in (0, 2, 4))


def rgb1_to_hex(colour: RGB1) -> str:
    """sRGB1 floats → ``'#1b6fb0'``, clipped to what a display can show.

    Simulating a colour can land it outside the gamut, and a figure has to paint *something*.
    Clipping here is what the screen would do anyway, and doing it in one place means no caller
    invents its own answer to the same question.
    """
    return "#" + "".join(
        f"{int(round(min(max(channel, 0.0), 1.0) * 255)):02x}" for channel in colour
    )


def simulate(colours: Sequence[RGB1], condition: str) -> list[RGB1]:
    """Render sRGB1 colours as one condition sees them.

    ``condition`` is ``"normal"``, one of ``CVD_TYPES``, or ``GRAYSCALE`` — the one place that
    branch is made, so no caller has to know which conditions need simulating.
    """
    if condition == NORMAL:
        return list(colours)

    if condition == GRAYSCALE:
        # Grayscale is not a Machado CVD type, so it is modelled directly: drop chroma in a
        # uniform appearance space, keeping lightness and hue.
        out = []
        for colour in colours:
            J, _, h = cspace_convert(colour, "sRGB1", "JCh")
            out.append(cspace_convert([J, 0.0, h], "JCh", "sRGB1"))
        return out

    if condition not in CVD_TYPES:
        raise ValueError(f"unknown condition {condition!r}")

    space = {"name": "sRGB1+CVD", "cvd_type": condition, "severity": SEVERITY}
    return [cspace_convert(colour, space, "sRGB1") for colour in colours]


def delta_e(a: RGB1, b: RGB1) -> float:
    """The distance between two sRGB1 colours, in the canon's uniform space."""
    return float(deltaE(a, b, input_space="sRGB1", uniform_space=DELTA_E_METRIC))
