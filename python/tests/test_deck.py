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


def test_a_separator_followed_by_a_heading_starts_a_slide_rather_than_a_frontmatter_block():
    """The blank line after a separator is a convention, not a guarantee. A block that does not
    read as `key: value` is content, and swallowing it would hide the slide from every check."""
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
