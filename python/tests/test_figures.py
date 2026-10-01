"""The two archetypes, and the rules they hold by construction.

Nothing here compares pixels. What the method actually asks of a generated figure is *structural*
— a distinct dash and marker for every series, colour drawn only from palette roles, the attention
role kept off the data — and structure is readable straight off the figure the caller receives.
The one exception is the reproducibility claim, which is about bytes and is therefore checked as
bytes.

The archetypes are the scope. A test that wanted a third chart shape would be asking for a
charting library, which `docs/slidev-reference-impl.md` §4 says this is not.
"""

import struct
from dataclasses import fields
from pathlib import Path

import pytest
from matplotlib import font_manager
from matplotlib.colors import to_hex

from legible import load_palette
from legible.cvd import GRAYSCALE, hex_to_rgb1, rgb1_to_hex, simulate
from legible.figures import (
    CSS_PX_PER_INCH,
    DASHES,
    MARKERS,
    FigureError,
    Series,
    multi_series,
    save,
    two_group,
)
from legible.fonts import BUNDLE
from legible.method import BODY_PX, DENSE_PX, DENSE_XS_PX, FONT_TEXT

FIVE_SERIES = [
    Series("Chronos", [1.0, 2.0, 3.0]),
    Series("MOIRAI", [1.5, 2.5, 3.5]),
    Series("TimesFM", [2.0, 3.0, 4.0]),
    Series("Ground truth", [0.5, 1.5, 2.5], role="reference"),
    Series("Baseline", [3.0, 2.0, 1.0], role="muted"),
]


def colours_in(figure) -> set[str]:
    """Every colour the figure paints, as hex — marks, type, rules and ground alike."""
    used = {to_hex(figure.get_facecolor())}
    for axes in figure.axes:
        used.add(to_hex(axes.get_facecolor()))
        used.update(to_hex(line.get_color()) for line in axes.get_lines())
        used.update(to_hex(patch.get_facecolor()) for patch in axes.patches)
        used.update(to_hex(spine.get_edgecolor()) for spine in axes.spines.values())
        used.update(to_hex(text.get_color()) for text in axes.texts)
        used.add(to_hex(axes.xaxis.label.get_color()))
        used.add(to_hex(axes.yaxis.label.get_color()))
        for axis in (axes.xaxis, axes.yaxis):
            for tick in axis.get_major_ticks():
                used.add(to_hex(tick.label1.get_color()))
                if tick.gridline.get_visible():
                    used.add(to_hex(tick.gridline.get_color()))
    return used


def texts_in(figure):
    return [text for axes in figure.axes for text in axes.texts]


def type_in(figure):
    """Every piece of type the figure will draw, legend and tick labels included."""
    type_ = []
    for axes in figure.axes:
        legend = axes.get_legend()
        type_ += [
            axes.xaxis.label,
            axes.yaxis.label,
            *axes.texts,
            *axes.get_xticklabels(),
            *axes.get_yticklabels(),
            *(legend.get_texts() if legend else []),
        ]
    return [text for text in type_ if text.get_text()]


def points(canvas_px: int) -> float:
    """A canvas pixel size as the points matplotlib reports it in."""
    return canvas_px * 72 / CSS_PX_PER_INCH


def png_size(path: Path) -> tuple[int, int]:
    """A PNG's pixel dimensions, read off its header rather than through an image library."""
    header = path.read_bytes()[16:24]
    return struct.unpack(">II", header)


def dash_of(line) -> tuple:
    """The dash sequence a line will actually be drawn with.

    matplotlib normalises every custom dash to the linestyle string ``'--'`` and offers no getter
    for the sequence behind it, so this reads the attribute it keeps it in. Contained here, so an
    upstream rename is one edit rather than one per test.
    """
    return line._unscaled_dash_pattern


# ── the multi-series archetype ────────────────────────────────────────────────


def test_every_series_gets_a_dash_and_a_marker_of_its_own(palette):
    """`never-sole-channel`, as the shape of the figure rather than as a review comment."""
    figure = multi_series(palette, FIVE_SERIES)

    lines = figure.axes[0].get_lines()
    assert len(lines) == len(FIVE_SERIES)
    assert len({dash_of(line) for line in lines}) == len(FIVE_SERIES)
    assert len({line.get_marker() for line in lines}) == len(FIVE_SERIES)


def test_a_series_carries_no_channel_to_opt_out_through(palette):
    """The redundancy is structural because there is nowhere to say "not this one"."""
    assert {field.name for field in fields(Series)} == {"label", "values", "role"}


def test_more_series_than_the_redundancy_can_carry_is_refused(palette):
    too_many = [Series(f"s{i}", [1.0, 2.0]) for i in range(len(DASHES) + 1)]

    with pytest.raises(FigureError) as error:
        multi_series(palette, too_many)

    assert "never-sole-channel" in str(error.value)


def test_the_dash_and_marker_supplies_are_the_same_length(palette):
    """One channel running out before the other would silently cap the other."""
    assert len(DASHES) == len(MARKERS)
    assert len(set(MARKERS)) == len(MARKERS)


def test_a_series_takes_the_next_colour_off_the_ramp_in_order(palette, base_palette):
    figure = multi_series(palette, FIVE_SERIES[:3])

    assert [line.get_color() for line in figure.axes[0].get_lines()] == base_palette["series"]


def test_more_series_than_the_palette_validated_is_refused_and_names_the_theme(
    base_palette, write_theme
):
    """The ramp's capacity is the theme's business; asking past it is an error, not a repeat."""
    base_palette["series"] = ["#1b6fb0", "#57c0ae"]
    palette = load_palette(write_theme(base_palette))

    with pytest.raises(FigureError) as error:
        multi_series(palette, [Series(f"s{i}", [1.0, 2.0]) for i in range(3)])

    assert "test" in str(error.value)


def test_a_series_may_be_pinned_to_the_anchor_roles(palette, base_palette):
    figure = multi_series(palette, FIVE_SERIES)

    coloured = dict(zip([s.label for s in FIVE_SERIES], figure.axes[0].get_lines(), strict=True))
    assert coloured["Ground truth"].get_color() == base_palette["reference"]
    assert coloured["Baseline"].get_color() == base_palette["muted"]


def test_two_series_cannot_wear_the_same_role(palette):
    with pytest.raises(FigureError) as error:
        multi_series(
            palette,
            [Series("a", [1.0], role="muted"), Series("b", [2.0], role="muted")],
        )

    assert "muted" in str(error.value)


def test_a_chart_needs_at_least_one_series(palette):
    with pytest.raises(FigureError):
        multi_series(palette, [])


def test_series_of_different_lengths_are_refused(palette):
    with pytest.raises(FigureError):
        multi_series(palette, [Series("a", [1.0, 2.0]), Series("b", [1.0])])


# ── the two-group archetype ───────────────────────────────────────────────────


def test_the_two_group_chart_is_the_de_emphasised_role_plus_exactly_one_highlight(
    palette, base_palette
):
    figure = two_group(palette, {"ARIMA": 0.51, "XGBoost": 0.44}, {"Ours": 0.29})

    bars = [to_hex(patch.get_facecolor()) for patch in figure.axes[0].patches]
    assert bars == [base_palette["muted"], base_palette["muted"], base_palette["brand"]]


def test_the_highlight_may_be_a_series_colour_instead_of_the_brand(palette, base_palette):
    figure = two_group(palette, {"ARIMA": 0.51}, {"Ours": 0.29}, highlight_role="series-1")

    assert to_hex(figure.axes[0].patches[-1].get_facecolor()) == base_palette["series"][0]


def test_the_highlight_cannot_be_the_role_it_is_supposed_to_stand_out_from(palette):
    with pytest.raises(FigureError):
        two_group(palette, {"ARIMA": 0.51}, {"Ours": 0.29}, highlight_role="muted")


def test_every_bar_is_labelled_where_it_stands_rather_than_in_a_legend(palette):
    figure = two_group(palette, {"ARIMA": 0.51, "XGBoost": 0.44}, {"Ours": 0.29})

    labelled = {text.get_text() for text in texts_in(figure)}
    assert {"0.51", "0.44", "0.29"} <= labelled
    assert figure.axes[0].get_legend() is None


def test_both_groups_have_to_be_there_for_it_to_be_a_comparison(palette):
    with pytest.raises(FigureError):
        two_group(palette, {}, {"Ours": 0.29})

    with pytest.raises(FigureError):
        two_group(palette, {"ARIMA": 0.51}, {})


# ── what colour may say, in either archetype ──────────────────────────────────


def test_nothing_in_a_multi_series_chart_is_a_colour_the_palette_does_not_have(palette):
    assert colours_in(multi_series(palette, FIVE_SERIES)) <= set(palette.roles.values())


def test_nothing_in_a_two_group_chart_is_a_colour_the_palette_does_not_have(palette):
    figure = two_group(palette, {"ARIMA": 0.51, "XGBoost": 0.44}, {"Ours": 0.29})

    assert colours_in(figure) <= set(palette.roles.values())


@pytest.mark.parametrize("role", ["accent", "accent-strong"])
def test_the_attention_roles_cannot_colour_a_data_series(palette, role):
    """`accent-is-attention`, enforced rather than reviewed, for both of its jobs."""
    with pytest.raises(FigureError) as error:
        multi_series(palette, [Series("a", [1.0, 2.0], role=role)])

    assert "accent-is-attention" in str(error.value)


@pytest.mark.parametrize("role", ["accent", "accent-strong"])
def test_the_attention_roles_cannot_colour_a_highlighted_group(palette, role):
    with pytest.raises(FigureError) as error:
        two_group(palette, {"ARIMA": 0.51}, {"Ours": 0.29}, highlight_role=role)

    assert "accent-is-attention" in str(error.value)


def test_a_structural_neutral_cannot_carry_data_either(palette):
    """The chrome roles are governed by WCAG contrast, not by the separation floor — the validator
    never measured them against each other, so a chart may not encode with them."""
    with pytest.raises(FigureError):
        multi_series(palette, [Series("a", [1.0, 2.0], role="neutral-soft")])


# ── rendering under a deficiency ──────────────────────────────────────────────


@pytest.mark.parametrize("condition", ["deuteranomaly", "protanomaly", "tritanomaly", GRAYSCALE])
def test_a_chart_can_render_as_a_deficiency_sees_it_using_the_validators_own_simulation(
    palette, base_palette, condition
):
    figure = multi_series(palette, FIVE_SERIES[:3], condition=condition)

    seen = simulate([hex_to_rgb1(c) for c in base_palette["series"]], condition)
    assert [line.get_color() for line in figure.axes[0].get_lines()] == [
        rgb1_to_hex(colour) for colour in seen
    ]


def test_the_deficiency_render_is_the_same_chart_and_not_a_second_drawing_path(palette):
    """Same marks, same redundancy — only the colours are what the eye in question receives."""
    normal = multi_series(palette, FIVE_SERIES)
    seen = multi_series(palette, FIVE_SERIES, condition="deuteranomaly")

    assert [dash_of(line) for line in seen.axes[0].get_lines()] == [
        dash_of(line) for line in normal.axes[0].get_lines()
    ]
    assert [line.get_marker() for line in seen.axes[0].get_lines()] == [
        line.get_marker() for line in normal.axes[0].get_lines()
    ]


def test_an_unknown_condition_is_refused(palette):
    with pytest.raises(ValueError):
        multi_series(palette, FIVE_SERIES, condition="astigmatism")


# ── the deck's type, and reproducibility ──────────────────────────────────────


def test_every_piece_of_type_in_the_figure_is_the_family_the_canon_names(palette):
    """Tick labels included, which is where a fallback would slip in: they are made during the
    layout pass rather than when the chart is written."""
    figure = multi_series(palette, FIVE_SERIES, x_label="window", y_label="MAE")

    assert {family for text in type_in(figure) for family in text.get_fontfamily()} == {FONT_TEXT}


def test_a_figure_is_set_at_the_body_size_by_default(palette):
    """`type-scale` puts body at the floor and marks the dense sizes as exceptions for tight
    panels. A chart that took the exception by default would put every label below the floor."""
    figure = multi_series(palette, FIVE_SERIES, x_label="window", y_label="MAE")

    assert {text.get_fontsize() for text in type_in(figure)} == {points(BODY_PX)}


def test_a_tight_panel_takes_the_exception_the_canon_marks_and_nothing_between(palette):
    figure = multi_series(palette, FIVE_SERIES, x_label="window", y_label="MAE", tight_panel=True)

    assert {text.get_fontsize() for text in type_in(figure)} <= {
        points(DENSE_PX),
        points(DENSE_XS_PX),
    }


def test_the_two_group_chart_is_set_at_the_body_size_too(palette):
    """Including the direct labels, which are the whole reason it has no value axis to read."""
    figure = two_group(palette, {"ARIMA": 0.51}, {"Ours": 0.29}, y_label="MAE")

    assert {text.get_fontsize() for text in type_in(figure)} == {points(BODY_PX)}


def test_every_piece_of_type_resolves_to_a_file_this_repo_ships(palette):
    """One step past the family name: the file behind it. Weights included — the highlighted
    group's labels are set semibold, and a weight the bundle lacks is a substitution too."""
    charts = [
        multi_series(palette, FIVE_SERIES, x_label="window", y_label="MAE"),
        two_group(palette, {"ARIMA": 0.51}, {"Ours": 0.29}, y_label="MAE"),
    ]

    for figure in charts:
        for text in type_in(figure):
            resolved = font_manager.findfont(text.get_fontproperties(), fallback_to_default=False)
            assert Path(resolved).parent == BUNDLE


def test_a_saved_figure_is_the_size_in_canvas_pixels_it_was_asked_for(palette, tmp_path):
    """Sized in the layout's own units, so a chart asked for at 640 lands 640 wide on the slide."""
    written = save(multi_series(palette, FIVE_SERIES, size_px=(640, 360)), tmp_path / "f.png")

    assert png_size(written) == (1280, 720)  # scale 2, for the projector


def test_regenerating_from_an_unchanged_palette_and_data_reproduces_the_same_figure(
    palette, tmp_path
):
    """The claim that makes a palette swap propagate: rerunning rewrites, it does not churn."""
    first = save(multi_series(palette, FIVE_SERIES), tmp_path / "first.png")
    second = save(multi_series(palette, FIVE_SERIES), tmp_path / "second.png")

    assert first.read_bytes() == second.read_bytes()


def test_a_changed_palette_changes_the_figure(base_palette, write_theme, tmp_path):
    """Otherwise the test above would pass on a helper that ignored its palette entirely."""
    before = save(
        multi_series(load_palette(write_theme(base_palette)), FIVE_SERIES), tmp_path / "a.png"
    )
    base_palette["series"][0] = "#8a1c5e"
    after = save(
        multi_series(load_palette(write_theme(base_palette, name="other.json")), FIVE_SERIES),
        tmp_path / "b.png",
    )

    assert before.read_bytes() != after.read_bytes()


def test_saving_creates_the_directory_it_is_pointed_at(palette, tmp_path):
    written = save(multi_series(palette, FIVE_SERIES), tmp_path / "public" / "figures" / "f.png")

    assert written.is_file()
