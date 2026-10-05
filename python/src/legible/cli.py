"""`cvd-validate` — the accessibility floor as a command with an exit code.

A thin shell over ``validate()``. It decides nothing: `separation-floor` and the contrast pairings
of `accent-is-attention` own what passes, and
``docs/cvd-validator-contract.md`` §4 fixes what this module adds — the shape of the human-readable
report, and the exit code everything downstream keys on (CI, the opt-in pre-commit hook, and the
review skill, which shells out here rather than reimplementing colour-vision simulation).

The report names every pair by **role**, never by hex, because a hex pair tells an author nothing
about which colour in their theme file to change.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence
from dataclasses import asdict
from pathlib import Path

from legible.cvd import CVD_CONDITIONS, GRAYSCALE
from legible.palette import PaletteError, load_palette
from legible.validate import CONTRAST_PRECISION, PRECISION, ContrastPair, Report, validate

#: The contract fixes 0 and 1. 2 says the check did not run — a theme that could not be read makes
#: no claim about its colours, and must not borrow 1's. It is argparse's code for bad arguments
#: too, which is the same statement about a different mistake.
PASSED, FAILED, NOT_CHECKED = 0, 1, 2

#: Column widths for the tag (`fail` / `warn`), the condition and the ΔE, so the minima and the
#: pairs beneath them line up. The condition column is measured off the canon's own conditions
#: rather than guessed, so adding one cannot misalign the report.
_TAG_WIDTH = 6
_CONDITION_WIDTH = max(len(condition) for condition in (*CVD_CONDITIONS, GRAYSCALE)) + 2
_DELTA_E_WIDTH = 5


def main(argv: Sequence[str] | None = None) -> int:
    """Check every theme named on the command line. Returns the process exit code."""
    args = _parser().parse_args(argv)

    failed = not_checked = False
    reported = False
    for theme in args.themes:
        try:
            palette = load_palette(theme)
        except (OSError, PaletteError) as error:
            # Say so and carry on: one unreadable file must not silence the verdict on the themes
            # named after it.
            print(f"cvd-validate: {error}", file=sys.stderr)
            not_checked = True
            continue

        report = validate(palette)
        if args.json:
            print(_as_json(report))
        else:
            if reported:
                print()  # one blank line between themes
            print(_as_text(theme, report))
        reported = True
        # Only a hard failure moves the exit code. Warnings never do.
        failed = failed or not report.passed

    # A palette measured below the floor outranks a file that never got measured — it is the more
    # actionable of the two, and both are non-zero, so a gate blocks either way.
    if failed:
        return FAILED
    return NOT_CHECKED if not_checked else PASSED


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="cvd-validate",
        description=(
            "Check a theme's data colours for perceptual separation under every condition the "
            "`separation-floor` rule names, and its attention and text pairings for the contrast "
            "`accent-is-attention` and `decorative-neutral-never-text` name. Exits 0 on pass, 1 if "
            "any pair falls below its floor, "
            "and 2 if a theme could not be read. Grayscale collisions are advisory and never "
            "change the exit code."
        ),
    )
    parser.add_argument(
        "themes",
        metavar="THEME",
        nargs="+",
        type=Path,
        help="theme JSON file(s) to check — this repo's, or your own",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="emit the report verbatim as JSON, one object per theme in the order given",
    )
    return parser


def _as_text(theme: Path, report: Report) -> str:
    """The verdict as an author reads it: what it scored, and which pair to change."""
    verdict = "PASS" if report.passed else "FAIL"
    achieved = f"{min(report.min_delta_e.values()):.{PRECISION}f}"
    floor = f"{report.threshold:.{PRECISION}f}"

    lines = [
        f"{verdict}  {theme} — min ΔE {achieved} (floor {floor})",
        "",
        "  min ΔE per condition",
    ]
    lines.extend(
        f"    {_measured(condition, minimum)}" for condition, minimum in report.min_delta_e.items()
    )
    lines.append(f"    {_measured(GRAYSCALE, report.grayscale_min)}  advisory")

    lines.append("")
    lines.append(f"  attention contrast (min {report.contrast_threshold:.{CONTRAST_PRECISION}f})")
    lines.extend(_contrast(pair, pair in report.contrast_failures) for pair in report.contrast)
    lines.append("")
    lines.append(f"  text contrast (min {report.text_contrast_threshold:.{CONTRAST_PRECISION}f})")
    lines.extend(
        _contrast(pair, pair in report.text_contrast_failures) for pair in report.text_contrast
    )

    if report.failures or report.warnings:
        lines.append("")
    lines.extend(
        _pair("fail", failure.condition, failure.delta_e, failure.role_a, failure.role_b)
        for failure in report.failures
    )
    lines.extend(
        _pair("warn", GRAYSCALE, warning.delta_e, warning.role_a, warning.role_b)
        for warning in report.warnings
    )
    return "\n".join(lines)


def _measured(condition: str, delta_e: float) -> str:
    """One condition and what it scored — the same columns wherever a ΔE is printed."""
    return f"{condition:<{_CONDITION_WIDTH}}{delta_e:>{_DELTA_E_WIDTH}.{PRECISION}f}"


def _contrast(pair: ContrastPair, failed: bool) -> str:
    """One contrast pairing, named by role, with what it achieved — and `fail` where it fell."""
    tag = "fail" if failed else ""
    return (
        f"  {tag:<{_TAG_WIDTH}}{pair.ratio:>{_DELTA_E_WIDTH}.{CONTRAST_PRECISION}f}"
        f"  {pair.foreground} on {pair.background}"
    )


def _pair(tag: str, condition: str, delta_e: float, role_a: str, role_b: str) -> str:
    return f"  {tag:<{_TAG_WIDTH}}{_measured(condition, delta_e)}  {role_a} ↔ {role_b}"


def _as_json(report: Report) -> str:
    """The report verbatim — every field under its own name, and nothing added.

    One line per report, so a run over several themes is a stream of whole reports rather than a
    shape that changes with the number of arguments.
    """
    data = asdict(report)
    data["failures"] = [failure._asdict() for failure in report.failures]
    data["warnings"] = [warning._asdict() for warning in report.warnings]
    data["contrast"] = [pair._asdict() for pair in report.contrast]
    data["contrast_failures"] = [pair._asdict() for pair in report.contrast_failures]
    data["text_contrast"] = [pair._asdict() for pair in report.text_contrast]
    data["text_contrast_failures"] = [pair._asdict() for pair in report.text_contrast_failures]
    return json.dumps(data)
