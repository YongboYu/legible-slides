"""The palette as a stylesheet.

Two claims. That the emitted file is the mapping docs/token-contract.md §5 fixes, role by role;
and that it is **deterministic** — the file is committed and CI diffs it against its palette, so an
emitter whose output moved with the path, the clock or the machine would turn every unrelated
commit into a spurious failure.
"""

from pathlib import Path

from legible import gen_css, load_palette

#: The one stylesheet this repo commits, and the palette it is generated from
#: (docs/slidev-reference-impl.md §5). CI gates the same comparison; the suite carries it too, so a
#: palette edit that forgot the regeneration surfaces before the push.
COMMITTED_STYLESHEET = Path(__file__).resolve().parents[2] / "theme" / "styles" / "tokens.css"
ITS_PALETTE = Path(__file__).resolve().parents[2] / "themes" / "leuven-blue.json"


def test_every_scalar_role_becomes_a_custom_property_of_the_same_name(base_palette, write_theme):
    css = gen_css(load_palette(write_theme(base_palette)))

    for role, colour in base_palette.items():
        if role not in ("meta", "series"):
            assert f"--{role}: {colour};" in css


def test_the_series_ramp_expands_to_one_indexed_property_per_colour(base_palette, write_theme):
    css = gen_css(load_palette(write_theme(base_palette)))

    assert "--series-1: #1b6fb0;" in css
    assert "--series-2: #57c0ae;" in css
    assert "--series-3: #4c3a78;" in css
    assert "--series:" not in css


def test_a_longer_ramp_expands_to_as_many_properties_as_it_has_colours(base_palette, write_theme):
    base_palette["series"] = ["#1b6fb0", "#57c0ae", "#4c3a78", "#a34a2a", "#2f6b4f"]

    css = gen_css(load_palette(write_theme(base_palette)))

    assert "--series-5: #2f6b4f;" in css
    assert "--series-6" not in css


def test_a_shorter_ramp_emits_no_property_for_a_series_the_palette_does_not_have(
    base_palette, write_theme
):
    base_palette["series"] = ["#1b6fb0", "#57c0ae"]

    css = gen_css(load_palette(write_theme(base_palette)))

    assert "--series-2: #57c0ae;" in css
    assert "--series-3" not in css


def test_the_properties_land_in_one_root_block(base_palette, write_theme):
    """A stylesheet the deck imports and nothing more — no selector of its own, no cascade."""
    css = gen_css(load_palette(write_theme(base_palette)))

    assert css.count(":root {") == 1
    assert css.endswith("}\n")


def test_the_stylesheet_says_it_is_generated_and_names_the_theme_it_came_from(
    base_palette, write_theme
):
    """It is committed like a lockfile, so the file has to tell an author who edits it as much."""
    base_palette["meta"] = {"name": "ochre"}

    css = gen_css(load_palette(write_theme(base_palette)))

    banner = css.split(":root")[0]
    assert "ochre" in banner
    assert "gen-css" in banner
    assert "do not edit" in banner.lower()


def test_a_named_theme_emits_the_same_stylesheet_from_wherever_it_is_read(
    base_palette, write_theme
):
    """CI diffs this file, so nothing outside the palette may reach it. A theme's *name* is inside
    it — and a theme that declares none is named after its file, which is the loader's business."""
    here = gen_css(load_palette(write_theme(base_palette, name="theme.json")))
    elsewhere = gen_css(load_palette(write_theme(base_palette, name="copy.json")))

    assert here == elsewhere


def test_regenerating_from_an_unchanged_palette_produces_no_diff(base_palette, write_theme):
    palette = load_palette(write_theme(base_palette))

    assert gen_css(palette) == gen_css(palette)


def test_the_committed_stylesheet_is_current():
    """The lockfile claim, asserted locally as well as in CI: what is committed is what this
    palette emits today."""
    assert COMMITTED_STYLESHEET.read_text(encoding="utf-8") == gen_css(load_palette(ITS_PALETTE))
