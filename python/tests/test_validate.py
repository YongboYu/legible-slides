from legible import load_palette, validate


def test_a_colliding_pair_fails_naming_both_roles_and_the_condition(write_theme, base_palette):
    base_palette["series"][1] = "#1b70b2"  # a hair off series-1 — indistinguishable everywhere

    report = validate(load_palette(write_theme(base_palette)))

    assert not report.passed
    pairs = {(failure.role_a, failure.role_b) for failure in report.failures}
    assert ("series-1", "series-2") in pairs
    assert {failure.condition for failure in report.failures} >= {"normal", "deuteranomaly"}
    assert all(failure.delta_e < report.threshold for failure in report.failures)


def test_a_grayscale_only_collision_warns_but_still_passes(write_theme, base_palette):
    # A rust that stays well clear of series-1 in colour but shares its lightness almost exactly.
    base_palette["series"][1] = "#a34a2a"

    report = validate(load_palette(write_theme(base_palette)))

    assert report.passed
    assert report.failures == ()
    collision = next(
        warning
        for warning in report.warnings
        if (warning.role_a, warning.role_b) == ("series-1", "series-2")
    )
    assert collision.delta_e < report.threshold


def test_brand_and_series_are_never_compared(themes_dir):
    """They live on mutually exclusive slides, so they cannot share an axis.

    The reference theme is the proof this matters: its brand (#00407a) and series-3 (#4c3a78) are
    both dark blue-purples that collapse to ΔE ≈ 0.7 under protanopia. Requiring them to separate
    would be wrong on the merits and impossible in practice — so the theme passes regardless, and
    the pair appears in no group and in no result.
    """
    report = validate(load_palette(themes_dir / "kuleuven.json"))

    for group in report.groups.values():
        series = [role for role in group.roles if role.startswith("series-")]
        assert not (series and "brand" in group.roles)

    reported = [(result.role_a, result.role_b) for result in (*report.failures, *report.warnings)]
    assert not [
        pair for pair in reported if "brand" in pair and any("series-" in role for role in pair)
    ]


def test_a_shorter_ramp_forms_groups_over_the_roles_present(write_theme, base_palette):
    base_palette["series"] = ["#1b6fb0"]

    report = validate(load_palette(write_theme(base_palette)))

    assert report.groups["G1"].roles == ("reference", "muted", "series-1")
    assert report.groups["G2"].roles == ("reference", "muted", "brand")
    assert report.passed


def test_a_longer_ramp_extends_the_per_series_group(write_theme, base_palette):
    base_palette["series"].append("#c8963c")

    report = validate(load_palette(write_theme(base_palette)))

    assert report.groups["G1"].roles == (
        "reference",
        "muted",
        "series-1",
        "series-2",
        "series-3",
        "series-4",
    )
    assert report.groups["G2"].roles == ("reference", "muted", "brand")


def test_a_stricter_threshold_moves_the_boundary(themes_dir):
    palette = load_palette(themes_dir / "kuleuven.json")

    assert validate(palette).passed
    assert not validate(palette, threshold=20.0).passed


def test_a_pair_landing_exactly_on_the_floor_passes(themes_dir):
    """The reference theme's per-series ramp sits at 15.0 — at capacity, and a pass.

    Comparison is inclusive by design: the dependency is pinned, so a value on the floor is
    reproducible rather than a coin flip.
    """
    palette = load_palette(themes_dir / "kuleuven.json")

    report = validate(palette, threshold=15.0)

    assert min(report.groups["G1"].min_delta_e.values()) == report.threshold
    assert report.passed
