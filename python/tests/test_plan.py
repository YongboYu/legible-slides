"""The talk plan's worked example, and the deck build mode made from it.

``docs/talk-plan.md`` fixes what a plan holds and what a deck built from one has to match. Both are
claims a script can settle against the worked example in ``skill/examples/pmf-tsfm/``: the plan is
complete, the deck follows it slide for slide, the deck clears the mechanical checks, and the review
attached to it reports what the linter reports. Nothing here asserts a judgment, for the reason
``test_skill.py`` gives.
"""

import importlib.util
import re
from pathlib import Path

import pytest

from legible.deck import read_deck
from legible.lint import lint

REPO = Path(__file__).resolve().parents[2]
FORMAT = REPO / "docs" / "talk-plan.md"
EXAMPLE = REPO / "skill" / "examples" / "pmf-tsfm"
PLAN = EXAMPLE / "plan.md"
DECK = EXAMPLE / "deck"
REVIEW = EXAMPLE / "review.md"
#: The example is the template stamped and then filled, so it wears the palette the template stamps.
PALETTE = REPO / "skill" / "template" / "themes" / "palette.json"

#: The layouts that carry evidence, as opposed to the cover, the answer and the conclusion.
CONTENT_LAYOUTS = frozenset({"assertion-evidence", "two-col-evidence"})

#: The fields every entry carries, and the ones only an entry on a content layout does.
EVERY_ENTRY = frozenset({"Layout", "Evidence", "Time"})
CONTENT_ENTRY = frozenset({"Section", "Source"})
EVIDENCE_KINDS = frozenset(
    {"figure", "table", "equation", "callout", "subtitle", "questions", "answers"}
)

#: The setup part's beats, in the order the talk makes its case before the findings.
SETUP_BEATS = ("stakes", "difficulty", "gap", "approach")

_ENTRY = re.compile(r"^### (?P<number>\d+)\. (?P<claim>.+)$", re.MULTILINE)
_FIELD = re.compile(r"^- \*\*(?P<key>[\w-]+):\*\* ?(?P<value>.*)$", re.MULTILINE)
_NUMBERED = re.compile(r"^\s*(?P<number>\d+)\. (?P<text>.+)$", re.MULTILINE)
_IMAGE = re.compile(r'src="/(?P<path>[^"]+)"')
_STATED_IN = re.compile(r"^\s+- \*\*Stated in:\*\* (?P<where>.+)$", re.MULTILINE)
_SLIDE_REFERENCE = re.compile(r"\bslides? (?P<number>\d+)", re.IGNORECASE)


class Entry:
    """One `###` entry of the plan: its number, its claim, and the fields listed under it."""

    def __init__(self, number: int, claim: str, body: str) -> None:
        self.number = number
        self.claim = claim
        self.body = body
        self.fields = {match["key"]: match["value"] for match in _FIELD.finditer(body)}

    @property
    def layout(self) -> str:
        return self.fields["Layout"]

    @property
    def kind(self) -> str:
        return self.fields["Evidence"].split(".", 1)[0]

    @property
    def beat(self) -> str | None:
        """The setup beat the entry makes, if it is one of the setup part's."""
        setup = self.fields.get("Setup")
        return setup.rstrip(".") if setup else None

    @property
    def answers(self) -> int | None:
        """The question the entry answers, if it is one of the findings."""
        answers = self.fields.get("Answers")
        return int(answers.rstrip(".")) if answers else None


def _headmatter(text: str) -> dict[str, str]:
    block = text.split("---", 2)[1]
    return dict(
        (key.strip(), value.strip())
        for key, value in (line.split(":", 1) for line in block.strip().splitlines())
    )


def _part(text: str, heading: str) -> str:
    """Everything under one `##` heading of the plan, up to the next one."""
    match = re.search(rf"^## {heading}\n(?P<body>.*?)(?=^## |\Z)", text, re.MULTILINE | re.DOTALL)
    assert match, f"the plan has no `## {heading}`"
    return match["body"]


def _numbered(text: str) -> list[str]:
    return [match["text"] for match in _NUMBERED.finditer(text)]


@pytest.fixture(scope="module")
def plan_text() -> str:
    return PLAN.read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def entries(plan_text) -> list[Entry]:
    slides = _part(plan_text, "Slides")
    matches = list(_ENTRY.finditer(slides))
    assert matches, "the plan has no slides"
    return [
        Entry(int(match["number"]), match["claim"], slides[match.end() : following])
        for match, following in zip(
            matches, [m.start() for m in matches[1:]] + [len(slides)], strict=True
        )
    ]


@pytest.fixture(scope="module")
def questions(plan_text) -> list[str]:
    return _numbered(_part(plan_text, "Questions"))


@pytest.fixture(scope="module")
def deck():
    return read_deck(DECK / "slides.md")


@pytest.fixture(scope="module")
def deck_text() -> str:
    return (DECK / "slides.md").read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def report():
    return lint(DECK / "slides.md", themes=[PALETTE])


@pytest.fixture(scope="module")
def talk(deck):
    """The deck's slides before its backups: the ones the plan's entries are for."""
    return [slide for slide in deck if not slide.backup]


# The plan, against its format.


def test_the_plan_names_its_slot_and_its_sources(plan_text):
    headmatter = _headmatter(plan_text)

    assert {"title", "speaker", "venue", "duration", "paper", "code"} <= headmatter.keys()


def test_the_plan_numbers_its_entries_in_order(entries):
    assert [entry.number for entry in entries] == list(range(1, len(entries) + 1))


def test_every_entry_carries_the_fields_the_format_asks_for(entries):
    for entry in entries:
        assert EVERY_ENTRY <= entry.fields.keys(), entry.claim
        assert entry.kind in EVIDENCE_KINDS, entry.claim
        if entry.layout in CONTENT_LAYOUTS:
            assert CONTENT_ENTRY <= entry.fields.keys(), entry.claim


def test_the_plan_opens_on_its_answer_and_closes_on_its_conclusion(entries):
    assert [entry.layout for entry in entries[:2]] == ["cover", "answer"]
    assert entries[-1].layout == "conclusion"


def test_the_conclusion_answers_every_question_by_its_number(entries, questions):
    assert questions
    assert len(_numbered(entries[-1].fields["Evidence"] + entries[-1].body)) == len(questions)


def test_the_plan_says_what_it_cut(plan_text):
    assert _part(plan_text, "Cut").strip()


def test_every_question_says_where_the_paper_states_it(plan_text, questions):
    """The talk's questions are the paper's own, so each names the section that states it and
    quotes it, rather than being read off the tables."""
    stated = [match["where"] for match in _STATED_IN.finditer(_part(plan_text, "Questions"))]

    assert len(stated) == len(questions)
    for where in stated:
        assert re.search(r"\bSection \d", where), where
        assert re.search(r'"[^"]+"', where), where


def test_the_setup_makes_every_beat_in_order_before_the_findings(entries):
    setup = [entry for entry in entries if entry.beat]
    findings = [entry for entry in entries if entry.answers]

    assert {entry.beat for entry in setup} <= set(SETUP_BEATS)
    assert [entry.beat for entry in setup] == sorted(
        (entry.beat for entry in setup), key=SETUP_BEATS.index
    )
    assert set(SETUP_BEATS) <= {entry.beat for entry in setup}
    answer = next(entry for entry in entries if entry.layout == "answer")
    assert setup[0].number > answer.number, "the setup comes after the answer slide (answer-first)"
    assert findings and setup[-1].number < findings[0].number


def test_the_findings_answer_every_question_in_its_order(entries, questions):
    answered = [entry.answers for entry in entries if entry.answers]

    assert answered == sorted(answered)
    assert set(answered) == set(range(1, len(questions) + 1))


def test_one_entry_is_marked_as_the_slide_the_talk_rests_on(entries):
    """Which slide carries the talk is the author's to say, so the plan records their answer."""
    assert len([entry for entry in entries if "Load-bearing" in entry.fields]) == 1


def test_the_plan_says_where_it_meets_each_challenge_it_expects(plan_text, entries):
    challenges = _part(plan_text, "Challenges")

    assert re.findall(r"^- \*\*", challenges, re.MULTILINE)
    for match in _SLIDE_REFERENCE.finditer(challenges):
        assert 1 <= int(match["number"]) <= len(entries), match[0]


def test_the_format_names_every_field_the_example_uses(entries):
    documented = FORMAT.read_text(encoding="utf-8")

    for key in {key for entry in entries for key in entry.fields} | {"Stated in"}:
        assert f"**{key}**" in documented, key
    for part in ("Questions", "Challenges", "Cut"):
        assert f"### {part}" in documented, part


# The deck, against the plan it was built from.


def test_the_deck_has_one_slide_per_entry_and_its_backups_after(deck, talk, entries):
    assert len(talk) == len(entries)
    assert all(slide.backup for slide in deck[len(talk) :])


def test_every_headline_is_its_entry_s_claim_word_for_word(talk, entries):
    """The plan is the deck's source: a headline reworded on the slide alone leaves them apart."""
    for slide, entry in zip(talk, entries, strict=True):
        assert slide.headline == entry.claim, slide.number


def test_every_slide_uses_its_entry_s_layout(talk, entries):
    for slide, entry in zip(talk, entries, strict=True):
        assert (slide.layout or "default") == entry.layout, slide.number


def test_every_content_slide_sits_in_its_entry_s_section(talk, entries):
    section = None
    for slide, entry in zip(talk, entries, strict=True):
        if slide.section is not None:
            section = slide.section
        if entry.layout in CONTENT_LAYOUTS:
            assert section == entry.fields["Section"], slide.number


def test_every_slide_budgets_its_entry_s_time(talk, entries, plan_text):
    assert talk[0].duration == _headmatter(plan_text)["duration"]
    for slide, entry in zip(talk, entries, strict=True):
        assert slide.time == entry.fields["Time"], slide.number


def test_the_answer_asks_the_plan_s_questions(deck_text, questions):
    asked = deck_text.split("::questions::", 1)[1].split("---", 1)[0]

    assert _numbered(asked) == questions


def test_the_conclusion_gives_the_plan_s_answers(deck_text, entries):
    given = deck_text.split("::answers::", 1)[1].split("<!--", 1)[0]

    assert _numbered(given) == _numbered(entries[-1].body)


def test_the_built_deck_passes_the_mechanical_checks(report):
    """Build mode's own acceptance bar: the gate tier is clean. Its advisories are the review's."""

    assert report.passed, [f for f in report.findings if f.severity == "error"]


# The figures, against the script that draws them.


@pytest.fixture(scope="module")
def figures():
    spec = importlib.util.spec_from_file_location("example_figures", DECK / "figures.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_every_image_the_deck_shows_is_committed(deck_text):
    shown = _IMAGE.findall(deck_text)

    assert shown
    for path in shown:
        assert (DECK / "public" / path).is_file(), path


def test_every_image_the_deck_shows_is_drawn_by_its_figure_script(figures, deck_text, tmp_path):
    """Regenerated from data, never redrawn: no image on a slide is one the script cannot make."""
    shown = set(_IMAGE.findall(deck_text))

    drawn = figures.draw(PALETTE, tmp_path)

    assert {path.relative_to(tmp_path).as_posix() for path in drawn} == shown


# The review, against the linter.


def test_the_review_is_attached_and_reports_the_linter_s_verdict(report):
    review = REVIEW.read_text(encoding="utf-8")

    verdict = "PASS" if report.passed else "FAIL"
    assert re.search(rf"^\*\*{verdict}\*\*", review, re.MULTILINE)


def test_the_review_carries_every_finding_on_its_slide(report):
    """The mechanical half arrives verbatim. A review that lost a finding would read cleaner than
    the deck is, and a deck edited after its review would leave it describing another deck."""
    review = REVIEW.read_text(encoding="utf-8")
    groups = dict(re.findall(r"^## (Slide \d+|Deck)\b.*?\n(.*?)(?=^## |\Z)", review, re.M | re.S))

    for finding in report.findings:
        where = f"Slide {finding.slide}" if finding.slide else "Deck"
        assert where in groups, where
        assert f"**{finding.severity}** · `{finding.rule}`" in groups[where], (where, finding.rule)
        assert finding.message in groups[where], (where, finding.message)
