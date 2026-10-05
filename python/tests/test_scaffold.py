"""The scaffold's half of the contract: what the skill stamps, held to the bar it stamps against.

``docs/agent-skill-contract.md`` §6 says the scaffold is review-ready from slide one, and #24 makes
the review mode itself the acceptance bar. That is a claim a script can settle, so it is settled
here rather than asserted in prose: the template deck goes through `legible lint` with its own
palette, and a stamped deck that broke a rule the canon decides by script would fail this suite
before it ever reached an author.

The rest is about drift. The template is files rather than instructions precisely so that a change
to the theme, the canon or the palette can fail here — a layout the theme grows and the scaffold
never stamps, a stylesheet that stopped following its palette, a stamped palette that drifted from
the theme's. What no test here asserts is a judgment, for the reason ``test_skill.py`` gives.
"""

import json
import re
from pathlib import Path

import pytest

from legible.css import gen_css
from legible.deck import read_deck
from legible.lint import lint
from legible.method import rules
from legible.palette import load_palette

REPO = Path(__file__).resolve().parents[2]
TEMPLATE = REPO / "skill" / "template"
SKILL = REPO / "skill" / "SKILL.md"
THEMES = REPO / "themes"

#: Where the stamped deck keeps its palette. Named for the job rather than for the palette it
#: arrives holding, so choosing another one is a change to this file's contents and to nothing that
#: names it — the checks, the stylesheet and the deck's own README all point at this path.
PALETTE = Path("themes") / "palette.json"

#: The palette it arrives holding: the project's one theme.
DEFAULT_THEME = "leuven-blue"

#: `default` is the alias `assertion-evidence` answers to rather than a fifth layout, so a skeleton
#: slide for it would be a second slide on the same layout.
LAYOUT_ALIAS = "default"

#: One slide's declared layout. The scaffold names one on every slide, including the one that could
#: leave it out: a form's blanks each say what they are.
_LAYOUT = re.compile(r"^layout:\s*(?P<layout>\S+)\s*$", re.MULTILINE)

#: The two commands the contract requires the stamped deck to hook as checks.
CHECKS = ("cvd-validate", "legible lint")

#: The review procedure's steps, which scaffold mode points at rather than repeats.
REVIEW_STEPS = (
    "## 1. Find what is under review",
    "## 2. Run the mechanical checks",
    "## 3. Render the deck, and look at every page",
    "## 4. Load the rules that need judgment",
    "## 5. Judge, slide by slide",
    "## 6. Merge into one report",
)


#: A palette named by path, wherever a stamped file names one.
_PALETTE_PATH = re.compile(r"themes/[\w.-]+\.json")

#: A rule addressed by its stable ID, which is the only way a stamped file may mention one.
_NAMED = re.compile(r"`(?P<rule>[a-z0-9-]+)`")

#: Hyphenated the way a rule ID is, and not one: the commands the stamped checks run, the two hook
#: IDs naming them, the two projects a stamped deck names, and the palette its generated stylesheet
#: names. The theme's and the palette's names are read off their own files; this project's is
#: written down, because the checkout's directory name is not it — a suite that read the name off
#: the filesystem would pass or fail on where somebody cloned to.
#: Anything opening with a dash is a flag or a custom property and is skipped rather than listed,
#: since the generated stylesheet declares one per palette role and a list would copy the token
#: contract.
NOT_RULES = frozenset(
    {
        "cvd-validate",
        "gen-css",
        "legible-lint",
        "pre-commit",
        "legible-slides",
        json.loads((REPO / "theme" / "package.json").read_text(encoding="utf-8"))["name"],
        load_palette(TEMPLATE / PALETTE).name,
    }
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _shipped_layouts() -> set[str]:
    """The layouts the theme offers a deck, asked of the theme rather than listed here — which is
    what makes a layout it grows or drops a failure in this suite rather than a surprise later."""
    return {path.stem for path in (REPO / "theme" / "layouts").glob("*.vue")} - {LAYOUT_ALIAS}


@pytest.fixture(scope="module")
def skill() -> str:
    """The router and every mode file it points at, read as one."""
    modes = sorted((SKILL.parent / "modes").glob("*.md"))
    return "\n".join(_read(path) for path in (SKILL, *modes))


@pytest.fixture(scope="module")
def slides() -> str:
    return _read(TEMPLATE / "slides.md")


@pytest.fixture(scope="module")
def palette_path() -> Path:
    return TEMPLATE / PALETTE


@pytest.fixture(scope="module")
def stamped() -> tuple[Path, ...]:
    """Every file the scaffold stamps, so a claim about the output covers all of it."""
    files = tuple(path for path in TEMPLATE.rglob("*") if path.is_file())
    assert files, "the scaffold stamps nothing"
    return files


@pytest.fixture(scope="module")
def prose(stamped) -> dict[Path, str]:
    """The stamped files an author reads as prose: the deck, and the markdown around it."""
    files = {path: _read(path) for path in stamped if path.suffix == ".md"}
    assert files, "the scaffold stamps no prose"
    return files


def test_the_stamped_deck_clears_the_mechanical_gate(palette_path):
    """The acceptance bar, and the whole of it: review-ready from slide one means the half of a
    review that gates finds nothing, on a deck nobody has written a word of yet."""
    report = lint(TEMPLATE / "slides.md", themes=[palette_path])

    assert report.passed
    assert not report.unchecked
    # Stricter than the gate on purpose, and not implied by it: `passed` tolerates a warning, and a
    # stamped deck arriving with one would be handing an author a finding they did not write.
    assert not report.findings


def test_nothing_stamped_states_a_rule_of_the_method(stamped):
    """The thin pointer reaches one file further out than ``test_skill.py`` takes it. What is
    stamped is a deck an author keeps, so a rule copied into it is a copy nobody will ever come back
    to correct — and one that would sit there, authoritative-looking, after the canon moved on. The
    template names rules by ID and points at `legible rules`, like everything else here."""
    for path in stamped:
        text = _read(path)
        for rule in rules():
            assert rule.statement not in text, f"{path.relative_to(TEMPLATE)} states `{rule.id}`"


def test_nothing_stamped_names_a_threshold(stamped):
    """The other half of the guard ``test_skill.py`` puts on the procedure. A number is the quiet
    way to copy a rule: a stamped README saying what the body size is reads as authoritative, ships
    into every deck scaffolded after it, and is wrong the day the canon is retuned."""
    for path in stamped:
        text = _read(path)
        for rule in rules():
            for key in rule.thresholds:
                assert key not in text, f"{path.relative_to(TEMPLATE)} names {key}"


def test_no_prose_the_scaffold_stamps_carries_one_of_the_canons_numbers(prose):
    """And the bare numbers, over the files an author reads rather than everything stamped.

    Prose is where a threshold gets copied. The rest of a deck is full of numbers that are nobody's
    threshold — an SVG's geometry, a version pin, a footnote's marker — and guarding those would
    buy false alarms rather than a stronger claim.
    """
    numbers = {
        value for rule in rules() for value in rule.thresholds.values() if _is_a_number(value)
    }

    for path, text in prose.items():
        body = "\n".join(line for line in text.splitlines() if not line.startswith("#"))
        # A tag's attributes are markup, not prose: a footnote's marker is `:number="1"`.
        body = re.sub(r"<[^>]*>", "", body)
        for number in numbers:
            found = re.search(rf"(?<![\w.]){re.escape(number)}(?![\w.])", body)
            assert not found, f"{path.relative_to(TEMPLATE)} carries {number}"


def _is_a_number(value: str) -> bool:
    try:
        float(value)
    except ValueError:
        return False
    return True


def test_every_rule_the_template_names_is_one_the_canon_carries(stamped):
    """Naming rules by ID has one failure mode, and it is a stale ID: a blank pointing an author at
    a rule the canon dropped teaches them to distrust the pointer."""
    stated = {rule.id for rule in rules()}
    for path in stamped:
        for named in _NAMED.finditer(_read(path)):
            rule = named.group("rule")
            if "-" in rule and not rule.startswith("-") and rule not in NOT_RULES:
                assert rule in stated, f"{path.relative_to(TEMPLATE)} names {rule}"


def test_the_stamped_palette_is_the_theme_s_own(palette_path):
    """A copy rather than a reference, because the deck is the author's and the palette is theirs to
    edit — and held to the original here, so the copy cannot start life already stale."""
    assert json.loads(_read(palette_path)) == json.loads(_read(THEMES / f"{DEFAULT_THEME}.json"))


def test_everything_stamped_points_at_the_one_palette(stamped):
    """Recolouring is a change to one file's contents precisely because nothing else changes with
    it. A stamped file naming a palette by some other path would be a second place to remember, and
    the one that gets forgotten."""
    for path in stamped:
        for named in _PALETTE_PATH.findall(_read(path)):
            assert named == PALETTE.as_posix(), f"{path.relative_to(TEMPLATE)} names {named}"


def test_the_stamped_stylesheet_is_what_its_palette_emits(palette_path):
    """The palette-to-stylesheet pipeline, wired: `legible gen-css` writes the deck's tokens and the
    stamped checks hold the two together. Committed like a lockfile, which is what lets the deck
    build import a stylesheet rather than run Python."""
    assert _read(TEMPLATE / "styles" / "tokens.css") == gen_css(load_palette(palette_path))


def test_the_deck_loads_the_stamped_stylesheet():
    """A generated file nothing imports is a pipeline that ends in a directory. The deck's own
    stylesheet entry is loaded after the theme's, so these are the colours that land."""
    assert "./tokens.css" in _read(TEMPLATE / "styles" / "index.ts")


def test_the_deck_is_wired_to_the_theme(slides):
    """The headmatter names a theme, which is the one line the whole stamp hangs off: a deck that
    named none would build in Slidev's own default and carry none of the method's machinery — and
    would still lint clean, because the linter reads slides rather than what renders them."""
    assert re.search(r"^theme:\s*\S", slides, re.MULTILINE)


def test_the_deck_sets_no_slide_transition(slides):
    """`motion-purpose`. Slidev sets none unless asked, so the stamp must not ask, and neither may
    the theme's defaults, which every deck on it inherits."""
    defaults = json.loads(_read(REPO / "theme" / "package.json"))["slidev"]["defaults"]

    assert not re.search(r"^transition:", slides, re.MULTILINE)
    assert "transition" not in defaults


def test_one_skeleton_slide_per_layout_the_theme_ships(slides):
    """The scaffold's coverage of the theme, kept honest in both directions: a layout the theme
    grows and this never stamps is a layout an author is left to discover, and a slide on a layout
    the theme dropped would not build."""
    stamped_layouts = [match.group("layout") for match in _LAYOUT.finditer(slides)]

    assert sorted(stamped_layouts) == sorted(_shipped_layouts())


def test_the_stamped_deck_stays_lean():
    """A clean start, not a worked deck. One slide per layout and not one more — the flagship is
    where the method is taught, and a scaffold that grew into a second one would be teaching it
    twice, from a file nobody reviews."""
    assert len(read_deck(TEMPLATE / "slides.md")) == len(_shipped_layouts())


@pytest.mark.parametrize("check", CHECKS)
def test_both_checks_are_hooked_in_the_stamped_deck(check):
    """The floor and the linter arrive wired, because a check an author has to remember to add is
    the one that gets added after the deck is written — which is the retrofitting this mode exists
    to make unnecessary."""
    hooks = _read(TEMPLATE / ".pre-commit-config.yaml")
    workflow = _read(TEMPLATE / ".github" / "workflows" / "method.yml")

    assert check in hooks
    assert check in workflow


def test_the_skill_carries_both_modes(skill):
    """One skill definition, two modes — the shape ``docs/agent-skill-contract.md`` §1 fixes."""
    assert "# Mode: scaffold" in skill
    assert "# Mode: review" in skill


def test_the_scaffold_does_not_restate_the_review_procedure(skill):
    """The two modes meet at the acceptance bar, which scaffold reaches by pointing at review rather
    than by carrying a copy of it. A second copy of a procedure is the same failure as a second copy
    of a rule, one file further out."""
    for step in REVIEW_STEPS:
        assert skill.count(step) == 1, step
