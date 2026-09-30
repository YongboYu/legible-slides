"""The rules a script decides.

One assertion per rule, at the boundary the canon draws: the ceiling is *exceeded* rather than
reached, a warning never fails the deck, and every finding names the slide and the rule it
enforces. The palette check is asserted through what the validator's exit code makes of a theme,
because that exit code is the whole interface — this linter does no colour arithmetic of its own.
"""

from pathlib import Path

import pytest

from legible.lint import lint

#: The fixture decks: one that breaks nothing, and one per rule, each named for the rule it breaks
#: so the deck and what it is expected to produce cannot drift apart.
DECKS = Path(__file__).resolve().parent / "fixtures" / "decks"
VIOLATION_DECKS = sorted(deck for deck in DECKS.glob("*.md") if deck.stem != "clean")


def rules(report):
    return [finding.rule for finding in report.findings]


def test_a_clean_slide_produces_nothing(write_deck):
    report = lint(
        write_deck(
            """\
            # Retrieval beats fine-tuning at a tenth of the cost

            - one point
            - a second point

            Evidence follows in the pane beside it.
            """
        )
    )

    assert report.passed
    assert report.findings == ()


def test_exceeding_the_bullet_ceiling_is_a_finding(write_deck):
    report = lint(
        write_deck(
            """\
            # Six things happened at once

            - one
            - two
            - three
            - four
            - five
            - six
            """
        )
    )

    assert rules(report) == ["bullet-ceiling"]
    assert not report.passed


def test_sitting_on_the_bullet_ceiling_is_not(write_deck):
    """The canon says the violation is *exceeding* it, so a slide sitting on the ceiling is a full
    slide rather than a fault."""
    report = lint(
        write_deck(
            """\
            # Five things happened at once

            - one
            - two
            - three
            - four
            - five
            """
        )
    )

    assert report.findings == ()


def test_exceeding_the_word_ceiling_on_a_bullet_is_a_finding(write_deck):
    report = lint(
        write_deck(
            """\
            # A claim

            - a bullet of thirteen words is a sentence and a sentence belongs elsewhere
            """
        )
    )

    assert rules(report) == ["word-ceiling"]


def test_sitting_on_the_word_ceiling_is_not(write_deck):
    report = lint(
        write_deck(
            """\
            # A claim

            - a bullet of twelve words is short enough to read at once
            """
        )
    )

    assert report.findings == ()


def test_an_em_dash_in_a_headline_is_a_finding(write_deck):
    report = lint(write_deck("# Retrieval wins — and it wins cheaply\n"))

    assert rules(report) == ["no-em-dash-headline"]


def test_an_em_dash_below_the_headline_is_not(write_deck):
    """The rule is about headlines. Prose may use one where it is genuinely the right mark."""
    report = lint(
        write_deck(
            """\
            # Retrieval wins, and it wins cheaply

            Cost fell by half — a result nobody expected.
            """
        )
    )

    assert report.findings == ()


def test_an_inflated_register_word_is_a_warning_rather_than_a_failure(write_deck):
    """`established-terminology` can legitimately override the wordlist, which is why the canon
    marks this one a warning — and why a deck carrying one still passes."""
    report = lint(
        write_deck(
            """\
            # A crucial result

            Evidence follows.
            """
        )
    )

    assert rules(report) == ["no-inflated-register"]
    assert report.findings[0].severity == "warning"
    assert report.passed


def test_an_inflated_register_word_is_found_wherever_it_is_written(write_deck):
    report = lint(
        write_deck(
            """\
            # A claim

            - we leverage the pipeline

            <!--
            A testament to the pipeline.
            -->
            """
        )
    )

    assert rules(report) == ["no-inflated-register", "no-inflated-register"]
    assert "leverage" in report.findings[0].message
    assert "testament to" in report.findings[1].message


def test_a_word_that_merely_contains_a_listed_one_is_not_a_hit(write_deck):
    report = lint(write_deck("# Robustness was never the question\n"))

    assert report.findings == ()


def test_a_skewed_sentence_opener_distribution_is_a_finding(write_deck):
    report = lint(
        write_deck(
            """\
            # A claim

            The first result held. The second held too. Costs fell by half.
            """
        )
    )

    assert rules(report) == ["opener-variety"]


def test_an_opener_at_half_the_passage_is_not(write_deck):
    """More than half, says the canon. Half is variety enough."""
    report = lint(
        write_deck(
            """\
            # A claim

            The first result held. The second held too. Costs fell by half. Latency held.
            """
        )
    )

    assert report.findings == ()


def test_a_monotonous_paragraph_is_not_diluted_by_the_paragraph_beside_it(write_deck):
    """A passage is a run of prose, not everything on the slide. Averaging the two would let a
    long second paragraph carry a monotonous first one under the ceiling — failing open."""
    report = lint(
        write_deck(
            """\
            # A claim

            The first result held. The second held too.

            Costs fell by half. Latency held. Nobody had to retune it. We shipped it.
            """
        )
    )

    assert rules(report) == ["opener-variety"]


def test_one_sentence_is_not_a_passage(write_deck):
    """The canon counts openers over a passage, not over one sentence — and a lone sentence
    opening with a listed word is otherwise a share of 1.0, which would flag every deck."""
    report = lint(write_deck("# A claim\n\nThe result held.\n"))

    assert report.findings == ()


def test_speaker_notes_are_a_passage_of_their_own(write_deck):
    report = lint(
        write_deck(
            """\
            # A claim

            <!--
            This is what I say here. This is what I say next. This is how I close.
            -->
            """
        )
    )

    assert rules(report) == ["opener-variety"]


def test_every_finding_names_the_slide_it_is_on(write_deck):
    report = lint(
        write_deck(
            """\
            # A clean claim

            ---

            # A second claim

            - one
            - two
            - three
            - four
            - five
            - six
            """
        )
    )

    assert [(finding.slide, finding.rule) for finding in report.findings] == [(2, "bullet-ceiling")]


def test_findings_arrive_in_slide_order(write_deck):
    report = lint(
        write_deck(
            """\
            # A crucial claim

            ---

            # A claim — with a dash
            """
        )
    )

    assert [finding.slide for finding in report.findings] == [1, 2]


def test_a_deck_that_cannot_be_read_raises(tmp_path):
    with pytest.raises(OSError):
        lint(tmp_path / "absent.md")


def test_a_theme_below_the_floor_is_a_finding_against_the_deck(
    write_deck, write_theme, colliding_palette
):
    """The palette check is the validator's exit code, nothing more: no colour arithmetic happens
    here, so there is no second implementation of the simulation to disagree with the first."""
    deck = write_deck("# A claim\n")

    report = lint(deck, themes=[write_theme(colliding_palette)])

    assert rules(report) == ["separation-floor"]
    assert report.findings[0].slide is None
    assert not report.passed


def test_a_theme_that_clears_the_floor_is_not(write_deck, themes_dir):
    report = lint(write_deck("# A claim\n"), themes=[themes_dir / "leuven-blue.json"])

    assert report.findings == ()
    assert report.unchecked == ()


def test_a_theme_that_could_not_be_read_is_unchecked_rather_than_a_violation(write_deck, tmp_path):
    """The validator distinguishes the two by exit code, so the linter does not collapse them: a
    palette nobody could measure makes no claim about its colours. Turning that into a non-zero
    exit is the command's business, the same split `cvd-validate` already draws."""
    report = lint(write_deck("# A claim\n"), themes=[tmp_path / "absent.json"])

    assert report.findings == ()
    assert report.passed
    assert [unchecked.theme for unchecked in report.unchecked] == [str(tmp_path / "absent.json")]


def test_the_clean_fixture_deck_produces_no_findings():
    """A deck written to the method, carrying the chrome a real one carries — headmatter, layouts,
    a figure, notes and a code block. Anything the linter says about it is a false positive."""
    report = lint(DECKS / "clean.md")

    assert report.passed
    assert report.findings == ()


@pytest.mark.parametrize("deck", VIOLATION_DECKS, ids=lambda deck: deck.stem)
def test_each_violation_fixture_deck_produces_exactly_its_own_finding(deck):
    """One deck per rule, each breaking that rule and no other: a check that fires on the wrong
    deck is as broken as one that never fires."""
    report = lint(deck)

    assert rules(report) == [deck.stem]
    assert [finding.slide for finding in report.findings] == [2]
