"""The rules a script decides.

One assertion per rule, at the boundary the canon draws: the ceiling is *exceeded* rather than
reached, a warning never fails the deck, and every finding names the slide and the rule it
enforces. The palette check is asserted through what the validator's exit code makes of a theme,
because that exit code is the whole interface — this linter does no colour arithmetic of its own.
"""

from pathlib import Path

import pytest

from legible.lint import lint
from legible.method import ELEMENTS_PER_SLIDE, FLOOR_PX, WORDS_PER_SLIDE

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


#: A claim that fills most of two rendered lines, and one grown past them. Their line counts are
#: Chromium's, in ``test_headline.py``.
TWO_LINE_HEADLINE = (
    "Used as they are, pre-trained forecasters cut the error by 17 to 28%, but the process models "
    "they forecast are no better."
)
THREE_LINE_HEADLINE = f"{TWO_LINE_HEADLINE[:-1]}, and on Sepsis they are much worse than last week."


def test_a_headline_past_two_rendered_lines_is_a_finding(write_deck):
    """The canon's ceiling, measured as the slide sets the headline. It carries no severity of its
    own, so it gates."""
    report = lint(write_deck(f"# {THREE_LINE_HEADLINE}\n"))

    assert rules(report) == ["headline-shape"]
    (finding,) = report.findings
    assert finding.severity == "error"
    assert "3 lines" in finding.message
    # What runs past the ceiling, so the author can see what has to go.
    assert "'Sepsis they are much worse than last week.'" in finding.message


def test_a_headline_that_fills_two_lines_is_not(write_deck):
    """Twenty-two words, and still two lines: the ceiling is lines, not words."""
    report = lint(write_deck(f"# {TWO_LINE_HEADLINE}\n"))

    assert report.findings == ()


def test_the_cover_s_title_is_not_a_headline(write_deck):
    """The cover is set heavier and has no headline zone for a third line to run into."""
    report = lint(
        write_deck(
            f"""\
            ---
            layout: cover
            ---

            # {THREE_LINE_HEADLINE}
            """
        )
    )

    assert report.findings == ()


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


def _sectioned(names, backup=()):
    """A deck with one slide per section name, the ones in ``backup`` declared as backup."""
    slides = []
    for name in names:
        flag = "\nbackup: true" if name in backup else ""
        slides.append(f"---\nsection: {name}{flag}\n---\n\n# A claim about {name.lower()}\n")
    return "\n".join(slides)


def test_more_sections_than_the_map_holds_is_a_warning(write_deck):
    """The label with a count still fits a deck that outgrew the map, so it warns and never gates.
    It names the slide the first section too many starts on, which is where a merge would go."""
    report = lint(write_deck(_sectioned(["One", "Two", "Three", "Four", "Five", "Six"])))

    assert rules(report) == ["section-locator"]
    assert [finding.severity for finding in report.findings] == ["warning"]
    assert [finding.slide for finding in report.findings] == [6]
    assert report.passed


def test_sitting_on_the_section_ceiling_is_not(write_deck):
    report = lint(write_deck(_sectioned(["One", "Two", "Three", "Four", "Five"])))

    assert report.findings == ()


def test_a_section_declared_again_is_still_one_section(write_deck):
    report = lint(write_deck(_sectioned(["One", "Two", "Three", "Four", "Five", "Two"])))

    assert report.findings == ()


def test_a_section_label_longer_than_the_map_holds_is_a_warning(write_deck):
    report = lint(write_deck(_sectioned(["Evaluations"])))

    assert rules(report) == ["section-locator"]
    assert [finding.severity for finding in report.findings] == ["warning"]
    assert "Evaluations" in report.findings[0].message


def test_a_section_label_on_the_ceiling_is_not(write_deck):
    report = lint(write_deck(_sectioned(["Evaluation"])))

    assert report.findings == ()


def test_backup_sections_are_outside_the_map(write_deck):
    """A backup shows its own label and no position, so it is not one of the map's sections: it
    neither counts towards the ceiling nor has to fit in one."""
    report = lint(
        write_deck(
            _sectioned(
                ["One", "Two", "Three", "Four", "Five", "Questions and answers"],
                backup=("Questions and answers",),
            )
        )
    )

    assert report.findings == ()


# ── type-scale ────────────────────────────────────────────────────────────────


def _sized(body: str) -> str:
    return f"# Retrieval carries the long tail at a tenth of the cost\n\n{body}\n"


def messages(report):
    return [finding.message for finding in report.findings]


@pytest.mark.parametrize(
    "body",
    [
        '<p style="font-size: 20px">Source: three runs.</p>',
        '<p style="color: red; font-size:24px;">Source: three runs.</p>',
        "<style>\n.source { font-size: 30px; }\n</style>",
        "<p :style=\"{ fontSize: '20px' }\">Source: three runs.</p>",
        '<p class="text-[20px]">Source: three runs.</p>',
    ],
)
def test_an_inline_px_size_is_a_finding_even_above_the_floor(write_deck, body):
    """Slides size text through the template's classes, so the floor can be checked: a px size
    written into a slide is the hole the floor would leak through, whatever it says today."""
    report = lint(write_deck(_sized(body)))

    assert rules(report) == ["type-scale"]
    assert "inline" in messages(report)[0]
    assert not report.passed


@pytest.mark.parametrize(
    ("body", "px"),
    [
        ('<p style="font-size: 0.75rem">Source.</p>', "12"),
        ('<p style="font-size: 10pt">Source.</p>', "13.3"),
        ('<p class="text-xs">Source.</p>', "12"),
        ('<p class="mt-2 text-sm">Source.</p>', "14"),
        ('<p class="text-base">Source.</p>', "16"),
    ],
)
def test_a_size_below_the_floor_is_a_finding(write_deck, body, px):
    report = lint(write_deck(_sized(body)))

    assert rules(report) == ["type-scale"]
    assert f"{px} px, below the {FLOOR_PX} px floor" in messages(report)[0]


def test_an_inline_px_size_below_the_floor_says_both(write_deck):
    report = lint(write_deck(_sized('<span style="font-size: 12px">small</span>')))

    assert len(report.findings) == 1
    assert "inline" in messages(report)[0]
    assert f"below the {FLOOR_PX} px floor" in messages(report)[0]


@pytest.mark.parametrize(
    "body",
    [
        '<p class="text-lg">At the floor.</p>',
        '<p class="text-xl text-red-500">Above it.</p>',
        '<p style="font-size: 1.25rem">Above it, in rem.</p>',
        '<p style="font-size: 0.8em">Relative to its parent, which the theme sizes.</p>',
        "```css\n.caption { font-size: 12px; }\n```",
        "Prose that mentions font-size: 12px is not markup.",
    ],
)
def test_sizes_on_or_above_the_floor_and_sizes_that_are_not_styles_pass(write_deck, body):
    """A size the template's own scale resolves, a size a reader cannot resolve without the page,
    and a size written as an example in a code block or a sentence are none of them findings."""
    report = lint(write_deck(_sized(body)))

    assert report.findings == ()


def test_a_size_in_the_speaker_notes_is_not_on_the_slide(write_deck):
    notes = '<!--\nSay it at <span style="font-size: 8px">8px</span>.\n-->'
    report = lint(write_deck(_sized(notes)))

    assert report.findings == ()


def test_an_svg_size_on_a_slide_is_an_inline_px_size(write_deck):
    """An SVG's ``font-size`` attribute is a size written into the slide, in px by another name."""
    svg = '<svg viewBox="0 0 400 100"><text font-size="8">Encoder</text></svg>'
    report = lint(write_deck(_sized(svg)))

    assert rules(report) == ["type-scale"]
    assert "inline" in messages(report)[0]
    assert f"8 px, below the {FLOOR_PX} px floor" in messages(report)[0]


@pytest.mark.parametrize(
    ("path", "source"),
    [
        (
            "components/Pipeline.vue",
            '<template><p class="tiny">x</p></template>\n'
            "<style scoped>\n.tiny { font-size: 8px; }\n</style>\n",
        ),
        (
            "components/Pipeline.vue",
            '<template><svg><text font-size="8">x</text></svg></template>\n',
        ),
        ("components/nested/Box.vue", '<template><p class="text-xs">x</p></template>\n'),
        ("style.css", ".label { font-size: 0.5rem; }\n"),
        ("styles/diagram.css", ".label { font-size: 9pt; }\n"),
    ],
)
def test_type_below_the_floor_in_the_decks_own_components_is_a_finding(
    write_deck, tmp_path, path, source
):
    """The slide is not the only place a deck sets type: a component's text lands on the slide
    just the same, and a lint that read only slides.md would pass it."""
    deck = write_deck(_sized("<Pipeline />"))
    (tmp_path / path).parent.mkdir(parents=True, exist_ok=True)
    (tmp_path / path).write_text(source, encoding="utf-8")

    report = lint(deck)

    assert rules(report) == ["type-scale"]
    finding = report.findings[0]
    assert finding.slide is None
    assert finding.message.startswith(path)
    assert f"below the {FLOOR_PX} px floor" in finding.message
    assert not report.passed


@pytest.mark.parametrize(
    "css",
    [
        ".label { font-size: var(--floor-px); }",
        ".label { font-size: 24px; }",
        ".label { font-size: calc(var(--body-px) * 0.5); }",
        ".label { font-size: 0.8em; }",
    ],
)
def test_component_sizes_at_the_floor_or_relative_to_the_page_pass(write_deck, tmp_path, css):
    """A component is the deck's own template, so a px size at or above the floor is how it works,
    and a relative size is the rendered slide's to measure."""
    deck = write_deck(_sized("<Pipeline />"))
    (tmp_path / "components").mkdir()
    (tmp_path / "components" / "Pipeline.vue").write_text(
        f'<template><p class="label">x</p></template>\n<style>\n{css}\n</style>\n',
        encoding="utf-8",
    )

    assert lint(deck).findings == ()


def test_the_flagship_deck_holds_the_floor():
    report = lint(Path(__file__).resolve().parents[2] / "deck" / "slides.md")

    assert [finding for finding in report.findings if finding.rule == "type-scale"] == []
    assert report.passed


#: A deck's last main slide, once the rule has something to read: a claim before it, so the deck has
#: a talk to close.
_OPENING = "# Retrieval beats fine-tuning at a tenth of the cost\n\nEvidence beside it.\n\n---\n\n"


@pytest.mark.parametrize(
    "headline",
    ["Thank you!", "Thanks", "Questions?", "Any questions?", "Q&A", "Conclusion", "Summary"],
)
def test_closing_on_a_label_is_a_warning(write_deck, headline):
    """`conclusion-stays-up`: the slide left up through Q&A is the answers, so a closing label put
    there hides them. It warns, because whether the slide answers the questions is judgment."""
    report = lint(write_deck(f"{_OPENING}# {headline}\n"))

    assert rules(report) == ["conclusion-stays-up"]
    assert [finding.severity for finding in report.findings] == ["warning"]
    assert [finding.slide for finding in report.findings] == [2]
    assert report.passed


def test_a_thank_you_inside_a_longer_headline_still_reads_as_one(write_deck):
    report = lint(write_deck(f"{_OPENING}# Thank you for listening to all of this\n"))

    assert rules(report) == ["conclusion-stays-up"]


def test_closing_with_no_headline_is_a_warning(write_deck):
    report = lint(write_deck(f"{_OPENING}A slide with words on it and nothing above them.\n"))

    assert rules(report) == ["conclusion-stays-up"]
    assert "no headline" in report.findings[0].message


def test_closing_on_a_claim_is_not(write_deck):
    """Naming the questions is what a conclusion does, so the word alone is not the tell."""
    report = lint(write_deck(f"{_OPENING}# All three research questions have an answer here\n"))

    assert report.findings == ()


def test_the_backups_after_the_close_are_not_the_close(write_deck):
    """The last *main* slide is the one left up. Backups sit after it, and a backup carries forward
    onto the slides after it like any section, so none of them is read as the close."""
    deck = (
        f"{_OPENING}# The method holds on every deck we tried\n\n---\n"
        "section: Backup\nbackup: true\n---\n\n# Sources\n\n---\n\n# More detail\n"
    )

    assert lint(write_deck(deck)).findings == ()


def test_a_thank_you_before_the_backups_is_still_the_close(write_deck):
    deck = f"{_OPENING}# Thank you\n\n---\nsection: Backup\nbackup: true\n---\n\n# Sources\n"
    report = lint(write_deck(deck))

    assert rules(report) == ["conclusion-stays-up"]
    assert [finding.slide for finding in report.findings] == [2]


def test_a_main_section_after_a_backup_ends_the_backups(write_deck):
    deck = (
        f"{_OPENING}# The method holds on every deck we tried\n\n"
        "---\nsection: Backup\nbackup: true\n---\n\n# Sources\n\n"
        "---\nsection: Close\n---\n\n# Questions?\n"
    )
    report = lint(write_deck(deck))

    assert rules(report) == ["conclusion-stays-up"]
    assert [finding.slide for finding in report.findings] == [4]


# ── the review advisories ─────────────────────────────────────────────────────
#
# Each one warns and never gates: the deck still passes, and the finding is the review's to weigh.


def _advisory(report, rule):
    """Exactly one finding, of ``rule``, as a warning that leaves the deck passing."""
    assert rules(report) == [rule]
    assert [finding.severity for finding in report.findings] == ["warning"]
    assert report.passed


def _paragraphs(count):
    return "\n\n".join(f"Evidence number {index}." for index in range(1, count + 1))


def test_more_visual_groups_than_the_ceiling_is_an_advisory(write_deck):
    report = lint(write_deck(f"# A claim\n\n{_paragraphs(ELEMENTS_PER_SLIDE + 1)}\n"))

    _advisory(report, "element-ceiling")
    assert f"{ELEMENTS_PER_SLIDE + 1} visual groups" in report.findings[0].message


def test_sitting_on_the_element_ceiling_is_not(write_deck):
    report = lint(write_deck(f"# A claim\n\n{_paragraphs(ELEMENTS_PER_SLIDE)}\n"))

    assert report.findings == ()


def test_more_words_on_a_slide_than_the_ceiling_is_an_advisory(write_deck):
    """One word past the budget outside the headline, which is not counted however long it runs."""
    words = " ".join(["word"] * (WORDS_PER_SLIDE + 1))
    report = lint(write_deck(f"# A headline whose own words are never counted here\n\n{words}\n"))

    _advisory(report, "on-slide-words")
    assert f"{WORDS_PER_SLIDE + 1} words" in report.findings[0].message


def test_sitting_on_the_word_budget_is_not_and_a_figure_s_text_is_not_counted(write_deck):
    words = " ".join(["word"] * WORDS_PER_SLIDE)
    caption = " ".join(["caption"] * 30)
    report = lint(
        write_deck(f'# A claim\n\n{words}\n\n<Figure\n  src="/f.png"\n  caption="{caption}"\n/>\n')
    )

    assert report.findings == ()


def test_a_second_emphasised_span_is_an_advisory(write_deck):
    report = lint(write_deck("# A claim\n\nOne **signal** and a **second** one.\n"))

    _advisory(report, "signal-budget")
    assert "2 emphasised spans" in report.findings[0].message


def test_a_second_callout_is_an_advisory(write_deck):
    report = lint(
        write_deck(
            """\
            # A claim

            <Callout title="One">First.</Callout>

            <Callout title="Two">Second.</Callout>
            """
        )
    )

    _advisory(report, "signal-budget")
    assert "2 callouts" in report.findings[0].message


def test_one_emphasised_span_and_one_callout_are_the_budget(write_deck):
    report = lint(
        write_deck(
            """\
            # A claim

            One **signal**, and *terms* in italics.

            <Callout title="One">First.</Callout>
            """
        )
    )

    assert report.findings == ()


def _acronyms(*slides):
    return "\n---\n\n".join(f"# A claim\n\n{words}\n" for words in slides)


def test_a_sixth_new_abbreviation_is_an_advisory_on_the_slide_it_appears(write_deck):
    report = lint(write_deck(_acronyms("CVD, PDF and QR.", "AV and CSS, then CVD again.", "LLMs.")))

    _advisory(report, "acronym-budget")
    assert report.findings[0].slide == 3
    assert "'LLM'" in report.findings[0].message


def test_five_abbreviations_used_again_and_again_are_the_budget(write_deck):
    """A word that merely starts with a capital, or a mixed-case name, is not an abbreviation."""
    report = lint(
        write_deck(
            _acronyms("CVD, PDF and QR.", "AV and CSS, then CVD again.", "PowerPoint, I and A.")
        )
    )

    assert report.findings == ()


def test_abbreviations_on_backup_slides_are_outside_the_talk(write_deck):
    deck = _acronyms("CVD, PDF and QR.", "AV and CSS.") + (
        "\n---\nsection: Backup\nbackup: true\n---\n\n# A claim\n\nLLMs and TSFMs.\n"
    )

    assert lint(write_deck(deck)).findings == ()


def _paced(duration, *budgets):
    headmatter = f"---\nduration: {duration}\n---\n\n" if duration else ""
    slides = [f"# A claim\n\n<!--\nTime: {budget}\n-->\n" for budget in budgets]
    return headmatter + "\n---\n\n".join(slides)


def test_budgets_past_the_pace_share_are_an_advisory_on_the_slide_that_crosses_it(write_deck):
    """Eighteen minutes of a twenty-minute slot is 90%: over by the third slide."""
    report = lint(write_deck(_paced("20min", "6min", "1:00", "11min", "0s")))

    _advisory(report, "pace-budget")
    assert report.findings[0].slide == 3
    assert "85%" in report.findings[0].message


def test_budgets_on_the_pace_share_are_not(write_deck):
    """Seventeen minutes of twenty is exactly 85%: the ceiling is exceeded rather than reached."""
    report = lint(write_deck(_paced("20min", "8min 30s", "510s")))

    assert report.findings == ()


def test_pace_is_unchecked_without_a_slot(write_deck):
    report = lint(write_deck(_paced(None, "30min")))

    assert report.findings == ()


def test_backup_slides_are_not_budgeted_into_the_slot(write_deck):
    deck = _paced("10min", "8min") + (
        "\n---\nsection: Backup\nbackup: true\n---\n\n# A claim\n\n<!--\nTime: 5min\n-->\n"
    )

    assert lint(write_deck(deck)).findings == ()


def test_an_abbreviation_is_its_run_of_capitals_and_not_the_digits_beside_it(write_deck):
    """``BPI2017`` and ``BPI2019`` are one abbreviation the room has to hold, not two."""
    report = lint(write_deck(_acronyms("CVD, PDF and QR.", "AV, BPI2017 and BPI2019.", "BPIs.")))

    assert report.findings == ()


def test_a_budget_the_linter_cannot_read_is_an_advisory_rather_than_silence(write_deck):
    """Skipping it would undercount the talk and report a pace that fits."""
    report = lint(write_deck(_paced("20min", "5min", "about a minute")))

    _advisory(report, "pace-budget")
    assert report.findings[0].slide == 2
    assert "about a minute" in report.findings[0].message


def test_a_slot_the_linter_cannot_read_is_an_advisory_on_the_first_slide(write_deck):
    report = lint(write_deck(_paced("twenty", "5min")))

    _advisory(report, "pace-budget")
    assert report.findings[0].slide == 1


# ── exceptions ────────────────────────────────────────────────────────────────


def _six_bullets(notes: str) -> str:
    bullets = "\n".join(f"- step {n}" for n in range(1, 7))
    return f"# The derivation takes six steps\n\n{bullets}\n\n<!--\n{notes}\n-->\n"


def test_an_exception_with_a_reason_turns_a_defaults_error_into_a_warning(write_deck):
    """The author departs from a default on one slide and says why: the finding stays, carrying the
    reason for the review to weigh, and no longer gates."""
    notes = "Exception: bullet-ceiling each step is one line of the worked derivation"
    report = lint(write_deck(_six_bullets(notes)))

    assert rules(report) == ["bullet-ceiling"]
    finding = report.findings[0]
    assert finding.severity == "warning"
    assert finding.message.endswith("excepted: each step is one line of the worked derivation")
    assert report.passed


def test_an_exception_reaches_only_the_slide_and_rule_it_names(write_deck):
    deck = (
        _six_bullets("Exception: word-ceiling a reason about another rule")
        + "\n---\n\n"
        + (_six_bullets(""))
    )
    report = lint(write_deck(deck))

    assert [(f.rule, f.slide, f.severity) for f in report.findings] == [
        ("bullet-ceiling", 1, "error"),
        ("bullet-ceiling", 2, "error"),
    ]


def test_an_exception_without_a_reason_is_reported_and_not_applied(write_deck):
    report = lint(write_deck(_six_bullets("Exception: bullet-ceiling")))

    severities = {(f.rule, f.severity) for f in report.findings}
    assert severities == {("bullet-ceiling", "error"), ("bullet-ceiling", "warning")}
    assert any("gives no reason" in f.message for f in report.findings)
    assert not report.passed


def test_no_reason_clears_a_floor(write_deck):
    """The floor is a reader's access to the slide, not a default of the method's style."""
    slide = (
        "# Retrieval carries the long tail at a tenth of the cost\n\n"
        '<p class="text-xs">Source.</p>\n\n'
        "<!--\nException: type-scale the table has to fit\n-->\n"
    )
    report = lint(write_deck(slide))

    severities = sorted((f.rule, f.severity) for f in report.findings)
    assert severities == [("type-scale", "error"), ("type-scale", "warning")]
    assert any("part of the floor" in f.message for f in report.findings)
    assert not report.passed


def test_an_exception_naming_no_rule_is_reported(write_deck):
    report = lint(write_deck(_six_bullets("Exception: bullet-cieling a typo in the ID")))

    assert ("bullet-cieling", "warning") in {(f.rule, f.severity) for f in report.findings}
    assert not report.passed
