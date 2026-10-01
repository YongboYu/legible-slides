"""The two figure archetypes the method prescribes — and deliberately nothing else.

A result chart here is **regenerated from data, never redrawn**, which is what makes a palette swap
actually propagate: change one theme file, rerun, and every figure is wearing the new colours.
``docs/design-provenance.md`` §4 records that practice; this module is where it becomes an API.

Two shapes, because two is what the canon prescribes:

- ``multi_series`` — the per-series comparison. Every line gets its own dash *and* its own marker,
  assigned by position rather than offered as an option, so `never-sole-channel` holds by
  construction. It can also render itself as a colour-vision deficiency sees it, which is the
  demonstration two of the flagship's beats are built on.
- ``two_group`` — the default headline chart: a de-emphasised comparison against one highlight,
  every bar labelled where it stands (`spend-colour-on-discrimination`).

This is **not a charting library**, and ``docs/slidev-reference-impl.md`` §4 is where that scope is
fixed. A third shape belongs in a ticket, not in a keyword argument.

Three things are enforced rather than documented, because a rule a caller can forget is a rule the
deck will eventually break:

- colour comes only from palette roles, so nothing downstream can hardcode a hex;
- only roles the validator actually measured may encode data, which puts the attention
  roles (`accent-is-attention`) and the structural neutrals out of reach;
- the dash/marker supply is finite, and a chart with more series than it can distinguish is
  refused instead of quietly repeating one.

Sizes are given in the canon's **canvas pixels** — the same logical units a slide layout is written
in — so a chart asked for at 640 occupies 640 of them when it lands, and the type sitting in it is
the same height as the type around it.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from contextlib import contextmanager
from dataclasses import dataclass, replace
from pathlib import Path

from matplotlib import rc_context, rcParams
from matplotlib.figure import Figure
from matplotlib.text import Text

from legible.cvd import NORMAL, hex_to_rgb1, rgb1_to_hex, simulate
from legible.fonts import register
from legible.method import (
    BODY_PX,
    CANVAS_HEIGHT_PX,
    CANVAS_WIDTH_PX,
    FLOOR_PX,
    FONT_TEXT,
)
from legible.palette import Palette

__all__ = [
    "DASHES",
    "EVIDENCE_PANE_PX",
    "MARKERS",
    "FigureError",
    "Series",
    "multi_series",
    "save",
    "smallest_type_px",
    "two_group",
]

#: One dash pattern per series, in assignment order — solid first, then patterns that stay apart at
#: projection distance rather than merely differing in a legend.
DASHES = (
    (0, ()),
    (0, (6, 2)),
    (0, (1, 1.6)),
    (0, (6, 2, 1, 2)),
    (0, (3, 1.4)),
    (0, (6, 2, 1, 2, 1, 2)),
)

#: One marker per series, same order. Shapes chosen to differ in silhouette, not only in size.
MARKERS = ("o", "s", "^", "D", "v", "P")

#: How many legend entries sit on one row at most. Three at body size is what fits across an
#: evidence pane without the labels running into each other; a narrower figure takes fewer.
LEGEND_COLUMNS = 3

#: The attention roles, the fill and the text-and-stroke one. `accent-is-attention` reserves both
#: for arrows and highlights, and this module is where "never a data series" stops being advice.
ATTENTION_ROLES = ("accent", "accent-strong")

#: The de-emphasised comparison group in the two-group archetype — fixed, because a chart that let
#: the caller choose it would be a chart that could highlight both sides.
COMPARISON_ROLE = "muted"

#: A default figure at three quarters of the canvas, which is about what an evidence pane gets.
#: Pass the real size of your pane; that is what these units are for.
EVIDENCE_PANE_PX = (CANVAS_WIDTH_PX * 3 // 4, CANVAS_HEIGHT_PX * 3 // 4)

#: The CSS reference pixel. It is what turns a size in canvas px into inches and points, and it is
#: fixed rather than chosen: the deck's px are CSS px, so this is the only rate at which a figure's
#: type comes out the same height as the slide's.
CSS_PX_PER_INCH = 96

#: How much bigger the file is than the canvas box it fills. A projector and a retina screen both
#: want the extra pixels; the layout is identical, so the figure still lands at its asked-for size.
DEFAULT_SCALE = 2


class FigureError(ValueError):
    """A figure the method does not allow to be drawn."""


@dataclass(frozen=True)
class Series:
    """One line on a multi-series chart.

    It carries no dash and no marker on purpose. Those are assigned by position, so there is
    nowhere for an author to say "not this one" and no way to ship colour as the sole channel.

    ``role`` pins the line to a named palette role — ``reference`` for a ground truth, ``muted``
    for the comparison everything else is read against. Left unset, the line takes the next colour
    off the theme's categorical ramp.
    """

    label: str
    values: Sequence[float]
    role: str | None = None


def multi_series(
    palette: Palette,
    series: Sequence[Series],
    *,
    x: Sequence[float] | None = None,
    x_label: str | None = None,
    y_label: str | None = None,
    condition: str = NORMAL,
    size_px: tuple[int, int] = EVIDENCE_PANE_PX,
    tight_panel: bool = False,
) -> Figure:
    """The per-series comparison: one line per series, each with a dash and a marker of its own.

    ``condition`` renders the chart as one pair of eyes receives it — ``"normal"``, one of the
    dichromacies the canon names, or ``"grayscale"``. That is the flagship's colour demonstration,
    and it is drawn by simulating the palette and then drawing the ordinary chart, so there is no
    second drawing path that could show something the ordinary one would not.

    ``tight_panel`` drops the type to the floor `type-scale` holds everything to, and is a choice
    for a pane too small for body type rather than a preference: take it then, and not otherwise.
    """
    if not series:
        raise FigureError("a chart needs at least one series")
    if len(series) > len(DASHES):
        raise FigureError(
            f"{len(series)} series is more than the {len(DASHES)} this chart can give a distinct "
            f"dash and marker to, and colour may not carry the rest (`never-sole-channel`)"
        )

    roles = _assign_roles(palette, series)
    xs = list(range(len(series[0].values))) if x is None else list(x)
    for line in series:
        if len(line.values) != len(xs):
            raise FigureError(
                f"series {line.label!r} has {len(line.values)} values against {len(xs)} on the "
                f"x axis: every series is read off one axis, so they share it"
            )

    with _pane(palette, condition, size_px, tight_panel) as (seen, axes):
        for index, (line, role) in enumerate(zip(series, roles, strict=True)):
            axes.plot(
                xs,
                list(line.values),
                label=line.label,
                color=seen[role],
                linestyle=DASHES[index],
                marker=MARKERS[index],
                markersize=5.0,
                linewidth=2.0,
            )

        axes.grid(axis="y", color=seen["neutral-soft"], linewidth=0.6)
        axes.set_axisbelow(True)
        _strip_chrome(axes, seen, keep=("left", "bottom"))
        if x_label:
            axes.set_xlabel(x_label)
        if y_label:
            axes.set_ylabel(y_label)
        # The legend is where the dash and the marker are *read*, which is why this archetype has
        # one at all: it is the redundancy made visible rather than a colour key. It sits below the
        # plot rather than inside it, because at body size a legend large enough to read is large
        # enough to land on the data, and "best" has nowhere good to put it.
        #
        # Three to a row where three fit, and fewer where they do not: a legend run off the edge of
        # a narrow pane has lost the entries that say which dash is which.
        for columns in range(min(len(series), LEGEND_COLUMNS), 0, -1):
            legend = axes.legend(
                frameon=False,
                loc="upper center",
                bbox_to_anchor=(0.5, -0.16),
                ncols=columns,
            )
            if legend.get_window_extent().width <= axes.figure.bbox.width:
                break

    return axes.figure


def two_group(
    palette: Palette,
    comparison: Mapping[str, float],
    highlight: Mapping[str, float],
    *,
    highlight_role: str = "brand",
    value_format: str = "{:.2f}",
    y_label: str | None = None,
    condition: str = NORMAL,
    size_px: tuple[int, int] = EVIDENCE_PANE_PX,
    tight_panel: bool = False,
) -> Figure:
    """The default headline chart: a de-emphasised comparison, then one highlighted group.

    Two groups is the signature, not a convention — there is no third argument to put a second
    highlight in. The comparison is always the de-emphasised role; the highlight is the brand or a
    colour off the ramp, and never an attention role. One highlight means one highlight *role*:
    however many bars stand in that group, the chart still spends exactly two colours.

    Every bar is labelled with its own value where it stands, so the chart needs no legend and no
    value axis: with the numbers on the bars, both would be ink spent on nothing (`figure-noise`).

    ``tight_panel`` sets the type at the floor, as in ``multi_series``.
    """
    if not comparison or not highlight:
        raise FigureError(
            "a two-group chart needs both groups: one group on its own is not a comparison"
        )
    role = _checked_role(
        palette,
        highlight_role,
        allowed=("brand", *palette.series_roles),
        what="the highlighted group",
    )

    with _pane(palette, condition, size_px, tight_panel) as (seen, axes):
        positions = range(len(comparison) + len(highlight))
        groups = (
            (comparison, seen[COMPARISON_ROLE], "normal"),
            (highlight, seen[role], "semibold"),
        )
        offset = 0
        for values, colour, weight in groups:
            bars = axes.bar(
                positions[offset : offset + len(values)],
                list(values.values()),
                width=0.65,
                color=colour,
            )
            axes.bar_label(
                bars,
                labels=[value_format.format(value) for value in values.values()],
                padding=4,
                # The label is `ink`, not the bar's own colour: a data role has only ever been
                # measured against other data roles, and text has to clear WCAG contrast at the
                # size it is set. Weight is what marks the highlight here.
                color=seen["ink"],
                fontweight=weight,
            )
            offset += len(values)

        axes.set_xticks(list(positions), [*comparison, *highlight])
        _strip_chrome(axes, seen, keep=("bottom",))
        # No value axis, and after the chrome pass so it is not undone by it: every bar already
        # says what it is worth, and a second copy of the same number down the side is exactly the
        # ink `figure-noise` asks for back.
        axes.tick_params(axis="y", length=0, labelleft=False)
        axes.margins(y=0.15)
        if y_label:
            axes.set_ylabel(y_label)

    return axes.figure


def save(figure: Figure, path: str | Path, *, scale: int = DEFAULT_SCALE) -> Path:
    """Write a figure to PNG at ``scale`` times its canvas size, and return where it went.

    Reproducible on purpose. Figures are committed alongside the deck, so the same palette and the
    same data have to produce the same file — otherwise every rerun is a diff and nobody reads the
    one that matters. Nothing about the *run* reaches the bytes: not the clock, and not the name
    and version matplotlib would otherwise stamp into the file. What a matplotlib upgrade renders
    is a separate question, and ``pyproject.toml`` says where that pin stands.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    # The family again, because text this draw creates reads it at creation. Sizes and colours are
    # already on the axes, where `tick_params` keeps them for ticks that do not exist yet.
    register()
    with rc_context({"font.family": FONT_TEXT}):
        figure.savefig(
            path,
            format="png",
            dpi=CSS_PX_PER_INCH * scale,
            metadata={"Software": None},
        )
    return path


def smallest_type_px(figure: Figure, *, lands_at_px: float | None = None) -> float | None:
    """The smallest piece of type the figure draws, in canvas px, at the width it lands on a slide.

    `type-scale` holds a figure's text to the floor *where it lands*, not where it was drawn: a
    chart drawn at 960 and shown in a 480 pane has every label at half the size it was set in.
    ``lands_at_px`` is that width on the canvas, and defaults to the width the figure was drawn at,
    which is what the archetypes are asked for. Axis labels, tick labels, the legend and the bar
    labels are all measured; a figure with no visible type has no smallest size.
    """
    drawn_px = figure.get_figwidth() * CSS_PX_PER_INCH
    scale = 1.0 if lands_at_px is None else lands_at_px / drawn_px
    sizes = [
        _px(text.get_fontsize()) * scale
        for text in figure.findobj(Text)
        if text.get_visible() and text.get_text().strip()
    ]
    return min(sizes, default=None)


# ── roles ─────────────────────────────────────────────────────────────────────


def _assign_roles(palette: Palette, series: Sequence[Series]) -> list[str]:
    """One palette role per series: the pinned ones as asked, the rest off the ramp in order.

    The roles a line may wear are the ones the validator measured as sharing an axis — the anchors
    plus the categorical ramp — because asking for a colour outside that set is asking for a pair
    nobody checked.
    """
    allowed = ("reference", COMPARISON_ROLE, *palette.series_roles)
    pinned = [
        _checked_role(palette, line.role, allowed=allowed, what=f"series {line.label!r}")
        for line in series
        if line.role is not None
    ]
    taken = set(pinned)
    if len(taken) != len(pinned):
        repeated = sorted({role for role in pinned if pinned.count(role) > 1})
        raise FigureError(
            "two series were pinned to the same role ("
            + ", ".join(f"`{role}`" for role in repeated)
            + "): a chart cannot say two things in one colour"
        )

    ramp = [role for role in palette.series_roles if role not in taken]
    assigned = []
    for line in series:
        if line.role is not None:
            assigned.append(line.role)
            continue
        if not ramp:
            raise FigureError(
                f"the `{palette.name}` theme validated {len(palette.series_roles)} series colours "
                f"and this chart asked for more; add one to the theme and re-run the validator"
            )
        assigned.append(ramp.pop(0))
    return assigned


def _checked_role(palette: Palette, role: str, *, allowed: Sequence[str], what: str) -> str:
    """One role, checked against what the method lets it encode."""
    if role in ATTENTION_ROLES:
        raise FigureError(
            f"`{role}` marks attention, never data (`accent-is-attention`), so it "
            f"cannot colour {what}"
        )
    if role not in allowed:
        known = f"unknown role `{role}`" if role not in palette.roles else f"role `{role}`"
        raise FigureError(
            f"{what} cannot be coloured by {known}: a chart encodes with "
            + ", ".join(f"`{name}`" for name in allowed)
            + ", the roles the validator measured against each other"
        )
    return role


def _seen_as(palette: Palette, condition: str) -> Palette:
    """The palette as one condition receives it — every role simulated together.

    The simulation is ``legible.cvd.simulate``, the same one the validator measures with. A chart
    that showed a palette collapsing while the report said it held would be worse than no chart,
    and there is only one implementation for the two of them to disagree over.
    """
    if condition == NORMAL:
        return palette

    simulated = simulate([hex_to_rgb1(colour) for colour in palette.roles.values()], condition)
    return replace(
        palette,
        roles=dict(zip(palette.roles, (rgb1_to_hex(c) for c in simulated), strict=True)),
    )


# ── the pane, and the type in it ──────────────────────────────────────────────


@contextmanager
def _pane(palette: Palette, condition: str, size_px: tuple[int, int], tight_panel: bool):
    """The setup both archetypes share, so neither can drift from the other.

    Yields the palette as ``condition`` receives it and the axes to draw on. Everything the two
    charts have in common lives here — the simulation, the deck's type, the palette's own chrome
    colours, the size in canvas pixels — which is what makes "the deficiency render is the same
    chart, only simulated" a property of the code rather than a claim about it.

    The figure is bare, as in built without pyplot: nothing registers with a global figure manager,
    so a caller drawing two hundred charts leaks none of them and a headless machine needs no
    backend chosen for it.
    """
    seen = _seen_as(palette, condition)
    width, height = size_px
    with rc_context({**_type_style(tight_panel), **_chart_style(seen)}):
        figure = Figure(
            figsize=(width / CSS_PX_PER_INCH, height / CSS_PX_PER_INCH),
            dpi=CSS_PX_PER_INCH,
            facecolor=seen["surface"],
        )
        yield seen, figure.subplots()
        # Inside the context, because laying out is what creates the tick labels.
        figure.tight_layout()


def _pt(px: float) -> float:
    """A canvas pixel in points — the deck's units expressed in the plotting backend's."""
    return px * 72 / CSS_PX_PER_INCH


def _px(pt: float) -> float:
    """A point in canvas pixels: ``_pt`` the other way round."""
    return pt * CSS_PX_PER_INCH / 72


def _type_style(tight_panel: bool) -> dict[str, object]:
    """The canon's type, in the units matplotlib sets it in.

    A figure's type defaults to the **body** size, not to the floor. `type-scale` sets evidence at
    body size and holds everything else at or above the floor, so a chart that went to the floor by
    default would set its whole message in the smallest type there is. ``tight_panel`` takes the
    floor deliberately, for a pane too small for body type; nothing here goes under it.

    Registering the bundled family here rather than at import is what makes the typeface guarantee
    hold for a caller who never thought about fonts: you cannot draw one of these without it.
    """
    register()
    size = _pt(FLOOR_PX if tight_panel else BODY_PX)
    return {
        "font.family": FONT_TEXT,
        "font.size": size,
        "axes.titlesize": size,
        "axes.labelsize": size,
        "xtick.labelsize": size,
        "ytick.labelsize": size,
        "legend.fontsize": size,
    }


def _chart_style(palette: Palette) -> dict[str, object]:
    """Every colour a chart spends outside its data, taken from the palette's own roles."""
    return {
        # The ground is on the figure itself rather than only here, because `save` writes outside
        # this context and takes the ground from the figure.
        "figure.facecolor": palette["surface"],
        "axes.facecolor": palette["surface"],
        "text.color": palette["ink"],
        "axes.labelcolor": palette["ink"],
        "axes.edgecolor": palette["neutral"],
        "xtick.color": palette["neutral"],
        "ytick.color": palette["neutral"],
        "grid.color": palette["neutral-soft"],
    }


def _strip_chrome(axes, palette: Palette, *, keep: Sequence[str]) -> None:
    """Hide the spines the chart does not need, and put the rest of its rules in a palette role.

    `figure-noise` as the default rather than as a cleanup pass: a box drawn round a chart is four
    lines of ink, of which at most two are ever load-bearing. Every spine is coloured, hidden ones
    included, so a caller who reveals one later gets the theme's colour rather than plain black.
    """
    for name, spine in axes.spines.items():
        spine.set_visible(name in keep)
        spine.set_color(palette["neutral"])
        spine.set_linewidth(0.8)
    # `colors` sets the tick marks and their labels together. Setting the size here as well as in
    # the style is what carries it to ticks a later draw invents: these stick to the axes, while
    # the style only reaches text created while it is in force.
    axes.tick_params(
        colors=palette["neutral"],
        labelsize=rcParams["xtick.labelsize"],
        length=4,
        width=0.8,
    )
