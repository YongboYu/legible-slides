"""The PowerPoint static proof, against the canon and the palette it was hand-set from.

The proof is a hand-authored native master, and `docs/pptx-static-proof.md` §6 is deliberate that it
stays one: the mapping from a palette to a tool's theme has to survive being rerun in Keynote and
Google Slides, neither of which can read a PowerPoint theme file, so the **documented mapping** is
the artifact and no generator derives the `.pptx` from `themes/kuleuven.json`.

That is the right call and it leaves the same exposure ``test_theme.py`` was written for, one step
further out. Twelve colours and four point sizes are typed into XML by hand, and a hand-typed number
is exactly where a mapping drifts in silence — recolour the palette or move a threshold in
``docs/method.md``, and nothing in a binary anybody downloads would say so.

So the copies are held to their originals, in both directions, and the shipped `.pptx` is held to
the sources it was packed from. Change a colour, a canon number or a part under ``pptx/src/``
without repacking, and these fail naming which.
"""

from __future__ import annotations

import importlib.util
import math
import posixpath
import re
import zipfile
from pathlib import Path
from xml.etree import ElementTree

import pytest

from legible import load_palette, validate
from legible.method import CANVAS_HEIGHT_PX, DELTA_E_FLOOR, FONT_MONO, FONT_TEXT, rule_thresholds

REPO = Path(__file__).resolve().parents[2]
PPTX = REPO / "pptx"
PACKAGE = PPTX / "legible-master.pptx"

#: The palette the proof commits to. The recipe is palette-agnostic; the shipped worked example is
#: the flagship's twin, which is what makes its argument "the same deck, in PowerPoint".
THEME = REPO / "themes" / "kuleuven.json"

A = "{http://schemas.openxmlformats.org/drawingml/2006/main}"
P = "{http://schemas.openxmlformats.org/presentationml/2006/main}"
R = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"
DC = "{http://purl.org/dc/elements/1.1/}"

#: What each of PowerPoint's twelve colour slots carries, from `docs/pptx-static-proof.md` §4. The
#: slot names are the theme file's own — `dk1`/`lt1` are what the master's colour map calls Text 1
#: and Background 1. The data-encoding ramp is absent, and `test_no_series_colour_reaches_a_slot`
#: is what holds it out.
THEME_SLOTS = {
    "dk1": "ink",
    "lt1": "surface",
    "dk2": "neutral",
    "lt2": "surface-alt",
    "accent1": "brand",
    "accent2": "accent",
    "accent3": "brand-strong",
    "accent4": "neutral-soft",
    "accent5": "reference",
    "accent6": "muted",
    "hlink": "brand-strong",
    "folHlink": "muted",
}

#: Which of the theme's layouts each PowerPoint layout mirrors, in the order the master lists them.
#: `default.vue` is not a fifth: it is `assertion-evidence` under the name Slidev falls back to, so
#: it has no counterpart to mirror here.
MIRRORS = {
    "Cover": "cover",
    "Assertion-Evidence": "assertion-evidence",
    "Two-Col Evidence": "two-col-evidence",
    "References": "references",
}

#: The four layouts, by the name the master's gallery lists them under.
LAYOUTS = tuple(MIRRORS)

#: The theme's layout directory, which the mirror above is a claim about.
THEME_LAYOUTS = REPO / "theme" / "layouts"

#: The alias, which is why it is not counted as a layout on either side.
ALIAS = "default"

#: The layouts that carry the skeleton, by part number — everything but the cover.
CONTENT_LAYOUTS = (2, 3, 4)

#: The chrome, as the two placeholder types PowerPoint already has for it. Native ones rather than
#: drawn shapes, because a presenter edits both: the locator when the section changes, the page
#: number never.
CHROME = ("ftr", "sldNum")

#: The one palette role with no slot to live in, so it is written as a literal fill. §4 records why.
HAIRLINE_ROLE = "hairline"

#: EMU per point, which is how PowerPoint measures a slide against how it measures type.
EMU_PER_POINT = 12700

#: A run's size, as OOXML writes it: hundredths of a point.
SZ_PER_POINT = 100

#: The group `separation-floor` forms over the per-series ramp, and the condition that binds this
#: palette. Both are what slide 2's caption is a claim about.
PER_SERIES = "G1"


def _load_packer():
    """``pptx/pack.py``, imported from where it lives beside what it packs.

    It is not part of the `legible` package and deliberately not a command: it is the container step
    for a hand-authored artifact, and putting it on the CLI would be the first half of the generator
    §6 declines to build.
    """
    spec = importlib.util.spec_from_file_location("legible_pptx_pack", PPTX / "pack.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


packer = _load_packer()


@pytest.fixture(scope="module")
def package() -> dict[str, bytes]:
    """Every part of the shipped `.pptx`, by the path it takes inside it."""
    with zipfile.ZipFile(PACKAGE) as archive:
        return {name: archive.read(name) for name in archive.namelist()}


@pytest.fixture(scope="module")
def palette():
    return load_palette(THEME)


def part(package: dict[str, bytes], name: str) -> ElementTree.Element:
    """One XML part of the package, parsed."""
    assert name in package, f"the package carries no {name}"
    return ElementTree.fromstring(package[name])


def layout(package: dict[str, bytes], number: int) -> ElementTree.Element:
    return part(package, f"ppt/slideLayouts/slideLayout{number}.xml")


def related(package: dict[str, bytes], name: str, kind: str) -> dict[str, str]:
    """One part's relationships of a kind, as ``relationship id`` → ``the part it points at``.

    Resolved to a path inside the package rather than left as the relative target a `.rels` file
    writes, because what these tests are checking is which part a slide actually reaches.
    """
    directory, _, base = name.rpartition("/")
    return {
        rel.get("Id"): posixpath.normpath(posixpath.join(directory, rel.get("Target")))
        for rel in part(package, f"{directory}/_rels/{base}.rels")
        if rel.get("Type").rsplit("/", 1)[-1] == kind
    }


def layout_name(package: dict[str, bytes], name: str) -> str:
    """A layout's name, as the master's gallery lists it."""
    return part(package, name).find(f"{P}cSld").get("name")


def shapes(root: ElementTree.Element) -> list[ElementTree.Element]:
    """Every shape and picture on a slide, layout or master, in the order it draws them."""
    tree = root.find(f"{P}cSld/{P}spTree")
    return [child for child in tree if child.tag in (f"{P}sp", f"{P}pic")]


def placeholders(root: ElementTree.Element) -> dict[str, ElementTree.Element]:
    """The shapes that are placeholders, by the placeholder type each declares."""
    found = {}
    for shape in shapes(root):
        declared = shape.find(f".//{P}nvPr/{P}ph")
        if declared is not None:
            found[declared.get("type", "obj")] = shape
    return found


def named(root: ElementTree.Element, name: str) -> ElementTree.Element:
    """One shape, by the name it carries in the file."""
    for shape in shapes(root):
        if shape.find(f".//{P}cNvPr").get("name") == name:
            return shape
    raise AssertionError(f"no shape named {name!r}")


def drawing_elements(package: dict[str, bytes]):
    """Every DrawingML element in every XML part of the package, in no particular order."""
    for name, data in package.items():
        if not name.endswith(".xml"):
            continue
        for element in ElementTree.fromstring(data).iter():
            yield name, element


def sizes(package: dict[str, bytes]) -> list[int]:
    """Every type size the package declares anywhere, in points."""
    return [
        int(element.get("sz")) // SZ_PER_POINT
        # A table column also carries a `sz`, and it is not a type size; nothing here builds one,
        # and reading the namespace keeps this honest if something later does.
        for _, element in drawing_elements(package)
        if element.get("sz") is not None and element.tag.startswith(A)
    ]


def points(px: int, package: dict[str, bytes]) -> int:
    """A canvas px of `type-scale`, as the point size that preserves its share of the slide height.

    The ratio is what governs back-row legibility, so the ratio is what is carried over rather than
    the number: the share is the shipped slide's height in points over the canon's canvas height,
    both read rather than written down, and the size is the canvas px times that.

    Rounded **up** to an even point. That is the direction that cannot land under the ratio, which
    is the property worth having whatever the canon's sizes are next year — rounding to nearest
    agrees on every size the canon carries today, and agreeing today is not the same as being safe.
    """
    slide_height = int(part(package, "ppt/presentation.xml").find(f"{P}sldSz").get("cy"))
    share = (slide_height / EMU_PER_POINT) / CANVAS_HEIGHT_PX
    return math.ceil(px * share / 2) * 2


def canon_px(key: str) -> int:
    return int(rule_thresholds("type-scale")[key])


# ── the master and its four layouts ─────────────────────────────────────────────────────────────


def test_the_master_carries_the_theme_s_four_layouts(package):
    """A full mirror, in order. The proof is only a proof if a presenter can build every slide the
    Slidev delivery can, so a missing layout is a missing claim rather than a convenience."""
    master = "ppt/slideMasters/slideMaster1.xml"
    listed = part(package, master).find(f"{P}sldLayoutIdLst")
    targets = related(package, master, "slideLayout")

    named_in_order = [layout_name(package, targets[entry.get(f"{R}id")]) for entry in listed]

    assert named_in_order == list(LAYOUTS)


def test_the_four_are_still_the_four_the_theme_ships():
    """ "Mirroring the theme's four" is a claim about two directories, so it is checked across both.
    Holding the master to its own list would leave a layout added to the Slidev theme silently
    unmirrored, and the proof one slide short of the delivery it is meant to be a twin of."""
    shipped = {path.stem for path in THEME_LAYOUTS.glob("*.vue")} - {ALIAS}

    assert shipped == set(MIRRORS.values())


def test_the_chrome_lives_on_the_master(package):
    """`ae-skeleton`'s persistent half, stated once. Both are real placeholders rather than
    drawings, so a presenter edits them where PowerPoint already lets them; the accent rule is not,
    because a rule is not a presenter's to type into."""
    master = part(package, "ppt/slideMasters/slideMaster1.xml")

    assert set(CHROME) <= set(placeholders(master))
    assert named(master, "Rule") is not None
    assert named(master, "Rule accent") is not None


@pytest.mark.parametrize("number", CONTENT_LAYOUTS)
def test_every_content_layout_inherits_the_chrome(package, number):
    """Inherited, not restated. A content layout carries the chrome placeholders and does not
    suppress the master's shapes, so a slide built on any of the three arrives with all five zones
    and none of them can be forgotten on one layout only."""
    content = layout(package, number)

    assert set(CHROME) <= set(placeholders(content))
    assert content.get("showMasterSp") != "0"


def test_the_cover_omits_the_chrome(package):
    """The native equivalent of the theme's per-slide opt-out, and the only slide that takes it: a
    cover is where orientation begins rather than something the locator has to carry.

    Both halves are needed. Dropping the master's shapes takes the accent rule off; switching the
    header-and-footer flags off is what keeps the locator and the page number from arriving with the
    placeholders PowerPoint would otherwise inherit."""
    cover = layout(package, 1)

    assert cover.get("showMasterSp") == "0"
    assert not set(CHROME) & set(placeholders(cover))
    switches = cover.find(f"{P}hf")
    assert switches is not None, "the cover does not switch the header and footer placeholders off"
    assert switches.get("ftr") == "0"
    assert switches.get("sldNum") == "0"


# ── the twelve colour slots ─────────────────────────────────────────────────────────────────────


@pytest.fixture(scope="module")
def slots(package) -> dict[str, str]:
    """The theme's twelve colour slots, as hexes, by slot name."""
    scheme = part(package, "ppt/theme/theme1.xml").find(f"{A}themeElements/{A}clrScheme")
    return {
        slot.tag.removeprefix(A): f"#{slot.find(f'{A}srgbClr').get('val').lower()}"
        for slot in scheme
    }


@pytest.mark.parametrize(("slot", "role"), THEME_SLOTS.items())
def test_the_twelve_theme_slots_are_the_shipped_palette_s(slots, palette, slot, role):
    """The mapping is hand-set once and documented, which is what makes it portable to a tool that
    cannot read a `.thmx`. This is the price of that: the copy is verified rather than avoided."""
    assert slots[slot] == palette[role].lower()


def test_the_theme_declares_exactly_twelve_slots(slots):
    """Twelve is the whole budget PowerPoint has, and the mapping spends all of it. A thirteenth
    would mean the file has stopped being a PowerPoint theme."""
    assert set(slots) == set(THEME_SLOTS)


def test_no_series_colour_reaches_a_slot(slots, palette):
    """The overflow that dissolves, and the reason it does: the data-encoding ramp exceeds the six
    accents *and* never needs one, because a figure arrives as a validated picture with those
    colours already inside it. A series colour turning up here would mean something on a slide is
    drawing data natively."""
    ramp = {palette[role].lower() for role in palette.series_roles}

    assert not ramp & set(slots.values())


def test_no_palette_colour_is_written_outside_the_theme(package, palette):
    """What makes the mapping load-bearing rather than decorative: every shape in the package asks
    the theme for its colour, so recolouring the proof is one file. `hairline` is the documented
    exception — it is a palette role with no slot to live in."""
    written = {
        f"#{element.get('val').lower()}"
        for name, element in drawing_elements(package)
        if element.tag == f"{A}srgbClr" and name != "ppt/theme/theme1.xml"
    }

    assert written == {palette[HAIRLINE_ROLE].lower()}


# ── the type scale ──────────────────────────────────────────────────────────────────────────────


def test_the_slide_is_the_canon_s_canvas_at_a_whole_number_of_emu(package):
    """The conversion the whole geometry rests on. The canon's canvas and a 16:9 PowerPoint slide
    are the same shape, and one canvas px is exactly 9525 EMU — so every zone in the master is the
    stylesheet's own number multiplied out, with nothing rounded and nothing redesigned."""
    type_scale = rule_thresholds("type-scale")
    width, height = (int(part_) for part_ in type_scale["canvas-aspect-ratio"].split(":"))
    size = part(package, "ppt/presentation.xml").find(f"{P}sldSz")
    cx, cy = int(size.get("cx")), int(size.get("cy"))

    assert cx * height == cy * width
    assert cx % int(type_scale["canvas-width-px"]) == 0
    assert cx // int(type_scale["canvas-width-px"]) == cy // CANVAS_HEIGHT_PX


def test_the_headline_and_the_body_are_the_canon_s_sizes(package):
    """The two sizes the method actually turns on, read where the master sets them for everything
    beneath it: the title style and the body style."""
    styles = part(package, "ppt/slideMasters/slideMaster1.xml").find(f"{P}txStyles")
    declared = {
        style.tag.removeprefix(P): int(style.find(f"{A}lvl1pPr/{A}defRPr").get("sz"))
        // SZ_PER_POINT
        for style in styles
    }

    assert declared["titleStyle"] == points(canon_px("headline-px"), package)
    assert declared["bodyStyle"] == points(canon_px("body-px"), package)


def test_the_chrome_is_set_at_the_canon_s_smallest_size(package):
    """The locator and the page number are orientation, not evidence, so they take the smallest size
    the canon carries — the same exception the theme takes for them, converted the same way."""
    master = part(package, "ppt/slideMasters/slideMaster1.xml")
    floor = points(canon_px("dense-xs-px"), package)

    for kind in CHROME:
        style = placeholders(master)[kind].find(f".//{A}lstStyle/{A}lvl1pPr/{A}defRPr")
        assert int(style.get("sz")) // SZ_PER_POINT == floor, kind


def test_the_figure_s_caption_takes_the_canon_s_dense_exception(package):
    """A caption labels the evidence and is not the evidence, which is the exception `type-scale`
    marks the dense size for. Named as that exception here so it cannot quietly become a knob."""
    caption = named(part(package, "ppt/slides/slide2.xml"), "Caption")
    run = caption.find(f".//{A}r/{A}rPr")

    assert int(run.get("sz")) // SZ_PER_POINT == points(canon_px("dense-px"), package)


def test_the_package_is_set_in_the_canon_s_four_sizes_and_no_others(package):
    """The half of `type-scale` that is a promise rather than a table: the scale is fixed by the
    method, so the proof has four sizes and no fifth one somebody reached for to fit a slide — which
    is also what puts a floor under it, since the smallest of the four is the canon's own smallest.

    Equality rather than containment, so a size that stopped being used says so too: four sizes of
    which only three are reachable is a scale with a zone nobody can read the size of."""
    scale = {
        points(canon_px(key), package)
        for key in ("headline-px", "body-px", "dense-px", "dense-xs-px")
    }

    assert set(sizes(package)) == scale


# ── the fonts ───────────────────────────────────────────────────────────────────────────────────


@pytest.fixture(scope="module")
def embedded(package) -> dict[str, ElementTree.Element]:
    """The embedded font list, by the family each entry names."""
    listed = part(package, "ppt/presentation.xml").find(f"{P}embeddedFontLst")
    return {entry.find(f"{P}font").get("typeface"): entry for entry in listed}


def test_both_of_the_canon_s_families_travel_inside_the_file(package, embedded):
    """`fonts` says bundled means bundled, and a `.pptx` leaves this repo on its own: a presenter on
    a strange machine gets the deck in the family it was designed in, or gets a fallback nobody
    verified. Whole faces rather than subsets, so the deck stays editable and not only viewable."""
    presentation = part(package, "ppt/presentation.xml")

    assert set(embedded) == {FONT_TEXT, FONT_MONO}
    assert presentation.get("embedTrueTypeFonts") == "1"
    assert presentation.get("saveSubsetFonts") == "0"


@pytest.mark.parametrize(
    ("family", "face", "source"),
    [
        (FONT_TEXT, "regular", "Inter-Regular.ttf"),
        (FONT_TEXT, "bold", "Inter-Bold.ttf"),
        (FONT_MONO, "regular", "JetBrainsMono-Regular.ttf"),
    ],
)
def test_each_embedded_face_is_the_bundled_outline(package, embedded, family, face, source):
    """The same outlines the figures are drawn in, byte for byte. A `.pptx` carrying a different
    release of Inter from the one `legible.fonts` registers is how a chart and the slide around it
    end up in two typefaces on one screen."""
    rel = embedded[family].find(f"{P}{face}").get(f"{R}id")
    target = related(package, "ppt/presentation.xml", "font")[rel]

    assert package[target] == (REPO / "theme" / "assets" / "fonts" / source).read_bytes()


@pytest.mark.parametrize("family", [FONT_TEXT, FONT_MONO])
def test_every_place_a_family_is_named_declares_what_stands_in_for_it(package, family):
    """The fallback, in the only terms OOXML has for one. There is no named-alternate list, so what
    a renderer that stripped the embedding — Mac PowerPoint, the web viewer — substitutes on is the
    face's PANOSE fingerprint and its pitch family. A name written without them is a name that falls
    back to whatever is first in that renderer's own list.

    Checked at every site rather than at the two the design happens to use today: the text family is
    named in the theme's font scheme, the mono one only where it is actually set, and a third site
    added later would otherwise arrive undeclared and unnoticed."""
    naming = [
        element
        for _, element in drawing_elements(package)
        if element.tag in (f"{A}latin", f"{P}font") and element.get("typeface") == family
    ]
    assert naming, f"nothing in the package names {family}"

    for declaration in naming:
        assert declaration.get("panose"), family
        assert declaration.get("pitchFamily"), family
        assert declaration.get("charset") is not None, family


# ── the worked example ──────────────────────────────────────────────────────────────────────────


def test_the_example_is_one_slide_per_layout(package):
    """Four slides on four layouts, which is what makes the example the worked example *and* the
    exercise of every master in one artifact."""
    listed = part(package, "ppt/presentation.xml").find(f"{P}sldIdLst")
    slides = related(package, "ppt/presentation.xml", "slide")

    built_on = []
    for entry in listed:
        slide = slides[entry.get(f"{R}id")]
        (on,) = related(package, slide, "slideLayout").values()
        built_on.append(layout_name(package, on))

    assert built_on == list(LAYOUTS)


def test_the_figure_arrives_as_the_flagship_s_own_generated_picture(package):
    """Regenerated, never redrawn — the practice the whole colour mapping rests on. The picture is
    the file `deck/figures.py` writes and the Slidev deck shows, so the proof cannot drift into
    showing a chart the validator never measured."""
    slide = part(package, "ppt/slides/slide2.xml")
    picture = next(shape for shape in shapes(slide) if shape.tag == f"{P}pic")
    rel = picture.find(f".//{A}blip").get(f"{R}embed")
    target = related(package, "ppt/slides/slide2.xml", "image")[rel]

    assert (
        package[target] == (REPO / "deck" / "public" / "redundant-deuteranomaly.png").read_bytes()
    )


def test_no_slide_draws_data_natively(package):
    """The other half of it. A native chart would put the data-encoding roles back on the slide, and
    the twelve slots have no room for them: the mapping only works because the data stays inside a
    validated image."""
    assert not [name for name in package if "chart" in name.lower()]


def test_the_caption_states_what_the_validator_measures_today(package, palette):
    """Slide 2's whole argument is that the floor is measured rather than promised, so the number on
    it has to be what `cvd-validate` says now — not what it said when it was typed. "Exactly the
    floor" is the load-bearing half: the ramp is at capacity, and one more series would fail."""
    caption = named(part(package, "ppt/slides/slide2.xml"), "Caption")
    stated = re.search(
        r"the closest pair lands on ([\d.]+), exactly the floor",
        caption.find(f".//{A}r/{A}t").text,
    )
    assert stated, "slide 2's caption no longer states where the binding pair lands"
    measured = validate(palette).groups[PER_SERIES]

    assert float(stated.group(1)) == min(measured.min_delta_e.values()) == DELTA_E_FLOOR


def test_the_non_endorsement_note_travels_with_the_file(package, palette):
    """A `.pptx` is downloaded and forwarded on its own, so the note cannot live only in a README
    beside it. It is the sentence the theme file already carries, quoted rather than reworded, which
    keeps `themes/kuleuven.json` the place it is written."""
    described = part(package, "docProps/core.xml").find(f"{DC}description").text

    assert described == palette.description


# ── the shipped file against its sources ────────────────────────────────────────────────────────


def test_the_shipped_file_is_what_the_sources_pack_to(package):
    """The `.pptx` is committed the way `theme/styles/tokens.css` is: an artifact people download
    without running anything, which is exactly why nothing else would notice it going stale. Edit a
    part under `pptx/src/`, or regenerate the figure, and this fails until `pack.py` has run."""
    assert packer.pack(packer.parts()) == PACKAGE.read_bytes()
