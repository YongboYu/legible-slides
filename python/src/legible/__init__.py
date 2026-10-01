"""The mechanical half of legible-slides: reading a theme file, checking its palette, and holding
a deck to the rules the canon decides by script.

``legible.figures`` is deliberately not re-exported here. It costs matplotlib at import, and
`cvd-validate` — the artifact strangers run against their own palette — would then pay for a chart
it never draws. Import it by module: ``from legible.figures import multi_series``.

``legible.deck`` is withheld for the other reason: what a slide *is* is the linter's own reading of
a deck, and exporting it here would publish a second surface nothing has asked for. It is one
import away — ``from legible.deck import parse_deck`` — for whoever eventually does.
"""

from legible.css import gen_css
from legible.lint import Finding, LintReport, Unchecked, lint
from legible.method import DELTA_E_FLOOR, MethodError, Rule, rule, rule_thresholds, rules
from legible.palette import Palette, PaletteError, load_palette
from legible.validate import ContrastPair, Failure, GrayscaleWarning, GroupReport, Report, validate

__all__ = [
    "DELTA_E_FLOOR",
    "ContrastPair",
    "Failure",
    "Finding",
    "GrayscaleWarning",
    "GroupReport",
    "LintReport",
    "MethodError",
    "Palette",
    "PaletteError",
    "Report",
    "Rule",
    "Unchecked",
    "gen_css",
    "lint",
    "load_palette",
    "rule",
    "rule_thresholds",
    "rules",
    "validate",
]
