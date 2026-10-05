from textwrap import dedent

import pytest

from legible import DELTA_E_FLOOR, load_palette, validate
from legible.method import (
    ATTENTION_CONTRAST_MIN,
    ATTENTION_CONTRAST_PAIRS,
    BULLETS_PER_SLIDE,
    CANON,
    EM_DASHES_PER_HEADLINE,
    INFLATED_REGISTER_SEVERITY,
    INFLATED_REGISTER_WORDS,
    OPENER_SHARE_MAX,
    OPENER_WORDS,
    SECTION_LABEL_CHARS_MAX,
    SECTION_LOCATOR_SEVERITY,
    SECTIONS_MAX,
    WORDS_PER_BULLET,
    MethodError,
    rule,
    rule_thresholds,
    rules,
)

CANON_EXCERPT = dedent(
    """\
    ### `separation-floor`: data colours stay perceptually separated

    Every pair of data colours that can share one chart axis stays above the floor.

    **Decided by** script · **Threshold** `delta-e-floor = 22.5`,
    `delta-e-metric = CAM02-UCS`, `cvd-severity = 80`,
    `cvd-conditions = [normal, deuteranomaly, protanomaly, tritanomaly]`,
    `grayscale = advisory` (violation when a pair's ΔE is below `delta-e-floor`)

    ---

    ### `motion-purpose`: motion segments or depicts

    **Decided by** judgment · **Threshold** `animation-seconds-max = 15`
    """
)

SUBSECTION_EXCERPT = dedent(
    """\
    ### 7a. Script-decided

    #### `opener-variety`: no more than half the sentences open the same way

    **Decided by** script · **Threshold** `opener-words = [The, This, It, In]`,
    `opener-share-max = 0.5`

    ### 7b. Judgment

    Every rule in this subsection carries no threshold, but this prose does: `not-a-rule = 99`.
    """
)


def test_a_rule_comes_back_as_the_canon_states_it():
    """What the review loads is the rule itself — its claim, and the prose that qualifies it —
    because a reviewer handed a rule ID and nothing else would have to remember the rest."""
    floor = rule("separation-floor", canon=CANON_EXCERPT)

    assert floor.statement == "data colours stay perceptually separated"
    assert "Every pair of data colours that can share one chart axis" in floor.text
    assert floor.thresholds["delta-e-floor"] == "22.5"


def test_a_threshold_is_quoted_from_the_canon_rather_than_re_derived():
    """Change the canon and the number changes — that is what "quote it" has to mean."""
    thresholds = rule_thresholds("separation-floor", canon=CANON_EXCERPT)

    assert thresholds["delta-e-floor"] == "22.5"
    assert thresholds["cvd-severity"] == "80"
    assert thresholds["delta-e-metric"] == "CAM02-UCS"


def test_thresholds_stop_at_the_rule_they_belong_to():
    thresholds = rule_thresholds("separation-floor", canon=CANON_EXCERPT)

    assert "animation-seconds-max" not in thresholds


def test_a_rule_the_canon_does_not_carry_is_an_error():
    with pytest.raises(MethodError, match="no-such-rule"):
        rule_thresholds("no-such-rule", canon=CANON_EXCERPT)


def test_a_rule_stated_under_a_subsection_is_read_like_any_other():
    """The voice rules sit a heading level deeper than the rest. A reader does not care, and
    neither may the parser — a rule the canon states is a rule the linter can quote."""
    thresholds = rule_thresholds("opener-variety", canon=SUBSECTION_EXCERPT)

    assert thresholds["opener-share-max"] == "0.5"


def test_a_threshold_footer_stops_at_the_end_of_its_own_paragraph():
    """The last rule of a subsection runs on into prose that is nobody's threshold."""
    thresholds = rule_thresholds("opener-variety", canon=SUBSECTION_EXCERPT)

    assert "not-a-rule" not in thresholds


def test_a_rule_states_which_side_of_the_seam_it_falls_on():
    """The seam the review is built along: what a script settles, and what a reader must."""
    assert rule("bullet-ceiling").decided_by == ("script",)
    assert rule("one-message").decided_by == ("judgment",)
    # A mixed rule names both halves, in the order the canon splits them.
    assert rule("never-sole-channel").decided_by == ("script", "judgment")


def test_a_rule_inherits_the_decision_its_subsection_states_once():
    """The canon says `**Decided by** judgment` once for a subsection rather than on each rule
    under it. A reader takes that as read, and so must anything reading the same page."""
    assert rule("no-reflexive-tricolon").decided_by == ("judgment",)


def test_the_judgment_rules_of_a_section_are_the_canons_to_name():
    """What the review's anti-slop pass loads. It asks for a section and a side of the seam rather
    than for a list of IDs, so a voice rule the canon grows is reviewed with nothing else edited."""
    voice = {rule_.id for rule_ in rules(section="voice", decided_by="judgment")}

    assert "no-contrast-for-emphasis" in voice
    assert "no-reflexive-tricolon" in voice
    # The script-decided half of the same section stays with the linter.
    assert "no-em-dash-headline" not in voice


def test_a_section_the_canon_does_not_have_selects_nothing():
    assert rules(section="prosody") == ()


def test_a_heading_between_a_subsection_and_its_rules_does_not_strip_their_decision():
    """A subsection declares once, for everything under it. A plain heading written inside it is
    deeper, not a new declaration — and a rule that lost its side of the seam would drop out of the
    review that asked for it and leave the deck reading clean."""
    canon = dedent(
        """\
        ## 7. Voice

        ### 7b. Judgment

        Every rule in this subsection is **Decided by** judgment.

        #### A note on reading these

        Read them aloud.

        #### `no-reflexive-tricolon`: three items because the claim has three

        Not because three sounds complete.
        """
    )

    assert rules(canon, decided_by="judgment")[0].id == "no-reflexive-tricolon"


def test_a_rule_shown_inside_a_fence_is_an_example_rather_than_a_rule():
    """The canon fences a diagram already, and it is a document about writing documents."""
    canon = dedent(
        """\
        ## 1. Structure

        ### `one-message`: every slide answers exactly one question

        Write the heading of a rule like this:

        ```markdown
        ### `invented-rule`: whatever you like
        ```

        **Decided by** judgment
        """
    )

    assert [rule_.id for rule_ in rules(canon)] == ["one-message"]
    assert rules(canon)[0].decided_by == ("judgment",)


def test_every_rule_the_shipped_canon_states_says_who_decides_it():
    """The canon's own integrity, and the one property the review cannot check for itself: a rule
    that named neither side would be quietly absent from both halves of it."""
    undecided = [rule_.id for rule_ in rules() if not rule_.decided_by]

    assert undecided == []


def test_the_shipped_canon_carries_the_separation_floor():
    thresholds = rule_thresholds("separation-floor")

    assert thresholds["delta-e-floor"] == "15.0"
    assert thresholds["cvd-severity"] == "100"


def test_the_default_threshold_is_the_canons_floor(themes_dir):
    report = validate(load_palette(themes_dir / "leuven-blue.json"))

    assert report.threshold == DELTA_E_FLOOR == 15.0


def test_the_shipped_canon_carries_the_numbers_the_linter_enforces():
    """Every ceiling the linter decides, read out of the canon rather than kept beside it."""
    assert BULLETS_PER_SLIDE == 5
    assert WORDS_PER_BULLET == 12
    assert EM_DASHES_PER_HEADLINE == 0
    assert OPENER_SHARE_MAX == 0.5


def test_the_shipped_canon_carries_the_wordlists_the_linter_enforces():
    assert "crucial" in INFLATED_REGISTER_WORDS
    # Multi-word entries survive the list: the canon writes one of them.
    assert "testament to" in INFLATED_REGISTER_WORDS
    assert OPENER_WORDS == ("The", "This", "It", "In")


def test_the_canon_decides_how_loudly_an_inflated_word_is_reported():
    """`established-terminology` wins over the wordlist, which is why the canon sets this to
    `warning` — and why the severity is quoted rather than chosen here."""
    assert INFLATED_REGISTER_SEVERITY == "warning"


def test_the_canon_says_the_field_s_term_wins_over_the_voice_rules():
    """A plain-words rule pulls a writer toward paraphrase, and `established-terminology` pulls
    back. Where they meet, the review follows the canon's precedence, so the canon has to state one,
    and the voice section has to point back at it before its first rule."""
    voice = CANON.read_text(encoding="utf-8").split("## 7. Voice", 1)[1]
    voice_lead = voice.split("###", 1)[0]

    assert "wins over every rule in [§7](#7-voice)" in rule("established-terminology").text
    assert "`established-terminology`" in voice_lead


def test_the_canon_decides_how_far_the_section_map_stretches_and_how_loudly():
    """A deck that outgrows the map still has the label with a count, which is why the canon sets
    this to `warning`."""
    assert SECTIONS_MAX == 5
    assert SECTION_LABEL_CHARS_MAX == 10
    assert SECTION_LOCATOR_SEVERITY == "warning"


def test_the_canon_names_the_attention_pairings_and_what_they_must_clear():
    """`accent-is-attention` splits the hue by job, and says which pairing each job is read in."""
    assert ATTENTION_CONTRAST_PAIRS == (
        ("ink", "accent"),
        ("accent-strong", "surface"),
        ("accent-strong", "surface-alt"),
    )
    assert ATTENTION_CONTRAST_MIN == 4.5
    assert rule_thresholds("accent-is-attention")["attention-stroke-px-min"] == "3"


def test_the_floor_is_the_accessibility_rules_and_nothing_else():
    """The rules no exception reaches. A style default marked as floor would be a preference
    nobody can argue with; a floor rule left unmarked would be one a reason could clear."""
    from legible.method import rules

    assert {rule.id for rule in rules() if rule.floor} == {
        "type-scale",
        "fonts",
        "light-ground",
        "never-sole-channel",
        "accent-is-attention",
        "decorative-neutral-never-text",
        "separation-floor",
        "motion-ceiling",
    }
