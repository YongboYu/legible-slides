"""The canon, quoted.

`docs/method.md` states every rule of the method and every number it turns on, once. This module is
how Python reads a number out of it, so the package quotes the canon rather than keeping a second
copy that can drift. Every rule carries a stable ID and a ``**Threshold**`` footer of
``key = value`` pairs; ``rule_thresholds`` returns one rule's pairs.

The colour numbers below all belong to `separation-floor`. Change that rule and they change here.
"""

from __future__ import annotations

import re
from pathlib import Path

#: A rule heading: `### \`rule-id\`: statement`.
_RULE = re.compile(r"^###\s+`(?P<rule>[a-z0-9-]+)`", re.MULTILINE)

#: One `key = value` pair inside a **Threshold** footer.
_THRESHOLD = re.compile(r"`(?P<key>[a-z0-9-]+)\s*=\s*(?P<value>[^`]+)`")


class MethodError(LookupError):
    """The canon could not be read, or does not carry what was asked of it."""


#: The canon, read in place rather than vendored — one copy, and the package quotes it.
CANON = Path(__file__).resolve().parents[3] / "docs" / "method.md"


def read_canon() -> str:
    """The text of `docs/method.md`."""
    try:
        return CANON.read_text(encoding="utf-8")
    except OSError as error:
        raise MethodError(f"cannot read the canon at {CANON} to quote its thresholds") from error


def rule_thresholds(rule_id: str, canon: str | None = None) -> dict[str, str]:
    """The ``key = value`` thresholds one rule declares, as written in the canon.

    Values come back as the strings the canon wrote, because the canon is the authority on both
    the number and its units; callers convert to whatever type they need.
    """
    text = read_canon() if canon is None else canon

    starts = {match.group("rule"): match.span()[0] for match in _RULE.finditer(text)}
    if rule_id not in starts:
        raise MethodError(f"the canon carries no rule `{rule_id}`")

    start = starts[rule_id]
    following = [pos for pos in starts.values() if pos > start]
    body = text[start : min(following)] if following else text[start:]

    _, marker, footer = body.partition("**Threshold**")
    if not marker:
        raise MethodError(f"rule `{rule_id}` declares no threshold")

    return {
        match.group("key"): match.group("value").strip() for match in _THRESHOLD.finditer(footer)
    }


_SEPARATION_FLOOR = rule_thresholds("separation-floor")

#: The perceptual floor every pair of data colours must clear. The canon owns the number and the
#: reasoning behind it; `docs/cvd-validator-contract.md` §3 records how it was arrived at.
DELTA_E_FLOOR = float(_SEPARATION_FLOOR["delta-e-floor"])

#: The uniform space distances are measured in.
DELTA_E_METRIC = _SEPARATION_FLOOR["delta-e-metric"]

#: Simulation severity. The canon picks full dichromacy: the worst case.
SEVERITY = int(_SEPARATION_FLOOR["cvd-severity"])

#: Every condition a palette is checked under, normal vision first.
CVD_CONDITIONS = tuple(
    condition.strip() for condition in _SEPARATION_FLOOR["cvd-conditions"].strip("[]").split(",")
)

#: The conditions that need simulating — everything but normal vision.
CVD_TYPES = tuple(condition for condition in CVD_CONDITIONS if condition != "normal")
