"""Reading a Slidev deck.

The linter's findings are only as good as what it thinks a slide is, so what is asserted here is
the reading: where one slide ends, which text is the headline, what counts as a bullet, and what is
prose rather than chrome. The rules applied to that reading are test_lint.py's business.
"""

from textwrap import dedent

import pytest

from legible.deck import parse_deck


def deck(text: str):
    return parse_deck(dedent(text))


def test_slides_are_split_on_the_separator_and_numbered_as_an_author_counts_them():
    slides = deck(
        """\
        # First

        ---

        # Second

        ---

        # Third
        """
    )

    assert [slide.number for slide in slides] == [1, 2, 3]
    assert [slide.headline for slide in slides] == ["First", "Second", "Third"]


def test_the_decks_own_headmatter_is_not_a_slide():
    slides = deck(
        """\
        ---
        theme: ../theme
        title: legible-slides
        ---

        # First
        """
    )

    assert len(slides) == 1
    assert slides[0].headline == "First"
    assert "theme" not in " ".join(slides[0].prose)


def test_a_slides_own_frontmatter_is_not_its_content():
    slides = deck(
        """\
        # First

        ---
        layout: two-col-evidence
        clicks: 3
        ---

        # Second
        """
    )

    assert len(slides) == 2
    assert slides[1].headline == "Second"
    assert slides[1].prose == ()


def test_a_frontmatter_block_that_opens_with_a_comment_is_still_frontmatter():
    """A comment before the first key is where a deck says why it wears the theme it wears, so a
    reading that took the block for content would make every deck that explains itself slide 1."""
    slides = deck(
        """\
        ---
        # The theme by path, the copy in this repo.
        theme: ../theme
        ---

        # First
        """
    )

    assert len(slides) == 1
    assert slides[0].headline == "First"


def test_a_closed_block_after_a_separator_is_frontmatter_whatever_it_opens_with():
    """Slidev asks only whether the line after the separator is blank, and takes everything up to
    the closing separator as frontmatter if it is not. A heading written there never reaches the
    room, so a reading that showed it would hold the deck to a slide nobody sees."""
    slides = deck(
        """\
        # First

        ---
        # Second

        Evidence follows.

        ---

        # Third
        """
    )

    assert [slide.headline for slide in slides] == ["First", "Third"]


def test_a_block_the_author_never_closed_is_content():
    """The other half of Slidev's rule: with no closing separator there is no frontmatter to
    strip, so the lines are a slide — and hiding them would take it out of every check."""
    slides = deck(
        """\
        # First
        ---
        # Second

        Evidence follows.
        """
    )

    assert [slide.headline for slide in slides] == ["First", "Second"]


def test_the_headline_is_the_slides_first_heading():
    slides = deck(
        """\
        # The claim this slide makes

        ## A second heading

        Prose.
        """
    )

    assert slides[0].headline == "The claim this slide makes"


@pytest.mark.parametrize("br", ["<br>", "<br/>", "<br />", "<BR>"])
def test_a_line_break_in_the_headline_is_kept_as_a_newline(br):
    """The author chose where the headline breaks, so its shape is measured with the breaks in."""
    slides = deck(f"# First line{br}Second line{br}Third line\n")

    assert slides[0].headline == "First line\nSecond line\nThird line"


@pytest.mark.parametrize(
    ("heading", "headline"),
    [
        ("First<br><br>Third", "First\n\nThird"),
        ("First <br> <br> Third", "First\n\nThird"),
        ("<br>First", "\nFirst"),
        ("First<br>", "First"),
        ("First<br><br>", "First\n"),
    ],
)
def test_the_headline_keeps_each_empty_line_its_breaks_set(heading, headline):
    """Each break starts a line, so two in a row leave an empty one. A break at the very end closes
    the last line and starts none. Chromium sets all five this way."""
    slides = deck(f"# {heading}\n")

    assert slides[0].headline == headline


def test_a_headline_of_breaks_alone_is_no_headline():
    slides = deck("# <br><br>\n")

    assert slides[0].headline is None


def test_a_line_break_in_a_bullet_or_a_passage_separates_its_words():
    slides = deck("# A claim\n\n- one<br>two\n\nThree<br/>four.\n")

    assert slides[0].bullets == ("one two",)
    assert slides[0].prose == ("Three four.",)


def test_a_break_in_inline_code_is_text_the_slide_shows():
    """The slide shows the tag in backticks as written, and breaks no line there."""
    slides = deck("# Use `<br>` with care\n\n- `<br/>` ends a line\n\nWrite ``<br>`` once.\n")

    assert slides[0].headline == "Use <br> with care"
    assert slides[0].bullets == ("<br/> ends a line",)
    assert slides[0].prose == ("Write <br> once.",)


def test_a_slide_with_no_heading_has_no_headline():
    slides = deck("Just a pane of evidence.\n")

    assert slides[0].headline is None


def test_bullets_come_back_without_their_markers():
    slides = deck(
        """\
        # Claim

        - first point
        * second point
        1. third point
        """
    )

    assert slides[0].bullets == ("first point", "second point", "third point")


def test_an_html_list_item_is_a_bullet():
    """An author writes the list in HTML to give an item a class or a click; it is still a list."""
    slides = deck(
        """\
        # Claim

        <ul>
          <li class="text-lg">first point</li>
          <li v-click>second
            point</li>
        </ul>
        <ol><li>third point</li><li>fourth <b>point</b></li></ol>

        A passage after the list.
        """
    )

    assert slides[0].bullets == ("first point", "second point", "third point", "fourth point")
    assert slides[0].prose == ("A passage after the list.",)


def test_a_nested_html_list_item_is_one_bullet_and_its_parent_another():
    slides = deck("# Claim\n\n<ul><li>parent<ul><li>child</li></ul></li></ul>\n")

    assert slides[0].bullets == ("parent", "child")


def test_a_parent_items_text_after_its_child_list_is_still_the_parents():
    """The browser sets both runs inside the parent's item, so its bullet holds both."""
    slides = deck("# Claim\n\n<ul><li>one two<ul><li>child</li></ul>three four</li></ul>\n")

    assert slides[0].bullets == ("one two three four", "child")
    assert slides[0].prose == ()


def test_an_html_list_item_runs_on_across_a_blank_line():
    """Markdown starts a paragraph after the blank line, and the browser sets it inside the item."""
    slides = deck("# Claim\n\n<ul><li>one two\n\nthree four\n\n</li></ul>\n\nAfter the list.\n")

    assert slides[0].bullets == ("one two three four",)
    assert slides[0].prose == ("After the list.",)


def test_a_list_tag_in_inline_code_is_text_and_opens_no_bullet():
    slides = deck("# The `<li>` element groups a list\n\nWrap each item in `<li>` and `</li>`.\n")

    assert slides[0].headline == "The <li> element groups a list"
    assert slides[0].bullets == ()
    assert slides[0].prose == ("Wrap each item in <li> and </li>.",)


def test_a_nested_bullet_is_a_bullet_the_room_still_reads():
    slides = deck(
        """\
        # Claim

        - parent
          - child
        """
    )

    assert slides[0].bullets == ("parent", "child")


def test_a_wrapped_bullet_is_one_bullet():
    """Otherwise the word ceiling is decided by where the author's editor wrapped the line."""
    slides = deck(
        """\
        # Claim

        - a bullet long enough that its author wrapped it
          across two lines of the source
        """
    )

    assert slides[0].bullets == (
        "a bullet long enough that its author wrapped it across two lines of the source",
    )


def test_a_code_block_is_evidence_rather_than_bullets_and_prose():
    slides = deck(
        """\
        # Claim

        ```python
        - not a bullet
        This is not prose.
        ```
        """
    )

    assert slides[0].bullets == ()
    assert slides[0].prose == ()


def test_a_separator_inside_a_code_block_does_not_split_the_deck():
    slides = deck(
        """\
        # Claim

        ```yaml
        ---
        layout: cover
        ---
        ```
        """
    )

    assert len(slides) == 1


def test_prose_paragraphs_exclude_the_headline_the_bullets_and_the_chrome():
    slides = deck(
        """\
        # Claim

        <div class="evidence">

        Prose that proves it.

        </div>

        - a bullet
        """
    )

    assert slides[0].prose == ("Prose that proves it.",)


def test_a_wrapped_paragraph_is_one_passage():
    slides = deck(
        """\
        Two lines of one paragraph,
        wrapped by its author.

        A second paragraph.
        """
    )

    assert slides[0].prose == (
        "Two lines of one paragraph, wrapped by its author.",
        "A second paragraph.",
    )


def test_speaker_notes_are_the_slides_last_comment_block():
    slides = deck(
        """\
        # Claim

        <!-- an aside about the layout -->

        Prose.

        <!--
        What the presenter says out loud.
        -->
        """
    )

    assert slides[0].notes == "What the presenter says out loud."
    assert slides[0].prose == ("Prose.",)


def test_a_slide_with_no_comment_has_no_notes():
    slides = deck("# Claim\n")

    assert slides[0].notes is None


def test_a_link_reads_as_its_text_and_an_image_as_nothing():
    """Word counts are about what the room reads, and nobody reads a URL off a slide."""
    slides = deck(
        """\
        # Claim

        ![a chart of the results](/figures/mae.png)

        - see [the method](https://example.com/method.md)
        """
    )

    assert slides[0].bullets == ("see the method",)
    assert slides[0].prose == ()


def test_a_slide_reports_the_section_its_frontmatter_declares():
    """`section-locator` is decided over the whole deck, so the reading has to keep the one key
    it turns on — and only where a slide declares it, because carrying it forward is the theme's
    job and counting sections is the linter's."""
    slides = deck(
        """\
        ---
        theme: ../theme
        section: Problem
        ---

        # First

        ---
        layout: two-col-evidence
        ---

        # Second

        ---
        section: 'Method' # a comment is not part of the name
        ---

        # Third
        """
    )

    assert [slide.section for slide in slides] == ["Problem", None, "Method"]


def test_a_slide_reports_the_layout_its_frontmatter_names():
    """Which slide is the deck's opening answer and which its close is a matter of layout, so the
    reading keeps the name a slide gives and leaves resolving a default to the theme."""
    slides = deck(
        """\
        ---
        theme: ../theme
        layout: cover
        ---

        # First

        ---
        layout: 'answer' # quoted, and commented
        ---

        # Second

        ---

        # Third
        """
    )

    assert [slide.layout for slide in slides] == ["cover", "answer", None]


def test_an_empty_section_is_declared_rather_than_absent():
    """`section: ''` clears the locator, which is a declaration of its own."""
    slides = deck(
        """\
        # First

        ---
        section: ''
        ---

        # Second
        """
    )

    assert [slide.section for slide in slides] == [None, ""]


def test_a_slide_reports_whether_it_opens_a_backup_section():
    slides = deck(
        """\
        # First

        ---
        section: Backup
        backup: true
        ---

        # Second
        """
    )

    assert [slide.backup for slide in slides] == [False, True]


def test_backup_is_read_the_way_yaml_reads_it():
    """The theme sees parsed YAML, so the linter must agree with it: `True` is a boolean and
    `"true"` is a string, not a backup."""
    slides = deck(
        """\
        ---
        section: A
        backup: True
        ---

        # First

        ---
        section: B
        backup: "true"
        ---

        # Second
        """
    )

    assert [slide.backup for slide in slides] == [True, False]


def test_a_quoted_section_keeps_a_hash_inside_its_quotes():
    slides = deck(
        """\
        ---
        section: "C # D" # the comment is after the quotes
        ---

        # First
        """
    )

    assert slides[0].section == "C # D"


def test_a_slide_of_frontmatter_alone_still_declares_its_section():
    """A full-bleed image slide has no body, and Slidev renders it all the same: the section it
    declares is on the footer, so it has to be in the count."""
    slides = deck(
        """\
        # First

        ---
        layout: image
        image: /x.png
        section: Results
        ---

        ---

        # Third
        """
    )

    assert [slide.section for slide in slides] == [None, "Results", None]
    assert [slide.number for slide in slides] == [1, 2, 3]


# ── what the review advisories read ───────────────────────────────────────────


def test_each_top_level_block_beneath_the_headline_is_one_visual_group():
    """A list is one group however many bullets it has, and a block of markup is one group whatever
    it wraps: a callout inside a click reveal is still the one thing the eye lands on."""
    [slide] = deck(
        """\
        # A claim

        ::left::

        Evidence sits beside the claim.

        - one
        - two

        | a | b |
        |---|---|
        | 1 | 2 |

        ![A chart](/chart.png)

        <v-click>

        <Callout title="Why">

        Because.

        </Callout>

        </v-click>

        ::right::

        <Figure
          src="/figure.png"
          caption="A caption long enough to wrap onto its own line"
        />

        ```python
        print("code")
        ```
        """
    )

    assert slide.groups == ("paragraph", "list", "table", "image", "v-click", "Figure", "code")


def test_a_slide_of_a_headline_alone_has_no_visual_groups():
    [slide] = deck("# A claim\n\n<!-- notes -->\n")

    assert slide.groups == ()


def test_a_figure_s_attributes_are_not_words_on_the_slide():
    """A component's attributes are the figure's, not prose the room reads, even where an author
    wrapped the tag over several lines."""
    [slide] = deck(
        """\
        # A claim

        <Figure
          src="/figure.png"
          caption="Ten pairs of colours under four conditions"
        />
        """
    )

    assert slide.prose == ()


def test_bold_and_highlighted_spans_are_emphasis_and_italics_are_not():
    [slide] = deck(
        """\
        # A **bold** claim

        One __strong__ point, one *term*, one <mark>highlight</mark> and `**code**`.

        - a <strong>bullet</strong>
        """
    )

    assert slide.emphasis == ("bold", "strong", "highlight", "bullet")


def test_every_callout_is_counted_wherever_it_sits():
    [slide] = deck(
        """\
        # A claim

        <Callout title="One">

        First.

        </Callout>

        <v-click>
        <Callout accent title="Two">Second.</Callout>
        </v-click>
        """
    )

    assert slide.callouts == 2


def test_the_slot_is_the_headmatter_s_duration():
    slides = deck(
        """\
        ---
        theme: ../theme
        duration: 20min
        ---

        # First

        ---

        # Second
        """
    )

    assert [slide.duration for slide in slides] == ["20min", None]


def test_a_slide_s_time_budget_is_the_notes_line_that_opens_time():
    [slide] = deck(
        """\
        # A claim

        <!--
        Signpost: now the method.
        Time: 1min 30s

        Point at the chart.
        -->
        """
    )

    assert slide.time == "1min 30s"


def test_a_slide_without_a_time_line_has_no_budget():
    [slide] = deck("# A claim\n\n<!--\nThe time is up when the slide is.\n-->\n")

    assert slide.time is None


def test_a_style_block_is_not_a_visual_group():
    [slide] = deck("# A claim\n\nEvidence.\n\n<style>\n.x { color: red }\n</style>\n")

    assert slide.groups == ("paragraph",)


def test_an_attribute_is_never_emphasis():
    """Underscores and stars inside a component's attributes are the component's business."""
    [slide] = deck(
        """\
        # A claim

        <Snapshot hero-edge="offer__sent__end" note="**not prose**" />

        One __real__ span.
        """
    )

    assert slide.emphasis == ("real",)


def test_footnotes_cite_rather_than_say_so_they_are_not_prose():
    """A footnote is attribution, set at the floor: the room is not reading it while you talk, and a
    source's title is not the author's register."""
    [slide] = deck(
        """\
        # A claim

        Red-green deficiency reaches about one man in twelve<sup>1</sup>.

        <Footnotes>
          <Footnote :number="1">Birch (2012), a robust survey of prevalence.</Footnote>
        </Footnotes>
        """
    )

    assert slide.prose == ("Red-green deficiency reaches about one man in twelve1.",)
    assert slide.groups == ("paragraph",)


def test_a_slot_marker_is_layout_and_not_prose():
    [slide] = deck("# A claim\n\n::left::\n\nEvidence.\n\n::right::\n\n- a point\n")

    assert slide.prose == ("Evidence.",)
    assert slide.bullets == ("a point",)


def test_a_self_closing_footnotes_tag_takes_nothing_after_it_with_it():
    [slide] = deck(
        """\
        # A claim

        <Footnotes />

        Evidence the room reads.

        <Callout title="Why">Because.</Callout>
        """
    )

    assert slide.prose == ("Evidence the room reads.", "Because.")


def test_footnotes_are_neither_a_group_nor_emphasis_and_a_line_break_is_not_a_group():
    [slide] = deck(
        """\
        # A claim

        Evidence.

        <br>

        <Footnotes>
          <Footnote :number="1">**Smith** (2020).</Footnote>
        </Footnotes>
        """
    )

    assert slide.groups == ("paragraph",)
    assert slide.emphasis == ()
