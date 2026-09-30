"""The flagship deck's figures, drawn from the theme file its slides are coloured from.

Two of the deck's beats are demonstrations that cannot be faked: one shows five series collapsing
when colour is the only thing telling them apart, the other shows the same five holding up under a
colour-vision deficiency and in black and white because each carries a dash and a marker of its own.
Hand-drawing either would gut it — and would contradict the practice the method is built on, that a
figure is **regenerated from data, never redrawn** (``docs/design-provenance.md`` §4).

So all three PNGs come from here, and three things about how are deliberate.

**The chart is drawn by the shipped archetype.** ``legible.figures.multi_series`` draws it, and the
colour-alone panel is that same figure with the dash and the marker taken back off afterwards. There
is no second drawing path, so the two panels differ in the one variable the demonstration is about
and in nothing else.

**The simulation is the validator's own.** ``legible.cvd.simulate`` is what ``cvd-validate``
measures with, so the palette a slide shows collapsing is the palette the report measured, at the
severity the canon names.

**The data is the palette measuring itself.** Each point is how far apart one pair of the theme's
data colours lands under one condition, which is the quantity `separation-floor` is about and the
quantity ``cvd-validate`` reports. A chart about separation, unreadable by colour alone, is the
argument rather than an illustration of it.

Run it from this directory, and commit what it writes:

    uv run --project ../python python figures.py
"""

from __future__ import annotations

import itertools
from pathlib import Path

from matplotlib.figure import Figure

from legible import load_palette
from legible.cvd import GRAYSCALE, delta_e, hex_to_rgb1, simulate
from legible.figures import Series, multi_series, save
from legible.method import CVD_CONDITIONS, DELTA_E_FLOOR
from legible.validate import PRECISION

#: The theme the deck is presented in. The figures wear its colours because the slides do.
THEME = Path("../themes/leuven-blue.json")

#: Where the deck serves them from.
PUBLIC = Path("public")

#: The roles the per-series group is formed over, in the order `separation-floor` names them: the
#: two anchors that appear in every chart, then the theme's ramp. Its pairs are what a chart plots.
ANCHORS = ("reference", "muted")

#: The pane each figure lands in: one half of a two-column evidence slide, in canvas px.
PANE_PX = (540, 350)

#: The condition the reference palette is bound by. Its ramp reaches the floor here and nowhere
#: else, which is what makes it the one worth showing a room.
BINDING = "deuteranomaly"


def pair_separations(palette, condition: str) -> list[float]:
    """How far apart every pair of the theme's data colours lands, as ``condition`` receives it.

    Pairs come back in the order ``itertools.combinations`` walks the roles, which is the order the
    validator walks them in too — so the tenth point of this line is the tenth pair of its report.
    Every ΔE is rounded the way the validator rounds it, and for the same reason: a number here and
    a number in its report cannot then disagree.
    """
    roles = (*ANCHORS, *palette.series_roles)
    seen = simulate([hex_to_rgb1(palette[role]) for role in roles], condition)
    return [round(delta_e(a, b), PRECISION) for a, b in itertools.combinations(seen, 2)]


def separation_chart(palette, condition: str) -> Figure:
    """The deck's five-series chart: every pair of data colours, measured under every condition.

    The floor is a line of its own rather than an annotation, because it is read the same way the
    conditions are: as a level the chart either stays above or does not. Roles are pinned rather
    than left to the ramp so that the floor wears the ground-truth colour, normal vision wears the
    de-emphasised one, and the three deficiencies take the ramp in the order the canon lists them.

    There is no x-axis label. The pane is one half of a slide and the legend sits under the plot, so
    the axis is named in the ``Figure`` caption beside it instead of in a third band of type.
    """
    measured = [
        Series(name, pair_separations(palette, name), role=role)
        for name, role in zip(CVD_CONDITIONS, ("muted", *palette.series_roles), strict=True)
    ]
    floor = Series(
        f"floor (ΔE {DELTA_E_FLOOR:.0f})",
        [DELTA_E_FLOOR] * len(measured[0].values),
        role="reference",
    )

    return multi_series(
        palette,
        [floor, *measured],
        x=range(1, len(floor.values) + 1),
        y_label="ΔE, CAM02-UCS",
        condition=condition,
        size_px=PANE_PX,
        # `type-scale`'s marked exception, taken deliberately: each of these lands in one half of a
        # two-column slide, too narrow for body type to fit an axis and a five-entry legend as well.
        tight_panel=True,
    )


def without_redundancy(figure: Figure) -> Figure:
    """The same figure with the dash and the marker taken off every line, and off its legend.

    What `never-sole-channel` forbids, so that the deck can show a room what it is for. Done by
    stripping the drawn figure rather than by a second drawing path, because the demonstration is
    only honest if nothing else about the chart moved. The legend is stripped too: its handles are
    copies made when it was built, and a legend still showing dashes would give away the answer the
    plot no longer carries.
    """
    axes = figure.axes[0]
    for line in (*axes.get_lines(), *axes.get_legend().get_lines()):
        line.set_linestyle("-")
        line.set_marker("None")
    return figure


def main() -> None:
    palette = load_palette(THEME)

    written = [
        save(without_redundancy(separation_chart(palette, BINDING)), PUBLIC / "colour-alone.png"),
        save(separation_chart(palette, BINDING), PUBLIC / "redundant-deuteranomaly.png"),
        save(separation_chart(palette, GRAYSCALE), PUBLIC / "redundant-grayscale.png"),
    ]
    for path in written:
        print(path)


if __name__ == "__main__":
    main()
