"""The three archetypes, and the rules they hold by construction.

Nothing here compares pixels. What the method actually asks of a generated figure is *structural*
— a distinct dash and marker for every series, colour drawn only from palette roles, the attention
role kept off the data — and structure is readable straight off the figure the caller receives.
The one exception is the reproducibility claim, which is about bytes and is therefore checked as
bytes.

The archetypes are the scope. A test that wanted a fourth chart shape would be asking for a
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
    LEGEND_COLUMNS,
    MARKERS,
    FigureError,
    Series,
    multi_series,
    save,
    small_multiples,
    smallest_type_px,
    two_group,
)
from legible.fonts import BUNDLE
from legible.method import BODY_PX, FLOOR_PX, FONT_TEXT

FIVE_SERIES = [
    Series("Chronos", [1.0, 2.0, 3.0]),
    Series("MOIRAI", [1.5, 2.5, 3.5]),
    Series("TimesFM", [2.0, 3.0, 4.0]),
    Series("Ground truth", [0.5, 1.5, 2.5], role="reference"),
    Series("Baseline", [3.0, 2.0, 1.0], role="muted"),
]


#: Four groups, a panel each, and the same three series in every one of them.
LOGS = ["BPI 2017", "BPI 2019", "Sepsis", "Billing"]
THREE_SERIES = [
    Series("Seasonal naive", [8.30, 14.47, 0.117, 1.77], role="reference"),
    Series("XGBoost", [8.50, 14.70, 0.169, 2.67], role="muted"),
    Series("Best pre-trained", [6.87, 10.75, 0.084, 1.39]),
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


# ── the small-multiples archetype ─────────────────────────────────────────────


def bars_in(axes) -> list:
    return [patch for patch in axes.patches if patch.get_visible()]


def test_small_multiples_draw_one_panel_per_group_titled_with_its_name_in_order(palette):
    figure = small_multiples(palette, THREE_SERIES, LOGS)

    assert [axes.get_title() for axes in figure.axes] == LOGS


def test_every_panel_carries_every_series_in_one_shared_order(palette):
    """The same series in the same place in every panel, so the eye compares like with like."""
    figure = small_multiples(palette, THREE_SERIES, LOGS)

    orders = [[to_hex(bar.get_facecolor()) for bar in bars_in(axes)] for axes in figure.axes]
    assert all(len(order) == len(THREE_SERIES) for order in orders)
    assert all(order == orders[0] for order in orders)


def test_each_bar_stands_where_its_series_does_and_holds_its_value(palette):
    figure = small_multiples(palette, THREE_SERIES, LOGS)

    for index, axes in enumerate(figure.axes):
        assert [bar.get_width() for bar in bars_in(axes)] == [
            line.values[index] for line in THREE_SERIES
        ]


def test_the_reference_series_wears_the_reference_role_and_the_rest_come_off_the_ramp(
    palette, base_palette
):
    figure = small_multiples(palette, THREE_SERIES, LOGS)

    assert [to_hex(bar.get_facecolor()) for bar in bars_in(figure.axes[0])] == [
        base_palette["reference"],
        base_palette["muted"],
        base_palette["series"][0],
    ]


def test_every_series_is_named_beside_its_bars_rather_than_in_a_colour_key(palette):
    """`never-sole-channel`: a series is told apart by its name and its place, and colour only
    repeats them. The names sit at the start of each row of panels, where the eye starts reading."""
    figure = small_multiples(palette, THREE_SERIES, LOGS, columns=2)

    first_column = [figure.axes[0], figure.axes[2]]
    for axes in first_column:
        assert [label.get_text() for label in axes.get_yticklabels()] == [
            line.label for line in THREE_SERIES
        ]
    assert all(axes.get_legend() is None for axes in figure.axes)


def test_every_bar_is_labelled_with_its_value(palette):
    figure = small_multiples(palette, THREE_SERIES, LOGS, value_format="{:.3g}")

    for index, axes in enumerate(figure.axes):
        labelled = {text.get_text() for text in axes.texts}
        assert {f"{line.values[index]:.3g}" for line in THREE_SERIES} <= labelled


def test_each_panel_may_format_its_values_its_own_way(palette):
    """Groups that do not share a scale need not share a precision: 8.30 and 0.117 both read."""
    formats = ["{:.2f}", "{:.2f}", "{:.3f}", "{:.2f}"]
    figure = small_multiples(palette, THREE_SERIES, LOGS, value_format=formats)

    assert {text.get_text() for text in figure.axes[0].texts} == {"8.30", "8.50", "6.87"}
    assert {text.get_text() for text in figure.axes[2].texts} == {"0.117", "0.169", "0.084"}


def test_one_format_per_group_or_one_for_all(palette):
    with pytest.raises(FigureError):
        small_multiples(palette, THREE_SERIES, LOGS, value_format=["{:.2f}"])


def test_the_panels_fill_a_grid_of_the_columns_asked_for_and_nothing_more(palette):
    three_groups = [Series(line.label, line.values[:3], line.role) for line in THREE_SERIES]
    figure = small_multiples(palette, three_groups, LOGS[:3], columns=2)

    assert len(figure.axes) == 3
    assert [axes.get_subplotspec().colspan.start for axes in figure.axes] == [0, 1, 0]


def test_small_multiples_need_a_group_and_a_series(palette):
    with pytest.raises(FigureError):
        small_multiples(palette, [], LOGS)

    with pytest.raises(FigureError):
        small_multiples(palette, THREE_SERIES, [])


def test_a_series_needs_one_value_per_group(palette):
    with pytest.raises(FigureError) as error:
        small_multiples(palette, [Series("a", [1.0, 2.0])], LOGS)

    assert "'a'" in str(error.value)


def test_small_multiples_refuse_more_series_than_the_palette_validated(palette):
    too_many = [Series(f"s{i}", [1.0]) for i in range(len(palette.series_roles) + 1)]

    with pytest.raises(FigureError):
        small_multiples(palette, too_many, ["one"])


@pytest.mark.parametrize("condition", ["deuteranomaly", "protanomaly", "tritanomaly", GRAYSCALE])
def test_small_multiples_render_as_a_deficiency_sees_them(palette, base_palette, condition):
    figure = small_multiples(palette, THREE_SERIES, LOGS, condition=condition)

    roles = [base_palette["reference"], base_palette["muted"], base_palette["series"][0]]
    seen = [rgb1_to_hex(c) for c in simulate([hex_to_rgb1(c) for c in roles], condition)]
    for axes in figure.axes:
        assert [to_hex(bar.get_facecolor()) for bar in bars_in(axes)] == seen


# ── what colour may say, in every archetype ───────────────────────────────────


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


def test_nothing_in_small_multiples_is_a_colour_the_palette_does_not_have(palette):
    assert colours_in(small_multiples(palette, THREE_SERIES, LOGS)) <= set(palette.roles.values())


@pytest.mark.parametrize("role", ["accent", "accent-strong"])
def test_the_attention_roles_cannot_colour_a_series_in_small_multiples(palette, role):
    with pytest.raises(FigureError) as error:
        small_multiples(palette, [Series("a", [1.0], role=role)], ["one"])

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
    """`type-scale` sets evidence at the body size and holds everything else to the floor. A chart
    that went to the floor by default would set its whole message in the smallest type there is."""
    figure = multi_series(palette, FIVE_SERIES, x_label="window", y_label="MAE")

    assert {text.get_fontsize() for text in type_in(figure)} == {points(BODY_PX)}


def test_a_tight_panel_sets_its_type_at_the_floor_and_nothing_under_it(palette):
    figure = multi_series(palette, FIVE_SERIES, x_label="window", y_label="MAE", tight_panel=True)

    assert {text.get_fontsize() for text in type_in(figure)} == {points(FLOOR_PX)}


@pytest.mark.parametrize("tight_panel", [False, True])
def test_every_label_holds_the_floor_where_the_figure_lands(palette, tight_panel):
    """Axis, ticks, legend and bar labels, measured in canvas px at the size the figure is shown,
    which is the size it was asked for: nothing in it is under the floor there."""
    charts = [
        multi_series(palette, FIVE_SERIES, x_label="w", y_label="MAE", tight_panel=tight_panel),
        two_group(palette, {"ARIMA": 0.51}, {"Ours": 0.29}, tight_panel=tight_panel),
        small_multiples(palette, THREE_SERIES, LOGS, tight_panel=tight_panel),
    ]

    assert all(smallest_type_px(figure) >= FLOOR_PX for figure in charts)


def test_a_figure_shown_smaller_than_it_was_drawn_is_measured_smaller(palette):
    """A figure squeezed into a narrower pane shrinks every label in it, and the measure says so
    rather than reporting the size the figure was drawn at."""
    figure = multi_series(palette, FIVE_SERIES, size_px=(800, 450), tight_panel=True)

    assert smallest_type_px(figure, lands_at_px=400) == pytest.approx(FLOOR_PX / 2)


def test_a_figure_with_no_type_has_no_smallest_size(palette):
    figure = multi_series(palette, FIVE_SERIES)
    for text in figure.findobj(lambda artist: hasattr(artist, "get_fontsize")):
        text.set_visible(False)

    assert smallest_type_px(figure) is None


def test_the_two_group_chart_is_set_at_the_body_size_too(palette):
    """Including the direct labels, which are the whole reason it has no value axis to read."""
    figure = two_group(palette, {"ARIMA": 0.51}, {"Ours": 0.29}, y_label="MAE")

    assert {text.get_fontsize() for text in type_in(figure)} == {points(BODY_PX)}


@pytest.mark.parametrize(("tight_panel", "size"), [(False, BODY_PX), (True, FLOOR_PX)])
def test_small_multiples_set_every_name_title_and_value_at_one_size(palette, tight_panel, size):
    figure = small_multiples(palette, THREE_SERIES, LOGS, tight_panel=tight_panel)

    type_ = type_in(figure) + [axes.title for axes in figure.axes]
    assert {text.get_fontsize() for text in type_} == {points(size)}


def test_every_piece_of_type_resolves_to_a_file_this_repo_ships(palette):
    """One step past the family name: the file behind it. Weights included — the highlighted
    group's labels are set semibold, and a weight the bundle lacks is a substitution too."""
    charts = [
        multi_series(palette, FIVE_SERIES, x_label="window", y_label="MAE"),
        two_group(palette, {"ARIMA": 0.51}, {"Ours": 0.29}, y_label="MAE"),
        small_multiples(palette, THREE_SERIES, LOGS),
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


def test_small_multiples_regenerate_to_the_same_bytes(palette, tmp_path):
    first = save(small_multiples(palette, THREE_SERIES, LOGS), tmp_path / "first.png")
    second = save(small_multiples(palette, THREE_SERIES, LOGS), tmp_path / "second.png")

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


def test_the_legend_wraps_to_fewer_columns_rather_than_run_off_the_figure(palette):
    """At the floor, five long labels three to a row are wider than half a slide. A legend cut off
    at the edge has lost the entries that say which dash is which, so it takes another row."""
    series = [
        Series("floor (ΔE 15)", [1.0, 1.0], role="reference"),
        Series("normal", [3.0, 3.0], role="muted"),
        *(Series(f"{name}anomaly", [1.0, 2.0]) for name in ("deuter", "prot", "trit")),
    ]
    figure = multi_series(palette, series, size_px=(540, 350), tight_panel=True)

    legend = figure.axes[0].get_legend().get_window_extent()
    assert 0 <= legend.x0 and legend.x1 <= figure.bbox.width


def test_the_legend_sits_below_the_x_label_rather_than_over_it(palette):
    """A legend wrapped onto more rows in a narrow pane reaches down; it starts under the axis'
    own label, so neither is printed over the other."""
    series = [
        Series("Offer created", [1.0, 2.0]),
        Series("Offer sent, then canceled", [2.0, 1.0]),
        Series("Offer sent, then returned", [1.5, 1.5]),
    ]
    figure = multi_series(
        palette, series, x_label="Week of the log", size_px=(540, 350), tight_panel=True
    )
    figure.canvas.draw()

    axes = figure.axes[0]
    legend = axes.get_legend().get_window_extent()
    label = axes.xaxis.label.get_window_extent()
    assert legend.y1 <= label.y0


def test_a_legend_that_fits_keeps_three_to_a_row(palette):
    figure = multi_series(palette, FIVE_SERIES)

    assert figure.axes[0].get_legend()._ncols == LEGEND_COLUMNS
