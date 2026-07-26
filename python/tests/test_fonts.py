"""The deck's typeface, as the plotting backend sees it.

One claim, and it is what `fonts` exists for: after registration the backend resolves the canon's
text family to a file **this repo ships**. A machine with no Inter installed must get the bundled
one rather than a lookalike, and a bundle that went missing must say so out loud instead of
quietly drawing the figures in something else.
"""

from pathlib import Path

import pytest
from matplotlib import font_manager

from legible.fonts import BUNDLE, FontError, register
from legible.method import FONT_TEXT


def test_the_backend_resolves_the_canon_s_text_family_to_a_bundled_file():
    """True on a bare machine and on one that already has the family installed: the bundled copy
    outranks it, so the same data renders the same way on both."""
    register()

    resolved = Path(font_manager.findfont(FONT_TEXT, fallback_to_default=False))

    assert resolved.parent == BUNDLE


def test_registering_again_adds_nothing_a_second_time():
    """Figures are drawn in batches, and every archetype registers before it draws."""
    register()
    before = len(font_manager.fontManager.ttflist)

    register()

    assert len(font_manager.fontManager.ttflist) == before


def test_register_reports_the_files_it_put_in_front_of_the_backend():
    registered = register()

    assert registered
    assert all(path.suffix == ".ttf" for path in registered)
    assert set(registered) == set(BUNDLE.glob("*.ttf"))


def test_a_bundle_with_no_typeface_in_it_is_an_error_and_names_where_it_looked(tmp_path):
    """The source project warned and fell back to DejaVu here. That is the silent mismatch."""
    with pytest.raises(FontError) as error:
        register(tmp_path)

    assert str(tmp_path) in str(error.value)


def test_a_bundle_that_does_not_carry_the_canon_s_family_is_an_error(monkeypatch):
    """Something to register is not the same as the right thing to register. Standing in for a
    bundle of the wrong typeface by asking for a family nothing provides — the same branch, and
    one that leaves no font file behind in the backend's global list."""
    monkeypatch.setattr("legible.fonts.FONT_TEXT", "Nonesuch Grotesk")

    with pytest.raises(FontError) as error:
        register()

    assert "Nonesuch Grotesk" in str(error.value)
