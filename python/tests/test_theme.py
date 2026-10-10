"""The shipped Slidev theme, against the canon it is set in.

The canon owns every number the method turns on, and `legible.method` is how this package quotes one
rather than keeping a second copy. A stylesheet and a `package.json` cannot do that: CSS has no way
to read `docs/method.md`, and the deck build is deliberately barred from running Python to find out
(``docs/slidev-reference-impl.md`` §5). So the theme writes the numbers down, and this is where the
copy is held to the original, because a hand-typed number is exactly where a copy drifts in
silence.

One claim, in both directions: change a number in the canon without changing the theme, or change
the theme's copy of one, and these tests fail naming which.
"""

import json
import re
from pathlib import Path

import pytest

from legible import headline, load_palette
from legible.contrast import contrast_ratio
from legible.method import TEXT_CONTRAST_MIN, rule, rule_thresholds

REPO = Path(__file__).resolve().parents[2]
THEME = REPO / "theme"

#: Every custom property in the theme's stylesheet that carries a canon number, against the rule and
#: the threshold key it comes from. `px` is the theme's unit and the canon's own.
DECLARED_PX = {
    "--headline-px": ("type-scale", "headline-px"),
    "--body-px": ("type-scale", "body-px"),
    "--floor-px": ("type-scale", "floor-px"),
}


@pytest.fixture(scope="module")
def stylesheet() -> str:
    return (THEME / "styles" / "layout.css").read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def chrome() -> str:
    return (THEME / "components" / "Chrome.vue").read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def cover() -> str:
    return (THEME / "layouts" / "cover.vue").read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def package() -> dict:
    return json.loads((THEME / "package.json").read_text(encoding="utf-8"))


def declared(stylesheet: str, custom_property: str) -> str:
    """One `:root` custom property's value, as the stylesheet writes it."""
    match = re.search(rf"^\s*{re.escape(custom_property)}:\s*([^;]+);", stylesheet, re.MULTILINE)
    assert match, f"the theme declares no {custom_property}"
    return match.group(1).strip()


@pytest.mark.parametrize(("custom_property", "source"), DECLARED_PX.items())
def test_the_theme_s_type_scale_is_the_canon_s(stylesheet, custom_property, source):
    rule, key = source

    assert declared(stylesheet, custom_property) == f"{rule_thresholds(rule)[key]}px"


def test_the_theme_s_headline_ceiling_is_the_canon_s(stylesheet):
    """The theme reserves the headline's zone by multiplying this out, so the ceiling it draws and
    the ceiling `headline-shape` states are one number."""
    ceiling = rule_thresholds("headline-shape")["headline-lines-max"]

    assert declared(stylesheet, "--headline-lines-max") == ceiling


def test_the_theme_s_canvas_is_the_canon_s(package):
    """The logical canvas a deck's px are written against — the same one a generated figure is sized
    in, so a chart asked for at 640 occupies 640 of the layout's units when it lands."""
    type_scale = rule_thresholds("type-scale")
    width, ratio = type_scale["canvas-width-px"], type_scale["canvas-aspect-ratio"]
    defaults = package["slidev"]["defaults"]

    assert defaults["canvasWidth"] == int(width)
    # Slidev spells a ratio with a slash; the canon spells it with a colon.
    assert defaults["aspectRatio"] == ratio.replace(":", "/")


def test_the_theme_locks_the_canon_s_colour_scheme(package):
    """`light-ground` is not a preference, so the theme does not offer it as one."""
    assert package["slidev"]["colorSchema"] == rule_thresholds("light-ground")["color-scheme"]


def test_the_theme_is_set_in_the_canon_s_families(package):
    """Declared to Slidev, so its own UI and any code block resolve to the bundled faces rather than
    to whatever the machine happens to have."""
    fonts = rule_thresholds("fonts")
    declared_fonts = package["slidev"]["defaults"]["fonts"]

    assert declared_fonts["sans"] == fonts["font-text"]
    assert declared_fonts["mono"] == fonts["font-mono"]


def test_the_theme_asks_no_font_provider_for_those_families(package):
    """The other half of `fonts`: bundled means bundled. Both families are named local, so Slidev
    excludes them from its webfont list, and no provider is consulted for anything else either."""
    fonts = rule_thresholds("fonts")
    declared_fonts = package["slidev"]["defaults"]["fonts"]

    assert declared_fonts["provider"] == "none"
    assert set(declared_fonts["local"]) == {fonts["font-text"], fonts["font-mono"]}


def _skeleton_bands() -> list[list[str]]:
    """The zones `ae-skeleton` names, top to bottom, a band per line of the diagram it draws."""
    diagram = re.search(r"```\n(.+?)\n```", rule("ae-skeleton").text, re.DOTALL)
    assert diagram, "`ae-skeleton` draws no diagram of its zones"
    return [[zone.strip() for zone in band.split("·")] for band in diagram.group(1).split("\n")]


def test_the_canon_s_skeleton_opens_on_the_headline_and_draws_nothing_under_it():
    """The zones the theme builds are the canon's: nothing above the claim, no rule between it and
    the evidence, and the locator sharing the footer with the page number."""
    assert _skeleton_bands() == [
        ["assertion headline"],
        ["evidence"],
        ["locator", "page number"],
    ]


def test_the_theme_draws_no_rule_under_the_headline(stylesheet, chrome):
    """The skeleton's zones, as the theme builds them. A rule zone left in the stylesheet, or a
    rule element left in the chrome, would draw what the canon dropped."""
    assert "--zone-rule" not in stylesheet
    assert "legible-rule" not in stylesheet
    assert "legible-rule" not in chrome
    headline = re.search(r"^\.slidev-layout h1 \{(.+?)^\}", stylesheet, re.MULTILINE | re.DOTALL)
    assert headline and "border" not in headline.group(1)


def test_the_evidence_keeps_one_gap_below_the_headline(stylesheet):
    """The whitespace that replaces the rule is one named zone, so every layout opens its evidence
    the same distance under the claim rather than wherever a margin happened to land."""
    headline = re.search(r"^\.slidev-layout h1 \{(.+?)^\}", stylesheet, re.MULTILINE | re.DOTALL)
    assert headline, "the theme styles no headline"

    assert declared(stylesheet, "--zone-headline-evidence-gap")
    assert "margin: 0 0 var(--zone-headline-evidence-gap) 0;" in headline.group(1)


def test_the_cover_is_undecorated(stylesheet, cover):
    """No bar and no glow: the cover is the title, its logos and who is speaking."""
    blocks = re.findall(r"^([^\s/*{}][^{]*)\{([^}]*)\}", stylesheet, re.MULTILINE)
    cover_rules = "".join(body for selector, body in blocks if "cover" in selector)
    assert cover_rules, "the theme styles no cover"

    assert "gradient" not in cover_rules
    assert "legible-cover-rule" not in stylesheet + cover
    assert "var(--accent)" not in cover_rules


#: The cover's two logo slots: the prop a slide sets, the `themeConfig` key a deck sets, and the
#: placeholder the theme falls back to when neither names an image.
LOGO_SLOTS = {
    "venue": ("venueLogo", "venue-logo.svg"),
    "affiliation": ("affiliationLogo", "affiliation-logo.svg"),
}


@pytest.mark.parametrize(("slot", "names"), LOGO_SLOTS.items())
def test_the_cover_exposes_each_logo_slot(cover, stylesheet, slot, names):
    key, _ = names

    assert f"{key}?: string" in cover, f"the cover takes no `{key}` prop"
    assert f"themeConfigs.{key}" in cover, f"a deck cannot set `{key}` once in themeConfig"
    assert f"legible-cover-{slot}-logo" in cover
    assert f".legible-cover-{slot}-logo" in stylesheet


@pytest.mark.parametrize(("slot", "names"), LOGO_SLOTS.items())
def test_each_logo_slot_falls_back_to_a_placeholder_the_theme_bundles(cover, slot, names):
    """Imported rather than served, so the build carries it into whatever deck names the theme: a
    theme's own `public/` is not served at a deck's root, and a fallback that pointed there would
    be a broken image on every cover that names no mark."""
    _, placeholder = names

    assert (THEME / "assets" / "placeholders" / placeholder).is_file()
    assert f"from '../assets/placeholders/{placeholder}?url'" in cover, (
        f"the {slot} slot does not fall back to its placeholder"
    )


@pytest.fixture(scope="module")
def fonts() -> str:
    return (THEME / "styles" / "fonts.css").read_text(encoding="utf-8")


def _block(stylesheet: str, selector: str) -> str:
    """The declarations of the one rule whose selector is exactly ``selector``."""
    match = re.search(rf"^{re.escape(selector)} \{{(.+?)^\}}", stylesheet, re.MULTILINE | re.DOTALL)
    assert match, f"the theme styles no {selector}"
    return match.group(1)


def test_a_content_slide_opens_on_its_headline(stylesheet):
    """Nothing is reserved above the claim any more: the headline's zone starts at the top edge's
    own gap, and no locator zone is added to it."""
    assert "--zone-locator-h" not in stylesheet
    assert "zone-locator" not in declared(stylesheet, "--zone-headline-top")


def test_the_locator_names_sections_and_carries_them_forward(chrome):
    """`section:` is the key, read off this slide and then off the slides before it. The old
    per-slide `locator:` key is read nowhere, so a deck still setting it is not silently obeyed."""
    assert "sectionAt($page.value, $frontmatter)" in chrome
    assert "for (let at = no; at >= 1; at--)" in chrome
    assert "declaring.section" in chrome
    assert "frontmatter.locator" not in chrome
    assert ").locator" not in chrome


def test_the_footer_shows_the_map_unless_the_deck_asks_for_the_label(chrome, stylesheet):
    assert "themeConfigs.locator === 'label' ? 'label' : 'map'" in chrome
    assert "legible-section-map" in chrome
    assert "legible-section-label" in chrome
    assert ".legible-section-count" in stylesheet


def test_the_locator_sits_in_the_footer(stylesheet):
    locator = _block(stylesheet, ".legible-locator")

    assert "bottom: var(--edge-bottom);" in locator
    assert "left: var(--edge-x);" in locator
    assert "top:" not in locator


def test_the_current_section_is_marked_by_weight_as_well_as_colour(stylesheet, fonts):
    """`never-sole-channel`: a reader who cannot tell the brand from the neutral still sees which
    section is bold. The weight is a face the theme bundles, never one a browser synthesises."""
    current = _block(stylesheet, ".legible-section-current")
    weight = re.search(r"font-weight: (\d+);", current)

    assert "color: var(--brand);" in current
    assert weight and weight.group(1) != "400"
    assert re.search(
        rf"font-family: 'JetBrains Mono';\s+font-style: normal;\s+font-weight: {weight.group(1)};",
        fonts,
    ), "the current section's weight is not a bundled face of the locator's family"


def test_no_locator_text_is_set_in_the_softest_neutral(stylesheet):
    """`decorative-neutral-never-text`, over every rule styling the locator and page number."""
    blocks = re.findall(r"^([^\s/*{}][^{]*)\{([^}]*)\}", stylesheet, re.MULTILINE)
    chrome_rules = [
        body
        for selector, body in blocks
        if any(name in selector for name in ("legible-locator", "legible-section", "legible-page"))
    ]
    assert chrome_rules

    assert all("--neutral-soft" not in body for body in chrome_rules)
    assert "color: var(--neutral);" in _block(stylesheet, ".legible-locator")


def test_a_backup_section_shows_its_own_label_and_no_count(chrome):
    """A backup sits outside the talk's sections: counting it would tell the room the talk had one
    more part than it gave."""
    assert "backup" in chrome
    assert re.search(r"v-if=\"[^\"]*backup", chrome), "the chrome never branches on a backup"


# ── attention ─────────────────────────────────────────────────────────────────


def _theme_sources() -> dict[str, str]:
    """Every file the theme styles anything in: its stylesheets, components and layouts."""
    paths = [*THEME.glob("styles/*.css"), *THEME.glob("**/*.vue")]
    return {
        str(path.relative_to(THEME)): path.read_text(encoding="utf-8")
        for path in paths
        if "node_modules" not in path.parts and path.name != "tokens.css"
    }


def test_the_attention_callout_is_a_fill_with_ink_on_it(stylesheet):
    """`accent-is-attention`: the fill role is a fill, and what sits on it is ink."""
    callout = _block(stylesheet, ".legible-callout.legible-callout-accent")
    title = _block(stylesheet, ".legible-callout-accent .legible-callout-title")

    assert "background: var(--accent);" in callout
    assert "color: var(--ink);" in callout
    assert "color: var(--ink);" in title
    assert "color: var(--ink);" in _block(stylesheet, ".slidev-layout .legible-callout-accent a")


def test_the_attention_callout_s_edge_is_a_stroke_the_canon_allows(stylesheet):
    """A stroke in the attention hue is drawn in the text-and-stroke role, at least as wide as the
    canon's stroke floor."""
    callout = _block(stylesheet, ".legible-callout.legible-callout-accent")
    edge = re.search(r"border-left: (\d+)px solid var\(--accent-strong\);", callout)

    floor = int(rule_thresholds("accent-is-attention")["attention-stroke-px-min"])

    assert edge, "the attention callout's edge is not an accent-strong stroke"
    assert int(edge.group(1)) >= floor


def test_the_attention_fill_is_never_text_or_a_stroke():
    """The fill colour is 2.7:1 on white: as text or a line, a projector loses it first."""
    misuse = re.compile(
        r"(?:^|[\s;{])(?:color|border(?:-[a-z]+)*|outline|stroke|fill):[^;]*var\(--accent\)"
    )
    offenders = [name for name, source in _theme_sources().items() if misuse.search(source)]

    assert offenders == []


# ── the type floor ────────────────────────────────────────────────────────────

#: The only sizes the theme may set text in: `type-scale`'s headline and body, and its floor.
SCALE = {"var(--headline-px)", "var(--body-px)", "var(--floor-px)"}

#: The deck's own stylesheet, which sizes its two demonstrations off the theme's scale.
DECK_STYLE = REPO / "deck" / "style.css"


def _font_sizes(source: str) -> list[str]:
    return [value.strip() for value in re.findall(r"font-size:\s*([^;]+);", source)]


def test_every_size_the_theme_sets_is_on_the_canon_s_scale():
    """No class sets text below the floor, because none sets it at anything but the scale's three
    sizes: a caption, a table header, the locator and the page number included."""
    sizes = {
        name: [size for size in _font_sizes(source) if size not in SCALE]
        for name, source in _theme_sources().items()
    }

    assert {name: off for name, off in sizes.items() if off} == {}


def test_the_dense_sizes_are_gone():
    """`type-scale` carries one floor and nothing under it, so no stylesheet may still name the
    sizes it used to mark as exceptions."""
    sources = {**_theme_sources(), "deck/style.css": DECK_STYLE.read_text(encoding="utf-8")}

    assert [name for name, source in sources.items() if "dense" in source] == []


#: The rules that set the template's small text: the chrome, a caption, a citation, a source line,
#: a table header. Each is text, so each colour has to clear contrast at the floor.
SMALL_TEXT = (
    ".legible-locator",
    ".legible-page",
    ".legible-figure figcaption",
    ".legible-footnote",
    ".slidev-layout .legible-reference-uri",
    ".slidev-layout th",
    ".legible-share-caption",
)


@pytest.mark.parametrize("selector", SMALL_TEXT)
def test_small_text_is_set_in_a_role_that_clears_contrast(stylesheet, themes_dir, selector):
    """`decorative-neutral-never-text`: a caption or a page number in the softest neutral is
    exactly the text the rule bans, and the floor is where contrast matters most."""
    colour = re.search(r"\bcolor: var\(--([a-z-]+)\);", _block(stylesheet, selector))
    assert colour, f"{selector} sets no colour role of its own"
    palette = load_palette(themes_dir / "leuven-blue.json")

    assert colour.group(1) != "neutral-soft"
    assert contrast_ratio(palette[colour.group(1)], palette["surface"]) >= TEXT_CONTRAST_MIN


@pytest.mark.parametrize("selector", [".legible-figure figcaption sup", ".legible-footnote-number"])
def test_a_citation_marker_in_the_small_text_is_set_at_the_floor(stylesheet, selector):
    """Both are `sup` elements, which a browser shrinks to about 80% of their parent unless told
    otherwise, and their parents already sit on the floor."""
    assert "font-size: var(--floor-px);" in _block(stylesheet, selector)


# ── the opening and the close ─────────────────────────────────────────────────


def _layout(name: str) -> str:
    return (THEME / "layouts" / f"{name}.vue").read_text(encoding="utf-8")


@pytest.mark.parametrize(("layout", "slot"), [("answer", "questions"), ("conclusion", "answers")])
def test_the_opening_and_the_close_each_have_a_layout(layout, slot):
    """`answer-first` and `conclusion-stays-up`: the result and its questions, then the questions
    answered. Each takes its numbered list in a slot of its own, so the layout can number both the
    same way and the close reads against the opening by number."""
    source = _layout(layout)

    assert f'<slot name="{slot}" />' in source
    assert "legible-numbered" in source


def test_the_questions_and_the_answers_are_numbered_alike(stylesheet):
    """The pairing is by number, so the number is text in a role that clears contrast, and a
    question and its answer wear the same one."""
    marker = _block(stylesheet, ".legible-numbered > ol > li::marker")

    assert re.search(r"content: 'Q' counter\(list-item\)", marker)
    assert "var(--neutral-soft)" not in marker


@pytest.mark.parametrize("layout", ["cover", "conclusion"])
def test_the_first_and_the_last_slide_carry_the_share_slot(layout):
    """`answer-first` puts a QR code to the slides on the cover; `conclusion-stays-up` puts it on
    the close, with the presenter's contact. One component, so the two cannot drift apart."""
    assert "<Share" in _layout(layout)


@pytest.fixture(scope="module")
def share() -> str:
    return (THEME / "components" / "Share.vue").read_text(encoding="utf-8")


@pytest.mark.parametrize("key", ["shareQr", "shareUrl", "contact"])
def test_the_share_slot_is_set_once_for_a_deck_or_per_slide(share, key):
    assert f"{key}?: string" in share, f"the share slot takes no `{key}` prop"
    assert f"themeConfigs.{key}" in share, f"a deck cannot set `{key}` once in themeConfig"


def test_the_qr_slot_falls_back_to_a_placeholder_the_theme_bundles(share):
    """Like the logo slots, and imported for the same reason: an unset slot renders as a blank to
    fill in rather than a broken image."""
    assert (THEME / "assets" / "placeholders" / "share-qr.svg").is_file()
    assert "from '../assets/placeholders/share-qr.svg?url'" in share


def test_the_qr_code_says_where_it_goes(share):
    """A QR code is an image nobody can read without a phone, so its link is also written out, and
    its alt text names it."""
    assert "legible-share-caption" in share
    assert re.search(r":alt=\"[^\"]*url", share)


def test_the_linter_wraps_a_headline_in_the_box_the_theme_sets_it_in(stylesheet):
    """`headline-shape` is measured in rendered lines, so the linter sets each headline in the
    theme's own box: its width, its weight and its tracking. A stylesheet cannot be read the way
    the canon is, so `legible.headline` writes them down, and this holds the copy to the theme."""
    h1 = re.search(r"^\.slidev-layout h1 \{(?P<body>[^}]*)\}", stylesheet, re.MULTILINE)
    assert h1, "the theme sets no headline"

    assert declared(stylesheet, "--edge-x") == f"{headline.EDGE_X_PX}px"
    assert declared(h1.group("body"), "font-weight") == str(headline.HEADLINE_WEIGHT)
    assert declared(h1.group("body"), "letter-spacing") == f"{headline.HEADLINE_TRACKING_EM}em"
    assert declared(h1.group("body"), "font-size") == "var(--headline-px)"


def test_every_file_the_theme_imports_is_in_its_published_package(package):
    """The npm archive holds only what `files` lists, so an import the list leaves out builds from
    a checkout and breaks from the registry."""
    shipped = [(THEME / entry).resolve() for entry in package["files"]]
    sources = [*THEME.glob("components/*.vue"), *THEME.glob("layouts/*.vue")]
    sources += [THEME / "slide-top.vue", *THEME.glob("styles/*.ts"), *THEME.glob("utils/*.ts")]

    imported = {
        (source.parent / match.group(1)).resolve()
        for source in sources
        for match in re.finditer(r"""import\s[^'"]*['"](\.{1,2}/[^'"?]+)""", source.read_text())
    }

    assert imported
    for path in imported:
        assert any(path == entry or entry in path.parents for entry in shipped), path
