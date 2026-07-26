import pytest

from legible import PaletteError, load_palette


def test_loads_a_shipped_theme_with_series_expanded_to_indexed_roles(themes_dir):
    palette = load_palette(themes_dir / "kuleuven.json")

    assert palette.name == "kuleuven"
    assert palette["ink"] == "#102a43"
    assert palette["series-1"] == "#1b6fb0"
    assert palette["series-3"] == "#4c3a78"
    assert palette.series_roles == ("series-1", "series-2", "series-3")


def test_a_file_that_is_not_json_fails_as_a_palette_error(tmp_path):
    """A malformed file is as much a bad theme as a missing role, and reads as one — the CLI
    hands this loader files it has never seen."""
    path = tmp_path / "broken.json"
    path.write_text('{"ink": "#102a43",')

    with pytest.raises(PaletteError, match="broken.json"):
        load_palette(path)


def test_a_missing_role_is_reported_by_name(write_theme, base_palette):
    del base_palette["muted"]

    with pytest.raises(PaletteError, match="muted"):
        load_palette(write_theme(base_palette))


def test_a_malformed_colour_is_reported_by_role(write_theme, base_palette):
    base_palette["accent"] = "dd8a2e"

    with pytest.raises(PaletteError, match="accent"):
        load_palette(write_theme(base_palette))


def test_a_malformed_series_colour_is_reported_by_indexed_role(write_theme, base_palette):
    base_palette["series"][1] = "#57c0a"

    with pytest.raises(PaletteError, match="series-2"):
        load_palette(write_theme(base_palette))


def test_series_must_be_a_list(write_theme, base_palette):
    base_palette["series"] = "#1b6fb0"

    with pytest.raises(PaletteError, match="series.*list"):
        load_palette(write_theme(base_palette))


def test_an_unknown_role_is_rejected_rather_than_silently_ignored(write_theme, base_palette):
    base_palette["surfaec"] = "#ffffff"

    with pytest.raises(PaletteError, match="surfaec"):
        load_palette(write_theme(base_palette))


def test_a_brand_free_theme_omits_the_logo(write_theme, base_palette):
    palette = load_palette(write_theme(base_palette))

    assert palette.logo is None


def test_a_theme_without_metadata_is_named_after_its_file(write_theme, base_palette):
    del base_palette["meta"]

    palette = load_palette(write_theme(base_palette, name="ochre.json"))

    assert palette.name == "ochre"
