"""The review skill's half of the contract, from the side a script can hold it to.

Two claims are testable here, and they are the two ``docs/agent-skill-contract.md`` §2 turns on.
The skill, `SKILL.md` and the mode files it routes to, carries the procedure and no rule, so
nothing in it may restate a rule's statement or one of its thresholds, and every rule it names by
ID has to be a rule the canon still carries. And the fixture deck breaks what it says it breaks,
so the review has something with a known answer to be tried against.

What no test here asserts is a judgment. Whether a slide carries one message is the reviewer's
call, and it is advisory precisely because it is fallible; asserting it would be asserting a reading
of a deck, which is the thing this repo declines to automate.
"""

import json
import re
from pathlib import Path

import pytest

from legible.lint import lint
from legible.method import rules

REPO = Path(__file__).resolve().parents[2]
SKILL = REPO / "skill" / "SKILL.md"
FIXTURES = REPO / "skill" / "fixtures"
CONTRACT = REPO / "docs" / "agent-skill-contract.md"

#: One row of the contract's coverage inventory (§4c): a rule, and what covers it.
_COVERAGE_ROW = re.compile(
    r"^\|\s*`(?P<rule>[a-z0-9-]+)`\s*\|\s*(?P<covered>[a-z, ]+?)\s*\|", re.MULTILINE
)

#: What may cover a rule, as §4c defines each.
COVERAGE = frozenset({"gate", "advisory", "theme", "review", "render", "plan", "none"})

#: One row of the fixture's table of planted violations: the slide, the rule, which half of the
#: review surfaces it, and the severity a reader should see it reported at.
_ROW = re.compile(
    r"^\|\s*(?P<slide>\d+)\s*\|\s*`(?P<rule>[a-z0-9-]+)`\s*"
    r"\|\s*(?P<found_by>\w+)\s*\|\s*(?P<severity>\w+)\s*\|",
    re.MULTILINE,
)

#: The half of the review a row belongs to. `linter` is `legible lint`'s to settle; `reading` is
#: the skill's own, and is where a rule the canon marks both lands when the deck's visual is
#: hand-made rather than generated.
LINTER, READING = "linter", "reading"

#: A rule addressed by its stable ID, which is the only way `SKILL.md` may mention one.
_NAMED = re.compile(r"`(?P<rule>[a-z0-9-]+)`")

#: Hyphenated the way a rule ID is, and not one: the command the palette check runs, the two
#: palette roles the worked report names, the Slidev directive build mode writes for a reveal, and
#: the two packages scaffold pins. Everything else shaped like a rule has to be one.
NOT_RULES = frozenset(
    {
        "cvd-validate",
        "series-1",
        "series-2",
        "v-click",
        "legible-slides",
        json.loads((REPO / "theme" / "package.json").read_text(encoding="utf-8"))["name"],
    }
)

#: The three numbers the procedure owns rather than the canon: `legible lint`'s exit codes, which
#: step 2 has to spell out to say what each of them means.
EXIT_CODES = frozenset({"0", "1", "2"})

#: The rules the v1 review judges by ID, fixed by ``docs/agent-skill-contract.md`` §4b. Its voice
#: check is a set the canon names rather than a rule, so it is asked for the way the skill asks.
SEMANTIC = (
    "one-message",
    "assertion-headline",
    "never-sole-channel",
    "no-script-on-slide",
    "established-terminology",
)


@pytest.fixture(scope="module")
def skill() -> str:
    """The whole skill as an agent can reach it: the router, then every mode file it points at."""
    modes = sorted((SKILL.parent / "modes").glob("*.md"))
    return "\n".join(path.read_text(encoding="utf-8") for path in (SKILL, *modes))


@pytest.fixture(scope="module")
def planted() -> tuple[dict[str, str], ...]:
    """Every violation the fixture's README says is planted in the fixture deck."""
    rows = tuple(match.groupdict() for match in _ROW.finditer(_read(FIXTURES / "README.md")))
    assert rows, "the fixture's README states no planted violations"
    return rows


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_the_skill_names_only_rules_the_canon_carries(skill):
    """A stale ID is the failure mode of addressing rules by ID, and the one thing that would let
    the review skip a check while still reporting a verdict."""
    stated = {rule.id for rule in rules()}
    named = {match.group("rule") for match in _NAMED.finditer(skill)}

    # Backticks carry commands and paths too, so the check is over the tokens shaped like a rule
    # ID, less the few that are legitimately something else.
    assert {name for name in named if "-" in name} - NOT_RULES <= stated


def test_the_skill_states_no_rule_of_the_method(skill):
    """The thin pointer, asserted: a rule restated in the procedure is a second copy of it, and the
    day the two disagree is the day the review enforces a rule nobody decided."""
    for rule in rules():
        assert rule.statement not in skill


def test_the_skill_names_no_threshold(skill):
    """The same claim about the numbers. A threshold is quoted at review time or not at all."""
    for rule in rules():
        for key in rule.thresholds:
            assert key not in skill


def test_the_skill_carries_none_of_the_canons_numbers(skill):
    """A threshold copied into a worked example is still a copy — it reads as authoritative, and it
    goes stale the moment the canon is retuned. Naming the key is the loud way to get this wrong;
    writing the bare number into an example report is the quiet way, and this is the check for it.

    Numbers alone, and headings and step references taken out: a rule's units and wordlists are
    words this procedure uses for its own reasons, and a heading or a step is numbered for
    navigation. `0`, `1` and `2` cannot be
    guarded here, because they are the exit codes step 2 documents.
    """
    body = "\n".join(line for line in skill.splitlines() if not line.startswith("#"))
    body = re.sub(r"\bsteps? \d+", "", body)
    numbers = {
        value for rule in rules() for value in rule.thresholds.values() if _is_a_number(value)
    }

    for number in numbers - EXIT_CODES:
        assert not re.search(rf"(?<![\w.]){re.escape(number)}(?![\w.])", body), number


def _is_a_number(value: str) -> bool:
    try:
        float(value)
    except ValueError:
        return False
    return True


def test_the_skill_names_every_rule_the_v1_review_judges(skill):
    for rule in SEMANTIC:
        assert f"`{rule}`" in skill


def test_the_voice_check_asks_the_canon_which_rules_it_covers(skill):
    """The anti-slop rules are a seed the canon says is extensible, so the skill selects them
    rather than listing them — which is what keeps a rule added there reviewed."""
    voice = rules(section="voice", decided_by="judgment")

    assert voice
    assert "--section voice --decided-by judgment" in skill
    # And it names none of them, because a list here would be the copy that goes stale.
    assert not any(f"`{rule.id}`" in skill for rule in voice)


def test_the_fixture_deck_breaks_the_mechanical_rules_its_table_claims(planted):
    """The fixture and what it is expected to produce, held together. A fixture that quietly healed
    would leave the review passing something it was built to fail — and a table that quietly grew a
    row would promise a finding nobody makes. Neither, in either direction."""
    expected = {
        (int(row["slide"]), row["rule"], row["severity"])
        for row in planted
        if row["found_by"] == LINTER
    }

    report = lint(FIXTURES / "non-compliant.md")

    assert not report.passed
    assert {(f.slide, f.rule, f.severity) for f in report.findings} == expected


def test_the_fixture_deck_plants_something_for_every_judgment_the_review_makes(planted):
    """Both halves surface on the same deck, which is what makes it a review fixture rather than a
    second set of linter fixtures."""
    judged = {row["rule"] for row in planted if row["found_by"] == READING}

    assert set(SEMANTIC) <= judged
    assert judged & {rule.id for rule in rules(section="voice", decided_by="judgment")}


def test_a_rule_the_fixture_leaves_to_a_reader_is_one_the_canon_leaves_to_one(planted):
    """The row the two halves part company on: `never-sole-channel` is marked both, and a
    hand-drawn visual is the half no script decides."""
    judgment = {rule.id for rule in rules(decided_by="judgment")}

    assert {row["rule"] for row in planted if row["found_by"] == READING} <= judgment


def test_every_rule_the_fixture_plants_is_a_rule_the_canon_carries(planted):
    stated = {rule.id for rule in rules()}

    assert {row["rule"] for row in planted} <= stated


def test_the_skill_carries_a_mode_for_every_step_from_paper_to_review(skill):
    for mode in ("draft", "build", "scaffold", "review"):
        assert f"# Mode: {mode}" in skill
        assert f"(modes/{mode}.md)" in _read(SKILL)


def test_the_skill_points_at_the_talk_plan_s_format(skill):
    """Draft and build name the plan's parts without restating them, so the format has to be
    where the skill says it is."""
    path = "docs/talk-plan.md"
    assert f"`{path}`" in skill
    assert (REPO / path).exists(), path


@pytest.fixture(scope="module")
def coverage() -> dict[str, set[str]]:
    """The contract's coverage inventory: every rule, and what covers it on an author's deck."""
    section = _read(CONTRACT).split("### 4c.", 1)[1].split("\n## ", 1)[0]
    rows = {}
    for match in _COVERAGE_ROW.finditer(section):
        assert match.group("rule") not in rows, f"`{match.group('rule')}` is listed twice"
        rows[match.group("rule")] = {part.strip() for part in match.group("covered").split(",")}
    return rows


def test_the_coverage_inventory_lists_every_rule_the_canon_carries(coverage):
    """What a PASS establishes is only legible if every rule says where it is covered. A rule added
    to the canon without a row here would read as covered when nothing covers it."""
    assert set(coverage) == {rule.id for rule in rules()}
    for rule_id, covered in coverage.items():
        assert covered <= COVERAGE, rule_id


def test_the_inventory_claims_a_gate_only_where_the_canon_decides_by_script(coverage):
    by_id = {rule.id: rule for rule in rules()}

    for rule_id, covered in coverage.items():
        if covered & {"gate", "advisory"}:
            assert "script" in by_id[rule_id].decided_by, rule_id


def test_the_skill_judges_every_rule_the_inventory_leaves_to_the_review(skill, coverage):
    """A row that says the review covers a rule is a promise the procedure has to keep. The voice
    rules are the exception the skill already makes: it asks the canon for them by section."""
    voice = {rule.id for rule in rules(section="voice")}

    for rule_id, covered in coverage.items():
        if covered & {"review", "render"} and rule_id not in voice:
            assert f"`{rule_id}`" in skill, rule_id
