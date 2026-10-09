"""Smoke tests for the `cvd-validate` console script.

A thin gate over a tested seam. What counts as a separation failure is settled in
test_validate.py; what is checked here is the part only the command has — the **exit code**
everything downstream keys on, and that `--json` round-trips into the documented report shape.
"""

import json

from legible import load_palette, validate
from legible.cli import main


def test_a_passing_theme_exits_zero_and_prints_the_achieved_minimum(capsys, themes_dir):
    """Headroom — or the lack of it — has to be visible on a pass, not only on a failure."""
    theme = themes_dir / "leuven-blue.json"
    report = validate(load_palette(theme))

    code = main([str(theme)])

    out = capsys.readouterr().out
    assert code == 0
    assert out.startswith("PASS")
    assert f"{min(report.min_delta_e.values()):.1f}" in out
    for condition in report.min_delta_e:
        assert condition in out


def test_a_colliding_palette_exits_one_and_names_the_pair_by_role(
    capsys, write_theme, colliding_palette
):
    code = main([str(write_theme(colliding_palette))])

    out = capsys.readouterr().out
    assert code == 1
    assert out.startswith("FAIL")
    assert "series-1 ↔ series-2" in out
    # By role, so the author knows which colour to change. Never by hex.
    for colour in colliding_palette["series"]:
        assert colour not in out


def test_a_grayscale_warning_alone_leaves_the_exit_code_at_zero(
    capsys, write_theme, grayscale_clash_palette
):
    """`never-sole-channel` is the fix the method already mandates, so grayscale cannot block."""
    code = main([str(write_theme(grayscale_clash_palette))])

    out = capsys.readouterr().out
    assert code == 0
    assert out.startswith("PASS")
    assert "series-1 ↔ series-2" in out


def test_one_failing_theme_among_several_fails_the_whole_run(
    capsys, write_theme, colliding_palette, themes_dir
):
    """What the CI gate rides on: every theme is reported, and one failure is enough."""
    code = main([str(themes_dir / "leuven-blue.json"), str(write_theme(colliding_palette))])

    out = capsys.readouterr().out
    assert code == 1
    assert "PASS" in out
    assert "FAIL" in out


def test_json_emits_the_report_verbatim(capsys, themes_dir):
    theme = themes_dir / "leuven-blue.json"
    expected = validate(load_palette(theme))

    code = main([str(theme), "--json"])

    report = json.loads(capsys.readouterr().out)
    assert code == 0
    assert report["passed"] is True
    assert report["threshold"] == expected.threshold
    assert report["min_delta_e"] == expected.min_delta_e
    assert report["grayscale_min"] == expected.grayscale_min
    assert report["failures"] == []
    assert report["warnings"] == [warning._asdict() for warning in expected.warnings]
    assert report["groups"]["G1"]["roles"] == list(expected.groups["G1"].roles)
    assert report["groups"]["G2"]["min_delta_e"] == expected.groups["G2"].min_delta_e


def test_json_failures_carry_the_condition_and_both_roles(capsys, write_theme, colliding_palette):
    code = main([str(write_theme(colliding_palette)), "--json"])

    report = json.loads(capsys.readouterr().out)
    assert code == 1
    assert report["passed"] is False
    pairs = {
        (failure["condition"], failure["role_a"], failure["role_b"])
        for failure in report["failures"]
    }
    assert ("normal", "series-1", "series-2") in pairs
    assert all(failure["delta_e"] < report["threshold"] for failure in report["failures"])


def test_json_emits_one_report_per_theme_in_argument_order(
    capsys, themes_dir, write_theme, grayscale_clash_palette
):
    """One object per line, so the shape of a report never depends on how many were asked for.

    Two palettes whose grayscale minima differ, so the order is something the assertion can see."""
    themes = [write_theme(grayscale_clash_palette), themes_dir / "leuven-blue.json"]

    code = main([*(str(theme) for theme in themes), "--json"])

    lines = capsys.readouterr().out.splitlines()
    assert code == 0
    assert [json.loads(line)["grayscale_min"] for line in lines] == [
        validate(load_palette(theme)).grayscale_min for theme in themes
    ]


def test_a_theme_that_cannot_be_read_is_neither_a_pass_nor_a_separation_failure(capsys, tmp_path):
    """Exit 1 means "this palette fails the floor". An unreadable file must not claim that."""
    code = main([str(tmp_path / "absent.json")])

    assert code == 2
    assert "absent.json" in capsys.readouterr().err


def test_a_theme_that_breaks_the_schema_names_the_role_it_is_missing(
    capsys, write_theme, base_palette
):
    del base_palette["muted"]

    code = main([str(write_theme(base_palette))])

    assert code == 2
    assert "muted" in capsys.readouterr().err


def test_an_unreadable_theme_does_not_silence_the_themes_named_after_it(
    capsys, tmp_path, themes_dir
):
    """The CI gate hands over every theme at once, so one bad file must not hide the rest."""
    code = main([str(tmp_path / "absent.json"), str(themes_dir / "leuven-blue.json")])

    captured = capsys.readouterr()
    assert code == 2
    assert "absent.json" in captured.err
    assert captured.out.startswith("PASS")


def test_a_theme_of_the_wrong_shape_does_not_silence_the_themes_named_after_it(
    capsys, write_theme, base_palette, themes_dir
):
    """Valid JSON that is no theme is as unreadable as a missing file, and not a crash."""
    base_palette["meta"] = None

    code = main([str(write_theme(base_palette)), str(themes_dir / "leuven-blue.json")])

    captured = capsys.readouterr()
    assert code == 2
    assert "meta" in captured.err
    assert captured.out.startswith("PASS")


def test_a_palette_below_the_floor_outranks_a_theme_that_could_not_be_read(
    capsys, tmp_path, write_theme, colliding_palette
):
    """Both are non-zero, so either blocks — but 1 is the more actionable of the two."""
    code = main([str(tmp_path / "absent.json"), str(write_theme(colliding_palette))])

    assert code == 1


def test_a_failing_attention_pairing_exits_one_and_names_it_by_role(
    capsys, write_theme, faint_attention_palette
):
    code = main([str(write_theme(faint_attention_palette))])

    out = capsys.readouterr().out
    assert code == 1
    assert out.startswith("FAIL")
    assert "accent-strong on surface" in out
    assert faint_attention_palette["accent-strong"] not in out


def test_a_passing_theme_prints_the_attention_contrast_it_achieved(capsys, themes_dir):
    main([str(themes_dir / "leuven-blue.json")])

    out = capsys.readouterr().out
    assert "ink on accent" in out
    assert "4.65" in out
