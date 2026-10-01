"""The accessibility floor, as something anyone can run.

``validate()`` takes a palette and returns a verdict: which pair of roles is too close together,
and under which vision. The rule is `separation-floor`, and the canon owns its floor, conditions
and grayscale carve-out; ``docs/cvd-validator-contract.md`` fixes what this module adds — the two
co-occurrence groups and the shape of the report.

It also reads the pairings `accent-is-attention` names in WCAG contrast, because attention that
cannot be read is a palette that fails as surely as two series that cannot be told apart. The canon
owns the pairings and the ratio they clear.
"""

from __future__ import annotations

import itertools
from collections.abc import Iterator, Sequence
from dataclasses import dataclass
from typing import NamedTuple

from legible.contrast import contrast_ratio
from legible.cvd import CVD_CONDITIONS, GRAYSCALE, delta_e, hex_to_rgb1, simulate
from legible.method import ATTENTION_CONTRAST_MIN, ATTENTION_CONTRAST_PAIRS, DELTA_E_FLOOR
from legible.palette import Palette

#: Decimal places every ΔE is measured, reported and compared at. One precision throughout, so the
#: verdict can never disagree with the figure printed beside it: a palette published as sitting on
#: the floor passes the floor. See docs/cvd-validator-contract.md §3.
PRECISION = 1

#: Decimal places a contrast ratio is measured, reported and compared at — the same one-precision
#: rule as ΔE, at the precision WCAG ratios are conventionally quoted in.
CONTRAST_PRECISION = 2


class Failure(NamedTuple):
    """A pair of roles closer than the threshold under one hard condition."""

    condition: str
    role_a: str
    role_b: str
    delta_e: float


class GrayscaleWarning(NamedTuple):
    """A pair of roles that collapses in grayscale. Advisory — never a failure."""

    role_a: str
    role_b: str
    delta_e: float


class ContrastPair(NamedTuple):
    """One pairing the canon names, and the WCAG contrast ratio it achieves."""

    foreground: str
    background: str
    ratio: float


@dataclass(frozen=True)
class GroupReport:
    """One co-occurrence group's achieved minima."""

    roles: tuple[str, ...]
    min_delta_e: dict[str, float]
    grayscale_min: float


@dataclass(frozen=True)
class Report:
    """The verdict, with every ΔE at ``PRECISION`` decimal places."""

    passed: bool
    threshold: float
    groups: dict[str, GroupReport]
    min_delta_e: dict[str, float]
    grayscale_min: float
    failures: tuple[Failure, ...] = ()
    warnings: tuple[GrayscaleWarning, ...] = ()
    contrast_threshold: float = ATTENTION_CONTRAST_MIN
    contrast: tuple[ContrastPair, ...] = ()
    contrast_failures: tuple[ContrastPair, ...] = ()


class _Pair(NamedTuple):
    role_a: str
    role_b: str
    delta_e: float


def validate(palette: Palette, threshold: float = DELTA_E_FLOOR) -> Report:
    """Check a palette's data-encoding roles for perceptual separation.

    Passes if every pair within each co-occurrence group stays at or above ``threshold`` under
    every condition the canon names, and every attention pairing clears its contrast ratio.
    Grayscale collisions come back as warnings instead: the method already covers them by never
    letting colour be the sole channel.
    """
    failures: list[Failure] = []
    warnings: list[GrayscaleWarning] = []
    group_reports: dict[str, GroupReport] = {}

    for key, roles in _groups(palette).items():
        colours = [hex_to_rgb1(palette[role]) for role in roles]

        minima: dict[str, float] = {}
        for condition in CVD_CONDITIONS:
            pairs = list(_pairs(roles, simulate(colours, condition)))
            minima[condition] = min(pair.delta_e for pair in pairs)
            failures.extend(Failure(condition, *pair) for pair in pairs if pair.delta_e < threshold)

        grayscale = list(_pairs(roles, simulate(colours, GRAYSCALE)))
        warnings.extend(GrayscaleWarning(*pair) for pair in grayscale if pair.delta_e < threshold)

        group_reports[key] = GroupReport(
            roles=roles,
            min_delta_e=minima,
            grayscale_min=min(pair.delta_e for pair in grayscale),
        )

    contrast = tuple(
        ContrastPair(
            foreground,
            background,
            round(contrast_ratio(palette[foreground], palette[background]), CONTRAST_PRECISION),
        )
        for foreground, background in ATTENTION_CONTRAST_PAIRS
    )
    contrast_failures = tuple(pair for pair in contrast if pair.ratio < ATTENTION_CONTRAST_MIN)

    return Report(
        passed=not failures and not contrast_failures,
        threshold=threshold,
        groups=group_reports,
        min_delta_e={
            condition: min(group.min_delta_e[condition] for group in group_reports.values())
            for condition in CVD_CONDITIONS
        },
        grayscale_min=min(group.grayscale_min for group in group_reports.values()),
        # The anchors sit in both groups, so an anchor pair would otherwise be reported twice.
        failures=tuple(dict.fromkeys(failures)),
        warnings=tuple(dict.fromkeys(warnings)),
        contrast_threshold=ATTENTION_CONTRAST_MIN,
        contrast=contrast,
        contrast_failures=contrast_failures,
    )


def _groups(palette: Palette) -> dict[str, tuple[str, ...]]:
    """The two sets of roles that can share one chart axis.

    G1 is the per-series ramp, G2 the two-group highlight. They live on mutually exclusive slides,
    so ``brand`` and ``series`` are never compared with each other — requiring them to be separable
    is wrong on the merits. The roles that appear in *every* chart anchor both groups.

    Each group is formed over the roles the palette actually has, so a theme with a shorter or
    longer ramp is checked over exactly the series it ships.
    """
    return {
        "G1": ("reference", "muted", *palette.series_roles),
        "G2": ("reference", "muted", "brand"),
    }


def _pairs(roles: Sequence[str], colours: Sequence[Sequence[float]]) -> Iterator[_Pair]:
    """Every pair of roles in one group, with the distance between them as one condition sees it."""
    for (i, a), (j, b) in itertools.combinations(enumerate(colours), 2):
        yield _Pair(roles[i], roles[j], round(delta_e(a, b), PRECISION))
