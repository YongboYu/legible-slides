"""Smoke tests for the `legible` command.

A thin gate over a tested seam. What the emitter produces is settled in test_css.py and what
counts as a violation in test_lint.py; what is checked here is the part only the command has —
where the bytes go, and the exit codes the CI gates key on.
"""

import json
from pathlib import Path

import pytest

from legible import gen_css, load_palette
from legible.command import main

DECKS = Path(__file__).resolve().parent / "fixtures" / "decks"


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


def test_lint_exits_zero_on_a_deck_that_breaks_no_rule(capsys, themes_dir):
    code = main(["lint", str(DECKS / "clean.md"), "--theme", str(themes_dir / "kuleuven.json")])

    assert code == 0
    assert capsys.readouterr().out.startswith("PASS")


def test_lint_exits_non_zero_on_a_violation_and_names_the_slide_and_the_rule(capsys):
    """The whole point of a mechanical gate: an objective violation blocks, and the report says
    which slide to open and which rule to read."""
    code = main(["lint", str(DECKS / "bullet-ceiling.md")])

    out = capsys.readouterr().out
    assert code == 1
    assert out.startswith("FAIL")
    assert "slide 2" in out
    assert "bullet-ceiling" in out


def test_a_warning_alone_leaves_the_exit_code_at_zero(capsys):
    """`established-terminology` can override the wordlist, so a hit reports without blocking."""
    code = main(["lint", str(DECKS / "no-inflated-register.md")])

    out = capsys.readouterr().out
    assert code == 0
    assert out.startswith("PASS")
    assert "no-inflated-register" in out


def test_lint_fails_on_a_theme_below_the_floor(capsys, write_theme, colliding_palette):
    code = main(["lint", str(DECKS / "clean.md"), "--theme", str(write_theme(colliding_palette))])

    out = capsys.readouterr().out
    assert code == 1
    assert "separation-floor" in out


def test_a_deck_that_cannot_be_read_is_not_a_violation(capsys, tmp_path):
    """Exit 1 means "this deck breaks a rule". A file nobody could read cannot say that."""
    code = main(["lint", str(tmp_path / "absent.md")])

    assert code == 2
    assert "absent.md" in capsys.readouterr().err


def test_a_theme_that_could_not_be_checked_is_not_a_violation_either(capsys, tmp_path):
    code = main(["lint", str(DECKS / "clean.md"), "--theme", str(tmp_path / "absent.json")])

    assert code == 2
    assert "absent.json" in capsys.readouterr().err


def test_a_violation_outranks_a_theme_that_could_not_be_checked(tmp_path):
    """Both are non-zero, so either blocks — but 1 is the more actionable of the two."""
    code = main(
        ["lint", str(DECKS / "bullet-ceiling.md"), "--theme", str(tmp_path / "absent.json")]
    )

    assert code == 1


def test_rules_prints_a_named_rule_as_the_canon_states_it(capsys):
    """How the review loads what it is reviewing against, with or without a checkout to read."""
    code = main(["rules", "one-message"])

    out = capsys.readouterr().out
    assert code == 0
    assert "`one-message`" in out
    assert "every slide answers exactly one question" in out
    # One rule asked for is one rule printed: the canon is long, and a reviewer reads what it loads.
    assert "bullet-ceiling" not in out


def test_rules_selects_by_section_and_by_which_side_of_the_seam_decides(capsys):
    """The anti-slop pass asks the canon which rules it has rather than carrying a list of them."""
    code = main(["rules", "--section", "voice", "--decided-by", "judgment"])

    out = capsys.readouterr().out
    assert code == 0
    assert "no-reflexive-tricolon" in out
    assert "no-em-dash-headline" not in out


def test_rules_json_carries_the_seam_and_the_thresholds(capsys):
    code = main(["rules", "separation-floor", "--json"])

    printed = json.loads(capsys.readouterr().out)
    assert code == 0
    assert printed[0]["id"] == "separation-floor"
    assert printed[0]["decided_by"] == ["script"]
    assert printed[0]["thresholds"]["delta-e-floor"] == "15.0"


def test_a_rule_the_canon_does_not_carry_is_not_a_rule_to_review_against(capsys):
    code = main(["rules", "one-message", "no-such-rule"])

    assert code == 2
    assert "no-such-rule" in capsys.readouterr().err


def test_a_selection_matching_nothing_says_so_rather_than_printing_nothing(capsys):
    """A review that loaded no rule would report no finding, and read as a pass."""
    code = main(["rules", "--section", "prosody"])

    assert code == 2
    assert "prosody" in capsys.readouterr().err


def test_lint_json_emits_the_findings_verbatim(capsys):
    code = main(["lint", str(DECKS / "word-ceiling.md"), "--json"])

    report = json.loads(capsys.readouterr().out)
    assert code == 1
    assert report["passed"] is False
    assert report["findings"] == [
        {
            "rule": "word-ceiling",
            "severity": "error",
            "slide": 2,
            "message": report["findings"][0]["message"],
        }
    ]
