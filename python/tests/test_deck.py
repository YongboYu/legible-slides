"""Reading a Slidev deck.

The linter's findings are only as good as what it thinks a slide is, so what is asserted here is
the reading: where one slide ends, which text is the headline, what counts as a bullet, and what is
prose rather than chrome. The rules applied to that reading are test_lint.py's business.
"""

from textwrap import dedent

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
        # The theme by path, until the package is on npm.
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
