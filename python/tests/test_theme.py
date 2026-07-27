"""The shipped Slidev theme, against the canon it is set in.

The canon owns every number the method turns on, and `legible.method` is how this package quotes one
rather than keeping a second copy. A stylesheet and a `package.json` cannot do that: CSS has no way
to read `docs/method.md`, and the deck build is deliberately barred from running Python to find out
(``docs/slidev-reference-impl.md`` §5). So the theme writes the numbers down, and this is where the
copy is held to the original — the same guard the spec asks for around the hand-authored PowerPoint
master, for the same reason: a hand-typed number is exactly where a mapping drifts in silence.

One claim, in both directions: change a number in the canon without changing the theme, or change
the theme's copy of one, and these tests fail naming which.
"""

import json
import re
from pathlib import Path

import pytest

from legible.method import rule_thresholds

THEME = Path(__file__).resolve().parents[2] / "theme"

#: Every custom property in the theme's stylesheet that carries a canon number, against the rule and
#: the threshold key it comes from. `px` is the theme's unit and the canon's own.
DECLARED_PX = {
    "--headline-px": ("type-scale", "headline-px"),
    "--body-px": ("type-scale", "body-px"),
    "--dense-px": ("type-scale", "dense-px"),
    "--dense-xs-px": ("type-scale", "dense-xs-px"),
}


@pytest.fixture(scope="module")
def stylesheet() -> str:
    return (THEME / "styles" / "layout.css").read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def package() -> dict:
    return json.loads((THEME / "package.json").read_text(encoding="utf-8"))


def declared(stylesheet: str, custom_property: str) -> str:
    """One `:root` custom property's value, as the stylesheet writes it."""
    match = re.search(rf"^\s*{re.escape(custom_property)}:\s*([^;]+);", stylesheet, re.MULTILINE)
    assert match, f"the theme declares no {custom_property}"
    return match.group(1).strip()


@pytest.mark.parametrize(("custom_property", "source"), DECLARED_PX.items())
def test_the_theme_s_type_scale_is_the_canon_s(stylesheet, custom_property, source):
    rule, key = source

    assert declared(stylesheet, custom_property) == f"{rule_thresholds(rule)[key]}px"


def test_the_theme_s_headline_ceiling_is_the_canon_s(stylesheet):
    """The theme reserves the headline's zone by multiplying this out, so the ceiling it draws and
    the ceiling `headline-shape` states are one number."""
    ceiling = rule_thresholds("headline-shape")["headline-lines-max"]

    assert declared(stylesheet, "--headline-lines-max") == ceiling


def test_the_theme_s_canvas_is_the_canon_s(package):
    """The logical canvas a deck's px are written against — the same one a generated figure is sized
    in, so a chart asked for at 640 occupies 640 of the layout's units when it lands."""
    type_scale = rule_thresholds("type-scale")
    width, ratio = type_scale["canvas-width-px"], type_scale["canvas-aspect-ratio"]
    defaults = package["slidev"]["defaults"]

    assert defaults["canvasWidth"] == int(width)
    # Slidev spells a ratio with a slash; the canon spells it with a colon.
    assert defaults["aspectRatio"] == ratio.replace(":", "/")


def test_the_theme_locks_the_canon_s_colour_scheme(package):
    """`light-ground` is not a preference, so the theme does not offer it as one."""
    assert package["slidev"]["colorSchema"] == rule_thresholds("light-ground")["color-scheme"]


def test_the_theme_is_set_in_the_canon_s_families(package):
    """Declared to Slidev, so its own UI and any code block resolve to the bundled faces rather than
    to whatever the machine happens to have."""
    fonts = rule_thresholds("fonts")
    declared_fonts = package["slidev"]["defaults"]["fonts"]

    assert declared_fonts["sans"] == fonts["font-text"]
    assert declared_fonts["mono"] == fonts["font-mono"]


def test_the_theme_asks_no_font_provider_for_those_families(package):
    """The other half of `fonts`: bundled means bundled. Both families are named local, so Slidev
    excludes them from its webfont list, and no provider is consulted for anything else either."""
    fonts = rule_thresholds("fonts")
    declared_fonts = package["slidev"]["defaults"]["fonts"]

    assert declared_fonts["provider"] == "none"
    assert set(declared_fonts["local"]) == {fonts["font-text"], fonts["font-mono"]}
