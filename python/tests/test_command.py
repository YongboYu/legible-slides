"""Smoke tests for the `legible` command.

A thin gate over a tested seam. What the emitter produces is settled in test_css.py; what is
checked here is the part only the command has — where the bytes go, and the exit code the CI
staleness gate keys on.
"""

import pytest

from legible import gen_css, load_palette
from legible.command import main


def test_gen_css_writes_the_stylesheet_to_stdout_by_default(capsys, base_palette, write_theme):
    theme = write_theme(base_palette)

    code = main(["gen-css", str(theme)])

    assert code == 0
    assert capsys.readouterr().out == gen_css(load_palette(theme))


def test_gen_css_writes_the_stylesheet_to_the_path_it_is_given(tmp_path, base_palette, write_theme):
    theme = write_theme(base_palette)
    output = tmp_path / "styles" / "tokens.css"

    code = main(["gen-css", str(theme), "--output", str(output)])

    assert code == 0
    assert output.read_text(encoding="utf-8") == gen_css(load_palette(theme))


def test_check_passes_when_the_stylesheet_matches_its_palette(tmp_path, base_palette, write_theme):
    theme = write_theme(base_palette)
    output = tmp_path / "tokens.css"
    output.write_text(gen_css(load_palette(theme)), encoding="utf-8")

    code = main(["gen-css", str(theme), "--output", str(output), "--check"])

    assert code == 0


def test_check_fails_on_a_stale_stylesheet_and_says_how_to_regenerate_it(
    capsys, tmp_path, base_palette, write_theme
):
    """The whole point of the gate: the palette moved and the committed file did not."""
    theme = write_theme(base_palette)
    output = tmp_path / "tokens.css"
    output.write_text(gen_css(load_palette(theme)), encoding="utf-8")
    base_palette["accent"] = "#b35c00"
    write_theme(base_palette)

    code = main(["gen-css", str(theme), "--output", str(output), "--check"])

    assert code == 1
    err = capsys.readouterr().err
    assert str(output) in err
    assert "gen-css" in err


def test_check_fails_when_the_stylesheet_has_never_been_generated(
    capsys, tmp_path, base_palette, write_theme
):
    theme = write_theme(base_palette)
    output = tmp_path / "tokens.css"

    code = main(["gen-css", str(theme), "--output", str(output), "--check"])

    assert code == 1
    assert str(output) in capsys.readouterr().err


def test_check_never_writes_the_file_it_is_checking(tmp_path, base_palette, write_theme):
    """A gate that fixes what it measures cannot fail, and CI would go quietly green."""
    theme = write_theme(base_palette)
    output = tmp_path / "tokens.css"
    output.write_text("/* stale */\n", encoding="utf-8")

    main(["gen-css", str(theme), "--output", str(output), "--check"])

    assert output.read_text(encoding="utf-8") == "/* stale */\n"


def test_a_theme_that_cannot_be_read_is_not_a_stale_stylesheet(capsys, tmp_path):
    """Exit 1 means "the committed file is out of date". A file nobody could read cannot say
    that — the same distinction cvd-validate draws."""
    code = main(["gen-css", str(tmp_path / "absent.json")])

    assert code == 2
    assert "absent.json" in capsys.readouterr().err


def test_a_theme_that_breaks_the_schema_names_the_role_it_is_missing(
    capsys, base_palette, write_theme
):
    del base_palette["muted"]

    code = main(["gen-css", str(write_theme(base_palette))])

    assert code == 2
    assert "muted" in capsys.readouterr().err


def test_checking_without_an_output_path_is_an_argument_error(base_palette, write_theme):
    """There is nothing to compare a stylesheet on stdout against."""
    with pytest.raises(SystemExit) as exit_:
        main(["gen-css", str(write_theme(base_palette)), "--check"])

    assert exit_.value.code == 2
