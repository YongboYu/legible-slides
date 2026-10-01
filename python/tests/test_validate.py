from legible import load_palette, validate


def test_a_colliding_pair_fails_naming_both_roles_and_the_condition(write_theme, colliding_palette):
    report = validate(load_palette(write_theme(colliding_palette)))

    assert not report.passed
    pairs = {(failure.role_a, failure.role_b) for failure in report.failures}
    assert ("series-1", "series-2") in pairs
    assert {failure.condition for failure in report.failures} >= {"normal", "deuteranomaly"}
    assert all(failure.delta_e < report.threshold for failure in report.failures)


def test_a_grayscale_only_collision_warns_but_still_passes(write_theme, grayscale_clash_palette):
    report = validate(load_palette(write_theme(grayscale_clash_palette)))

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
    report = validate(load_palette(themes_dir / "leuven-blue.json"))

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
    palette = load_palette(themes_dir / "leuven-blue.json")

    assert validate(palette).passed
    assert not validate(palette, threshold=20.0).passed


def test_a_pair_landing_exactly_on_the_floor_passes(themes_dir):
    """The reference theme's per-series ramp sits at 15.0 — at capacity, and a pass.

    Comparison is inclusive by design: the dependency is pinned, so a value on the floor is
    reproducible rather than a coin flip.
    """
    palette = load_palette(themes_dir / "leuven-blue.json")

    report = validate(palette, threshold=15.0)

    assert min(report.groups["G1"].min_delta_e.values()) == report.threshold
    assert report.passed


def test_the_shipped_theme_clears_every_attention_pairing(themes_dir):
    """The ratios the accent research published, measured rather than quoted."""
    report = validate(load_palette(themes_dir / "leuven-blue.json"))

    assert report.passed
    assert report.contrast_failures == ()
    measured = {(pair.foreground, pair.background): pair.ratio for pair in report.contrast}
    assert measured == {
        ("ink", "accent"): 5.40,
        ("accent-strong", "surface"): 5.00,
        ("accent-strong", "surface-alt"): 4.65,
    }


def test_attention_text_too_faint_on_the_ground_fails_naming_the_pairing(
    write_theme, faint_attention_palette
):
    report = validate(load_palette(write_theme(faint_attention_palette)))

    assert not report.passed
    # A contrast failure is not a separation failure: the data colours are untouched.
    assert report.failures == ()
    failing = {(pair.foreground, pair.background) for pair in report.contrast_failures}
    assert failing == {("accent-strong", "surface"), ("accent-strong", "surface-alt")}
    assert all(pair.ratio < report.contrast_threshold for pair in report.contrast_failures)
