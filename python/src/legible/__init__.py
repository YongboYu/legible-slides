"""The mechanical half of legible-slides: reading a theme file, and checking its palette.

``legible.figures`` is deliberately not re-exported here. It costs matplotlib at import, and
`cvd-validate` — the artifact strangers run against their own palette — would then pay for a chart
it never draws. Import it by module: ``from legible.figures import multi_series``.
"""

from legible.css import gen_css
from legible.method import DELTA_E_FLOOR, MethodError, rule_thresholds
from legible.palette import Palette, PaletteError, load_palette
from legible.validate import Failure, GrayscaleWarning, GroupReport, Report, validate

__all__ = [
    "DELTA_E_FLOOR",
    "Failure",
    "GrayscaleWarning",
    "GroupReport",
    "MethodError",
    "Palette",
    "PaletteError",
    "Report",
    "gen_css",
    "load_palette",
    "rule_thresholds",
    "validate",
]
